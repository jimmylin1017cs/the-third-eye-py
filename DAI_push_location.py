import glob
import os

import time, requests, random
import json

import iottalk_package.DAN as DAN

ServerURL = 'http://192.168.1.134:9999'
#Reg_addr = None #if None, Reg_addr = MAC address
Reg_addr = "B06EBF60297F"

DAN.profile['dm_name']='ObjLoc'
DAN.profile['df_list']=['Loc-I']
DAN.profile['d_name']= None # None for autoNaming
DAN.device_registration_with_retry(ServerURL, Reg_addr)

beacon_data_dir = "beacon_dataset/"

SAVE_DATA = False

def get_beacon_data():

    beacon_dataset = dict()

    if os.path.isdir(beacon_data_dir):

        all_beacon_data = glob.glob(beacon_data_dir + '*.txt')
        #print(all_beacon_data)

        for beacon_data in all_beacon_data:

            with open(beacon_data, 'r') as f:

                id = os.path.basename(beacon_data).split('.')[0]
                #print("id : {}".format(id))
                
                l = f.readline().strip()
                l = l.split(",")
                room_id = int(l[0])
                pt = [int(l[1]), int(l[2])]
                #print(pt)
                beacon_dataset[id] = [room_id, pt]

    return beacon_dataset

def send_location_to_iottalk(time_stamp, beacon_dataset):

    try:
        location = [time_stamp]
        for user_id in beacon_dataset.keys():
            room_id = beacon_dataset[user_id][0]
            position = beacon_dataset[user_id][1]
            location.append([int(room_id), int(user_id), position[0], position[1]])

        #print(location)

        DAN.push('Loc-I', str(location))
    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            #time.sleep(1)
    #time.sleep(0.2)


def main():
    
    # initial save data
    if SAVE_DATA:
        beacon_data_file = None

    while True:

        time_stamp = time.time()
        beacon_dataset = get_beacon_data()

        print(beacon_dataset)

        # =========================================== Save Data File ==============================================

        if SAVE_DATA:
            
            if beacon_data_file is None:
                beacon_data_file = open("save/beacon_" + str(time_stamp) + ".log", 'w')

            if beacon_data_file is not None:
                beacon_data_file.write("{}\n".format(str(time_stamp)))
                user_ids = list(beacon_dataset.keys())
                user_ids.sort()
                for user_id in user_ids:
                    room_id = beacon_dataset[user_id][0]
                    position = beacon_dataset[user_id][1]
                    x = position[0]
                    y = position[1]
                    data_log = str(user_id) + '=' + str([room_id, x, y])
                    beacon_data_file.write("{}\n".format(data_log))

        # =========================================== Save Data File End ==============================================
        
        send_location_to_iottalk(time_stamp, beacon_dataset)

if __name__ == '__main__':
    main()