import dric
import json
import random
import string
import eventlet

from .waypoint_exceptions import *

SYSTEM = 0
CLIENT = 1
MAV_COMP_ID_MISSIONPLANNER = 190         

class Event(object):
    """ An event used to update the state of the state-machine """
    def __init__(self, src, payload, esid):
        self.src = src
        self.payload = payload
        self.esid = esid

    def __str__(self):
        return 'Event(src={}, esid={}, payload={})'.format(self.src, self.esid, self.payload)

class State(object):
    def __init__(self, name):
        self.name = name

    def next_state(self, event, environ):
        if event.src == SYSTEM:
            if event.payload.get_type() == 'MISSION_ACK':
                return IdleState()
        raise NoStateTransitionError(self, event)

class IdleState(State):
    STATE_IDLE = 'STATE_IDLE'
    def __init__(self):
        super(IdleState, self).__init__(self.STATE_IDLE)

    def next_state(self, event, environ):
        if event.src == CLIENT:
            if event.payload['command'] == 'WS_READ_LIST':
                return RequestListState(event.payload['data'])
            elif event.payload['command'] == 'WS_WRITE_LIST':
                return WriteListState(event.esid, event.payload['data'])
            elif event.payload['command'] == 'WS_CLEAR_ALL':
                return ClearAllState(event.esid)
            elif event.payload['command'] == 'WS_SET_CURRENT':
                return SetCurrentState(event.esid, event.payload['data'])
        elif event.src == SYSTEM:
            if event.payload.get_type() == 'MISSION_CURRENT':
                environ.push_mission_current(event.esid, event.payload.seq)
                return IdleState()
            elif event.payload.get_type() == 'MISSION_ITEM_REACHED':
                environ.push_mission_item_reached(event.esid, event.payload.seq)
                return IdleState()
        raise NoStateTransitionError(self, event)

class SetCurrentState(State):
    STATE_SET_CURRENT = 'STATE_SET_CURRENT'
    def __init__(self, esid, data):
        super(SetCurrentState, self).__init__(self.STATE_SET_CURRENT)
        try: target_system = int(esid.split('-')[1])
        except: raise StateInitializationError(self, 'Cannot extract target system id from esid "{}".'.format(event['esid']))
        try: seq = int(data['seq'])
        except: raise StateInitializationError(self, 'Cannot extract seq from data"{}".'.format(data))
        target_component = MAV_COMP_ID_MISSIONPLANNER
        message = {
            'target_system': target_system,
            'target_component': target_component,
            'seq': seq
        }
        dric.bus.publish('SEND_MAVLINK', esid, 'MISSION_SET_CURRENT', message)

    def next_state(self, event, environ):
        return IdleState().next_state(event, environ)

class ClearAllState(State):
    STATE_CLEAR_ALL = 'STATE_CLEAR_ALL'
    def __init__(self, esid):
        super(ClearAllState, self).__init__(self.STATE_CLEAR_ALL)
        try: target_system = int(esid.split('-')[1])
        except: raise StateInitializationError(self, 'Cannot extract target system id from esid "{}".'.format(event['esid']))
        target_component = MAV_COMP_ID_MISSIONPLANNER
        message = {
            'target_system': target_system,
            'target_component': target_component
        }
        dric.bus.publish('SEND_MAVLINK', esid, 'MISSION_CLEAR_ALL', message)

    def next_state(self, event, environ):
        if event.src == SYSTEM:
            if event.payload.get_type() == 'MISSION_ACK':
                environ.push_mission_ack(event.esid, event.payload.type)
                return IdleState()
        raise NoStateTransitionError(self, event)


class WriteListState(State):
    STATE_WRITE_LIST = 'STATE_WRITE_LIST'
    def __init__(self, esid, data):
        super(WriteListState, self).__init__(self.STATE_WRITE_LIST)
        try: target_system = int(esid.split('-')[1])
        except: raise StateInitializationError(self, 'Cannot extract target system id from esid "{}".'.format(event['esid']))
        target_component = MAV_COMP_ID_MISSIONPLANNER

        self.waypoints = data['waypoints']
        self.target_system = target_system
        self.target_component = target_component

        message = {
            'target_system': target_system,
            'target_component': target_component,
            'count': len(self.waypoints)
        }

        dric.bus.publish('SEND_MAVLINK', esid, 'MISSION_COUNT', message)

    def next_state(self, event, environ):
        return WriteState(self.target_system, self.target_component, event.esid, self.waypoints).next_state(event, environ)

class WriteState(State):
    STATE_WRITE = 'STATE_WRITE'
    def __init__(self, target_system, target_component, esid, waypoints, seq=None):
        super(WriteState, self).__init__(self.STATE_WRITE)
        self.waypoints = waypoints
        self.target_system = target_system
        self.target_component = target_component
        if seq is not None:
            message = {
                'target_system': target_system,
                'target_component': target_component,
                'seq': seq,
                'frame': waypoints[seq]['frame'],
                'command': waypoints[seq]['command'],
                'current': 0,
                'autocontinue': waypoints[seq]['autocontinue'],
                'param1': waypoints[seq]['param1'],
                'param2': waypoints[seq]['param2'],
                'param3': waypoints[seq]['param3'],
                'param4': waypoints[seq]['param4'],
                'x': waypoints[seq]['x'],
                'y': waypoints[seq]['y'],
                'z': waypoints[seq]['z']
            }
            dric.bus.publish('SEND_MAVLINK', esid, 'MISSION_ITEM', message)
        
    def next_state(self, event, environ):
        if event.src == SYSTEM:
            if event.payload.get_type() == 'MISSION_REQUEST':
                seq = event.payload.seq
                return WriteState(self.target_system, self.target_component, event.esid, self.waypoints, seq)
            elif event.payload.get_type() == 'MISSION_ACK':
                environ.push_mission_ack(event.esid, event.payload.type)
                return IdleState()
        raise NoStateTransitionError(self, event)

class RequestListState(State):
    STATE_REQLIST = 'STATE_REQLIST'
    def __init__(self, event):
        super(RequestListState, self).__init__(self.STATE_REQLIST)
        if 'esid' not in event: raise StateInitializationError(self, 'No esid specified')
        try: target_system = int(event['esid'].split('-')[1])
        except: raise StateInitializationError(self, 'Cannot extract target system id from esid "{}".'.format(event['esid']))
        target_component = MAV_COMP_ID_MISSIONPLANNER
        self.target_system = target_system
        self.target_component = target_component

        message = {
            'target_system': target_system,
            'target_component': target_component
        }

        dric.bus.publish('SEND_MAVLINK', event['esid'], 'MISSION_REQUEST_LIST', message)

    def next_state(self, event, environ):
        if event.src == SYSTEM:
            if event.payload.get_type() == 'MISSION_COUNT':
                environ.push_mission_count(event.esid, event.payload.count)
                return MissionRequest(event.esid, event.payload.count, 0, self.target_system, self.target_component)
        raise NoStateTransitionError(self, event)

class MissionRequest(State):
    STATE_REQMISSION = 'STATE_REQMISSION'
    def __init__(self, esid, count, seq, target_system, target_component):
        super(MissionRequest, self).__init__(self.STATE_REQMISSION)
        self.acknowledge = False
        self.count = count
        self.target_system = target_system
        self.target_component = target_component
        message = {
            'target_system': target_system,
            'target_component': target_component
        }
        if seq < count:
            message['seq'] = seq
            dric.bus.publish('SEND_MAVLINK', esid, 'MISSION_REQUEST', message)
        else:
            message['type'] = 0     # MAV_MISSION_SUCCESS
            self.acknowledge = True
            dric.bus.publish('SEND_MAVLINK', esid, 'MISSION_ACK', message)

    def next_state(self, event, environ):
        if not self.acknowledge:
            if event.src == SYSTEM:
                if event.payload.get_type() == 'MISSION_ITEM':
                    environ.push_mission_item(event.payload)
                    return MissionRequest(event.esid, self.count, event.payload.seq + 1, self.target_system, self.target_component)
        else:
            return IdleState().next_state(event, environ)
        raise NoStateTransitionError(self, event)

class Environ(object):
    def __init__(self, ws=None, wsl=[]):
        """
        wsl stands for websocket list
        ws is appended to wsl
        """
        self.wsl = wsl
        if ws is not None: self.wsl.append(ws)

    def push_mission_item_reached(self, esid, seq):
        message = json.dumps({
            'command': 'MISSION_ITEM_REACHED',
            'data': {
                'seq': seq
            },
            'esid': esid
        })
        for ws in self.wsl:
            ws.send(unicode(message))
    def push_mission_current(self, esid, seq):
        message = json.dumps({
            'command': 'MISSION_CURRENT',
            'data': {
                'seq': seq
            },
            'esid': esid
        })
        for ws in self.wsl:
            ws.send(unicode(message))

    def push_mission_item(self, msg):
        message = json.dumps({
            'command': 'MISSION_ITEM',
            'data': {
                'msg': str(msg)
            }
        })
        for ws in self.wsl:
            ws.send(unicode(message))
    def push_mission_count(self, esid, count):
        message = json.dumps({
            'command': 'MISSION_COUNT',
            'esid': esid,
            'data': {
                'count': count
            }
        })
        for ws in self.wsl:
            ws.send(unicode(message))

    def push_mission_ack(self, esid, type):
        message = json.dumps({
            'command': 'MISSION_ACK',
            'esid': esid,
            'data': {
                'type': type
            }
        })
        for ws in self.wsl:
            ws.send(unicode(message))

class WaypointPlugin(dric.Plugin):
    
    def __init__(self, *args, **kwargs):
        self.state = IdleState()
        self.wsl = {}

    @dric.on('MAVLINK')
    def waypointmav(self, esid, message):

        if message.get_type().startswith('MISSION'):
            print(message.get_type())
        environ = Environ(wsl=self.wsl.values())
        event = Event(SYSTEM, message, esid)
        try: self.state = self.state.next_state(event, environ)
        except NoStateTransitionError: return

    @dric.websocket('waypointws', '/map/waypoint', ['jwp'])
    def waypointws(self, ws, request):
        while True:
            myrandomkey = ''.join(random.choice(string.letters+string.digits) for _ in range(32))
            if myrandomkey not in self.wsl: break
        try:
            self.wsl[myrandomkey] = ws
            while True:
                msg = ws.wait()
                if msg is None: break
                try: parsed = json.loads(msg)
                except ValueError as e: 
                    ws.send(unicode(str(CannotParseMessageWsError(msg))))
                else:
                    if 'command' not in parsed: ws.send(unicode(str(MissingParameterWsError('command', msg))))
                    elif parsed['command'].startswith('_'):   # debug command
                        self.debug(ws, parsed)
                    elif 'data' not in parsed: ws.send(unicode(str(MissingParameterWsError('data', msg))))
                    elif 'esid' not in parsed: ws.send(unicode(str(MissingParameterWsError('esid', msg))))
                    else:
                        event = Event(CLIENT, parsed, parsed['esid'])
                        environ = Environ(ws=ws)
                        try:
                            self.state = self.state.next_state(event, environ)
                        except NoStateTransitionError as e:
                            ws.send(unicode(str(NoStateTransitionErrorWsError(msg, e))))
                        except StateInitializationError as e:
                            ws.send(unicode(str(StateInitializationErrorWsError(msg, e))))
        finally:
            self.wsl.pop(myrandomkey)

    def debug(self, ws, parsed):
        if parsed['command'] == '_GET_STATE':
            ws.send(unicode(json.dumps({'state':self.state.name})))

dric.register(__name__, WaypointPlugin())