"""
Plugin support library
"""

import dric
from hashlib import sha1

class ContentScriptInjector(dric.Plugin):
    def __init__(self, content_scripts):
        self.__content_scripts = content_scripts
        
    def setup(self, eventbus):
        self.__eventbus = eventbus
        self.__eventbus.subscribe('index.contentscript', self.inject)

    def inject(self):
        return self.__content_scripts;

def inject_content_script(path, runat='async'):
    name = __name__ + '-content-script-' + path
    dric.register(name, ContentScriptInjector({'path':path, 'runat':runat}))


def route(endpoint, route):
    """
    A function decorator for request handlers
    """
    def route_decorator(func):
        func.route = route
        func.event = endpoint
        return func
    return route_decorator

def event_listener (event):
    """
    A fuction decorator for event listeners
    """
    def on_decorator(func):
        func.event = event
        return func
    return on_decorator