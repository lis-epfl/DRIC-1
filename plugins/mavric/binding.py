import dric

from .mavricbinding import MAVLink


class MavricBinding(dric.Plugin):
    @dric.funpass('mavlink-binding', 'mavric')
    def binding(self):
        return MAVLink

dric.register(__name__, MavricBinding())