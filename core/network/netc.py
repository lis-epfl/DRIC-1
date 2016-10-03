#"""
#Manage clients.
#"""


#import dric
#import json
#from threading import Lock
#from threading import Timer
#from future.utils import itervalues
#from eventlet import spawn
#import select

#class NetClient:
#    def __init__(self, ip, name, cid, cleaner, notif):
#        self.ip = ip
#        self.name = name
#        self.cid = cid
#        self.cleaner = cleaner
#        self.notif = 0
    
        
#class NetClientManager(dric.Plugin):
#    NAMES = ['ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO', 'FOXTROT', 'GOLF' 'HOTEL', 'INDIA', 'JULIET', 'KILO', 'LIMA', 'MIKE', 'NOVEMBER', 'OSCAR', 'PAPA', 'QUEBEC', 'ROMEO', 'SIERRA', 'TANGO', 'UNIFORM', 'VICTOR', 'WHISKEY', 'X-RAY', 'YANKEE', 'ZULU']
    
#    def setup(self, ebus):
#        self.__clients = {}
#        self.__cleaners = {}
#        self.__eventbus = ebus
#        self.__ssevents = []
#        self.lock = Lock()
    
    
#    @dric.route('network.clients', '/network/clients')
#    def clients(self, request=None):
#        self.lock.acquire()
#        clients = []
#        for client in itervalues(self.__clients):
#            clients.append({
#                           'name': client.name, 
#                           'ip': client.ip
#                           })
#        self.lock.release()
#        return dric.JSONResponse(clients)

#    @dric.route('network.me', '/network/me')
#    def me(self, request=None):
#        self.__heartbeat(request)
#        client = self.__clients[request.args['cid']]
#        return dric.JSONResponse({
#                          'ip': client.ip,
#                          'name': client.name
#                          })

    

#    @dric.route('network.stream', '/network/stream')
#    def stream(self, request):
#        self.__heartbeat(request)
#        cid = request.args['cid']
#        self.lock.acquire()
#        client = self.__clients[cid]
#        if client.notif < len(self.__ssevents):
#            notif = client.notif
#            client.notif += 1
#            self.lock.release()
#            return dric.Response(self.__ssevents[notif](), mimetype='text/event-stream', content_type='text/event-stream');
#        else:
#            self.lock.release()
#            return dric.Response('', mimetype='text/event-stream', content_type='text/event-stream')
    
#    def ssevent_connection(self):
#        yield 'event: net\n'
#        yield 'data: connect\n\n'
    
#    def __heartbeat(self, request):
#        self.lock.acquire()
#        cid = request.args['cid']
#        if cid not in self.__clients:
#            self.__register(request)
#        client = self.__clients[cid]
#        client.cleaner.cancel()
#        self.__schedule_cleaner(client)
#        self.lock.release()
        
#    def __schedule_cleaner(self, client):
#        client.cleaner = Timer(5.0, self.unregister, [client.cid])
#        client.cleaner.start()
        
#    def __register(self, request):
#        cid = request.args['cid']
#        ip = request.remote_addr
#        name = self.__name()
#        cleaner = Timer(1.0, self.unregister, [cid])
        
#        self.__clients[cid] = NetClient(ip=ip, name=name, cid=cid, cleaner=cleaner, notif=len(self.__ssevents))
#        self.__clients[cid].cleaner.start()
#        print('Client connected ' + cid)
#        self.__ssevents.append(self.ssevent_connection)
#        return name
        
#    def unregister(self, cid):
#        print('Client disconnected ' + cid)
#        self.lock.acquire()
#        del self.__clients[cid]
#        self.__ssevents.append(self.ssevent_connection)
#        self.lock.release()
    
#    def __name(self):
#        i = 0
#        while True:
#            name = self.NAMES[i]
#            if i >= len(self.NAMES):
#                name += i % len(self.NAMES)
#            unused = True
#            for client in itervalues(self.__clients):
#                if client.name == name:
#                    unused = False
#                    break
#            if unused:
#                return name
#            else:
#                i += 1

#dric.register(__name__, NetClientManager())