import time
import glob
import os
import cv2
import numpy as np
import configparser
import ast

# use dtw algorithm
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

config = configparser.ConfigParser()
config.read('fusion_config.ini')

#beacon_on_image = np.array([[1824, 840], [1786, 215], [272, 258], [190, 893]], dtype = "float32")
#beacon_on_world = np.array([[540, 1100], [540, 100], [10, 100], [10, 1100]], dtype = "float32")

FUSION_WINDOWS = config.get('Fusion_Config', 'Fusion_Windows')
FUSION_WINDOWS = int(FUSION_WINDOWS)

USERNAME_FILE = config.get('Fusion_Config', 'Username_File')
BEACON_ON_IMAGE = config.get('Fusion_Config', 'Beacon_On_Image')
BEACON_ON_WORLD = config.get('Fusion_Config', 'Beacon_On_World')

BEACON_ON_IMAGE = ast.literal_eval(BEACON_ON_IMAGE)
BEACON_ON_WORLD = ast.literal_eval(BEACON_ON_WORLD)

print("FUSION_WINDOWS = {}".format(FUSION_WINDOWS))
print("USERNAME_FILE = {}".format(USERNAME_FILE))
print("BEACON_ON_IMAGE = {}".format(BEACON_ON_IMAGE))
print("BEACON_ON_WORLD = {}".format(BEACON_ON_WORLD))

class FusionModel():

    username_file = USERNAME_FILE
    username_table = None

    def __init__(self, room_id):

        self.room_id = room_id
        self.beacon_history = dict()
        self.yolo_history = dict()
        self.beacon_on_image = np.array(BEACON_ON_IMAGE, dtype = "float32")
        self.beacon_on_world = np.array(BEACON_ON_WORLD, dtype = "float32")
        self.funsion_windows = FUSION_WINDOWS

        self.transform_matrix = self.generate_transform_matrix(self.beacon_on_world, self.beacon_on_image)

    def get_username_table():
        if FusionModel.username_table is None:
            FusionModel.username_table = dict()
            FusionModel.generate_username()
        return FusionModel.username_table

    def generate_username():

        if os.path.exists(FusionModel.username_file):

            with open(FusionModel.username_file, 'r') as f:

                for line in f.readlines():

                    l = line.strip().split("=")
                    id = int(l[0])
                    username = l[1]
                    FusionModel.username_table[id] = username

        #print("FusionModel.username_table : {}".format(FusionModel.username_table))

    def get_room_id(self):
        return self.room_id
    
    def get_yolo_history(self):
        return self.yolo_history

    def get_beacon_history(self):
        return self.beacon_history

    def get_transform_matrix(self):
        return self.transform_matrix

    def generate_transform_matrix(self, src_pts, dest_pts):

        transform_matrix = cv2.getPerspectiveTransform(src_pts, dest_pts)

        return transform_matrix

    def convert_coordinate(self, pts, transform_matrix):
    
        convert_pts = cv2.perspectiveTransform(pts, transform_matrix)

        return convert_pts

    def do_fusion_model(self, track_bbs_ids, beacon_dataset):

        # yolo id if appear
        existe_yolo_id = list()
        # beacon id if appear
        existe_beacon_id = list()

        #
        # transform location to image dimension
        #
        for beacon_id in beacon_dataset.keys():
            
            x_b = beacon_dataset[beacon_id][0]
            y_b = beacon_dataset[beacon_id][1]

            pts = [x_b, y_b]
            pts = np.array([pts], dtype = "float32")
            pts = np.array([pts])
            convert_pts = self.convert_coordinate(pts, self.transform_matrix)

            convert_x_b = convert_pts[0][0][0]
            convert_y_b = convert_pts[0][0][1]

            # store location history
            if beacon_id not in self.beacon_history:
                self.beacon_history[beacon_id] = list()
            self.beacon_history[beacon_id].append([convert_x_b, convert_y_b])

        #
        # store yolo data
        #
        for det in track_bbs_ids:
            
            # 6 : have category
            if len(det) == 5:
                x1, y1, x2, y2, id = [p for p in det]
            elif len(det) == 6:
                x1, y1, x2, y2, id, cat = [p for p in det]

            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
            pts = [x, y]
            existe_yolo_id.append(id)


            if id not in self.yolo_history:
                self.yolo_history[id] = list()
            self.yolo_history[id].append([x, y])


        # yolo id disappear
        disappear_yolo_id = list()

        #
        # remove disappear yolo id
        #
        for yolo_id in self.yolo_history.keys():
            if yolo_id not in existe_yolo_id:
                disappear_yolo_id.append(yolo_id)

        for yolo_id in disappear_yolo_id:
            self.yolo_history.pop(yolo_id, None)

        '''
        # beacon id disappear
        disappear_beacon_id = list()

        #
        # remove disappear beacon id
        #
        for beacon_id in self.beacon_history.keys():
            if beacon_id not in existe_beacon_id:
                disappear_beacon_id.append(beacon_id)

        for beacon_id in disappear_beacon_id:
            self.beacon_history.pop(beacon_id, None)'''


        #print("self.yolo_history : {}".format(self.yolo_history))
        #print("self.beacon_history : {}".format(self.beacon_history))

        #
        # { beacon_id : { yolo_id : distance } }
        #
        #             | yolo_id_1 | yolo_id_2 |
        # beacon_id_1 |    123    |    456    |
        # beacon_id_2 |    789    |    987    |
        #
        #
        dtw_table = dict()
        for beacon_id in self.beacon_history.keys():
            b = self.beacon_history[beacon_id]
            b_len = len(b)
            for yolo_id in self.yolo_history.keys():
                p = self.yolo_history[yolo_id]
                p_len = len(p)
                min_len = min(b_len, p_len, self.funsion_windows)
                distance, path = fastdtw(p[-min_len:], b[-min_len:], dist=euclidean)
                if beacon_id not in dtw_table:
                    dtw_table[beacon_id] = dict()
                dtw_table[beacon_id][yolo_id] = distance
                    
                            
        #print("dtw_table : {}".format(dtw_table))

        dtw_variance = dict()

        for beacon_id in self.beacon_history.keys():
            if beacon_id in dtw_table:
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

        fusion_map = dict()

        for i in range(len(sorted_dtw_variance)):

            # sorted_dtw_variance = variance : beacon id
            # get beacon id and its row
            current_id = sorted_dtw_variance[i][1]
            sorted_dtw_table = dtw_table[current_id]
            # check if sorted_dtw_table is empty
            if not sorted_dtw_table:
                break
            # sort by distance small -> large and choose smallest distance yolo id (fusion id)
            sorted_dtw_table = sorted([(value, key) for (key, value) in sorted_dtw_table.items()], reverse=False)
            fusion_id = sorted_dtw_table[0][1]

            # create fusion result { fusion id (yolo id) : username by beacon id }
            fusion_map[fusion_id] = self.username_table[current_id]

            # remove yolo id already choosed from table
            for beacon_id in self.beacon_history.keys():
                dtw_table[beacon_id].pop(fusion_id, None)

        #print("fusion_map : {}".format(fusion_map))

        fusion_result = []
        for det in track_bbs_ids:

            if len(det) == 5:
                x1, y1, x2, y2, id = [int(p) if isinstance(p, int) else p for p in det]
            elif len(det) == 6:
                x1, y1, x2, y2, id, cat = [int(p) if isinstance(p, int) else p for p in det]

            if id in fusion_map:
                username = fusion_map[id]
            else:
                username = "unknown"

            fusion_result.append([x1, y1, x2, y2, username])

        for beacon_id in self.beacon_history.keys():
            b = self.beacon_history[beacon_id]
            b_len = len(b)

            if b_len > self.funsion_windows:
                self.beacon_history[beacon_id] = b[-self.funsion_windows:]

        for yolo_id in self.yolo_history.keys():
            p = self.yolo_history[yolo_id]
            p_len = len(p)
            if p_len > self.funsion_windows:
                self.yolo_history[yolo_id] = p[-self.funsion_windows:]

        return fusion_result

if __name__ == "__main__":
    fm = FusionModel(1)
