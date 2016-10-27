import dric
import subprocess
from logging import getLogger
from sys import stdout, stderr
from os.path import dirname, realpath

if(dric.env == 'dev'):
    _devlogger = getLogger('dric.devtools.webpack')
    class WebpackWatchPlugin(dric.Plugin):
        def setup(self, eventbus):
            cwd = dirname(realpath(__file__)) 
            _devlogger.info('Start webpack --watch')
            process = subprocess.Popen(['webpack', '--watch'], stdout=stdout, stderr=stdout, cwd=cwd, shell=True)
    dric.register(__name__ + '/dev-webpack', WebpackWatchPlugin());