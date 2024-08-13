import asyncio
import websockets
import subprocess
from flask import Flask, render_template

app = Flask(__name__)

async def video_stream(websocket, path):
    # Start libcamera-vid to capture video in MJPEG format
    command = [
        'libcamera-vid',
        '--codec', 'mjpeg',
        '--width', '640',
        '--height', '480',
        '--framerate', '30',
        '--inline',
        '-o', '-'  # Output to stdout
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        # Read MJPEG data from libcamera-vid
        frame = process.stdout.read(1024 * 1024)  # Read a chunk of data

        if not frame:
            print('No frame data received')
            continue

        # Send the frame over the WebSocket
        await websocket.send(frame)

@app.route('/')
def index():
    return render_template('index.html')

# Start the WebSocket server
start_server = websockets.serve(video_stream, '0.0.0.0', 8765, debug=True)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

