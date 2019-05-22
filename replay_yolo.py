import os
import time
import cv2
import numpy as np

import ast

import draw_package.draw_utils as draw_utils

REPLAY_YOLO = False
REPLAY_SORT = True
REPLAY_FUSION = False

if __name__ == "__main__":

    if REPLAY_YOLO:
        data_filename = "yolo_1_1558535063.6604247"
    if REPLAY_SORT:
        data_filename = "yolo_1_sort_1558535063.6604247"
    if REPLAY_FUSION:
        data_filename = "yolo_1_fusion_1558535063.6604247"

    video_filename = "yolo_1_1558535063.6604247"

    video_file = "save/" + video_filename + ".avi"
    data_file = "save/" + data_filename + ".log"

    cap = cv2.VideoCapture(video_file)

    f = open(data_file, 'r')
    lines = f.readlines()
    f.close()

    #print(lines)

    line_number = 0

    while True:
        r, frame = cap.read()
        
        l = lines[line_number].strip()
        n = l.split(' ')[1]
        n = int(n)

        print(n)

        if REPLAY_YOLO:

            detections_with_category = list()

            for i in range(n):
                line_number += 1
                l = lines[line_number].strip()
                box = ast.literal_eval(l)

                cat, bounds, score = box
                x1, y1, x2, y2 = bounds

                detections_with_category.append([x1, y1, x2, y2, score, cat])
            
            print(detections_with_category)

            line_number += 1

        elif REPLAY_SORT:

            track_bbs_ids = list()

            for i in range(n):
                line_number += 1
                l = lines[line_number].strip()
                box = ast.literal_eval(l)

                cat, sort_id, bounds, score = box
                x1, y1, x2, y2 = bounds

                track_bbs_ids.append([x1, y1, x2, y2, sort_id, cat])
            
            print(track_bbs_ids)

            line_number += 1

        elif REPLAY_FUSION:

            fusion_result = list()

            for i in range(n):
                line_number += 1
                l = lines[line_number].strip()
                box = ast.literal_eval(l)

                username, bounds, score = box
                x1, y1, x2, y2 = bounds

                fusion_result.append([x1, y1, x2, y2, username])
            
            print(fusion_result)

            line_number += 1

        if r:

            if REPLAY_YOLO:
                frame = draw_utils.draw_box(frame, detections_with_category)
            if REPLAY_SORT:
                frame = draw_utils.draw_sort_box(frame, track_bbs_ids)
            if REPLAY_FUSION:
                frame = draw_utils.draw_fusion_box(frame, fusion_result)

            cv2.namedWindow("preview",0)
            cv2.resizeWindow("preview", 640, 480)
            cv2.imshow("preview", frame)

            k = cv2.waitKey(1)
            if k == 0xFF & ord("q"):
                break

        