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
    try:
        while True:
            frame = process.stdout.read(8086)  # Read a chunk of data
            if not frame:
                print('No frame data received')
                await asyncio.sleep(0.5)
                continue
            else:
                await websocket.send(frame)
                await asyncio.sleep(3)
#                await websocket.recv()  # Wait for client acknowledgment
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        process.terminate()
        process.wait()
        print("Connection closed")

# Start the WebSocket server
async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())
