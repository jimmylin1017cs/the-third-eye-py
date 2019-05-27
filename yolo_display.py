import cv2
import numpy as np
import time

import fusion_model
import yolo_server
import draw_package.draw_utils as draw_utils
import iottalk_package.DAI_pull as DAI_pull


if __name__ == "__main__":
    
    yolo_server.init_yolo_server()

    fusion_model.get_username()

    #frame_buffer = dict()

    prev_time_stamp = 0
    time_stamp = time.time()

    while True:

        '''prev_time_stamp = time_stamp
        time_stamp = time.time()
        fps = 1 / (time_stamp - prev_time_stamp)'''

        #print(prev_time_stamp)
        #print(time_stamp)

        #print("FPS : {}".format(str(fps)))

        #frame_time_stamp = yolo_server.get_frame_time_stamp()
        #frame_time_stamp = str(frame_time_stamp)
        frame_buffer = yolo_server.get_frame_buffer()
        #time.sleep(1)
        frame_time_stamp, track_bbs_ids = DAI_pull.receive_data_from_iottalk()
        frame_time_stamp = str(frame_time_stamp)
        #print(frame_time_stamp)
        #print(track_bbs_ids)
        #print(frame_buffer)

        client_id = 1

        if frame_buffer is not None:

            if client_id in frame_buffer:

                frame_buffer = frame_buffer[client_id]

                #frame_buffer[frame_time_stamp] = frame

                #print(frame_buffer[1])

                '''cv2.namedWindow("preview",0)
                cv2.resizeWindow("preview", 640, 480)
                cv2.imshow("preview", frame_buffer)

                k = cv2.waitKey(1)
                if k == 0xFF & ord("q"):
                    break'''

                if frame_time_stamp is not None and frame_time_stamp in frame_buffer:

                    #print(frame_time_stamp)
                    #print(track_bbs_ids)

                    beacon_dataset = fusion_model.get_beacon_data()
                    fusion_result = fusion_model.fusion_model(track_bbs_ids, beacon_dataset)
                    frame = draw_utils.draw_fusion_box(frame_buffer[frame_time_stamp], fusion_result)

                    prev_time_stamp = time_stamp
                    time_stamp = time.time()
                    fps = 1 / (time_stamp - prev_time_stamp)

                    print("FPS : {}".format(str(fps)))

                    cv2.namedWindow("preview",0)
                    cv2.resizeWindow("preview", 640, 480)
                    cv2.imshow("preview", frame)

                    k = cv2.waitKey(1)
                    if k == 0xFF & ord("q"):
                        break