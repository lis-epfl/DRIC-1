import dric
from os.path import isfile, dirname, abspath, join
from mimetypes import guess_type
from werkzeug.wsgi import wrap_file

class FaviconPlugin(dric.Plugin):
    @dric.route('favicon', '/favicon.ico')
    def serve(self, request):        
        path = join(abspath(dirname(__file__)), 'favicon.ico')
        if isfile(path):
            f = open(path, 'rb')
            mimetype = guess_type(request.url)
            
            return dric.GzipResponse(wrap_file(request.environ, f), mimetype=mimetype[0], content_type=mimetype[0],  direct_passthrough=True)
        else:
            raise dric.NotFound()

dric.register(__name__, FaviconPlugin())