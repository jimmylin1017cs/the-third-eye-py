import socket
import sys
import cv2
import struct


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

    def send_frame(self, frame):

        jpg_string = cv2.imencode('.jpg', frame)[1].tostring()

        packet = struct.pack('I', len(jpg_string)) + jpg_string

        print(len(packet))

        #jpg_string = jpg_string.encode()

        send_byte = self.s.sendall(packet)

        print("send_byte: {}".format(send_byte))