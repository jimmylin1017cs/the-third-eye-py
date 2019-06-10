import socket
import sys
import cv2
import numpy as np
import time
import threading
import struct

frame_receiver_lock = threading.Lock()

class FrameReceiver(threading.Thread):

    is_initial = False
    client_amount = 0

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.lock = frame_receiver_lock

        self.host = host
        self.port = port
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(10)

        FrameReceiver.is_initial = True
        print("Listening...")

    def run(self):

        while True:
            (client, addr) = self.sock.accept()
            FrameHandler(client, addr, self.lock).start()

class FrameHandler(threading.Thread):

    frame_buffer = None

    def __init__(self, socket, addr, lock):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = addr
        self.lock = lock
        self.client_id = 0

        FrameReceiver.client_amount += 1

        #cv2.namedWindow(str(self.socket),0)
        #cv2.resizeWindow(str(self.socket), 640, 480)

    def run(self):
        print("Connected with {} : {}".format(self.address[0], str(self.address[1])))
        while True:

            #print("FrameReceiver.client_amount : {}".format(FrameReceiver.client_amount))

            # receive client id by 4 bytes (unsigned int)
            raw_client_id = self.socket.recv(4)
            #print("raw_client_id : {}".format(raw_client_id))

            if(raw_client_id == b""):
                break
            client_id = struct.unpack('I', raw_client_id)[0]
            #print("client_id : {}".format(client_id))

            if self.client_id == 0:
                self.client_id = client_id

            #
            # ================================================
            #

            # receive time stamp by 8 bytes (double)
            raw_time_stamp = self.socket.recv(8)
            #print("raw_time_stamp : {}".format(raw_time_stamp))
            if(raw_time_stamp == b""):
                break
            time_stamp = struct.unpack('d', raw_time_stamp)[0]
            #print("time_stamp : {}".format(time_stamp))

            #
            # ================================================
            #

            # receive data length by 4 bytes (unsigned int)
            raw_data_len = self.socket.recv(4)
            #print("raw_data_len : {}".format(raw_data_len))

            # if not have any data -> client was disconnect
            if(raw_data_len == b""):
                break

            # convert first 4 bytes to integer
            data_len = struct.unpack('I', raw_data_len)[0]
            #print("data_len : {}".format(data_len))

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

            if FrameHandler.frame_buffer is None:
                FrameHandler.frame_buffer = dict()

            if client_id not in FrameHandler.frame_buffer:
                FrameHandler.frame_buffer[client_id] = dict()

            FrameHandler.frame_buffer[client_id][str(time_stamp)] = frame

            if len(FrameHandler.frame_buffer[client_id]) > 20:
                
                time_stamp_list = list(FrameHandler.frame_buffer[client_id].keys())
                time_stamp_list.sort()

                del FrameHandler.frame_buffer[client_id][time_stamp_list[0]]
                #print("Delete Frame {}".format(time_stamp_list[0]))
            
            self.lock.release()

            #cv2.imshow(str(self.socket), FrameHandler.frame_buffer)
            #k = cv2.waitKey(1)
            #if k == 0xFF & ord("q"):
                #break
        
        self.socket.close()
        FrameReceiver.client_amount -= 1

        del FrameHandler.frame_buffer[self.client_id]

        print("Client {} disconnected".format(str(self.socket)))


def init_frame_receiver(host, port):
    
    print("FrameReceiver.is_initial : {}".format(FrameReceiver.is_initial))

    if(not FrameReceiver.is_initial):
        FrameReceiver(host, port).start()

def frame_sender_amount():

    return FrameReceiver.client_amount

def get_frame_buffer():

    frame_buffer = None

    frame_receiver_lock.acquire()

    if FrameHandler.frame_buffer is not None:
        frame_buffer = FrameHandler.frame_buffer

    frame_receiver_lock.release()

    return frame_buffer

def get_target_frame(client_id, time_stamp):

    frame = None

    frame_receiver_lock.acquire()

    if FrameHandler.frame_buffer is not None:
    
        if client_id in FrameHandler.frame_buffer:

            frame_buffer = FrameHandler.frame_buffer[client_id]

            if time_stamp in frame_buffer:
                frame = frame_buffer[time_stamp]

    frame_receiver_lock.release()

    return frame

def get_frame(client_id):

    frame = None

    frame_receiver_lock.acquire()

    if FrameHandler.frame_buffer is not None:
    
        if client_id in FrameHandler.frame_buffer:

            frame_buffer = FrameHandler.frame_buffer[client_id]
            time_stamp = list(frame_buffer.keys())
            time_stamp.sort()
            frame = frame_buffer[time_stamp[-1]]

    frame_receiver_lock.release()

    return frame

def get_frame_time_stamp():

    return FrameHandler.frame_time_stamp

if __name__ == "__main__":

    host = "0.0.0.0"
    port = 8091

    FrameReceiver(host, port).start()

    cv2_windows_conrtol = []

    while True:

        frame_buffer = get_frame_buffer()
        #time_stamp = get_frame_time_stamp()

        #print(frame_buffer)

        if frame_buffer is not None:

            frame_buffer = frame_buffer.copy()

            for client_id in frame_buffer.keys():

                #print("client_id : {}".format(client_id))

                if client_id not in cv2_windows_conrtol:
                    cv2_windows_conrtol.append(client_id)
                
                if frame_buffer[client_id]:
                    time_stamp = list(frame_buffer[client_id].keys())
                    time_stamp.sort()
                    #print(time_stamp[-1])
                    frame = frame_buffer[client_id][time_stamp[-1]]

                    if frame is not None:
                        window_name = "preview_" + str(client_id)
                        cv2.namedWindow(window_name,0)
                        cv2.resizeWindow(window_name, 640, 480)
                        cv2.imshow(window_name, frame)

                        k = cv2.waitKey(1)
                        if k == 0xFF & ord("q"):
                            break

            client_ids = cv2_windows_conrtol.copy()
            for client_id in client_ids:
                if client_id not in frame_buffer:
                    window_name = "preview_" + str(client_id)
                    cv2.destroyWindow(window_name)
                    cv2_windows_conrtol.remove(client_id)