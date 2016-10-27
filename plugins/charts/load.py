import dric
import dric.support
import subprocess
from sys import stderr, stdout
from os.path import dirname, realpath
from logging import getLogger
            

dric.support.inject_content_scripts([{'path': '/content/plugins/charts/js/bundle-charts.js'}, 
{'path':'/content/plugins/charts/node_modules/bootstrap-treeview/dist/bootstrap-treeview.min.css'}])


if(dric.env == 'dev'):
    _devlogger = getLogger('dric.charts.webpack')

    class WebpackWatchPlugin(dric.Plugin):
        def setup(self, eventbus):
            cwd = dirname(realpath(__file__)) 
            _devlogger.info('Start webpack --watch')
            process = subprocess.Popen(['webpack', '--watch'], stdout=stdout, stderr=stdout, cwd=cwd, shell=True)
    dric.register(__name__ + '/dev-webpack', WebpackWatchPlugin());