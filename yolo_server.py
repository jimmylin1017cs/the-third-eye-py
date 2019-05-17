import socket
import sys
import cv2
import numpy as np
import time
import threading
import struct

class YoloServer(threading.Thread):

    is_initial = False
    client_amount = 0

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()

        self.host = host
        self.port = port
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(10)

        YoloServer.is_initial = True
        print("Listening...")

    def run(self):

        while True:
            (client, addr) = self.sock.accept()
            YoloHandler(client, addr, self.lock).start()

class YoloHandler(threading.Thread):

    frame_buffer = None

    def __init__(self, socket, addr, lock):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = addr
        self.lock = lock

        YoloServer.client_amount += 1

        #cv2.namedWindow(str(self.socket),0)
        #cv2.resizeWindow(str(self.socket), 640, 480)

    def run(self):
        print("Connected with {} : {}".format(self.address[0], str(self.address[1])))
        while True:

            print("YoloServer.client_amount : {}".format(YoloServer.client_amount))

            # receive data length by first 4 bytes
            raw_data_len = self.socket.recv(4)
            print("raw_data_len : {}".format(raw_data_len))

            # if not have any data -> client was disconnect
            if(raw_data_len == b""):
                break

            # convert first 4 bytes to integer
            data_len = struct.unpack('I', raw_data_len)[0]
            print("data_len : {}".format(data_len))

            # receive all data with data length
            data = b""
            while len(data) < data_len:
                packet = self.socket.recv(data_len - len(data))
                if not packet:
                    return None
                data += packet

            # convert byte string to numpy
            jpg_string = np.fromstring(data, np.uint8)
            # convert jpg to numpy image
            frame = cv2.imdecode(jpg_string, cv2.IMREAD_COLOR)
            self.lock.acquire()
            YoloHandler.frame_buffer = frame
            self.lock.release()

            #cv2.imshow(str(self.socket), YoloHandler.frame_buffer)
            #k = cv2.waitKey(1)
            #if k == 0xFF & ord("q"):
                #break
        
        self.socket.close()
        YoloServer.client_amount -= 1
        print("Client {} disconnected".format(str(self.socket)))


def init_yolo_server():
    
    host = "0.0.0.0"
    port = 8091
    print("YoloServer.is_initial : {}".format(YoloServer.is_initial))

    if(not YoloServer.is_initial):
        YoloServer(host, port).start()

def yolo_client_amount():

    return YoloServer.client_amount

def get_frame_buffer():

    return YoloHandler.frame_buffer

if __name__ == "__main__":

    host = "0.0.0.0"
    port = 8091

    YoloServer(host, port).start()