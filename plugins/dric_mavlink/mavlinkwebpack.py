import dric
import dric.support
from logging import getLogger

if(dric.env == 'dev'):
    dric.register('mavlink/webpack-watch', dric.support.WebpackWatchPlugin(__file__, getLogger('dric.mavlink.webpack')))