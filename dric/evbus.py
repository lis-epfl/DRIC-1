from __future__ import absolute_import, division, print_function
from builtins import super

from eventlet.greenpool import GreenPool
import eventlet.greenthread
import eventlet

eventlet.monkey_patch()

def join_append_to_list(joined, elem):
    if joined is None:
        joined = []
    joined.append(elem)
    return joined

def join_append_to_str(joined, elem):
    if joined is None:
        joined = ''
    joined += elem
    return joined

class EventBus(object):
    def __init__(self):
        self.listeners = {}
        return super().__init__()
    def subscribe(self, event, listener, allow_duplicates=False):
        if event not in self.listeners:
            self.listeners[event] = []
        if allow_duplicates is False and listener in self.listeners[event]:
            raise DuplicateListenerError(event, listener)
        self.listeners[event].append(listener)
    def unsubscribe(self, event, listener):
        if event not in self.listeners:
            return
        self.listeners[event].remove(listener)
    def publish(self, event, *args, **kwargs):
        if event not in self.listeners:
            return
        join=join_append_to_list
        joined = None
        for listener in self.listeners[event]:
            joined = join(joined, listener(*args, **kwargs))
        return joined

class AsyncMixin(object):
    def __init__(self):
        self.pool = GreenPool()
    def publish_async(self, event, callback, *args, **kwargs):
        return self.pool.spawn(self.__publish_async, event, callback, *args, **kwargs)

    def __publish_async(self, event, callback, *args, **kwargs):
        if event not in self.listeners:
            return
        for listener in self.listeners[event]:
            self.pool.spawn(self.__worker(listener, callback), *args, **kwargs)

    def __worker(self, listener, callback):
        def worker(*args, **kwargs):
            callback(listener(*args, **kwargs))
        return worker

class AsyncEventBus(EventBus, AsyncMixin):
    def __init__(self):
        return super().__init__()

class DuplicateListenerError(Exception):
    def __init__(self, event, listener):
        self.event = event
        self.listener = listener
