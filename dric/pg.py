from collections import namedtuple
import logging
import sys
import dric
from dric.static import serve_file, serve_dir
from dric.evbus import AsyncEventBus as EventBus
from future.utils import iteritems

_plugins = dict()
_logger = logging.getLogger('dric.pg')

def register(name, plugin):
    if isinstance(plugin, Plugin):
        _plugins[name] = plugin
        _logger.info('register %s', name)
    else:
        raise TypeError('Plugin must inherit from Plugin: ' + str(type(plugin)))

def get_plugin(name):
    return _plugins[name]

def has_plugin(name):
    return name in _plugins

def start_plugins():
    # for serving static files
    dric.bus.subscribe('static_file', serve_file)
    dric.bus.subscribe('static_dir', serve_dir)
    for name, plugin in iteritems(_plugins):
        try:
            _logger.info('setup %s', name)
            _setup_plugin(plugin, name)
        except:
            _logger.error("Unexpected error: %s", sys.exc_info()[0])
            raise
    for name, plugin in iteritems(_plugins):
        try:
            _logger.info('start %s', name)
            plugin.start()
        except:
            _logger.error("Unexpected error: %s", sys.exc_info()[0])
            raise
    # Event `dric.running` is published when all plugins have been setup 
    # and started
    dric.bus.publish('dric.running')
    
def _setup_plugin(plugin, name):
    # All passes
    for pass_ in dric.get_pass_manager():
        try:
            pass_.load(plugin, name)
        except:
            _logger.error("Unexpected error while applying pass %s on plugin %s: %s", pass_, name, sys.exc_info()[0])
            raise

    plugin.setup(dric.bus)

class Plugin(object):
    def setup(self, eventbus):
        """ Initialize the plugin """
        pass
    def start(self):
        """ Called when the plugin is started """
        pass
    def stop(self):
        """ Called when the plugin is stopped """
        pass