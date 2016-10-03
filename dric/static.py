import os.path
import mimetypes
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound
from werkzeug.wsgi import wrap_file
from io import open 

_files = {}
_dirs = {}

def add_file(pdir, f, url):
    _files[url] = os.path.join(pdir, f)

def serve_file(request=None):
    if request.path in _files:
        f = open(_files[request.path], 'rb')
        mimetype=mimetypes.guess_type(request.url)
        return Response(wrap_file(request.environ, f), mimetype=mimetype[0], content_type=mimetype[0],  direct_passthrough=True)
    
def add_dir(pdir, d, url):
    _dirs[url] = os.path.join(pdir, d)

def serve_dir(request=None, fpath=None):
    dir_url = request.path.replace(fpath, '')
    if dir_url in _dirs:
        dir_path = _dirs[dir_url]
        file_path = os.path.join(dir_path, fpath)
        if os.path.isfile(file_path):
            f = open(file_path, 'rb')
            mimetype=mimetypes.guess_type(request.url)
            
            return Response(wrap_file(request.environ, f), mimetype=mimetype[0], content_type=mimetype[0],  direct_passthrough=True)
    raise NotFound