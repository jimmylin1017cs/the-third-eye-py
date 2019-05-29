import iottalk_package.DAN as DAN
import time, requests, random
import json
import numpy as np
import cv2
import base64
from ast import literal_eval

#from requests.utils import requote_uri

#ServerURL = 'http://IP:9999' #with no secure connection
#ServerURL = 'https://DomainName' #with SSL connection
ServerURL = 'http://192.168.1.134:9999'
#Reg_addr = None #if None, Reg_addr = MAC address
Reg_addr = "B06EBF60297E"

#DAN.profile['dm_name']='HumanBox'
#DAN.profile['df_list']=['BoxCoord-I', 'BoxID-I', 'FrameID-I']
DAN.profile['dm_name']='ObjBox'
DAN.profile['df_list']=['Box-I']
DAN.profile['d_name']= None # None for autoNaming
DAN.device_registration_with_retry(ServerURL, Reg_addr)

#cv2.setUseOptimized(True)

#cap = cv2.VideoCapture('time_counter.flv')

def send_data_to_iottalk(yolo_id, time_stamp, track_bbs_ids):

    try:

        obj_box = []
        obj_box.append(yolo_id)
        obj_box.append(time_stamp)

        for det in track_bbs_ids:

            x1, y1, x2, y2, id, cat = [int(p) if isinstance(p, int) else p for p in det]

            person = []
            person.append(id)
            person.append(x1)
            person.append(y1)
            person.append(x2)
            person.append(y2)

            obj_box.append(person)

        DAN.push('Box-I', str(obj_box))
        print('push')

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            #time.sleep(1)
    #time.sleep(0.02)


def send_boxes_to_iottalk(boxes):

    #print(type(buf))
    #array = buf.tolist()
    #print(len(buf))

    #boxes_information = json.dumps(boxes)
    #print(boxes_information)

    #print(data)
    #print(len(data))

    try:
        # @0: json
        #print(boxes)

        obj_box = [boxes[0]['timer']]
        
        for i in range(len(boxes)):

            person = []

            id = boxes[i]['id']
            x1 = boxes[i]['x1']
            y1 = boxes[i]['y1']
            x2 = boxes[i]['x2']
            y2 = boxes[i]['y2']

            person.append(id)
            person.append(x1)
            person.append(y1)
            person.append(x2)
            person.append(y2)

            obj_box.append(person)

        DAN.push('Box-I', str(obj_box))
        print('push')

        #if(len(boxes) > 0):
            #DAN.push('Box-I', int(boxes[0]['stamp']))

            
    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            #time.sleep(1)
    #time.sleep(0.2)


'''
def send_boxes_to_iottalk(boxes):

    #print(type(buf))
    #array = buf.tolist()
    #print(len(buf))

    #boxes_information = json.dumps(boxes)
    #print(boxes_information)

    #print(data)
    #print(len(data))

    try:
        # @0: json
        #print(boxes)
        for i in range(len(boxes)):
            DAN.push('FrameID-I', int(boxes[i]['stamp']))
            DAN.push('BoxID-I', int(boxes[i]['id']))
            DAN.push('BoxCoord-I', int(boxes[i]['x1']), int(boxes[i]['y1']), int(boxes[i]['x2']), int(boxes[i]['y2']))
            time.sleep(0.5)
        print('push')
    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            #time.sleep(1)
    #time.sleep(0.2)
'''
