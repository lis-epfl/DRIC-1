import dric

from .dronecoursebinding import MAVLink

class DronecourseBinding(dric.Plugin):
    @dric.funpass('mavlink-binding', 'dronecourse')
    def binding(self):
        return MAVLink

dric.register(__name__, DronecourseBinding())