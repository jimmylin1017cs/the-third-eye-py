import socket
import sys
import cv2
import numpy as np
import struct

class FrameReceiver():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket()

        try:
            self.s.bind((self.host, self.port))
        except socket.error as msg:
            print("Bind failed. Error code: {}, Error message : {}".format(str(msg[0]), msg[1]))
            sys.exit()
        print("Socket bind complete")

    def start(self):
        self.s.listen(1)
        print("Socket listening...")
        self.conn, self.addr = self.s.accept()
        print("Connected with {} : {}".format(self.addr[0], str(self.addr[1])))

    def receive_frame(self):

        data = self.recvall(self.conn)

        jpg_string = np.fromstring(data, np.uint8)
        frame = cv2.imdecode(jpg_string, cv2.IMREAD_COLOR)

        return frame

    def recvall(self, conn):
        # int(4 bytes) + data

        raw_data_len = self.conn.recv(4)
        data_len = struct.unpack('I', raw_data_len)[0]

        print("data_len : {}".format(data_len))

        data = b""
        while len(data) < data_len:
            packet = self.conn.recv(data_len - len(data))
            if not packet:
                return None
            data += packet

        return data