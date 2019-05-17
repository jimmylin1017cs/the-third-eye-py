import cv2
import numpy as np

# use dtw algorithm
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

def draw_box(frame, track_bbs_ids, fusion_result):

    for det in track_bbs_ids:
        #det = track_bbs_ids[i]
        #print("det: {}".format(det))
        x1, y1, x2, y2, id = [int(p) for p in det]
        cv2.rectangle(frame, (x1 , y1), (x2, y2),(0, 255, 0), 5)

        if id in fusion_result:
            username = fusion_result[id]
            cv2.putText(frame, username, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 5)
        else:
            cv2.putText(frame, "unknown", (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 5)
        #cv2.putText(frame, str(cat.decode("utf-8")), (int(x-w/2), int(y-h/2)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0))

    return frame

def draw_yolo_path(frame, yolo_history):

    for yolo_id in yolo_history.keys():
        p = yolo_history[yolo_id]
        for pt in p:
            cv2.putText(frame, str(yolo_id), (int(pt[0]), int(pt[1])), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1, cv2.LINE_AA)

    return frame

def draw_beacon_path(frame, beacon_history):

    for beacon_id in beacon_history.keys():
        b = beacon_history[beacon_id]
        for pt in b:
            #cv2.putText(frame, str(beacon_id), (int(pt[0]), int(pt[1])), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, '*' + str(beacon_id), (int(pt[0]), int(pt[1])), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)

    return frame