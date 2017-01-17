import SocketServer
import SimpleHTTPServer
import threading
import os
from .pg import start_plugins
from .ld import load_plugins
from .server import Server
from .lockf import LockFileHelper

class Kernel(object):
    def __init__(self, ask_user=True):
        """ ask_user if we should remove the lock if it exists. See lockf. """
        lfh = LockFileHelper('drickernel.lock')
        lfh.acquire_lock(ask_user)

    def boot(self):
        """ Boot kernel by starting plugins and servers """
        start_plugins()
        threading.Thread(target=self.start_frontend_server).start()
        Server('0.0.0.0', 9555).start()

    def start_frontend_server(self):
        os.chdir('./dricgcss_index/dist')
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(('', 8080), Handler)
        httpd.serve_forever()
