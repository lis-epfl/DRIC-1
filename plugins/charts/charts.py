import dric
from random import random
from eventlet import sleep, spawn
from math import sin, cos, radians
import sys

class SampleChartPlugin(dric.Plugin):
    @dric.datasource('Samples/rng')
    def rng_datasource(self):
        while True:
            yield random()
    rng_datasource.isTimeSerie = True

    @dric.datasource('Samples/rng2')
    def rng2_datasource(self):
        while True:
            yield -random()
    rng2_datasource.isTimeSerie = True

    @dric.datasource('SamplesTrig/sin')
    def sin_datasource(self):
        while True:
            for i in range(0, 360, 5):
                yield sin(radians(i))
    sin_datasource.isTimeSerie = True

    @dric.datasource('SamplesTrig/cos')
    def cos_datasource(self):
        while True:
            for i in range(0, 360, 5):
                yield cos(radians(i))
    cos_datasource.isTimeSerie = True

dric.register(__name__, SampleChartPlugin())



"""
    @dric.websocket('samples.charts.data', '/samples/charts/ws/rng')
    def random(self, ws, request):
        sleep_time = request.args.get('p', 1000, type=int)/1000.0

        while True:
            ws.send(str(random()))
            sleep(sleep_time)

    @dric.websocket('samples.charts.sin', '/samples/charts/ws/sin')
    def sinus(self, ws, request):
        sleep_time = request.args.get('p', 1000, type=int)/1000.0
        
        spawn(self.on_receive, ws, request)

        try:
            while ws.websocket_closed is False:
                for i in range(0, 360, 5):
                    ws.send(str(sin(radians(i))))
                    sleep(sleep_time)
        except BrokenPipeError:
            return

    def on_receive(self, ws, request):
        m = ws.wait()
        while m is not None:
            print(m)
            m = ws.wait()

    @dric.websocket('samples.charts.datasources', '/datasources')
    def datasource(self, ws, request):
        sleep_time = request.args.get('p', 1000, type=int)/1000.0
        if 's' not in request.args:
            raise dric.NotFound
        source_name = request.args.get('s', type=str)
        source = None
        if source_name == 'rng':
            source = self.rng_datasource
        elif source_name == 'sin':
            source = self.sin_datasource
        else:
            raise dric.NotFound
        try:
            for msg in source():
                strmsg = "{} {}".format(time() - start_time, msg)
                print(strmsg);
                ws.send(strmsg)
                sleep(sleep_time)
        except:
            e = sys.exc_info()[0]
            print(e)
"""