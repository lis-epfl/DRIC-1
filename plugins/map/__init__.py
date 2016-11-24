from . import map, mapslicer, position

import dric
import dric.support
if dric.env == 'dev':
    dric.register('webpack/map', dric.support.WebpackWatchPlugin(__file__))