import cv2
import frame_receiver

host = "0.0.0.0"
port = 8091

server = frame_receiver.FrameReceiver(host, port)

server.start()

while True:

    frame = server.receive_frame()

    cv2.namedWindow("preview",0)
    cv2.resizeWindow("preview", 640, 480)
    cv2.imshow("preview", frame)

    k = cv2.waitKey(1)
    if k == 0xFF & ord("q"):
        break