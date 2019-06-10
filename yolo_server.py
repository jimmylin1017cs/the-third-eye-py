import socket
import sys
import cv2
import numpy as np
import time
import threading
import struct
import ast

yolo_server_lock = threading.Lock()

class YoloServer(threading.Thread):

    is_initial = False
    client_amount = 0

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.lock = yolo_server_lock

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

    data_buffer = None
    update = False

    def __init__(self, socket, addr, lock):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = addr
        self.lock = lock
        self.client_id = 0

        YoloServer.client_amount += 1

        #cv2.namedWindow(str(self.socket),0)
        #cv2.resizeWindow(str(self.socket), 640, 480)

    def run(self):
        print("Connected with {} : {}".format(self.address[0], str(self.address[1])))
        while True:

            #print("YoloServer.client_amount : {}".format(YoloServer.client_amount))

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

            # convert byte string to string
            data = data.decode('utf-8')
            # convert string to list
            data = ast.literal_eval(data)

            self.lock.acquire()

            if YoloHandler.data_buffer is None:
                YoloHandler.data_buffer = dict()

            #if client_id not in YoloHandler.data_buffer:
                #YoloHandler.data_buffer[client_id] = []

            box_data = []
            box_data.append(time_stamp)

            for det in data:
                id, x1, y1, x2, y2 = [int(p) if isinstance(p, int) else p for p in det]
                box_data.append([id, x1, y1, x2, y2])

            YoloHandler.data_buffer[client_id] = box_data

            '''if len(YoloHandler.data_buffer[client_id]) > 20:
                
                time_stamp_list = list(YoloHandler.data_buffer[client_id].keys())
                time_stamp_list.sort()

                del YoloHandler.data_buffer[client_id][time_stamp_list[0]]
                print("Delete Frame {}".format(time_stamp_list[0]))'''

            YoloHandler.update = True

            self.lock.release()

            #cv2.imshow(str(self.socket), YoloHandler.data_buffer)
            #k = cv2.waitKey(1)
            #if k == 0xFF & ord("q"):
                #break
        
        self.socket.close()
        YoloServer.client_amount -= 1

        del YoloHandler.data_buffer[self.client_id]

        print("Client {} disconnected".format(str(self.socket)))


def init_yolo_server(host, port):
    
    print("YoloServer.is_initial : {}".format(YoloServer.is_initial))

    if(not YoloServer.is_initial):
        YoloServer(host, port).start()

def yolo_client_amount():

    return YoloServer.client_amount

def get_data_buffer():

    data_buffer = None

    yolo_server_lock.acquire()

    if YoloHandler.data_buffer is not None:
        data_buffer = YoloHandler.data_buffer.copy()

    yolo_server_lock.release()

    return data_buffer

def get_data(client_id):

    if YoloHandler.data_buffer is None:
        return None
    
    if client_id in YoloHandler.data_buffer:

        data_buffer = YoloHandler.data_buffer[client_id]
        time_stamp = list(data_buffer.keys())
        time_stamp.sort()
        frame = data_buffer[time_stamp[-1]]
        return frame

    else:
        return None

def get_frame_time_stamp():

    return YoloHandler.frame_time_stamp

if __name__ == "__main__":

    host = "0.0.0.0"
    port = 8093

    YoloServer(host, port).start()

    cv2_windows_conrtol = []

    import iottalk_package.DAI_push as DAI_push

    while True:

        data_buffer = get_data_buffer()
        #time_stamp = get_frame_time_stamp()

        #print(data_buffer)

        if data_buffer is not None:

            data_buffer = data_buffer.copy()

            print(data_buffer)

            data_list = []
            for yolo_id in data_buffer.keys():
                data_list.append([yolo_id, data_buffer[yolo_id]])
                #time_stamp = data_buffer[yolo_id][0]
                #print("time_stamp : {}".format(time_stamp))
                #for i in range(1, len(data_buffer[yolo_id])):
                #    track_bbs_ids.append(data_buffer[yolo_id][i])
                #print("track_bbs_ids : {}".format(track_bbs_ids))
                #DAI_push.send_data_to_iottalk(yolo_id, time_stamp, track_bbs_ids)

            print("data_list : {}".format(data_list))

            DAI_push.send_all_data_to_iottalk(data_list)

            '''for client_id in data_buffer.keys():

                #print("client_id : {}".format(client_id))

                if client_id not in cv2_windows_conrtol:
                    cv2_windows_conrtol.append(client_id)
                
                if data_buffer[client_id]:
                    time_stamp = list(data_buffer[client_id].keys())
                    time_stamp.sort()
                    #print(time_stamp[-1])
                    frame = data_buffer[client_id][time_stamp[-1]]

                    if frame is not None:
                        window_name = "preview_" + str(client_id)
                        cv2.namedWindow(window_name, 0)
                        cv2.resizeWindow(window_name, 640, 480)
                        cv2.imshow(window_name, frame)

                        k = cv2.waitKey(1)
                        if k == 0xFF & ord("q"):
                            break

            client_ids = cv2_windows_conrtol.copy()
            for client_id in client_ids:
                if client_id not in data_buffer:
                    window_name = "preview_" + str(client_id)
                    cv2.destroyWindow(window_name)
                    cv2_windows_conrtol.remove(client_id)'''