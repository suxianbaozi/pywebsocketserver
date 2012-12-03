# -*- coding: utf8 -*-

from pywebsocketserver.server import SocketServer
from pywebsocketserver.baseio import BaseIO

class MyIO(BaseIO):
    def onData(self,uid,text):
        print text,uid
        self.sendData(uid,"我收到了你的消息：%s"%(text,))


myIo = MyIO()
SocketServer(myIo).run()    