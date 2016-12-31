import dric
import dric.support
from lxml import etree

class MavCommandPlugin(dric.Plugin):
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
        
        dric.bus.publish('send_MAV_CMD', esid, 'COMMAND_LONG', command_parameters)
        return dric.Response('', status=204)

class MavCommandPluginDebugger(dric.Plugin):
    def __init__(self):
        self.sent_commands = []

    @dric.on('send_MAV_CMD')
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