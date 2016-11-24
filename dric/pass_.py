from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass
from . import Plugin

class Pass(with_metaclass(ABCMeta)):
    """
    A single pass
    """
    @abstractmethod
    def load(self, plugin, name):
        """
        Called on each loaded plugin
        """
        pass

class _PassManager(object):
    """
Holds all the passes to be use on plugins
    """
    def __init__(self):
        # contains the passes
        self.__passes = list()

    def __iter__ (self):
        return iter(self.__passes)
    
    def add_pass(self, pass_):
        if isinstance(pass_, Pass) is False:
            raise TypeError('pass_ must be a Pass')
        self.__passes.append(pass_)
    
    def remove_pass(self, pass_):
        if isinstance(pass_, Pass) is False:
            raise TypeError('pass_ must be a Pass')
        self.__passes.remove(pass_)

_pass_manager = _PassManager()

class funpass(object):
    def __init__(self, pass_id, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pass_id = pass_id

    def __call__(self, f):
        if not hasattr(f, 'pass_info'):
            f.pass_info = {}
        f.pass_info[self.pass_id] = {'args':self.args, 'kwargs':self.kwargs}
        return f

class FunPass(Pass):

    def __init__(self, pass_id):
        self.pass_id = pass_id

    def load(self, plugin, name):
        # Iterate over all class attributes
        for method_name in dir(plugin):
            method = getattr(plugin, method_name)
            if callable(method):    # only methods
                if hasattr(method, 'pass_info'):
                    pass_info = getattr(method, 'pass_info')
                    if self.pass_id in pass_info:
                        self.loadfun(plugin, name, method, *pass_info[self.pass_id]['args'], **pass_info[self.pass_id]['kwargs'])

    def loadfun(self, plugin, name, function, *args, **kwargs):
        pass

def get_pass_manager():
    return _pass_manager