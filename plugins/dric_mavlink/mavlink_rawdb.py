import dric

class MavlinkRawDBPlugin(dric.Plugin):
    def __init__(self, *args, **kwargs):
        pass

    @dric.on('MAVLINK_RAW')
    def saveRaw(self, data):
        pass


dric.register(__name__, MavlinkRawDBPlugin())

