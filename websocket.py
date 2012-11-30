# -*- coding: utf8 -*-

import socket
import time
from threading import Thread
import hashlib
import base64
import struct

class returnCrossDomain(Thread):
    def __init__(self,connection):
        Thread.__init__(self)
        self.con = connection
        self.isHandleShake = False
    def run(self):
        while True:
            if not self.isHandleShake: #握手
                print "握手"
                clientData  = self.con.recv(1024)
                dataList = clientData.split("\r\n")
                header = {}
                print clientData
                for data in dataList:
                    if ": " in data:
                        unit = data.split(": ")
                        header[unit[0]] = unit[1]
                secKey = header['Sec-WebSocket-Key'];
                resKey = base64.encodestring(hashlib.new("sha1",secKey+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest());
                
                response = '''HTTP/1.1 101 Switching Protocols\r\n'''
                response += '''Upgrade: websocket\r\n'''
                response += '''Connection: Upgrade\r\n'''
                response += '''Sec-WebSocket-Accept: %s\r\n'''%(resKey,)
                response += '''Sec-WebSocket-Protocol: chat,superchat\r\n\r\n\r\n'''
                self.con.send(response)
                self.isHandleShake = True
                print "握手成功"
            else:
                try:
                    data_head = self.con.recv(1)
                    header = struct.unpack("B",data_head)[0]
                    opcode = header & 0b00001111
                    print "操作符号%d"%(opcode,)
                    
                    if opcode==8:
                        print "客户端断开链接"
                        self.con.close()
                        return
                    
                    
                    data_length = self.con.recv(1)
                    data_lengths= struct.unpack("B",data_length)
                    data_length = data_lengths[0]& 0b01111111
                    print bin(data_lengths[0])
                    masking = data_lengths[0] >> 7
                    
                    if data_length<=125:
                        payloadLength = data_length
                    elif data_length==126:
                        payloadLength = struct.unpack("H",self.con.recv(2))[0]
                    elif data_length==127:
                        payloadLength = struct.unpack("Q",self.con.recv(8))[0]

                    print "字符串长度是:%d"%(data_length,)

                    if masking==1:
                        print "是masking"
                        maskingKey = self.con.recv(4)
                        self.maskingKey = maskingKey
                    data = self.con.recv(payloadLength)
                    i = 0
                    true_data = ''
                    for d in data:
                        true_data += chr(ord(d) ^ ord(maskingKey[i%4]))
                        i += 1
                    self.onData(true_data)
                except Exception,e:
                    print e
                    self.con.close()
                    break
    def onData(self,text) :
        
        self.sendData("haha")
        
        print text
        
    def sendData(self,text) :
        #self.con.send("\xff%s\x00"%(text,))
        #return
        #头
        
        self.con.send(struct.pack("!B",0x81))
        #计算长度
        length = len(text)
        
        masking = 0b00000000;
        
        
        if length<=125:
            self.con.send(struct.pack("!B",length | masking))
            
        elif length<=65536:
            self.con.send(struct.pack("!B",126 | masking))
            self.con.send(struct.pack("!H",length))
        else:
            self.con.send(struct.pack("!B",127 | masking))
            self.con.send(struct.pack("!Q",length))
        if masking == 0b10000000:
            self.con.send(self.maskingKey);
        self.con.send(struct.pack("!%ds"%(length,),text))

def main():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('',88))
    sock.listen(100)
    while True:
        try:
            connection,address = sock.accept()
            returnCrossDomain(connection).start()
            print "收到一个请求"  
        except:
            time.sleep(1)
        break

if __name__=="__main__":
    main()
            


 
