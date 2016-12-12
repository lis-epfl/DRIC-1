import dric

from re import compile


class Handler(object):
    def __init__(self, ws):
        self.ws = ws

    def push(self, e):
        try:
            self.ws.send(unicode(e))
        except Exception as err:
            self.ws.close()

class MAVLinkErrorPlugin(dric.Plugin):
    
    def __init__(self):
        self.handlers = {}
        self.ESID = compile(r'^(.+)-(.+)$')
    
    @dric.websocket('mavlink_error_ws', '/mavlink/errors/<esid>')
    def maverror_ws(self, ws, esid, request):
        channel, system = self.parse(esid)

        if channel not in self.handlers:
            self.handlers[channel] = {}
        if system not in self.handlers[channel]:
            self.handlers[channel][system] = []
        self.handlers[channel][system].append(Handler(ws))
        ws.wait()

    @dric.on("MAVLINK_ERROR")
    def maverror(self, e, esid):
        channel, system = self.parse(esid)
        
        if '*' in self.handlers and '*' in self.handlers['*']:
            for handler in self.handlers['*']['*']:
                try:
                    handler.push(e)
                except:
                    self.handlers['*']['*'].remove(handler)

        if channel in self.handlers and '*' in self.handlers[channel]:
            for handler in self.handlers[channel]['*']:
                try:
                    handler.push(e)
                except:
                    self.handlers[channel]['*'].remove(handler)

        if channel in self.handlers and system in self.handlers[channel]:
            for handler in self.handlers[channel][system]:
                try:
                    handler.push(e)
                except:
                    self.handlers[channel][system].remove(handler)

    def parse(self, esid):
        match = self.ESID.match(esid)
        if not match:
            raise dric.exceptions.BadRequest()

        channel = match.group(1)
        system  = match.group(2)
        return channel, system

dric.register(__name__, MAVLinkErrorPlugin())