import logging
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request, Response
import dric
from future.utils import raise_from



_logger = logging.getLogger('dric.router')
_url_map = Map()

def add(url, endpoint):
    rule = Rule(url, endpoint=endpoint)
    _url_map.add(rule)

def dispatch(request):
    urls = _url_map.bind_to_environ(request.environ)
    try:
        endpoint, args = urls.match()
    except HTTPException as e:
        return e
    args['request']=request
    try:
        rep = dric.bus.publish(endpoint, **args)
    except HTTPException as e:
        return e
    else:
        try:
            return rep[0]
        except TypeError:
            return NotFound()