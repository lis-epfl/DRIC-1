import dric

from logging import getLogger
from copy import deepcopy

_logger = getLogger('dric.mavlink.filtering')

def mavlink_filter(f):
    def copy(*args):
        if len(args) == 1:
            return f(deepcopy(args[0]))
        elif len(args) == 2:
            return f(args[0], deepcopy(args[1]))
        else:
            return f(args)
    copy.mavlink_filter = True
    return copy


class MavlinkFiltering(dric.Pass):
    
    def __init__(self):
        _logger.debug('Initializing mavlink.filtering')
        def identity(x):
            return x
        self.filter = identity
        _logger.debug('Done initializing mavlink.filtering')

    def decorate(self, f, g):
        def decorated(x):
            return f(g(x))
        return decorated

    def load(self, plugin, name):
        for fname in dir(plugin):
            f = getattr(plugin, fname)
            if callable(f) and hasattr(f, 'mavlink_filter') and f.mavlink_filter is True:
                _logger.debug('Composing one filter %s', str(f))
                self.filter = self.decorate(f, self.filter)

class FilterableMessage(object):
    def __init__(self, name, i, message):
        self.name = name
        self.i = i
        self.message = message
        

mavlink_filtering = MavlinkFiltering()
dric.get_pass_manager().add_pass(mavlink_filtering)