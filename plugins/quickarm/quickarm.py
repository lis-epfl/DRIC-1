import dric
import struct


class QuickArmPlugin(dric.Plugin):
    def __init__(self):
        self.handlers = {}

    @dric.route('route_quickarm_arm', '/quickarm/arm')
    def arm(self, request):
        self.__arm_disarm(request, 1)
        return dric.Response('', status=200)

    @dric.route('route_quickarm_disarm', '/quickarm/disarm')
    def disarm(self, request):
        self.__arm_disarm(request, 0)
        return dric.Response('', status=200)

    @dric.on("MAVLINK/HEARTBEAT")
    def heartbeat(self, event):
        if event.esid in self.handlers:
            message = '1' if event.mav_message.base_mode & 128 == 128 else '0'
            for ws in self.handlers[event.esid]:
                try: ws.send(unicode(message))
                except: self.handlers[event.esid].remove(ws)

    @dric.websocket('ws_quickarm', '/quickarm/ws', [])
    def websocket(self, ws, request):
        esid = request.args.get('esid', default=None, type=str)
        if esid is None: raise dric.exceptions.BadRequest('Arguments "esid" is missing.')
        if esid not in self.handlers: self.handlers[esid] = []
        self.handlers[esid].append(ws)
        ws.wait()

    def __arm_disarm(self, request, state):
        esid = request.args.get('esid', default=None, type=str)
        if esid is None: raise dric.exceptions.BadRequest('Arguments "esid" is missing.')

        try: target_system = int(esid.split('-')[1])
        except: raise dric.exceptions.BadRequest('Could not extract target system from esid "{}".'.format(esid))

        command_parameters = {
            'target_system': int(target_system),	    # uint8_t	System which should execute the command
            'target_component': 0,	                    # uint8_t	Component which should execute the command, 0 for all components
            'command': 400,
            'confirmation': 0,
            'param1': float(state),
            'param2': float(0),
            'param3': float(0),
            'param4': float(0),
            'param5': float(0),
            'param6': float(0),
            'param7': float(0),
        }
        
        dric.bus.publish('SEND_MAVLINK', esid, 'COMMAND_LONG', command_parameters)

dric.register(__name__, QuickArmPlugin())