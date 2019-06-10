import cv2
import numpy as np
import time
import configparser

import fusion_models
import frame_receiver
import frame_sender
import draw_package.draw_utils as draw_utils
import iottalk_package.DAI_pull as DAI_pull


config = configparser.ConfigParser()
config.read('display_config.ini')

ENABLE_SERVER = config.getboolean('Display_Server', 'Enable_Server')
if ENABLE_SERVER:
    SERVER_IP = config.get('Display_Server', 'Server_IP')
    SERVER_PORT = config.get('Display_Server', 'Server_Port')
    SERVER_PORT = int(SERVER_PORT)

print("ENABLE_SERVER = {}".format(ENABLE_SERVER))

ENABLE_SENDER = config.getboolean('Frame_Sender', 'Enable_Sender') # send frame to server

if ENABLE_SENDER:
    RECEIVER_IP = config.get('Frame_Sender', 'Receiver_IP')
    RECEIVER_PORT = config.get('Frame_Sender', 'Receiver_Port')
    RECEIVER_PORT = int(RECEIVER_PORT)

print("ENABLE_SENDER = {}".format(ENABLE_SENDER))

SHOW_PREVIEW = config.getboolean('Display_Function', 'Show_Preview')
SAVE_VIDEO = config.getboolean('Display_Function', 'Save_Video')
SAVE_DATA = config.getboolean('Display_Function', 'Save_Data')
print("SHOW_PREVIEW = {}".format(SHOW_PREVIEW))
print("SAVE_VIDEO = {}".format(SAVE_VIDEO))
print("SAVE_DATA = {}".format(SAVE_DATA))

if __name__ == "__main__":
    

    if ENABLE_SERVER:
        frame_receiver.init_frame_receiver(SERVER_IP, SERVER_PORT)
    
    #frame_buffer = dict()

    # initial sender
    if ENABLE_SENDER:
        dest_ip = RECEIVER_IP
        dest_port = RECEIVER_PORT
        sender = frame_sender.FrameSender(dest_ip, dest_port)
        sender.start()

    # initial fusion model
    username_table = fusion_models.FusionModel.get_username_table()
    print("username_table : {}".format(username_table))

    prev_time_stamp = 0
    time_stamp = time.time()
    prev_beacon_dataset = {}
    prev_enable_ids = [0, 1, 2]
    #prev_enable_usernames = {1: ['unknown', 'apple', 'orange'], 2: ['unknown', 'apple', 'orange']}
    prev_enable_usernames = {}

    call_fusion_models = {}

    yolo_ids = [1, 2]

    for yolo_id in yolo_ids:
        call_fusion_models[yolo_id] = fusion_models.FusionModel(yolo_id)

    while True:

        '''prev_time_stamp = time_stamp
        time_stamp = time.time()
        fps = 1 / (time_stamp - prev_time_stamp)'''

        #print(prev_time_stamp)
        #print(time_stamp)

        #print("FPS : {}".format(str(fps)))

        #frame_time_stamp = frame_receiver.get_frame_time_stamp()
        #frame_time_stamp = str(frame_time_stamp)
        frame_buffer = frame_receiver.get_frame_buffer()
        #time.sleep(1)
        frame_yolo_id, frame_time_stamp, track_bbs_ids, location_time_stamp, beacon_dataset, cmd_room_id, enable_ids = DAI_pull.receive_data_from_iottalk()
        frame_time_stamp = str(frame_time_stamp)
        #print(frame_time_stamp)
        #print(track_bbs_ids)
        #print(frame_buffer)

        #yolo_ids = [frame_yolo_id]

        if location_time_stamp is None:
            beacon_dataset = prev_beacon_dataset
        prev_beacon_dataset = beacon_dataset

        #print("beacon_dataset : {}".format(beacon_dataset))

        if cmd_room_id is None:
            #enable_ids = prev_enable_ids
            enable_usernames = prev_enable_usernames
        else:
            enable_usernames[cmd_room_id] = []
            for user_id in enable_ids:
                enable_usernames[cmd_room_id].append(username_table[user_id])

        #for yolo_id in yolo_ids:
        if frame_yolo_id is not None:
            yolo_id = frame_yolo_id

            fm = call_fusion_models[yolo_id]

            if yolo_id in enable_usernames:
                enable_username = enable_usernames[yolo_id]
            else:
                enable_username = []

            if frame_buffer is not None:

                if yolo_id in frame_buffer:

                    frame_buffer = frame_buffer[yolo_id]

                    #frame_buffer[frame_time_stamp] = frame

                    #print(frame_buffer[1])

                    '''cv2.namedWindow("preview",0)
                    cv2.resizeWindow("preview", 640, 480)
                    cv2.imshow("preview", frame_buffer)

                    k = cv2.waitKey(1)
                    if k == 0xFF & ord("q"):
                        break'''

                    if frame_time_stamp is not None and frame_time_stamp in frame_buffer:
                        
                        #print("enable_username : {}".format(enable_username))
                        #print(frame_time_stamp)
                        #print(track_bbs_ids)

                        #beacon_dataset = fusion_model.get_beacon_data()
                        #fusion_result = fusion_model.fusion_model(track_bbs_ids, beacon_dataset)
                        if yolo_id in beacon_dataset:
                            fusion_result = fm.do_fusion_model(track_bbs_ids, beacon_dataset[yolo_id])
                        else:
                            fusion_result = fm.do_fusion_model(track_bbs_ids, {})
                        #print("fusion_result : {}".format(fusion_result))
                        #print("yolo_id : {}\nframe_buffer.keys() : {}".format(yolo_id, frame_buffer.keys()))
                        frame = draw_utils.draw_fusion_box_select_username(frame_buffer[frame_time_stamp], fusion_result, enable_username)

                        #print(fm.get_yolo_history())

                        prev_time_stamp = time_stamp
                        time_stamp = time.time()
                        fps = 1 / (time_stamp - prev_time_stamp)

                        print("FPS : {}".format(str(fps)))

                        if ENABLE_SENDER:
                            #room_id = 1
                            room_id = fm.get_room_id()
                            print("room_id : {}".format(room_id))
                            sender.send_frame(room_id, time_stamp, frame)

                        if SHOW_PREVIEW:
                            cv2.namedWindow("preview",0)
                            cv2.resizeWindow("preview", 640, 480)
                            cv2.imshow("preview", frame)

                            k = cv2.waitKey(1)
                            if k == 0xFF & ord("q"):
                                break