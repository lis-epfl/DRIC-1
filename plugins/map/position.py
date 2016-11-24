import dric
import dric.support
from eventlet import sleep
from struct import pack

class PositionPlugin(dric.Plugin):

    def __init__(self, *args, **kwargs):
        self.x = 0
        self.y = 0

    @dric.on("MAVLINK/LOCAL_POSITION_NED")
    def update_position(self, id, message):
        self.x = message[x]
        self.y = message[y]
        print("received" + str(self.x) + " " +str(self.y))

    @dric.support.datasource.noplot()
    @dric.datasource("mavlink/localposition")
    def localpositiondatasource(self):
        while True:
            yield pack('!dd', float(self.x), float(self.y));
            sleep(1)

dric.register(__name__, PositionPlugin())