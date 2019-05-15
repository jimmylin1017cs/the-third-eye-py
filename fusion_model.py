import time

import cv2
import numpy as np

# use dtw algorithm
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw


beacon_location = [[206.30429, 567.3016], [306.30429, 667.3016]]
beacon_on_image = np.array([[1824, 840], [1786, 215], [272, 258], [190, 893]], dtype = "float32")
beacon_on_world = np.array([[540, 1100], [540, 100], [10, 100], [10, 1100]], dtype = "float32")

beacon_hostiry = dict()
yolo_history = dict()

# box = [x, y, w, h]
# Data = [x, y]
# Fusion_result = [num, name]
# Video_data = [num, x, y]

def generate_transform_matrix(src_pts, dest_pts):

    transform_matrix = cv2.getPerspectiveTransform(src_pts, dest_pts)

    return transform_matrix

def convert_coordinate(pts, transform_matrix):
    
    convert_pts = cv2.perspectiveTransform(pts, transform_matrix)

    return convert_pts

def fusion_model(track_bbs_ids):

    transform_matrix = generate_transform_matrix(beacon_on_image, beacon_on_world)

    for det in track_bbs_ids:
        #det = track_bbs_ids[i]
        #print("det: {}".format(det))
        #x1, y1, x2, y2, id = [int(p) for p in det]
        x1, y1, x2, y2, id = [p for p in det]
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        pts = [x, y]

        pts = np.array([pts], dtype = "float32")
        pts = np.array([pts])
        convert_pts = convert_coordinate(pts, transform_matrix)
        x_b = convert_pts[0][0][0] + 250
        y_b = convert_pts[0][0][1] + 100

        if id in yolo_history:
            yolo_history[id].append([x, y])
        else:
            yolo_history[id] = list()
            yolo_history[id].append([x, y])

        if id in beacon_hostiry:
            beacon_hostiry[id].append([x_b, y_b])
        else:
            beacon_hostiry[id] = list()
            beacon_hostiry[id].append([x_b, y_b])

    print("yolo_history : {}".format(yolo_history))
    print("beacon_hostiry : {}".format(beacon_hostiry))

    dtw_table = dict()
    for beacon_id in beacon_hostiry.keys():
        b = beacon_hostiry[beacon_id]
        for yolo_id in yolo_history.keys():
            p = yolo_history[yolo_id]
            distance, path = fastdtw(p, b, dist=euclidean)
            if beacon_id not in dtw_table:
                dtw_table[beacon_id] = dict()
            dtw_table[beacon_id][yolo_id] = distance
                
                        
    print("dtw_table : {}".format(dtw_table))

    #distance1, path = fastdtw(p1, b1, dist=euclidean)
    #print("p1 - b1 : {}".format(distance1))
    #distance2, path = fastdtw(p1, b2, dist=euclidean)
    #print("p1 - b2 : {}".format(distance2))
    #print("1 : {}".format(distance2 - distance1))

    #distance1, path = fastdtw(p2, b1, dist=euclidean)
    #print("p2 - b1 : {}".format(distance1))
    #distance2, path = fastdtw(p2, b2, dist=euclidean)
    #print("p2 - b2 : {}".format(distance2))
    #print("2 : {}".format(distance2 - distance1))

def draw_path(frame, track_bbs_ids):

    exist_id = list()

    for det in track_bbs_ids:
        x1, y1, x2, y2, id = [p for p in det]
        exist_id.append(id)

    for beacon_id in beacon_hostiry.keys():
        if beacon_id not in exist_id:
            continue
        b = beacon_hostiry[beacon_id]
        for pt in b:
            cv2.putText(frame, str(beacon_id), (int(pt[0]), int(pt[1])), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)
    for yolo_id in yolo_history.keys():
        if yolo_id not in exist_id:
            continue
        p = yolo_history[yolo_id]
        for pt in p:
            cv2.putText(frame, str(yolo_id), (int(pt[0]), int(pt[1])), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1, cv2.LINE_AA)

    return frame


def do_fustion(id, pts):

    transform_matrix = generate_transform_matrix(beacon_on_image, beacon_on_world)

    #print(transform_matrix)

    pts = np.array([pts], dtype = "float32")
    pts = np.array([pts])
    #pts = np.array([983, 294], dtype = "float32")
    #print(pts)

    convert_pts = convert_coordinate(pts, transform_matrix)

    #print(convert_pts)
    print("b{} = {}, {}".format(id, convert_pts[0][0][0], convert_pts[0][0][1]))

if __name__ == "__main__":
    fusion_model([])

class FusionServer():

    def __init__(self):
        pass
