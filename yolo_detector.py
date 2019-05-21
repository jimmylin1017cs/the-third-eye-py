import time
import frame_sender

import draw_package.draw_utils as draw_utils

from pydarknet import Detector, Image
import cv2
import numpy as np
import sort
import fusion_model

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

ENABLE_SENDER = config.getboolean('Yolo_Client', 'Enable_Sender') # send frame to server

if ENABLE_SENDER:
    RECEIVER_IP = config.get('Yolo_Client', 'Receiver_IP')
    RECEIVER_PORT = config.get('Yolo_Client', 'Receiver_Port')
    RECEIVER_PORT = int(RECEIVER_PORT)

print("ENABLE_SENDER = {}".format(ENABLE_SENDER))

ENABLE_IOTTALK = config.getboolean('IoTTalk_Config', 'Enable_IoTTalk')

print("ENABLE_IOTTALK = {}".format(ENABLE_IOTTALK))

ENABLE_FUSION_MODEL = config.getboolean('Yolo_Function', 'Enable_Fusion_Model')
ENABLE_SORT_ALGORITHM = config.getboolean('Yolo_Function', 'Enable_Sort_Algorithm')
SHOW_PREVIEW = config.getboolean('Yolo_Function', 'Show_Preview')
SAVE_VIDEO = config.getboolean('Yolo_Function', 'Save_Video')
SAVE_DATA = config.getboolean('Yolo_Function', 'Save_Data')

print("ENABLE_FUSION_MODEL = {}".format(ENABLE_FUSION_MODEL))
print("ENABLE_SORT_ALGORITHM = {}".format(ENABLE_SORT_ALGORITHM))
print("SHOW_PREVIEW = {}".format(SHOW_PREVIEW))
print("SAVE_VIDEO = {}".format(SAVE_VIDEO))
print("SAVE_DATA = {}".format(SAVE_DATA))

YOLO_ID = config.get('Yolo_Config', 'Yolo_ID')
YOLO_ID = int(YOLO_ID)

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

    # initial camera
    cap = cv2.VideoCapture("test.mp4")

    # initial sort class
    mot_tracker = sort.Sort() 

    # initial save video
    if SAVE_VIDEO:
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_fps = int(cap.get(cv2.CAP_PROP_FPS))
        #print("frame_width : {}, frame_height : {}, frame_fps : {}".format(frame_width, frame_height, frame_fps))
        out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), frame_fps, (frame_width, frame_height))
    
    # initial save data
    if SAVE_DATA:
        yolo_data_file = open("yolo_" + str(YOLO_ID) + ".log", 'w')

    # initial sender
    if ENABLE_SENDER:
        dest_ip = RECEIVER_IP
        dest_port = RECEIVER_PORT
        sender = frame_sender.FrameSender(dest_ip, dest_port)
        sender.start()

    # initial iottalk connection
    if ENABLE_IOTTALK:
        import iottalk_package.DAI_push as DAI_push

    # initial fusion model
    if ENABLE_FUSION_MODEL:
        fusion_model.get_username()

    prev_time_stamp = 0
    time_stamp = time.time()

    while True:
        r, frame = cap.read()

        prev_time_stamp = time_stamp
        time_stamp = time.time()
        fps = 1 / (time_stamp - prev_time_stamp)

        print("FPS : {}".format(str(fps)))

        # save original video file
        if SAVE_VIDEO:
            out.write(frame)
        
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
            detections_with_class = list()
            for cat, score, bounds in results:
                x, y, w, h = bounds
                #detections.append([int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2), score])
                detections.append([x-w/2, y-h/2, x+w/2, y+h/2, score])
                detections_with_class.append([int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2), cat, score])
                #detections.append([x, y, w, h, score])
            
            #detections = np.array(detections)
            track_bbs_ids = mot_tracker.update(detections)

            if ENABLE_FUSION_MODEL:
                fusion_result = fusion_model.fusion_model(track_bbs_ids)

            #print("track_bbs_ids : {}".format(track_bbs_ids))
            #print("detections_with_class : {}".format(detections_with_class))

            # [time_stamp, ]

            if SAVE_DATA and ENABLE_FUSION_MODEL:
                for det in track_bbs_ids:
                    x1, y1, x2, y2, id = [int(p) for p in det]
                    data_log = [time_stamp, "person", id, (x1, y1, x2, y2), "Event"]
                    #print("data_log : {}".format(data_log))
                    yolo_data_file.write("{}\n".format(str(data_log)))
            elif SAVE_DATA:
                yolo_data_file.write("{}\n".format(str(track_bbs_ids)))

        #yolo_history = fusion_model.get_yolo_history()
        #print("yolo_history : {}".format(yolo_history))
        #frame = draw_utils.draw_yolo_path(frame, yolo_history)

        #beacon_history = fusion_model.get_beacon_history()
        #print("beacon_history : {}".format(beacon_history))
        #frame = draw_utils.draw_beacon_path(frame, beacon_history)

        if ENABLE_FUSION_MODEL:
            frame = draw_utils.draw_fusion_box(frame, fusion_result)
        elif ENABLE_SORT_ALGORITHM:
            frame = draw_utils.draw_box(frame, track_bbs_ids)

        if ENABLE_SENDER:
            room_id = YOLO_ID
            sender.send_frame(room_id, time_stamp, frame)

        if ENABLE_IOTTALK:
            DAI_push.send_data_to_iottalk(time_stamp, track_bbs_ids)

        if SHOW_PREVIEW:
            cv2.namedWindow("preview",0)
            cv2.resizeWindow("preview", 640, 480)
            cv2.imshow("preview", frame)

            k = cv2.waitKey(1)
            if k == 0xFF & ord("q"):
                break

    yolo_data_file.close() 
            