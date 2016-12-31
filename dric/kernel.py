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
        """ Boot kernel by starting plugins and server """
        start_plugins()
        Server('0.0.0.0', 9555).start()