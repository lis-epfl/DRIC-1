import dric

from .bindings import CommonMAVLink, MinimalMAVLink, StandardMAVLink
from werkzeug.wsgi import wrap_file

ROUTE_COMMON = '/driconx/bindings/common.xml'
ROUTE_STANDARD = '/driconx/bindings/standard.xml'
ROUTE_MINIMAL = '/driconx/bindings/minimal.xml'

class DefinitionPlugin(dric.Plugin):
    @dric.route('driconx-definitions.xml', '/driconx/bindings/<definitonfile>')
    def definitions(self, definitonfile, request):
        pass
        

class CommonBinding(dric.Plugin):
    @dric.funpass('mavlink-binding', 'common')
    def binding(self):
        return CommonMAVLink
    
class StandardBinding(dric.Plugin):
    @dric.funpass('mavlink-binding', 'standard')
    def binding(self):
        return CommonMAVLink

class MinimalBinding(dric.Plugin):
    @dric.funpass('mavlink-binding', 'minimal')
    def binding(self):
        return MinimalMAVLink

def name(binding):
    return "driconx.default_bindings/{}".format(binding)

dric.register(name('common'), CommonBinding())
dric.register(name('standard'), StandardBinding())
dric.register(name('minimal'), MinimalBinding())