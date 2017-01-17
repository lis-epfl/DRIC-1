import os
import dric
import dric.support
from werkzeug.wsgi import wrap_file
from os.path import join, abspath, isdir
from os import listdir
from mimetypes import guess_type
from logging import getLogger

_logger = getLogger('dric.map')

@dric.support.Configurable('config.yml', 'config')
@dric.support.Configurable('maps.ini', 'maps')
class MapPlugin(dric.Plugin):

    def configure(self, cfg):
        if(cfg.id == 'config'):
            self.tiles_dir = cfg.configuration['map']['tiles']
            self.source_dir = cfg.configuration['map']['source']
            if not os.path.exists(self.tiles_dir):
                _logger.info('mkdir "%s".', abspath(self.tiles_dir))
                os.makedirs(self.tiles_dir)
            if not os.path.exists(self.source_dir): 
                _logger.info('mkdir "%s".', abspath(self.source_dir))
                os.makedirs(self.source_dir)
        elif (cfg.id == 'maps'):
            self.maps = cfg.configuration

    @dric.route('map-tiles', '/map/<string:name>/<int:z>/<int:x>/<int:y>.png')
    def serve(self, request, name, z, x, y):

        path = abspath(join(self.tiles_dir, name, str(z), str(x), str(y) + '.png'))
        try:
            f = open(path, 'rb')
            mimetype = 'image/png'
            
            return dric.Response(wrap_file(request.environ, f), mimetype=mimetype[0], content_type=mimetype[0],  direct_passthrough=True)
        except(IOError, OSError):
            raise dric.NotFound()

    @dric.route('map-tiles', '/map/full/<string:name>/<string:file>')
    def serve(self, name, file, request):
        path = abspath(join(self.source_dir, name, file))
        try:
            f = open(path, 'rb')
            mimetype = guess_type(file)
            
            return dric.Response(wrap_file(request.environ, f), mimetype=mimetype[0], content_type=mimetype[0],  direct_passthrough=True)
        except(IOError, OSError):
            raise dric.NotFound()
    
    @dric.route('map-info', '/map/<string:name>')
    def map_info(self, name, request):
        path = abspath(join(self.source_dir, name, 'info.json'))
        try:
            f = open(path, 'rb')
            mimetype = 'application/json'
            return dric.Response(wrap_file(request.environ, f), mimetype=mimetype[0], content_type=mimetype[0],  direct_passthrough=True)
        except(IOError, OSError):
            raise dric.NotFound()

    @dric.route('map-maps', '/map/maps')
    def list_maps(self, request):
        maps = list()
        for map_dir in listdir(self.source_dir):
            if(isdir(map_dir)):
                maps.append(map_dir)
        return dric.JSONResponse(listdir(self.source_dir))
    

dric.register(__name__, MapPlugin())


#dric.support.inject_content_script('/content/plugins/map/leaflet/leaflet.css')
#dric.support.inject_content_script('/content/plugins/map/leaflet/leaflet.js')