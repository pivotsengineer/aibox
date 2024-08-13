import asyncio
import websockets
import subprocess

def video_stream():
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
        frame = process.stdout.read(1024)  # Read a chunk of MJPEG data

        if not frame:
            print('no frame')
            continue

        yield (b'--frame\r\n'
               b'Content-Type: video/mjpeg\r\n\r\n' + frame + b'\r\n')

# Start the WebSocket server
async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())