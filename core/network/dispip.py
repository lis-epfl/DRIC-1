"""
Provide server's LAN ip on endpoint /network/ip.
"""

import dric
import socket
import json


class Dispip(dric.Plugin):
    def setup(self, eventbus):
        self.__eventbus = eventbus
        
    def start(self):
        self.__ip = self.__getip()
    
    def __getip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("gmail.com",80))
            ip = s.getsockname()[0]
            s.close()
        except socket.gaierror:
            return '?.?.?.?'
        return ip
    
    @dric.route('network.ip', '/network/ip')
    def index(self, request=None):
        return dric.JSONResponse({
            'ip': self.__ip
        })


dric.register(__name__, Dispip())