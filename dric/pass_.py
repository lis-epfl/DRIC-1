from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass
from . import Plugin
from logging import getLogger

_logger = getLogger('dric.pass_')

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

    def __init__(self, pass_id=None, attr_name='pass_info'):
        """ 
        If pass_id is None, all functions with attribute 'attr_name' will be matched.
        Else, all functions with value 'pass_id' for attribute 'attr_name'.
        """
        self.pass_id = pass_id
        self.attr_name = attr_name

    def load(self, plugin, name):
        if not hasattr(self, 'loadfun') or not callable(getattr(self, 'loadfun')):
            _logger.warn('FunPass does not override member function \'funload\'. Plugin \'{}\' ignored.')
            return
        # Iterate over all class attributes
        for method_name in dir(plugin):
            method = getattr(plugin, method_name)
            if callable(method):    # only methods
                if hasattr(method, self.attr_name):
                    pass_info = getattr(method, self.attr_name)
                    if self.pass_id is not None and self.pass_id in pass_info:
                        self.loadfun(plugin, name, method, *pass_info[self.pass_id]['args'], **pass_info[self.pass_id]['kwargs'])
                    elif self.pass_id is None:
                        self.loadfun(plugin, name, method, pass_info)

    #def loadfun(self, plugin, name, function, *args, **kwargs):
    #    pass

def get_pass_manager():
    return _pass_manager