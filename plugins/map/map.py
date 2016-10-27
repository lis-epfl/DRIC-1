import dric
import dric.support
from werkzeug.wsgi import wrap_file
from os.path import join, abspath, isdir
from os import listdir

@dric.support.Configurable('config.yml', 'config')
@dric.support.Configurable('maps.ini', 'maps')
class MapPlugin(dric.Plugin):

    def configure(self, cfg):
        if(cfg.id == 'config'):
            self.tiles_dir = cfg.configuration['map']['tiles']
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

    @dric.route('map-maps', '/map/maps')
    def list_maps(self, request):
        maps = list()
        for map_dir in listdir(self.tiles_dir):
            if(isdir(map_dir)):
                maps.append(map_dir)
        return dric.JSONResponse(listdir(self.tiles_dir))
    

dric.register(__name__, MapPlugin())

dric.support.inject_content_script('/content/plugins/map/js/map.js')

dric.support.inject_content_script('/content/plugins/map/ol/ol.js');
dric.support.inject_content_script('/content/plugins/map/ol/ol.css');

#dric.support.inject_content_script('/content/plugins/map/leaflet/leaflet.css')
#dric.support.inject_content_script('/content/plugins/map/leaflet/leaflet.js')