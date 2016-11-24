import dric
from dric.support import inject_content_script
import sys
from eventlet import sleep, spawn
from logging import getLogger
from werkzeug.urls import url_decode
import socket
from time import time
from operator import itemgetter
from struct import pack


_logger = getLogger('dric.dsws')

class _Helper(object):
    def __init__(self, source, ws, request, source_name, sleep_time, start_time, sid):
        self.__source = source
        self.__ws = ws
        self.__request = request
        self.__source_name = source_name
        self.__sleep_time = sleep_time
        self.__start_time = start_time
        self.__sid = sid

    def start(self):
        spawn(self.__wait_msg)
        
        buffer = []
        max_buffer_size = 5

        source = self.__source(self.__source_name)

        def message_source():
            if hasattr(source, 'withcontext') and source.withcontext:
                return source({"cid":self.__sid, "start":self.__start_time})
            else:
                return source()

        self.__ws.send(pack('!i', 200))
        for msg in message_source():
            try:
                # TIME SERIES
                if hasattr(source, 'isTimeSerie') and source.isTimeSerie:
                    event_time = time() - self.__start_time

                    buffer.append(event_time)
                    buffer.append(msg);
    
                    if len(buffer) >= max_buffer_size:
                        # BIG-ENDIAN (default for javascript's dataview)
                        # we enforce it here
                        struct_format = '!{}d'.format(len(buffer));
                        strmsg = pack(struct_format, *buffer)
                        self.__ws.send(strmsg)
                        del buffer[:]
                else:
                    self.__ws.send(msg)
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
    MAX_START_TIMES = 2

    def __init__(self):
        self.__start_times = {}

    def clean(self):
        if len(self.__start_times) > self.MAX_START_TIMES:
            # sort dict by time
            sorted_start_times = sorted(self.__start_times.items(), key=itemgetter(1))
            while len(self.__start_times) > self.MAX_START_TIMES:
                _logger.warn('Max number of client reached (%d/%d)', len(self.__start_times), self.MAX_START_TIMES)
                self.__start_times.pop(sorted_start_times.pop()[0])


# only time series
    @dric.route('datasources_list', '/dsws_datasources')
    def datasources_list(self, request):
        all = request.args.get('all', False, bool)
        out = []
        for source_name in self.sources():
            if all:
                out.append(source_name)
            elif not (hasattr(self.source(source_name), 'noplot') and self.source(source_name).noplot is True):
                out.append(source_name)
                
            
        return dric.JSONResponse(out)

    @dric.websocket('datasource', '/datasource', supported_protocols=['datasource'])
    def datasource(self, ws, request):
        try:
            sleep_time = request.args.get('p', 0, type=int)/1000.0

            if 's' not in request.args:
                raise dric.NotFound
            source_name = request.args.get('s', type=str)
            _logger.debug('Incoming connection for datasource %s', source_name)

            sid = None
            if 'sid' in request.args:
                sid = request.args.get('sid', type=str);
                if sid not in self.__start_times:
                    self.clean()
                    self.__start_times[sid] = time()
                start_time = self.__start_times[sid]
            else:
                start_time = time()

            if self.has_source(source_name) is False:
                raise dric.NotFound
            _logger.info('Serving datasource %s', source_name)

            _Helper(self.source, ws, request, source_name, sleep_time, start_time, sid).start()
        except dric.NotFound:
            ws.send(pack('!i', 404));

dric.register(__name__, DatasourceWebsocketPlugin())

inject_content_script(path='/content/core/dsws/js/datasources.js', runat='start')