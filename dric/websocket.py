import eventlet

def websocket(endpoint, route):
    def websocket_wrap(func):
        def handler(self, request, *args, **kwargs):
            def ws_handler_with_self(ws):
                return func(self, ws, request)
            return eventlet.websocket.WebSocketWSGI(ws_handler_with_self)
        handler.route = route
        handler.event = endpoint
        return handler
    return websocket_wrap
