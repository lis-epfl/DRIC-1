from __future__ import absolute_import, division, print_function
from builtins import super

from eventlet import wsgi
import eventlet
from . import router
from werkzeug.wrappers import Request, Response
import logging

_logger = logging.getLogger('dric.server')
_eventlet_logger = logging.getLogger('dric.server.eventlet')
_eventlet_logger.setLevel(logging.INFO)

def funCORS(environ):
    return [('Access-Control-Allow-Origin', '*')]


def _app(environ, start_response):
    # create Request wrapper
    request = Request(environ)
    
    # dispatch request, create response
    Response.default_mimetype='text/html'
    response = router.dispatch(request)
    try:
        response.headers.add('Access-Control-Allow-Origin', '*')
    except:
        response.get_headers = funCORS
	print(type(response))
    return response(environ, start_response)

class Server(object):
    def __init__(self, bind, port):
        self.__addr = (bind, port)
        self.__wsgi_app = _app
    def start(self):
        _logger.info('WSGI server started')
        wsgi.server(eventlet.listen(self.__addr), self.__wsgi_app, log=_eventlet_logger)
        _logger.info('WSGI server stopped')