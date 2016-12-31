import unittest
from dric.lockf import LockFileHelper
from os.path import exists
import os

LOCK_FILE = 'lock.file'

class TestLockf(unittest.TestCase):
    def setUp(self):
        if exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    def tearDown(self):
        if exists(LOCK_FILE):
            os.remove(LOCK_FILE)

    def test_lock(self):
        lfh = LockFileHelper(LOCK_FILE)
        self.assertTrue(lfh.acquire_lock())
        self.assertFalse(lfh.acquire_lock())
    
if __name__ == '__main__':
    unittest.main()
