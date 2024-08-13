import subprocess
import cv2
import numpy as np
from flask import Flask, Response

app = Flask(__name__)

def generate_frames():
    while True:

        command = ['libcamera-vid', '--output', 'frame.mjpeg', '--width', '640', '--height', '480', '--codec', 'mjpeg', '--timeout', '50']
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Read the MJPEG stream
        with open('frame.mjpeg', 'rb') as f:
            frame = f.read()

        yield (b'--frame\r\n'
               b'Content-Type: video/mjpeg\r\n\r\n' + frame + b'\r\n')

        # Capture a single frame using libcamera
        # command = ['libcamera-still', '-o', 'frame.jpg', '-t' '50' '--width' '640' '--height' '480']
        # subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # # Read the captured frame
        # frame = cv2.imread('frame.jpg')

        # if frame is None:
        #     print('frame is None')
        #     continue

        # # Resize the frame
        # frame = cv2.resize(frame, (640, 480))  # Adjust the resolution as needed

        # # Encode the frame in JPEG format
        # _, buffer = cv2.imencode('.jpg', frame)
        # frame = buffer.tobytes()

        # # Yield the frame to the response
        # yield (b'--frame\r\n'
        #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html>
    <head>
        <title>Video Stream</title>
    </head>
    <body>
        <h1>Video Stream</h1>
        <img src="/video_feed" width="640" height="480">
    </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
