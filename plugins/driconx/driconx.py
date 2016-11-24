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

_logger = getLogger('dric.driconx')

class driconxws(dric.funpass):
    def __init__(self, *args, **kwargs):
        return super(driconxws, self).__init__("driconxws-funpass", *args, **kwargs)

class ConnectionSubroutine(object):
    def __init__(self, mavlink, connection, update_driconxwsockets):
        self.mavlink = mavlink
        self.connection = connection
        self.connection['systems_last_time'] = {}
        self.connection['systems'] = []
        self.prefix = self.connection['name'] + '-'
        self.update_driconxwsockets = update_driconxwsockets

    def __call__(self, sock):
        try:
            while True:
                data = sock.recv(1024)
                sleep(0.01) # security
                try:
                    messages = self.mavlink.parse_buffer(data)
                    if messages is not None:
                        #print("{}:{}".format(time(), len(messages)))
                        for message in messages:
                            esid = self.prefix + str(message.get_srcSystem())
                            if esid not in self.connection['systems']:
                                self.connection['systems'].append(esid)
                                self.update_driconxwsockets()
                            dric.bus.publish('MAVLINK', message.get_type(), esid, message.to_dict())

                except Exception as e:
                    dric.bus.publish('MAVLINK_ERROR', e, 'ALL-255')
        except: # socket closed
            return

class DriconxPlugin(dric.Plugin):

    def __init__(self):
        self.driconxwsockets = []
        self.bindings = {}
        self.DRICONXWS_MESSAGE_HEADER = compile(r"^(/\S+)\s(.*)")
        self.connections = {}
        self.sockets = {}

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
        m = 'A'
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
                    if key == 'systems':
                        systems = etree.SubElement(e, 'systems')
                        for system_name in connection[key]:
                            system = etree.SubElement(systems, 'system')
                            system.text = unicode(system_name)
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

            return dric.Response(str(my_connection))
        except dric.exceptions.NotFound as e:
            raise e
        except Exception as e:
            raise dric.exceptions.BadRequest()

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