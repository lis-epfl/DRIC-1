import dric
import dric.support
from eventlet import sleep
from struct import pack

class PositionPlugin(dric.Plugin):

    def __init__(self, *args, **kwargs):
        self.handlers = {}

    @dric.on("MAVLINK/GLOBAL_POSITION_INT")
    def update_position(self, event):
        self.__create_handler(event.esid)
        self.handlers[event.esid].message = event.mav_message

    @dric.on("MAVLINK/LOCAL_POSITION_NED")
    def update_local(self, event):
        self.__create_handler(event.esid)
        self.handlers[event.esid].localmessage = event.mav_message

    @dric.on('MAVLINK/VFR_HUD')
    def update_hud(self, event):
        self.__create_handler(event.esid)
        self.handlers[event.esid].hudmessage = event.mav_message

    def __create_handler(self, esid):
        if esid not in self.handlers: 
            self.handlers[esid] = Handler()
            name = "map-position/global${}".format(esid)
            dric.add_datasource(name, self.handlers[esid])

class Handler(object):
    def __init__(self, sleep=0.1):
        self.noplot = True
        self.message = None
        self.hudmessage = None
        self.localmessage = None
        self.sleep = sleep

    def __call__(self):
        while True:
            if self.message is not None and self.hudmessage is not None and self.localmessage is not None:
                yield pack('!7d', 
                    self.message.lat,
                    self.message.lon,
                    self.message.alt,
                    self.hudmessage.heading,
                    self.localmessage.y,
                    self.localmessage.x,
                    self.localmessage.z
                )
            sleep(self.sleep)

dric.register(__name__, PositionPlugin())