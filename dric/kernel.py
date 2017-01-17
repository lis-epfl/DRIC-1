import dric
import SocketServer
import SimpleHTTPServer
import threading
import os
import os.path
import logging
import sys
from .pg import start_plugins
from .ld import load_plugins
from .server import Server
from .lockf import LockFileHelper

_logger = logging.getLogger('dric.kernel')

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
        if dric.dconfig['backend_only']: return
        frontend_dir = os.path.join('dricgcss_index', 'dist')
        if not os.path.exists(frontend_dir):
            _logger.warn('Directory "{}" not found. Frontend server will not be started.'.format(frontend_dir))
            return
        os.chdir(frontend_dir)
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(('', 8000), Handler)
        httpd.serve_forever()
