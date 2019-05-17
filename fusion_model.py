import time

import glob
import os

import cv2
import numpy as np

# use dtw algorithm
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw


beacon_location = [[206.30429, 567.3016], [306.30429, 667.3016]]
beacon_on_image = np.array([[1824, 840], [1786, 215], [272, 258], [190, 893]], dtype = "float32")
beacon_on_world = np.array([[540, 1100], [540, 100], [10, 100], [10, 1100]], dtype = "float32")

beacon_data_dir = "beacon_dataset/"

username_file = "username.txt"
username_table = dict()

beacon_history = dict()
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

def get_username():

    if os.path.exists(username_file):

        with open(username_file, 'r') as f:

            for line in f.readlines():

                l = line.strip().split("=")
                id = l[0]
                username = l[1]
                username_table[id] = username

    print(username_table)

def get_yolo_history():
    return yolo_history

def get_beacon_history():
    return beacon_history

def get_beacon_data():

    beacon_dataset = dict()

    if os.path.isdir(beacon_data_dir):

        all_beacon_data = glob.glob(beacon_data_dir + '*')
        #print(all_beacon_data)

        for beacon_data in all_beacon_data:

            with open(beacon_data, 'r') as f:

                id = os.path.basename(beacon_data).split('.')[0]
                #print("id : {}".format(id))
                
                l = f.readline().strip()
                l = l.split(",")
                pt = [int(a) for a in l]
                #print(pt)
                beacon_dataset[id] = pt

    return beacon_dataset

def fusion_model(track_bbs_ids):

    # generate transform matrix image -> world
    #transform_matrix = generate_transform_matrix(beacon_on_image, beacon_on_world)
    # generate transform matrix world -> image
    transform_matrix = generate_transform_matrix(beacon_on_world, beacon_on_image)

    existe_yolo_id = list()
    existe_beacon_id = list()

    beacon_dataset = get_beacon_data()
    print("beacon_dataset : {}".format(beacon_dataset))

    # store beacon data
    for beacon_id in beacon_dataset.keys():
            
        x_b = beacon_dataset[beacon_id][0]
        y_b = beacon_dataset[beacon_id][1]

        pts = [x_b, y_b]
        pts = np.array([pts], dtype = "float32")
        pts = np.array([pts])
        convert_pts = convert_coordinate(pts, transform_matrix)

        convert_x_b = convert_pts[0][0][0]
        convert_y_b = convert_pts[0][0][1]

        if beacon_id not in beacon_history:
            beacon_history[beacon_id] = list()
        #beacon_history[beacon_id].append([x_b, y_b])
        beacon_history[beacon_id].append([convert_x_b, convert_y_b])

    # store yolo data
    for det in track_bbs_ids:
        #det = track_bbs_ids[i]
        #print("det: {}".format(det))
        #x1, y1, x2, y2, id = [int(p) for p in det]
        x1, y1, x2, y2, id = [p for p in det]
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        pts = [x, y]
        existe_yolo_id.append(id)
        #existe_beacon_id.append(id)

        '''pts = np.array([pts], dtype = "float32")
        pts = np.array([pts])
        convert_pts = convert_coordinate(pts, transform_matrix)'''

        #convert_x = convert_pts[0][0][0]
        #convert_y = convert_pts[0][0][1]

        if id not in yolo_history:
            yolo_history[id] = list()
        #yolo_history[id].append([convert_x, convert_y])
        yolo_history[id].append([x, y])
        

        '''x_b = convert_pts[0][0][0] + 250
        y_b = convert_pts[0][0][1] + 100

        if id in yolo_history:
            yolo_history[id].append([x, y])
        else:
            yolo_history[id] = list()
            yolo_history[id].append([x, y])

        if id in beacon_history:
            beacon_history[id].append([x_b, y_b])
        else:
            beacon_history[id] = list()
            beacon_history[id].append([x_b, y_b])'''

    # yolo id disappear
    disappear_yolo_id = list()

    for yolo_id in yolo_history.keys():
        if yolo_id not in existe_yolo_id:
            disappear_yolo_id.append(yolo_id)

    for yolo_id in disappear_yolo_id:
        yolo_history.pop(yolo_id, None)


    # beacon id disappear
    '''disappear_beacon_id = list()

    for beacon_id in beacon_history.keys():
        if beacon_id not in existe_beacon_id:
            disappear_beacon_id.append(beacon_id)

    for beacon_id in disappear_beacon_id:
        beacon_history.pop(beacon_id, None)'''


    #print("yolo_history : {}".format(yolo_history))
    #print("beacon_history : {}".format(beacon_history))

    #
    # { beacon_id : { yolo_id : distance } }
    #
    #             | yolo_id_1 | yolo_id_2 |
    # beacon_id_1 |    123    |    456    |
    # beacon_id_2 |    789    |    987    |
    #
    #
    dtw_table = dict()
    for beacon_id in beacon_history.keys():
        b = beacon_history[beacon_id]
        b_len = len(b)
        for yolo_id in yolo_history.keys():
            p = yolo_history[yolo_id]
            p_len = len(p)
            min_len = min(b_len, p_len)
            distance, path = fastdtw(p[-min_len:], b[-min_len:], dist=euclidean)
            if beacon_id not in dtw_table:
                dtw_table[beacon_id] = dict()
            dtw_table[beacon_id][yolo_id] = distance
                
                        
    #print("dtw_table : {}".format(dtw_table))

    dtw_variance = dict()

    for beacon_id in beacon_history.keys():
        a = np.array(list(dtw_table[beacon_id].values()))
        #print("a : {}".format(a))
        variance = np.var(a)
        dtw_variance[beacon_id] = variance
        #print(dtw_table[beacon_id].values())

    #print(dtw_variance)

    # sort by variance large -> small
    # largest variance has more priority to choose yolo id
    sorted_dtw_variance = sorted([(value, key) for (key, value) in dtw_variance.items()], reverse=True)
    #print(sorted_dtw_variance)

    fusion_result = dict()

    for i in range(len(sorted_dtw_variance)):

        # get beacon id and its row
        current_id = sorted_dtw_variance[i][1]
        sorted_dtw_table = dtw_table[current_id]
        # sort by distance small -> large and choose smallest distance yolo id (fusion id)
        sorted_dtw_table = sorted([(value, key) for (key, value) in sorted_dtw_table.items()], reverse=False)
        fusion_id = sorted_dtw_table[0][1]

        # create fusion result { fusion id (yolo id) : username by beacon id }
        fusion_result[fusion_id] = username_table[current_id]

        # remove yolo id already choosed from table
        for beacon_id in beacon_history.keys():
            dtw_table[beacon_id].pop(fusion_id, None)

    print("fusion_result : {}".format(fusion_result))

    return fusion_result

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
