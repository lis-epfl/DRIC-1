import dric
from dric.pg import get_plugin
from eventlet import spawn, sleep

class MavlinkHeartbeatSenderPlugin(dric.Plugin):

    def __init__(self, freq=1):
        self.interval = 1/freq

    def start(self):
        driconxplugin = dric.pg.get_plugin("driconx.driconx")
        self.connections = driconxplugin.connections
        spawn(self.send_heartbeats)


    def send_heartbeats(self):
        while(1):
            for connection in self.connections:
                esid = str(connection) + "-0"
                command_parameters = {
                    'type':int(6),               # replace hard coded
                    'autopilot': int(8),
                    'base_mode': int(0),
                    'custom_mode': int(0),
                    'system_status': int(4),
                    'mavlink_version': int(3)
                }
                dric.bus.publish('SEND_MAVLINK', esid, 'HEARTBEAT', command_parameters)
            sleep(self.interval)


dric.register(__name__, MavlinkHeartbeatSenderPlugin())