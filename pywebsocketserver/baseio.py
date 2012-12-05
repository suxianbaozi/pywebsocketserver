# -*- coding: utf8 -*-

import socket
import time
from threading import Thread
import hashlib
import base64
import struct
import json


class BaseIO:

    def __init__(self):
        return
    def onData(self,uid,text):
        '''请重写这个方法'''
        return
    def onConnect(self,uid):
        return
    
    def sendData(self,uid,text):
        self.server.sendData(uid,text)
        '''发送数据'''
        return
    def onClose(self,uid):
        return
    def setServer(self,server):
        self.server = server


    




