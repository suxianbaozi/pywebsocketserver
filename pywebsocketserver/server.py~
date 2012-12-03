# -*- coding: utf8 -*-

import socket
import time
from threading import Thread
import hashlib
import base64
import struct
import json

from thread import SocketIoThread
from baseio import BaseIO


class SocketServer:
    def __init__(self,IO):
        self.io = IO
        self.io.setServer(self)
        self.uid = 0
        self.IoList = {}
    def run(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind(('',88))
        sock.listen(100)
        while True:
            try:
                connection,address = sock.accept()
                self.uid += 1
                self.IoList[self.uid] = SocketIoThread(connection,self.uid,self.io)
                self.IoList[self.uid].start()
            except:
		time.sleep(1)
            
    def sendData(self,uid,text):
        if self.IoList.has_key(uid):
            self.IoList[uid].sendData(text)
        


            


