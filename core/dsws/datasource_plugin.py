import dric
from dric.support import inject_content_script
import sys
from eventlet import sleep, spawn
from logging import getLogger
from werkzeug.urls import url_decode
import socket

_logger = getLogger('dric.dsws')

class _Helper(object):
    def __init__(self, source, ws, request, source_name, sleep_time):
        self.__source = source
        self.__ws = ws
        self.__request = request
        self.__source_name = source_name
        self.__sleep_time = sleep_time

    def start(self):
        spawn(self.__wait_msg)

        
        for msg in self.__source(self.__source_name)():
            try:
                self.__ws.send(str(msg))
            except socket.error as e:
                return
            sleep(self.__sleep_time)
    
    def __wait_msg(self):
        m = self.__ws.wait()
        while m is not None:            
            self.__on_receive(m)
            m = self.__ws.wait()
    
    def __on_receive(self, m):
        query = url_decode(m)
        if(query.has_key('s')):
            self.__source_name = query.get('s', type=str)
        if(query.has_key('p')):
            p = query.get('p', type=int) / 1000.0
            if p > 0:
                self.__sleep_time = p
        


class DatasourceWebsocketPlugin(dric.Plugin, dric.DatasourceEndpoint):

    @dric.route('datasources_list', '/dsws_datasources')
    def datasources_list(self, request):
        return dric.JSONResponse(self.sources())

    @dric.websocket('datasource', '/datasource')
    def datasource(self, ws, request):
        sleep_time = request.args.get('p', 1000, type=int)/1000.0
        if 's' not in request.args:
            raise dric.NotFound
        source_name = request.args.get('s', type=str)

        if self.has_source(source_name) is False:
            raise dric.NotFound
        _logger.info('Serving datasource %s', source_name)

        _Helper(self.source, ws, request, source_name, sleep_time).start()
        
    


dric.register(__name__, DatasourceWebsocketPlugin())

inject_content_script(path='/content/core/dsws/js/datasources.js', runat='start')