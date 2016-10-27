import dric
import dric.support
import dronekit
from logging import getLogger
import subprocess
from os.path import dirname, realpath
from sys import stdout, stderr
from werkzeug.exceptions import ServiceUnavailable
from eventlet import sleep, spawn_after
from logging import getLogger

_logger = getLogger('dric.dronekit')

class DronekitPlugin(dric.Plugin):

    vehicle = None
    __kill_subroutine = None

    @dric.route('dronekit-connect', '/dronekit/connect')
    def connect(self, request):
        ip = request.form.get('ip')
        try:
            self.vehicle = dronekit.connect(ip=ip, wait_ready=True, heartbeat_timeout=5)
        except dronekit.APIException as e:
            raise ServiceUnavailable(e)
        else:
            self.vehicle.add_message_listener('HEARTBEAT', self.heartbeat)
            self.vehicle.add_message_listener('*', self.forward)
            return dric.JSONResponse({'status': self.vehicle.system_status.state})
    
    def forward(self, vehicle, name, message):
        dric.bus.publish('MAVLINK', name, 255, message)

    def heartbeat(self, vehicle, name, message):
        if self.__kill_subroutine is not None:
            self.__kill_subroutine.cancel()
        self.__kill_subroutine = spawn_after(3, self.kill)

    def kill(self):
        _logger.info('No heartbeat, vehicle is dead')
        self.vehicle.close()
        self.vehicle = None

    @dric.route('dronekit-status', '/dronekit/status')
    def status(self, request):
        return dric.JSONResponse({'status': self.vehicle.system_status.state})

    @dric.datasource('dronekit-heartbeat')
    def ds_status(self):
        while True:
            if self.vehicle == None:
                yield unicode('___NOVEHICLE__')
            else:
                yield unicode(self.vehicle.mode.name)
            sleep(1)

dric.register(__name__, DronekitPlugin())

dric.support.inject_content_script('/content/plugins/dric_dronekit/js/dronekit.js')

if(dric.env == 'dev'):
    _devlogger = getLogger('dric.dronekit.webpack')

    class WebpackWatchPlugin(dric.Plugin):
        def setup(self, eventbus):
            cwd = dirname(realpath(__file__)) 
            _devlogger.info('Start webpack --watch')
            process = subprocess.Popen(['webpack', '--watch'], stdout=stdout, stderr=stdout, cwd=cwd, shell=True)
    dric.register(__name__ + '/dev-webpack', WebpackWatchPlugin());