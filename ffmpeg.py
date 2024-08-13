import subprocess
import cv2
from flask import Flask, Response

app = Flask(__name__)

def generate_frames():
    # Use ffmpeg to capture video and stream it as MJPEG
    command = [
        'ffmpeg', 
        '-f', 'video4linux2', 
        '-i', '/dev/media2',  # Adjust according to your camera device
        '-f', 'mjpeg', 
        '-'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        frame = process.stdout.read(1024*1024)  # Read a chunk of MJPEG data

        if not frame:
            continue

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
