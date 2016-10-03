
import logging
import logging.handlers
import time

class MySocketHandler(logging.handlers.SocketHandler):
    def makePickle(self, record):
        return bytearray(self.formatter.format(record) , 'utf-8')

_logger = logging.getLogger('dric')
_logger.setLevel(logging.DEBUG)

_handler = logging.StreamHandler()
_handler.setLevel(logging.DEBUG)
_handler.setFormatter(logging.Formatter('[%(levelno)s] %(message)s (%(name)s)'))
_logger.addHandler(_handler)

_handler = MySocketHandler('127.0.0.1', 28777)
_handler.setLevel(logging.DEBUG)
_handler.setFormatter(logging.Formatter('+log|dric|%(name)s|%(levelname)s|%(message)s\r\n'))
#_logger.addHandler(_handler)

from .evbus import AsyncEventBus as EventBus
from .server import Server
from .pg import start_plugins, Plugin, register
from .ld import load_plugins
from werkzeug.wrappers import Response, Request
import eventlet.websocket
from werkzeug.exceptions import NotFound, Forbidden
from .wrapper import JSONResponse, GzipResponse
from .websocket import websocket
from .pass_ import Pass, get_pass_manager
from .passes import *
from .datasource import datasource, DatasourceEndpoint
from .datasource import DatasourcePass as _DatasourcePass
from .support import route, event_listener as on

bus = EventBus()

get_pass_manager().add_pass(EventPass())
get_pass_manager().add_pass(_DatasourcePass())

def get_bus():
    return bus