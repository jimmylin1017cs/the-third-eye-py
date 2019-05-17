import time
import frame_sender

#import iottalk_package.DAI_push as DAI_push
import draw_package.draw_utils as draw_utils

from pydarknet import Detector, Image
import cv2
import numpy as np
import sort
import fusion_model

sender_enable = False

if __name__ == "__main__":
    # Optional statement to configure preferred GPU. Available only in GPU version.
    # pydarknet.set_cuda_device(0)

    #cfg_file = "hscc.cfg/yolov3.cfg"
    #weights_file = "hscc.cfg/weights/yolov3_10000.weights"
    #cfg_file = "hscc.cfg/yolov3-tiny.cfg"
    #weights_file = "hscc.cfg/weights/yolov3-tiny_100000.weights"
    cfg_file = "hscc.cfg/yolov2.cfg"
    weights_file = "hscc.cfg/weights/yolov2_10000.weights"

    data_file = "hscc.cfg/hscc.data"

    net = Detector(bytes(cfg_file, encoding="utf-8"), bytes(weights_file, encoding="utf-8"), 0,
                    bytes(data_file, encoding="utf-8"))

    cap = cv2.VideoCapture("test.mp4")
    mot_tracker = sort.Sort() 

    dest_ip = "127.0.0.1"
    dest_port = 8091

    if sender_enable:
        sender = frame_sender.FrameSender(dest_ip, dest_port)
        sender.start()

    fusion_model.get_username()

    while True:
        r, frame = cap.read()
        if r:
            start_time = time.time()

            # Only measure the time taken by YOLO and API Call overhead

            dark_frame = Image(frame)
            results = net.detect(dark_frame)
            del dark_frame

            end_time = time.time()
            #print("Elapsed Time:",end_time-start_time)

            #print("results : {}".format(results))
            detections = list()
            for cat, score, bounds in results:
                x, y, w, h = bounds
                detections.append([int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2), score])
                #detections.append([x, y, w, h, score])
            
            #detections = np.array(detections)
            track_bbs_ids = mot_tracker.update(detections)
            fusion_result = fusion_model.fusion_model(track_bbs_ids)

            #print("track_bbs_ids : {}".format(track_bbs_ids))

        #yolo_history = fusion_model.get_yolo_history()
        #print("yolo_history : {}".format(yolo_history))
        #frame = draw_utils.draw_yolo_path(frame, yolo_history)

        #beacon_history = fusion_model.get_beacon_history()
        #print("beacon_history : {}".format(beacon_history))
        #frame = draw_utils.draw_beacon_path(frame, beacon_history)

        frame = draw_utils.draw_box(frame, track_bbs_ids, fusion_result)

        if sender_enable:
            sender.send_frame(frame)

        cv2.namedWindow("preview",0)
        cv2.resizeWindow("preview", 640, 480)
        cv2.imshow("preview", frame)

        k = cv2.waitKey(1)
        if k == 0xFF & ord("q"):
            break

            