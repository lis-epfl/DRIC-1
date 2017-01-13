import dric
import dric.support.accept

from eventlet import spawn, sleep
from eventlet.green import socket
from time import time
from lxml import etree
from eventlet import sleep
from re import compile
from json import loads, dumps
from logging import getLogger
from hashlib import sha1
from time import time
from past.builtins import basestring
import inspect
import re

_logger = getLogger('dric.driconx')

class driconxws(dric.funpass):
    def __init__(self, *args, **kwargs):
        return super(driconxws, self).__init__("driconxws-funpass", *args, **kwargs)

class FileLikeUDPSender(object):
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
    def write(self, buf):
        print(self.address)
        self.socket.sendto(buf, self.address)

class UDPSender(object):
    def __init__(self): 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    def writer(self, address):
        return FileLikeUDPSender(self.socket, address)

class ConnectionSubroutine(object):
    def __init__(self, mavlink, connection, update_driconxwsockets):
        self.mavlink = mavlink
        self.connection = connection
        self.connection['systems_last_time'] = {}
        self.connection['systems'] = []
        self.prefix = self.connection['name'] + '-'
        self.update_driconxwsockets = update_driconxwsockets
        self.reply_socket = None
        self.connection['reply_address'] = None

    def __call__(self, sock):
        try:
            while True:
                data, address = sock.recvfrom(1024)

                self.connection['reply_address'] = address

                dric.bus.publish('MAVLINK_RAW', self.connection['name'], data, self.mavlink)
                sleep(0.0001) # security
                try:
                    messages = self.mavlink.parse_buffer(data)
                    if messages is not None:
                        #print("{}:{}".format(time(), len(messages)))
                        for mav_message in messages:
                            esid = self.prefix + str(mav_message.get_srcSystem())
                            if esid not in self.connection['systems']:
                                self.connection['systems'].append(esid)
                                self.update_driconxwsockets()
                            dric.bus.publish('MAVLINK', esid, mav_message)
                except Exception as e:
                    if e.__class__.__name__ == 'MAVError': dric.bus.publish('MAVLINK_ERROR', e, 'ALL-255')
                    else: _logger.exception('Unexpected exception')
        except Exception as e: # socket closed
            _logger.exception('Socket closed')
            return

class DriconxPlugin(dric.Plugin):

    def __init__(self):
        self.driconxwsockets = []
        self.bindings = {}
        self.DRICONXWS_MESSAGE_HEADER = compile(r"^(/\S+)\s(.*)")
        self.connections = {}
        self.sockets = {}
        self.udpsender = UDPSender()
        self.senders = {}

    def connect(self, type, address, port, binding, connection):
        typesocks = {'tcp': socket.SOCK_STREAM, 'udp': socket.SOCK_DGRAM}
        sock = socket.socket(socket.AF_INET, typesocks[type.lower()])
        sock.bind((address, int(port)))

        self.sockets[connection['name']] = sock

        mavlink_class_provider = self.bindings[binding]
        mavlink_class = mavlink_class_provider()
        mavlink = mavlink_class(None)

        spawn(ConnectionSubroutine(mavlink, connection, self.update_driconxwsockets), sock)

    @dric.websocket('driconx_connect', '/driconx/ws')
    def connectws(self, ws, request):
        self.driconxwsockets.append(ws)
        m = 'A' # send A for update
        while m == 'A':
            ws.send(unicode(dumps([self.connections[cname] for cname in self.connections])))
            m = ws.wait()
        self.driconxwsockets.remove(ws)

    def add_connection(self, connection):
        self.connections[connection['name']] = connection
        
        self.update_driconxwsockets()

    def update_driconxwsockets(self):
        update = unicode(dumps([self.connections[cname] for cname in self.connections]))
        for driconxwsocket in self.driconxwsockets:
            try:
                driconxwsocket.send(update)
            except:
                self.driconxwsockets.remove(driconxwsocket)
    
    @dric.route('driconx_list_connections', '/driconx/connections')
    def connections_list(self, request):
        if dric.support.accept.xml_over_json(request):
            root = etree.Element('connections')
            for connection_name in self.connections:
                connection = self.connections[connection_name]
                e = etree.SubElement(root, 'connection')
                for key in connection:
                    # maybe implement a visitor pattern or similar for special cases. Or make all values implement a 'toXml(parent)' function...
                    if key == 'systems':
                        systems = etree.SubElement(e, 'systems')
                        for system_name in connection[key]:
                            system = etree.SubElement(systems, 'system')
                            system.text = unicode(system_name)
                    elif key == 'reply_address':
                        reply_address_element = etree.SubElement(e, 'reply')
                        host, port = connection[key]
                        etree.SubElement(reply_address_element, 'port').text = str(port)
                        etree.SubElement(reply_address_element, 'host').text = str(host)
                    else:
                        parameter = etree.SubElement(e, key)
                        parameter.text = unicode(connection[key])
                e.set('name', connection_name)
            return dric.Response(etree.tostring(root, xml_declaration=True, encoding='UTF-8'), content_type="application/xml")
        elif dric.support.accept.json_over_xml(request):
            return dric.JSONResponse([self.connections[cname] for cname in self.connections])
        else:
            raise dric.exceptions.NotAcceptable()

    @dric.route('driconx_new_connection', '/driconx/new')
    def connection_new(self, request):
        if request.content_length > 1024 * 10:
            raise dric.exceptions.RequestEntityTooLarge()
        if request.method == 'OPTIONS':
            rep = dric.Response('', status=204)
            rep.headers['Access-Control-Allow-Methods'] ='PUT'
            return rep
        if request.method != 'PUT':
            raise dric.exceptions.MethodNotAllowed()
        try:
            connection = loads(request.get_data(as_text=True))

            connection['connection_string'] = "{}://{}:{}/{}".format(connection['type'], connection['host'], connection['port'], connection['binding'])
            connection['name'] = sha1(connection['connection_string']).hexdigest()[:10]

            try:
                self.connect(connection['type'], connection['host'], connection['port'], connection['binding'], connection)
            except Exception as e:
                _logger.warn(e)
                connection['connected'] = False
                connection['connecting'] = False
                raise dric.exceptions.Conflict('Connection already opened')

            connection['connected'] = True
            connection['connecting'] = False
            self.add_connection(connection)

            return dric.Response(str(connection))
        except dric.exceptions.Conflict as e:
            raise e
        except Exception as e:
            raise dric.exceptions.BadRequest()

    @dric.route('driconx_disconnect', '/driconx/disconnect')
    def connection_disconnect(self, request):
        if request.content_length > 1024 * 10:
            raise dric.exceptions.RequestEntityTooLarge()
        if request.method == 'OPTIONS':
            rep = dric.Response('', status=204)
            rep.headers['Access-Control-Allow-Methods'] ='POST'
            return rep
        if request.method != 'POST':
            raise dric.exceptions.MethodNotAllowed()
        try:
            connection = loads(request.get_data(as_text=True))
            
            if connection['name'] not in self.connections or connection['name'] not in self.sockets:
                raise dric.exceptions.NotFound()
            
            socket = self.sockets[connection['name']]
            socket.close()
            my_connection = self.connections[connection['name']]
            my_connection['connected'] = False
            my_connection['connecting'] = False
            
            self.update_driconxwsockets()

            return dric.Response(str(my_connection))
        except dric.exceptions.NotFound as e:
            raise e
        except Exception as e:
            raise dric.exceptions.BadRequest()

    @dric.route('driconx_delete', '/driconx/delete')
    def connection_delete(self, request):
        if request.content_length > 1024 * 10:
            raise dric.exceptions.RequestEntityTooLarge()
        if request.method == 'OPTIONS':
            rep = dric.Response('', status=204)
            rep.headers['Access-Control-Allow-Methods'] ='POST'
            return rep
        if request.method != 'POST':
            raise dric.exceptions.MethodNotAllowed()
        try:
            connection = loads(request.get_data(as_text=True))
            
            if connection['name'] not in self.connections or connection['name'] not in self.sockets:
                raise dric.exceptions.NotFound()
            
            my_connection = self.connections[connection['name']]
            self.sockets[connection['name']].close()
            self.sockets.pop(connection['name'])
            self.connections.pop(connection['name'])

            self.update_driconxwsockets()

            return dric.Response(str(my_connection))
        except dric.exceptions.NotFound as e:
            raise e
        except Exception as e:
            raise dric.exceptions.BadRequest(e)

    @dric.route("driconx_bindings_list", '/driconx/bindings')
    def route_bindings_list(self, request):
        accepted = request.accept_mimetypes.best_match(['application/xml', 'text/xml', 'application/json'])
        if accepted == 'application/xml' or accepted == 'text/xml':
            elemBindings = etree.Element("bindings")
            for binding in self.bindings:
                elemBinding = etree.SubElement(elemBindings, 'binding')
                elemBinding.text = binding
            return dric.Response(etree.tostring(elemBindings, xml_declaration=True, encoding='UTF-8'), content_type=accepted)
        elif accepted == 'application/json':
            return dric.JSONResponse([binding for binding in self.bindings])
        else:
            return dric.Response('Not acceptable', status=406)

    @dric.route('driconx_cmd_list', '/driconx/<connection>/cmd')
    def connection_cmd(self, connection, request):
        """ show all available commands for the connection """
        connection = connection.split("-")[0]   # also accept esid
        if connection not in self.connections:
            raise dric.exceptions.NotFound("Connection '{}' not found".format(connection))
        binding_name = self.connections[connection]['binding']
        if binding_name not in self.bindings:
            raise dric.exceptions.NotFound("Binding '{}' not found".format(binding_name))
        
        binding = self.bindings[binding_name]()(None)
        module = inspect.getmodule(binding)
        output = []
        for cmd in module.enums['MAV_CMD']:
            entry = module.enums['MAV_CMD'][cmd]
            output.append({'name':entry.name, 'id':cmd, 'description':entry.description, 'param':entry.param})

        if dric.support.accept.xml_over_json(request):
            root = etree.Element('commands')
            root.set('connection', connection)
            root.set('binding', binding_name)
            for entry in output:
                c = etree.SubElement(root, 'command')
                c.set('name', entry['name'])
                c.set('id', str(entry['id']))
                d = etree.SubElement(c, 'description')
                d.text = entry['description']
                for key in entry['param']:
                    p = etree.SubElement(c, 'parameter')
                    p.set('index', str(key))
                    p.text = entry['param'][key]
            return dric.XMLResponse(root)
        elif dric.support.accept.json_over_xml(request):
            return dric.JSONResponse(output)
        else:
            raise dric.exceptions.NotAcceptable()

    @dric.route('driconx_enum_list', '/driconx/<connection>/enums/<enum>')
    def connection_enums(self, connection, enum, request):
        """ show all command in enum for the connection """
        connection = connection.split("-")[0]   # also accept esid
        if connection not in self.connections:
            raise dric.exceptions.NotFound("Connection '{}' not found".format(connection))
        binding_name = self.connections[connection]['binding']
        if binding_name not in self.bindings:
            raise dric.exceptions.NotFound("Binding '{}' not found".format(binding_name))

        binding = self.bindings[binding_name]()(None)
        module = inspect.getmodule(binding)        
        if enum not in module.enums: raise dric.exceptions.NotFound
        output = []
        for cmd in module.enums[enum]:
            entry = module.enums[enum][cmd]
            if entry.name == '{}_ENUM_END'.format(enum): continue
            output.append({'name':entry.name, 'id':cmd, 'description':entry.description, 'param':entry.param})        
        
        if dric.support.accept.xml_over_json(request):
            root = etree.Element('commands')
            root.set('connection', connection)
            root.set('binding', binding_name)
            for entry in output:
                c = etree.SubElement(root, 'command')
                c.set('name', entry['name'])
                c.set('id', str(entry['id']))
                d = etree.SubElement(c, 'description')
                d.text = entry['description']
                for key in entry['param']:
                    p = etree.SubElement(c, 'parameter')
                    p.set('index', str(key))
                    p.text = entry['param'][key]
            return dric.XMLResponse(root)
        elif dric.support.accept.json_over_xml(request):
            return dric.JSONResponse(output)
        else:
            raise dric.exceptions.NotAcceptable()
        

    @dric.on('SEND_MAVLINK')
    def send_mav_cmd(self, esid, command, parameters):
        if esid not in self.senders:
            self.senders[esid] = self.get_binding_for_esid(esid)
        binding = self.senders[esid]
        module = inspect.getmodule(binding)

        # if command is a string, try to find the corresponding id#
        if isinstance(command, basestring):
            command_id_name = 'MAVLINK_MSG_ID_{}'.format(command)

            if not hasattr(module, command_id_name):
                raise ValueError('No such command: "{}".'.format(command_id_name))

            command = getattr(module, command_id_name)
        
        # with command the command id, find the corresponding message class from the map
        if command not in module.mavlink_map:
            raise KeyError('Command id "{}" not found in mavlink map.'.format(command))
        message_class = module.mavlink_map[command]

        # reorder parameters, and keep only values
        parameters = [parameters[param_name] for param_name in message_class.fieldnames]

        # send message
        binding.send(message_class(*parameters))

    def get_binding_for_esid(self, esid):
        connection_name, system_id = esid.split('-')
        if connection_name not in self.connections:
            raise dric.exceptions.NotFound("Connection '{}' not found".format(connection_name))
        binding_name = self.connections[connection_name]['binding']
        socket = self.sockets[connection_name]
        if binding_name not in self.bindings:
            raise dric.exceptions.NotFound("Binding '{}' not found".format(binding_name))
        reply_address = self.connections[connection_name]['reply_address']
        return self.bindings[binding_name]()(self.udpsender.writer(reply_address), srcSystem=255)
        
driconxplugin = DriconxPlugin()
dric.register(__name__, driconxplugin)

class BindingFunPass(dric.FunPass):
    def __init__(self, pass_id, target):
        self.target = target
        return super(BindingFunPass, self).__init__(pass_id)
    def loadfun(self, plugin, name, function, binding_name):
        self.target.bindings[binding_name] = function

dric.get_pass_manager().add_pass(BindingFunPass('mavlink-binding', driconxplugin))

class DriconxwsFunPass(dric.FunPass):
    def __init__(self, pass_id, target):
        self.target = target
        return super(DriconxwsFunPass, self).__init__(pass_id)
    def loadfun(self, plugin, name, function, action):
        self.target.driconxwshandlers[action] = function

dric.get_pass_manager().add_pass(DriconxwsFunPass('driconxws-funpass', driconxplugin))

dric.support.inject_content_script('/content/plugins/driconx/dist/driconx.js')
dric.support.inject_content_script('/content/plugins/driconx/css/driconx.css')