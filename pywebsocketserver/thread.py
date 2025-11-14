# -*- coding: utf8 -*-

import base64
import hashlib
import struct
from threading import Thread


class SocketIoThread(Thread):
    def __init__(self, connection, uid, io):
        super().__init__()
        self.con = connection
        self.isHandleShake = False
        self.uid = uid
        self.io = io
        self.signKey = "ADS#@!D"
        self.online = True

    def _recv_exact(self, size):
        data = bytearray()
        while len(data) < size:
            chunk = self.con.recv(size - len(data))
            if not chunk:
                break
            data.extend(chunk)
        return bytes(data)

    def run(self):
        while True:
            if not self.isHandleShake:  # 握手
                try:
                    print("握手")
                    header_data = []
                    # 已经收到的头大小
                    header_size = 0
                    # 最大大小
                    max_skip_size = 4096

                    row = bytearray()
                    while True:
                        d = self.con.recv(1)
                        if not d:
                            self.onClose()
                            return
                        row.extend(d)
                        if row[-2:] == b'\r\n':
                            row_str = row[:-2].decode('latin-1')
                            header_data.append(row_str)
                            row = bytearray()
                            if row_str == '':
                                break
                        header_size += 1

                        if header_size > max_skip_size:
                            self.onClose()
                            break

                    header = {}
                    for data in header_data:
                        if ": " in data:
                            unit = data.split(": ", 1)
                            header[unit[0]] = unit[1]
                    secKey = header.get('Sec-WebSocket-Key')
                    if not secKey:
                        self.onClose()
                        return
                    accept_source = (secKey + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode('utf-8')
                    resKey = base64.b64encode(hashlib.sha1(accept_source).digest()).decode('ascii')
                    response = '''HTTP/1.1 101 Switching Protocols\r\n'''
                    response += '''Upgrade: websocket\r\n'''
                    response += '''Connection: Upgrade\r\n'''
                    response += '''Sec-WebSocket-Accept: %s\r\n\r\n''' % (resKey,)
                    self.con.sendall(response.encode('utf-8'))
                    self.isHandleShake = True
                    # 返回用户id
                    self.sendData("SETUID")
                    self.io.onConnect(self.uid)
                    print("握手成功")
                except Exception:
                    return
            else:
                try:
                    data_head = self.con.recv(1)
                    if not data_head:
                        print("客户端断开链接")
                        self.onClose()
                        return

                    header = data_head[0]
                    opcode = header & 0b00001111
                    print("操作符号%d" % (opcode,))

                    if opcode == 8:
                        print("客户端断开链接")
                        self.onClose()
                        return

                    data_length = self.con.recv(1)
                    if not data_length:
                        self.onClose()
                        return
                    data_lengths = data_length[0]
                    data_length = data_lengths & 0b01111111
                    masking = data_lengths >> 7
                    if data_length <= 125:
                        payloadLength = data_length
                    elif data_length == 126:
                        payloadLength = struct.unpack("!H", self._recv_exact(2))[0]
                    elif data_length == 127:
                        payloadLength = struct.unpack("!Q", self._recv_exact(8))[0]
                    else:
                        payloadLength = 0
                    print("字符串长度是:%d" % (payloadLength,))
                    maskingKey = b''
                    if masking == 1:
                        maskingKey = self._recv_exact(4)
                        if len(maskingKey) < 4:
                            self.onClose()
                            return
                        self.maskingKey = maskingKey
                    data = self._recv_exact(payloadLength)
                    if len(data) < payloadLength:
                        self.onClose()
                        return
                    if masking == 1:
                        decoded = bytes(
                            byte ^ maskingKey[i % 4] for i, byte in enumerate(data)
                        )
                        self.onData(decoded.decode('utf-8', errors='replace'))
                    else:
                        self.onData(data.decode('utf-8', errors='replace'))
                except Exception as e:
                    print(e, 111)
                    self.onClose()
                    return

    def onData(self, text):
        try:
            uid, sign, value = text.split("<split>")
            uid = int(uid)
        except Exception:
            print("数据格式不正确")
            self.con.close()
            return
        hash_input = (str(uid) + self.signKey).encode('utf-8')
        hashStr = hashlib.md5(hash_input).hexdigest()
        if hashStr != sign:
            print("非法请求")
            self.con.close()
            return
        return self.io.onData(uid, value)

    def onClose(self):
        self.con.close()
        self.online = False
        self.io.onClose(self.uid)

    def packData(self, text):

        sign = hashlib.md5((str(self.uid) + self.signKey).encode('utf-8')).hexdigest()
        data = '%s<split>%s<split>%s' % (self.uid, sign, text)
        return data

    def sendData(self, text):

        text = self.packData(text)
        print(text)
        encoded_text = text.encode('utf-8')
        # 头
        self.con.sendall(struct.pack("!B", 0x81))
        # 计算长度
        length = len(encoded_text)
        # masking = 0b00000000;

        if length <= 125:
            self.con.sendall(struct.pack("!B", length))

        elif length <= 65536:
            self.con.sendall(struct.pack("!B", 126))
            self.con.sendall(struct.pack("!H", length))
        else:
            self.con.sendall(struct.pack("!B", 127))
            self.con.sendall(struct.pack("!Q", length))

        self.con.sendall(struct.pack("!%ds" % (length,), encoded_text))
