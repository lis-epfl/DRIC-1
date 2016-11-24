class AQ(object):
    def __init__(self, update_provider):
        self.__clients = []
        self.__update_provider = update_provider
    
    def incoming(self, ws):
        self.__clients.append(ws)

        m = 'A'
        while m == 'A':
            self.__send_update(ws)
            try:
                m = ws.wait()
            except:
                break

        self.__clients.remove(ws)

    def update_all(self):
        update = self.__update_provider()
        for ws in self.__clients:
            self.__send(ws, update)

    def close(self):
        for ws in self.__clients:
            try:
                ws.close()
            except:
                pass
            self.__clients.remove(ws)
            

    def __send_update(self, ws):
        update = self.__update_provider()
        self.__send(ws, update)

    def __send(self, ws, update):
        try:
            ws.send(update)
        except:
            self.__clients.remove(ws)