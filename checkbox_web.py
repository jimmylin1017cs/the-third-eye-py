from flask import Flask, render_template, Response, g, request
from flask_bootstrap import Bootstrap

import cv2
import time
import threading
import os
import glob

import iottalk_package.DAN as DAN

ServerURL = 'http://192.168.1.134:9999'
#Reg_addr = None #if None, Reg_addr = MAC address
Reg_addr = "B06EBF60298F"

DAN.profile['dm_name']='Cmd'
DAN.profile['df_list']=['Cmd-I']
DAN.profile['d_name']= None # None for autoNaming
DAN.device_registration_with_retry(ServerURL, Reg_addr)


# username -> id
def generate_username():

    username_file = "username.txt"
    username_table = {}

    if os.path.exists(username_file):

        with open(username_file, 'r') as f:

            for line in f.readlines():

                l = line.strip().split("=")
                id = l[0]
                username = l[1]
                username_table[username] = id

    return username_table

class CheckBoxServer(threading.Thread):

    app = Flask(__name__)
    #app._static_folder = "static"
    Bootstrap(app)
    name_list = {}
    username_table = {}

    def __init__(self, host, port):
        threading.Thread.__init__(self)

        self.host = host
        self.port = port
        self.lock = threading.Lock()

        if not CheckBoxServer.username_table:
            CheckBoxServer.username_table = generate_username()

        '''if room_id not in name_list:
            name_list[room_id] = []'''

    @app.route('/fusion/<int:room_id>', methods=['GET', 'POST'])
    def fusion_index(room_id):
        g.name_list = CheckBoxServer.name_list[room_id]
        enable_list = list(map(str, request.form.getlist("person")))
        print(enable_list)
        g.enable_list = enable_list

        enable_ids = []
        for username in enable_list:
            enable_ids.append(CheckBoxServer.username_table[username])

        DAN.push('Cmd-I', str([room_id, enable_ids]))

        return render_template("index.html")

    @app.route('/sort/<int:room_id>', methods=['GET', 'POST'])
    def sort_index(room_id):
        g.name_list = CheckBoxServer.name_list[room_id]
        enable_list = list(map(str, request.form.getlist("person")))
        print(enable_list)
        g.enable_list = enable_list

        DAN.push('Cmd-I', str([room_id, enable_list]))

        return render_template("index.html")

    def add_name_list(self, room_id, name_list):
        self.lock.acquire()
        CheckBoxServer.name_list[room_id] = name_list
        self.lock.release()

    def run(self):
        self.app.run(host=self.host, port=self.port, threaded=True, debug=True, use_reloader=False)

if __name__ == "__main__":
    
    host = "0.0.0.0"
    port = 8099

    cbs = CheckBoxServer(host, port)
    cbs.add_name_list(1, CheckBoxServer.username_table.keys())
    cbs.add_name_list(2, CheckBoxServer.username_table.keys())
    cbs.start()
