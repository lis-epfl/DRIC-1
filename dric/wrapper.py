from werkzeug.wrappers import BaseResponse, Request
from json import dumps
from builtins import super
import StringIO
import gzip

class JSONResponse(BaseResponse):
    def __init__(self, response=None, status=None, headers=None, mimetype=None, content_type=None, direct_passthrough=False):
        content = dumps(response)
        if mimetype is None:
            mimetype = 'application/json'
        if content_type is None:
            content_type = 'application/json'
        
        super().__init__(response=content, status=status, headers=headers, mimetype=mimetype, content_type=content_type, direct_passthrough=direct_passthrough)
        
class GzipResponse(BaseResponse):
    
    def __init__(self, response=None, status=None, headers=None, mimetype=None, content_type=None, direct_passthrough=False):        
        super().__init__(response=response, status=status, headers=headers, mimetype=mimetype, content_type=content_type, direct_passthrough=direct_passthrough)

    def __call__(self, environ, start_response):
        # First, check if client supports Gzip compression
        request = Request(environ)
        if('gzip' not in request.accept_encodings):
            return super().__call__(environ, start_response)   # no gzip

        # retrieve the response to be gzipped and intercept the headers
        start_response_interceptor = StartResponseInterceptor()
        raw = super().__call__(environ, start_response_interceptor);

        if(self.__class__.should_gzip(start_response_interceptor.response_headers) is True):            
            # compression
            raw = ''.join(raw)
            gzipped = StringIO.StringIO()
            gzip_file = gzip.GzipFile(None, 'wb', 9, gzipped)
            gzip_file.write(raw)
            gzip_file.close()

            # change the header to add the gzip content-encoding header and the content-length header
            start_response_interceptor.response_headers.append(('content-encoding', 'gzip'))
            start_response_interceptor.response_headers.append(('content-length', str(len(gzipped.getvalue()))))

            ret = [gzipped.getvalue()]
        else:
            ret = raw

        # forward everything to supplied start_response callable
        write = start_response(start_response_interceptor.status, start_response_interceptor.response_headers, start_response_interceptor.exc_info)

        # for old APIs 
        if(start_response_interceptor.body is not None):
            write(start_response_interceptor.body)

        return ret;

    @staticmethod
    def should_gzip(headers):
        GZIPABLE_TYPES = ['application/javascript', 'text/javascript', 'text/plain', 'text/css', 'text/html']
        for header in headers:
            if(header[0].lower() == 'content-type'):
                return header[1] in GZIPABLE_TYPES

class StartResponseInterceptor(object):    
    
    def __init__(self, *args, **kwargs):
        self.status = None
        self.response_headers = None
        self.exc_info = None
        self.body = None

    def __call__(self, status, response_headers, exc_info=None):
        self.status = status
        self.response_headers = response_headers
        self.exc_info = exc_info
        
        def write():
            self.body = body
        
        return write