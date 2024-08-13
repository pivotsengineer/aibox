import asyncio
import websockets
import subprocess

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

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
        frame = process.stdout.read(1024)  # Read a chunk of data

        if not frame:
            print('No frame data received')
            continue

        print('before')
        # Send the frame over the WebSocket
        await websocket.send(frame)
        print('after')

# Start the WebSocket server
async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

asyncio.run(main())
