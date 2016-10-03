from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass
from . import Plugin

class Pass(with_metaclass(ABCMeta)):
    """
    A single pass
    """
    @abstractmethod
    def load(self, plugin):
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

def get_pass_manager():
    return _pass_manager