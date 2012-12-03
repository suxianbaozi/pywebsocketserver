# -*- coding: utf8 -*-
import sys
from pywebsocketserver.server import SocketServer
from pywebsocketserver.baseio import BaseIO

class MyIO(BaseIO):
    def onData(self,uid,text):
        print text,uid
        self.sendData(uid,"我收到了你的消息：%s"%(text,))
try:
    port = sys.argv[1]
except:
    port = 81

port = int(port)
myIo = MyIO()
SocketServer(port,myIo).run()    
