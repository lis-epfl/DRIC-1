import dric
import subprocess
from logging import getLogger
from sys import stdout, stderr
from os.path import dirname, realpath

if(dric.env == 'dev'):
    dric.register('devtools/webpack-watch', dric.support.WebpackWatchPlugin(__file__, getLogger('dric.devtools.webpack')))