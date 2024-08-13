import subprocess
import cv2
import numpy as np
from flask import Flask, Response

app = Flask(__name__)

def generate_frames():
    # Start libcamera-vid to capture video in MJPEG format
    process = subprocess.Popen(
        ['libcamera-vid', '--codec', 'mjpeg', '--width', '640', '--height', '480', '--inline', '--no-qt'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    while True:
        # Read the MJPEG stream
        frame = process.stdout.read(1024 * 1024)  # Read a chunk of data

        if not frame:
            continue

        # Yield the frame to the response
        yield (b'--frame\r\n'
               b'Content-Type: video/mjpeg\r\n\r\n' + frame + b'\r\n')

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
