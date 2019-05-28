from pydarknet import Detector, Image

import os
import time
import cv2
import numpy as np
import configparser

import sort_with_category

import frame_sender
import fusion_model
import draw_package.draw_utils as draw_utils

config = configparser.ConfigParser()
config.read('detector_config.ini')

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
ENABLE_DRAW_BOX = config.getboolean('Yolo_Function', 'Enable_Draw_Box')


print("ENABLE_FUSION_MODEL = {}".format(ENABLE_FUSION_MODEL))
print("ENABLE_SORT_ALGORITHM = {}".format(ENABLE_SORT_ALGORITHM))
print("ENABLE_DRAW_BOX = {}".format(ENABLE_DRAW_BOX))

SHOW_PREVIEW = config.getboolean('Yolo_Function', 'Show_Preview')
SAVE_VIDEO = config.getboolean('Yolo_Function', 'Save_Video')
SAVE_DATA = config.getboolean('Yolo_Function', 'Save_Data')
print("SHOW_PREVIEW = {}".format(SHOW_PREVIEW))
print("SAVE_VIDEO = {}".format(SAVE_VIDEO))
print("SAVE_DATA = {}".format(SAVE_DATA))

YOLO_ID = config.get('Yolo_Config', 'Yolo_ID')
YOLO_ID = int(YOLO_ID)

category_table = []

def get_category_table():

    category_file = "hscc.cfg/hscc.names"

    if os.path.exists(category_file):

        with open(category_file, 'r') as f:

            for line in f.readlines():

                category = line.strip()

                category_table.append(category)

    print(category_table)

if __name__ == "__main__":

    process_start_time_stamp = time.time()

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
    mot_tracker = sort_with_category.Sort() 

    # initial category table
    get_category_table()

    # initial save video
    if SAVE_VIDEO:
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_fps = int(cap.get(cv2.CAP_PROP_FPS))
        #print("frame_width : {}, frame_height : {}, frame_fps : {}".format(frame_width, frame_height, frame_fps))
        out = cv2.VideoWriter("save/yolo_" + str(YOLO_ID) + "_" + str(process_start_time_stamp) + ".avi", cv2.VideoWriter_fourcc('M','J','P','G'), frame_fps, (frame_width, frame_height))
    
    # initial save data
    if SAVE_DATA:
        yolo_data_file = open("save/yolo_" + str(YOLO_ID) + "_" + str(process_start_time_stamp) + ".log", 'w')
        if ENABLE_FUSION_MODEL:
            fusion_data_file = open("save/yolo_" + str(YOLO_ID) + "_fusion_" + str(process_start_time_stamp) + ".log", 'w')
            sort_data_file = open("save/yolo_" + str(YOLO_ID) + "_sort_" + str(process_start_time_stamp) + ".log", 'w')
        if ENABLE_SORT_ALGORITHM:
            sort_data_file = open("save/yolo_" + str(YOLO_ID) + "_sort_" + str(process_start_time_stamp) + ".log", 'w')

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
            detections_with_category = list()
            detections_with_category_id = list()
            for cat, score, bounds in results:
                cat = cat.decode("utf-8")
                x, y, w, h = bounds
                #detections.append([int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2), score])
                #detections.append([x-w/2, y-h/2, x+w/2, y+h/2, score])

                #detections_with_category.append([x-w/2, y-h/2, x+w/2, y+h/2, score, cat])
                detections_with_category.append([int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2), score, cat])
                category_id = category_table.index(cat)
                detections_with_category_id.append([int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2), score, category_id])
                #detections.append([x, y, w, h, score])
            
            #detections = np.array(detections)
            #track_bbs_ids = mot_tracker.update(detections)

            if ENABLE_SORT_ALGORITHM or ENABLE_FUSION_MODEL:
                detections_with_category_id = np.array(detections_with_category_id)
                track_bbs_ids = mot_tracker.update(detections_with_category_id)

                # re-create the track_bbs_ids with string type catefory
                track_bbs_ids = list(track_bbs_ids)
                track_bbs_ids_copy = track_bbs_ids.copy()
                track_bbs_ids.clear()
                for det in track_bbs_ids_copy:
                    x1, y1, x2, y2, id, cat = [int(p) for p in det]
                    track_bbs_ids.append([x1, y1, x2, y2, id, category_table[cat]])

            if ENABLE_FUSION_MODEL:
                beacon_dataset = fusion_model.get_beacon_data()
                fusion_result = fusion_model.fusion_model(track_bbs_ids, beacon_dataset)

            #print("track_bbs_ids : {}".format(track_bbs_ids))
            #print("detections_with_category : {}".format(detections_with_category))

            # [time_stamp, ]

            if SAVE_DATA:

                # save fusion file
                if ENABLE_FUSION_MODEL:
                    fusion_data_file.write("{} {}\n".format(str(time_stamp), str(len(fusion_result))))
                    for det in fusion_result:
                        x1, y1, x2, y2, username = [int(p) if isinstance(p, int) else p for p in det]
                        data_log = [username, (x1, y1, x2, y2), "Event"]
                        fusion_data_file.write("{}\n".format(str(data_log)))
                
                # save sort file
                if ENABLE_SORT_ALGORITHM or ENABLE_FUSION_MODEL:
                    sort_data_file.write("{} {}\n".format(str(time_stamp), str(len(track_bbs_ids))))
                    for det in track_bbs_ids:
                        x1, y1, x2, y2, id, cat = [int(p) if isinstance(p, int) else p for p in det]
                        data_log = [cat, id, (x1, y1, x2, y2), "Event"]
                        sort_data_file.write("{}\n".format(str(data_log)))

                # save yolo file
                yolo_data_file.write("{} {}\n".format(str(time_stamp), str(len(detections_with_category))))
                for det in detections_with_category:
                    x1, y1, x2, y2, score, cat = [int(p) if isinstance(p, int) else p for p in det]
                    data_log = [cat, (x1, y1, x2, y2), score]
                    yolo_data_file.write("{}\n".format(str(data_log)))
                

        #yolo_history = fusion_model.get_yolo_history()
        #print("yolo_history : {}".format(yolo_history))
        #frame = draw_utils.draw_yolo_path(frame, yolo_history)

        #beacon_history = fusion_model.get_beacon_history()
        #print("beacon_history : {}".format(beacon_history))
        #frame = draw_utils.draw_beacon_path(frame, beacon_history)
        if ENABLE_DRAW_BOX:
            if ENABLE_FUSION_MODEL:
                frame = draw_utils.draw_fusion_box(frame, fusion_result)
            elif ENABLE_SORT_ALGORITHM:
                frame = draw_utils.draw_sort_box(frame, track_bbs_ids)
            else:
                frame = draw_utils.draw_box(frame, detections_with_category)

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
            