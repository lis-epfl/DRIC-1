from .pg import start_plugins
from .ld import load_plugins
from .server import Server


def start():
    load_plugins()
    start_plugins()
    Server('0.0.0.0', 80).start()



from os.path import exists
from os import remove, utime
from builtins import input
from sys import exit
from atexit import register as register_exit_handler
## Lock file

lock_file = 'dric.lock'
def exit_handler():
    if(exists(lock_file)):
        remove(lock_file)


if exists(lock_file):
    do_continue = input('An instance of the program seems to be already running on this computer. '
            'Either a previous session of the program did not exit correctly, or another instance '
            'of the program is running on this computer.'
            'If you are sure that no other instances of the program are running, '
            'and are willing to delete the lock file, type y to continue...') == 'y'
    if not do_continue:
        exit(0)
    remove(lock_file)

register_exit_handler(exit_handler)
with open(lock_file, 'a') as f:
    f.write('\n')

start()