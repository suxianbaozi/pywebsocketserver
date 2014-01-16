# -*- coding: utf8 -*-

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


    




