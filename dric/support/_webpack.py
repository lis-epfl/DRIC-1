import dric
import subprocess
from logging import getLogger
from sys import stdout, stderr
from os.path import dirname, realpath

class WebpackWatchPlugin(dric.Plugin):
    def __init__(self, from_file, logger=None):
        self.__cwd = dirname(realpath(from_file)) 
        if logger is None:
            self.__logger = getLogger('dric.support.webpack')
        else:
            self.__logger = logger

    def setup(self, eventbus):
        self.__logger.info('Start webpack --watch')
        subprocess.Popen(['webpack', '--watch'], stdout=stdout, stderr=stdout, cwd=self.__cwd, shell=True)