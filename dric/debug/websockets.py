import dric
from lxml import etree

class WebSocketListPlugin(dric.Plugin):

    def __init__(self):
        self.wsl = list()

    """ This plugin show a list of routes """
    @dric.route('dric_debug_ws', '/_debug/websockets')
    def debug_routes(self, request):
        if dric.support.accept.xml_over_json(request):
            root = etree.Element('websockets')
            for endpoint, route, protocols in self.wsl:                
                e = etree.SubElement(root, 'websocket')
                e.set('endpoint', endpoint)
                e.set('route', route)
                for protocol in protocols:
                    p = etree.SubElement(e, 'protocol')
                    p.text = protocol
            return dric.Response(etree.tostring(root, xml_declaration=True, encoding='UTF-8'), content_type="application/xml")
        elif dric.support.accept.json_over_xml(request):
            return dric.JSONResponse([{'endpoint':endpoint,'route':route, 'protocols':protocols} for endpoint, route, protocols in self.wsl])
        else:
            raise dric.exceptions.NotAcceptable()

    def append(self, tuple):
        self.wsl.append(tuple)

class WebsocketPass(dric.FunPass):
    def __init__(self, target):
        self.target = target
        return super(WebsocketPass, self).__init__(pass_id=None, attr_name='ws')
    def loadfun(self, plugin, name, function, *args, **kwargs):
        tuple = (function.event, function.route, function.supported_protocols)
        self.target.append(tuple)

# register plugin
plugin = WebSocketListPlugin()
dric.register(__name__, plugin)

# register pass
dric.get_pass_manager().add_pass(WebsocketPass(plugin))