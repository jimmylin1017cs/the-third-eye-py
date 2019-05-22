import os
import time
import cv2
import numpy as np

import ast

import draw_package.draw_utils as draw_utils

if __name__ == "__main__":


    filename = "yolo_1_1558531516.886696"

    video_file = "save/" + filename + ".avi"
    data_file = "save/" + filename + ".log"

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

        if r:

            frame = draw_utils.draw_box(frame, detections_with_category)

            cv2.namedWindow("preview",0)
            cv2.resizeWindow("preview", 640, 480)
            cv2.imshow("preview", frame)

            k = cv2.waitKey(1)
            if k == 0xFF & ord("q"):
                break

        