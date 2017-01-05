import eventlet

def websocket(endpoint, route, supported_protocols=[]):
    def websocket_wrap(func):
        def handler(self, *args, **kwargs):
            def ws_handler_with_self(ws):
                return func(self, ws, *args, **kwargs)
            ws = eventlet.websocket.WebSocketWSGI(ws_handler_with_self)
            ws.supported_protocols = supported_protocols
            return ws
        handler.route = route
        handler.event = endpoint
        handler.supported_protocols = supported_protocols
        handler.ws = True
        return handler
    return websocket_wrap
