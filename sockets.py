import asyncio
import websockets
import subprocess

async def video_stream(websocket, path):
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
            frame = process.stdout.read(8096*5)  # Chunk size, 8096 as an example
            if not frame:
                print('No frame data received')
                await asyncio.sleep(0.5)
                continue
            await websocket.send(frame)
            try:
                await websocket.recv()  # Wait for client acknowledgment (e.g., ping)
            except websockets.ConnectionClosedOK:
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        process.terminate()
        process.wait()
        print("Connection closed")

async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())
