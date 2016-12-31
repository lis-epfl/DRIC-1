"""
Manage a global lock file
"""
from os.path import exists
from os import remove
from builtins import input
from sys import exit
from atexit import register as register_exit_handler


class LockFileHelper(object):

    def __init__(self, lock_file):
        """ lock_file: name of the file """
        self.lock_file = lock_file
        
    def acquire_lock(self, ask_user=False):
        """ 
        Attempt to get the lock. 
        ask_user: asks the user if he wants to force acquisition of the lock
        """
        if exists(self.lock_file):
            if ask_user:
                do_continue = input('An instance of the program seems to be already running on this computer. '
                        'Either a previous session of the program did not exit correctly, or another instance '
                        'of the program is running on this computer.'
                        'If you are sure that no other instances of the program are running, '
                        'and are willing to delete the lock file, type y to continue...') == 'y'
                if not do_continue:
                    return False
                remove(self.lock_file)
            else: 
                return False

        def exit_handler():
            if(exists(self.lock_file)):
                remove(self.lock_file)
        register_exit_handler(exit_handler)

        with open(self.lock_file, 'a') as f:
            f.write('\n')
        return True