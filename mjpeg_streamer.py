from flask import Flask, render_template, Response

import cv2
import yolo_server
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('stream.html')

def gen(client_id):

    while True:
        frame = yolo_server.get_frame(client_id)
        client_amount = yolo_server.yolo_client_amount()
        if(client_amount > 0 and frame is not None):
            try:
                jpg_string = cv2.imencode('.jpg', frame)[1].tostring()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpg_string + b'\r\n\r\n')
            except Exception as e:
                print("Opencv Error : {}".format(e))
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def video_feed2():
    return Response(gen(2), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    
    yolo_server.init_yolo_server()
    time.sleep(1)
    app.run(host='0.0.0.0', port=8090, threaded=True, debug=True, use_reloader=False)
