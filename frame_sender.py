import socket
import sys
import cv2
import struct
import time
import random


class FrameSender():
    def __init__(self, dest_ip, dest_port):
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        try:
            self.s.connect((self.dest_ip, self.dest_port))
            print("Socket Connected to {} on ip {}".format(self.dest_ip, self.dest_port))
        except socket.error as msg:
            print("Failed to connect. Error code: {}, Error message : {}".format(str(msg[0]), msg[1]))
            sys.exit()

    def send_frame(self, client_id, time_stamp, frame):
        start_time = time.time()
        jpg_string = cv2.imencode('.jpg', frame)[1].tostring()

        end_time = time.time()
        print("imencode Time : {}".format((end_time - start_time)))

        #start_time = time.time()
        packet = struct.pack('I', client_id) + struct.pack('d', time_stamp) + struct.pack('I', len(jpg_string)) + jpg_string
        #end_time = time.time()
        #print("pack Time : {}".format((end_time - start_time)))
        #print("packet length : {}".format(len(packet)))

        #jpg_string = jpg_string.encode()

        #start_time = time.time()      
        send_byte = self.s.sendall(packet)
        #end_time = time.time()
        #print("sendall Time : {}".format((end_time - start_time)))

        #print("send_byte: {}".format(send_byte))


if __name__ == "__main__":

    # initial camera
    cap = cv2.VideoCapture("test.mp4")

    prev_time_stamp = 0
    time_stamp = time.time()

    dest_ip = "127.0.0.1"
    dest_port = 8092

    sender = FrameSender(dest_ip, dest_port)
    sender.start()

    #room_id = random.randint(0, 1000)
    #room_id = int((time_stamp * 100000) % 100)
    room_id = 2

    while True:
        r, frame = cap.read()

        prev_time_stamp = time_stamp
        time_stamp = time.time()
        fps = 1 / (time_stamp - prev_time_stamp)

        print("FPS : {}".format(str(fps)))

        if r:
            sender.send_frame(room_id, time_stamp, frame)
        else:
            break