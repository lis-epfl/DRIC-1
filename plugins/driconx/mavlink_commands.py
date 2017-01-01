import dric
import dric.support
import random
import string
from lxml import etree

class MavCommandPlugin(dric.Plugin):

    def __init__(self, *args, **kwargs):
        self.commands = dict()
        self.subscribers = dict()

    @dric.websocket('mavlink_commands_acknowledgement', '/mavlink/command/ack', ['CMD_ACK'])
    def cmd_ack_ws(self, ws, request):
        """
        The CMD_ACK subprotocol: all commands have the form 'command:parameter1'.
            - "sub:{id}": subscribe to id. Will not subscribe if a subscriber already exists for {id}
            - "subf:{id}": force subscribe to id
            - "unsub:{id}": unsubscribe from id
            - "close:": unsubscribe from all, close connection
            - "list:{command}": unordered list. List all subscribed {id}, prefixed with {command}. Example: "ul:li" will trigger a message "li:{id}"
            - "li:{id}": list item, no action   
            - "endlist:": no more items to list
            - "nop:": nothing to do
            - "msg:{id}:{message}": message 
        """
        msg = ws.wait()
        while msg is not None:
            if msg == 'close:':
                return
            elif msg.startswith('sub:'):            # subscribe if not already subscribed
                subto = msg[len('sub:'):]
                if subto not in self.subscribers:
                    self.subscribers[subto] = ws
                    ws.send(unicode('sub:{}'.format(subto)))
                else:
                    ws.send(unicode('nop:'))
            elif msg.startswith('subf:'):            # always subscribe
                subto = msg[len('subf:'):]
                if subto in self.subscribers:
                    self.subscribers[subto].send('unsub:forced') 
                self.subscribers[subto] = ws
                ws.send(unicode('sub:{}'.format(subto)))
            elif msg.startswith('unsub:'):          # unsubscribe
                subto = msg[len('unsub:'):]
                if subto in self.subscribers:
                    self.subscribers.pop(subto)
                    ws.send(unicode('unsub:{}'.format(subto)))
                else:
                    ws.send(unicode('nop:'))
            elif msg.startswith('list:'):
                command = msg[len('list:'):]
                [ws.send(unicode('{}:{}'.format(command, key))) for key in self.subscribers if self.subscribers[key] == ws]
                ws.send(unicode('endlist:'))
            else:
                ws.send(unicode('error:malformed command "{}"'.format(msg)))
            msg = ws.wait()

    @dric.on('MAVLINK')
    def cmd_ack(self, name, esid, message):
        if name != 'COMMAND_ACK':
            return
        command = message['command']
        result = message['result']
        key = (esid, command)
        if key not in self.commands:
            return
        ack_random = self.commands[key]
        if ack_random in self.subscribers:
            self.subscribers[ack_random].send(unicode('msg:{}:{}'.format(ack_random, result)))

    @dric.route('mavlink_send_command', '/mavlink/command/<esid>/<command>')
    def send_command(self, esid, command, request):
        parameters = request.form.getlist('p[]')
        try:
            parameters = [(0 if param == '' else float(param)) for param in parameters]
        except ValueError:
            raise dric.exceptions.BadRequest('Parameters must be floats')

        try:
            target_connection, target_system = esid.split('-')
        except:
            raise dric.exceptions.BadRequest('ESID must match \'connection-system\'. Got \'{}\'.'.format(esid))

        try:
            command_id = int(command)
        except:
            raise dric.exceptions.BadRequest('Command must be an int. Got \'{}\''.format(command))

        command_parameters = {
            'target_system': int(target_system),	    # uint8_t	System which should execute the command
            'target_component': 0,	                    # uint8_t	Component which should execute the command, 0 for all components
            'command': command_id,                      # uint16_t	Command ID, as defined by MAV_CMD enum.
            'confirmation': 0,                          # uint8_t	0: First transmission of this command. 1-255: Confirmation transmissions (e.g. for kill command)
            'param1': float(parameters[0]),
            'param2': float(parameters[1]),
            'param3': float(parameters[2]),
            'param4': float(parameters[3]),
            'param5': float(parameters[4]),
            'param6': float(parameters[5]),
            'param7': float(parameters[6])
        }
        
        dric.bus.publish('SEND_MAVLINK', esid, 'COMMAND_LONG', command_parameters)
        
        ack_random = ''.join(random.choice(string.letters+string.digits) for _ in range(512))
        key = (esid, command_id)
        self.commands[key] = ack_random
        
        return dric.Response(ack_random)    # use this random to identify the reply to the command

class MavCommandPluginDebugger(dric.Plugin):
    def __init__(self):
        self.sent_commands = []

    @dric.on('SEND_MAVLINK')
    def listen(self, esid, command, parameters):
        self.sent_commands.append((esid, command, parameters))

    @dric.route('mavlink_send_command_debug', '/mavlink/debug/sent_commands')
    def send_command_debug(self, request):
        if dric.support.accept.xml_over_json(request):
            root = etree.Element('history')
            for esid, command, parameters in self.sent_commands:
                c = etree.SubElement(root, 'command')
                c.set('command', command)
                c.set('target', esid)
                if parameters is not None:
                    for name in parameters:
                        p = etree.SubElement(c, 'parameter')
                        p.set('name', str(name))
                        p.text = str(parameters[name])
            return dric.XMLResponse(root)
        elif dric.support.accept.json_over_xml(request):
            return dric.JSONResponse([{'esid': esid, 'command': command, 'parameters': parameters} for esid, command, parameters in self.sent_commands])
        else:
            raise dric.exceptions.NotAcceptable()
            

dric.register(__name__, MavCommandPlugin())
dric.register('debug_' + __name__, MavCommandPluginDebugger())