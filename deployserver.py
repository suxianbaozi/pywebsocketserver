# -*- coding: utf8 -*-
import sys
from pywebsocketserver.server import SocketServer
from pywebsocketserver.baseio import BaseIO
import json
import os
import time
from gaga import settings

class MyIO(BaseIO):
    def onData(self,uid,text):    
        data = json.loads(text)
        action = data['action']
        self.action(data)
        self.sendData(uid,"我收到了你的消息：%s"%(text,))
    
    
    def preview(self,data):
        date = data['date']
        






myIo = MyIO()
SocketServer(8181,myIo).run()    
