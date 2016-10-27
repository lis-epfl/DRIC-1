import dric
import dric.support

class DevToolPlugin(dric.Plugin):
    __plugins = {}

    def new_plugin(self, name, plugin):
        self.__plugins[name] = plugin

    @dric.route('devtools-listplugins', '/devtools/plugins')
    def listPlugins(self, request=None):
        return dric.JSONResponse(self.__plugins.keys())


class DevToolPass(dric.Pass):
    def __init__(self, listener):
        self.__listener = listener

    def load(self, plugin, name):
        self.__listener.new_plugin(name, plugin)        


dric.support.inject_content_script('/content/core/devtools/js/devtools.js')

_plugin = DevToolPlugin()
dric.get_pass_manager().add_pass(DevToolPass(_plugin))
dric.register(__name__, _plugin)