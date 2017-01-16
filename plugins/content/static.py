import dric
from os.path import isfile
from mimetypes import guess_type
from werkzeug.wsgi import wrap_file

class StaticContentPlugin(dric.Plugin):
    @dric.route('static-content', '/content/<path:path>')
    def serve(self, request, path):        
        if isfile(path):
            f = open(path, 'rb')
            mimetype = guess_type(request.url)
            
            return dric.GzipResponse(wrap_file(request.environ, f), mimetype=mimetype[0], content_type=mimetype[0],  direct_passthrough=True)
        else:
            raise dric.NotFound()

dric.register(__name__, StaticContentPlugin())