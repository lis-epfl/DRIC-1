import dric
from lxml import etree

class RouteListPlugin(dric.Plugin):

    def __init__(self):
        self.routes = list()
    
    @dric.route('dric_debug_routes', '/_debug')
    def la(self, request):
        return dric.Response('LDOPJI')

    """ This plugin show a list of routes """
    @dric.route('dric_debug_routes', '/_debug/routes')
    def debug_routes(self, request):
        if dric.support.accept.xml_over_json(request):
            root = etree.Element('routes')
            for endpoint, route in self.routes:                
                e = etree.SubElement(root, 'route')
                e.set('endpoint', endpoint)
                e.text = route
            return dric.Response(etree.tostring(root, xml_declaration=True, encoding='UTF-8'), content_type="application/xml")
        elif dric.support.accept.json_over_xml(request):
            return dric.JSONResponse([{'endpoint':endpoint,'route':route} for endpoint, route in self.routes])
        else:
            raise dric.exceptions.NotAcceptable()

    def append(self, tuple):
        self.routes.append(tuple)

class RoutePass(dric.FunPass):
    def __init__(self, target):
        self.target = target
        return super(RoutePass, self).__init__(pass_id=None, attr_name='route')
    def loadfun(self, plugin, name, function, *args, **kwargs):
        tuple = (function.event, function.route)
        self.target.append(tuple)

# register plugin
plugin = RouteListPlugin()
dric.register(__name__, plugin)

# register pass
dric.get_pass_manager().add_pass(RoutePass(plugin))