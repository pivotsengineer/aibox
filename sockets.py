import asyncio
import websockets
import subprocess

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

# Start the WebSocket server
async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())
