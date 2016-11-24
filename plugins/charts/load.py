import dric
import dric.support
import subprocess
from sys import stderr, stdout
from os.path import dirname, realpath
from logging import getLogger
            

dric.support.inject_content_scripts([{'path': '/content/plugins/charts/js/bundle-charts.js'}, 
{'path':'/content/plugins/charts/node_modules/bootstrap-treeview/dist/bootstrap-treeview.min.css'}])


if(dric.env == 'dev'):
    dric.register('charts/webpack-watch', dric.support.WebpackWatchPlugin(__file__, getLogger('dric.charts.webpack')))