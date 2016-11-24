from . import index
import dric
from logging import getLogger

if(dric.env == 'dev'):
    dric.register('index/webpack-watch', dric.support.WebpackWatchPlugin(__file__, getLogger('dric.index.webpack')))