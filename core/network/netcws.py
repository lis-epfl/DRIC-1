"""
Manage clients.
"""


import dric
import json
from threading import Lock
from threading import Timer
from future.utils import itervalues
from eventlet import spawn, sleep
import socket

class NetClient(object):
    def __init__(self, ip, name):
        self.ip = ip
        self.name = name
        self.close = False
        self.messages = []    

class NamesManager(object):
    def __init__(self):
       self.__NAMES = ['ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO', 'FOXTROT', 'GOLF' 'HOTEL', 'INDIA', 'JULIET', 'KILO', 'LIMA', 'MIKE', 'NOVEMBER', 'OSCAR', 'PAPA', 'QUEBEC', 'ROMEO', 'SIERRA', 'TANGO', 'UNIFORM', 'VICTOR', 'WHISKEY', 'X-RAY', 'YANKEE', 'ZULU']
    
    def get(self):
         return self.__NAMES.pop(0)
    
    def free(self, n):
        self.__NAMES.insert(0, n)
        
        
class NetClientManager(dric.Plugin):    
    def setup(self, ebus):
        self.__clients = {}
        self.__names = NamesManager()
    
    @dric.websocket('network.ws', '/network/ws')
    def network_ws(self, ws, request):
        #connected
        client = NetClient(request.remote_addr, self.__names.get())
        self.add_client(client)

        #send info
        msg = 'Y'
        msg += json.dumps({'ip': client.ip,'name': client.name});
        ws.send(msg)
        #wait or disconnection loop
        spawn(self.wait_for_disconnect, ws, client)
    
        try:
            while client.close is False:
                while(len(client.messages) > 0):
                    ws.send(client.messages.pop(0))
                sleep(1)
        except socket.error as e:
            print(e)
        finally:
            #disconnected
            self.remove_client(client)


    @dric.route('network.clients', '/network/clients')
    def clients(self, request=None):
        clients = []
        for client_name in self.__clients:
            client = self.__clients[client_name];
            clients.append({
                           'name': client.name, 
                           'ip': client.ip
                           })
        return dric.JSONResponse(clients)

    def wait_for_disconnect(self, ws, client):
        while True:
            if ws.wait() is None:
                client.close = True
                return

    def add_client(self, client):
        self.__clients[client.name] = client;
        for client_name in self.__clients:
            self.__clients[client_name].messages.append("C{}".format(client.name))

    def remove_client(self, client):
        del self.__clients[client.name]
        self.__names.free(client.name)
        for client_name in self.__clients:
            self.__clients[client_name].messages.append("D{}".format(client.name))

dric.register(__name__, NetClientManager())