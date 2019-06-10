import iottalk_package.DAN as DAN
import time, requests, random
import json
import numpy as np
import cv2
import base64
#from ast import literal_eval
import ast

#from requests.utils import requote_uri


#ServerURL = 'http://IP:9999' #with no secure connection
#ServerURL = 'https://DomainName' #with SSL connection
ServerURL = 'http://192.168.1.134:9999'
#Reg_addr = None #if None, Reg_addr = MAC address
Reg_addr = "B06EBF60297A"

#DAN.profile['dm_name']='HumanRecognition'
#DAN.profile['df_list']=['BoxCoord-O', 'BoxID-O', 'FrameID-O']
DAN.profile['dm_name']='ObjID'
DAN.profile['df_list']=['Box-O', 'Cmd-O', 'Loc-O']
DAN.profile['d_name']= None # None for autoNaming
DAN.device_registration_with_retry(ServerURL, Reg_addr)

#cap = cv2.VideoCapture('time_counter.flv')

def receive_all_data_from_iottalk():

    #print('start receive frame from iottalk')
    yolo_dataset = {}
    yolo_time_stamp = {}

    beacon_dataset = {}
    beacon_time_stamp = None

    enable_ids = []
    cmd_room_id = None

    try:

        # pull boxes information
        box = DAN.pull('Box-O')

        # boxes information
        if box != None:

            #print("pull boxes information")
            #rint(box)

            box_list = ast.literal_eval(box[0])
            #print("box_list : {}".format(box_list))


            for i in range(len(box_list)):
                yolo_id = box_list[i][0]
                #print("yolo_id : {}".format(yolo_id))
                if yolo_id not in yolo_dataset:
                    yolo_dataset[yolo_id] = []

                box_data = box_list[i][1]

                time_stamp = box_data[0]
                yolo_time_stamp[yolo_id] = time_stamp
                #print("time_stamp : {}".format(time_stamp))

                #print("box_data : {}".format(box_data))
                for j in range(1, len(box_data)):
                    det = box_data[j]
                    id, x1, y1, x2, y2 = [int(p) for p in det]
                    yolo_dataset[yolo_id].append([x1, y1, x2, y2, id])

        #print("yolo_dataset : {}".format(yolo_dataset))
        #print("yolo_time_stamp : {}".format(yolo_time_stamp))


        # pull beacon information
        beacon = DAN.pull('Loc-O')

        # beacon information
        if beacon != None:

            #print("pull beacon information")
            #rint(box)

            beacon_list = ast.literal_eval(beacon[0])
            beacon_time_stamp = beacon_list[0]

            #print('frame: {}'.format(frame_id))

            for i in range(1, len(beacon_list)):

                location = beacon_list[i]
                room_id, user_id, x, y = [int(p) for p in location]
                room_id = room_id
                user_id = user_id
                
                if room_id not in beacon_dataset:
                    beacon_dataset[room_id] = {}
                beacon_dataset[room_id][user_id] = [x, y]

        # pull cmd information
        cmd = DAN.pull('Cmd-O')

        # cmd information
        if cmd != None:

            #print("pull cmd information")
            #rint(box)

            cmd_list = ast.literal_eval(cmd[0])
            cmd_room_id = cmd_list[0]

            #print('frame: {}'.format(frame_id))

            for user_id in cmd_list[1]:

                enable_ids.append(user_id)

        return (yolo_time_stamp, yolo_dataset, beacon_time_stamp, beacon_dataset, cmd_room_id, enable_ids)

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            #time.sleep(1)    

    #time.sleep(0.02)
    return None

def receive_data_from_iottalk():

    #print('start receive frame from iottalk')
    track_bbs_ids = []
    yolo_id = None
    box_time_stamp = None

    beacon_dataset = {}
    beacon_time_stamp = None

    enable_ids = []
    cmd_room_id = None

    try:

        # pull boxes information
        box = DAN.pull('Box-O')

        # boxes information
        if box != None:

            #print("pull boxes information")
            #rint(box)

            box_list = ast.literal_eval(box[0])
            yolo_id = box_list[0]
            box_time_stamp = box_list[1]

            #print('frame: {}'.format(frame_id))

            for i in range(2, len(box_list)):

                det = box_list[i]
                id, x1, y1, x2, y2 = [int(p) for p in det]
                
                track_bbs_ids.append([x1, y1, x2, y2, id])

        # pull beacon information
        beacon = DAN.pull('Loc-O')

        # beacon information
        if beacon != None:

            #print("pull beacon information")
            #rint(box)

            beacon_list = ast.literal_eval(beacon[0])
            beacon_time_stamp = beacon_list[0]

            #print('frame: {}'.format(frame_id))

            for i in range(1, len(beacon_list)):

                location = beacon_list[i]
                room_id, user_id, x, y = [int(p) for p in location]
                room_id = room_id
                user_id = user_id
                
                if room_id not in beacon_dataset:
                    beacon_dataset[room_id] = {}
                beacon_dataset[room_id][user_id] = [x, y]

        # pull cmd information
        cmd = DAN.pull('Cmd-O')

        # cmd information
        if cmd != None:

            #print("pull cmd information")
            #rint(box)

            cmd_list = ast.literal_eval(cmd[0])
            cmd_room_id = cmd_list[0]

            #print('frame: {}'.format(frame_id))

            for user_id in cmd_list[1]:

                enable_ids.append(user_id)

        return (yolo_id, box_time_stamp, track_bbs_ids, beacon_time_stamp, beacon_dataset, cmd_room_id, enable_ids)

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            #time.sleep(1)    

    #time.sleep(0.02)
    return None


#all_beacon_information_record = None

def receive_frame_from_iottalk():

    global all_beacon_information_record

    start_time = time.time()
    #time.sleep(0.02)

    #print('start receive frame from iottalk')
    all_boxes_information = list()
    all_beacon_information = list()
    display_ids = list()
    display_ids_record = None
    try:

        # pull boxes information
        pull_box = False
        box = DAN.pull('Box-O')

        #print(box_x, box_y, box_ids, frame_id)

        # pull beacon information
        user = DAN.pull('Loc-O')

        # pull display information
        display_ids = DAN.pull('Cmd-O')


        # boxes information
        if box != None:

            print("pull boxes information")
            #rint(box)

            box_list = ast.literal_eval(box[0])
            box_time_stamp = box_list[0]

            #print('frame: {}'.format(frame_id))

            for i in range(1, len(box_list)):
                #print('person: {}'.format(box_ids[i]))
                #print('x: {}, {}'.format(box_x[i*2], box_x[i*2+1]))
                #print('y: {}, {}'.format(box_y[i*2], box_y[i*2+1]))

                boxes_information = dict()
                boxes_information['stamp'] = box_time_stamp
                boxes_information['id'] = box_list[i][0]
                boxes_information['x1'] = box_list[i][1]
                boxes_information['y1'] = box_list[i][2]
                boxes_information['x2'] = box_list[i][3]
                boxes_information['y2'] = box_list[i][4]

                all_boxes_information.append(boxes_information)

            #print(all_boxes_information)
            pull_box = True

        # beacon information
        if user != None:

            print("pull beacon information")
            #print(user)

            user_list = ast.literal_eval(user[0])
            user_time_stamp = user_list[0]

            for i in range(1, len(user_list)):
                #print('person: {}'.format(user_ids[i]))
                #print('x: {}'.format(user_x[i]))
                #print('y: {}'.format(user_y[i]))

                beacon_information = dict()
                beacon_information['stamp'] = user_time_stamp
                beacon_information['id'] = user_list[i][0]
                beacon_information['x'] = user_list[i][1]
                beacon_information['y'] = user_list[i][2]

                all_beacon_information.append(beacon_information)

            all_beacon_information_record = all_beacon_information

        # display information
        if display_ids != None:

            #print("pull display information")
            #print(display_ids)

            display_ids = ast.literal_eval(display_ids[0])
            display_ids_record = list(display_ids)

            #print(display_ids)
        #display_ids_record = [1, 2]

        #time.sleep(0.02)
        #print((all_boxes_information, display_ids_record, all_beacon_information_record), time.time() - start_time)
        return (all_boxes_information, display_ids_record, all_beacon_information_record)
            #return (tmp_boxes, tmp_enable_name, tmp_beacon)

            
            #print(frame_id)
            #print(box_coord)
            #print(box_id)

            #print(box_coord)
            
            #box_coords = json.loads(box_coord[0])
            #print(str(frame_id[0]) + ' : ' + str(box_coords))

            #boxes_information['stamp'] = frame_id[0]
            #boxes_information['id'] = box_id[0]
            #boxes_information['x1'] = box_coord[0]
            #boxes_information['y1'] = box_coord[1]
            #boxes_information['x2'] = box_coord[2]
            #boxes_information['y2'] = box_coord[3]
            #print(boxes_information)

            #all_boxes_information = data[0].split('|')
            #all_boxes_information_size = len(all_boxes_information)
            #boxes_information = all_boxes_information[0]
            #enable_name = all_boxes_information[all_boxes_information_size - 1]
            #print(person_information)
            
            
            
            #tmp_boxes = json.loads(boxes_information)
            #tmp_enable_name = json.loads(enable_name)
            #print(tmp_boxes)
            #print(tmp_enable_name)

            #tmp_beacon = list()
            #for i in range(1, all_boxes_information_size - 1):
            #    tmp_beacon.append(json.loads(all_boxes_information[i]))

            #print(tmp_beacon)
            
            #tmp_nparray = np.array(tmp_array)
            #tmp_buf = tmp_nparray.astype('uint8')
            #frame = cv2.imdecode(tmp_buf, 1)
            #cv2.imshow('Receive',frame)
            #cv2.waitKey(1)

            #return (tmp_boxes, tmp_enable_name, tmp_beacon)

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            #time.sleep(1)    

    #time.sleep(0.02)
    return None


if __name__ == "__main__":

    while True:
        receive_frame_from_iottalk()

'''def receive_frame_from_iottalk():

    #print('start receive frame from iottalk')
    try:
        data = DAN.pull('ODF_ALL')
        if data != None:
            print("pull")
            print(data[0])
            all_boxes_information = data[0].split('|')
            all_boxes_information_size = len(all_boxes_information)
            boxes_information = all_boxes_information[0]
            enable_name = all_boxes_information[all_boxes_information_size - 1]
            #print(person_information)
            tmp_boxes = json.loads(boxes_information)
            tmp_enable_name = json.loads(enable_name)
            print(tmp_boxes)
            print(tmp_enable_name)

            tmp_beacon = list()
            for i in range(1, all_boxes_information_size - 1):
                tmp_beacon.append(json.loads(all_boxes_information[i]))

            print(tmp_beacon)
            
            #tmp_nparray = np.array(tmp_array)
            #tmp_buf = tmp_nparray.astype('uint8')
            #frame = cv2.imdecode(tmp_buf, 1)
            #cv2.imshow('Receive',frame)
            #cv2.waitKey(1)

            return (tmp_boxes, tmp_enable_name, tmp_beacon)

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            #time.sleep(1)    

    #time.sleep(0.2)
    return None'''
