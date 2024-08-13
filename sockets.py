import asyncio
import websockets
import subprocess

async def video_stream(websocket, path):
    # Use ffmpeg to capture video from the camera and stream it as MJPEG
    command = [
        'ffmpeg',
        '-f', 'video4linux2',   # Specify V4L2 as the input format
        '-i', '/dev/video0',     # Use the correct video device
        '-f', 'mjpeg',           # Output format MJPEG
        '-q:v', '5',             # Set quality level (adjust as needed)
        '-'                      # Output to stdout
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        buffer = b''
        while True:
            chunk = process.stdout.read(4096)  # Read a larger chunk of MJPEG data
            if not chunk:
                break

            buffer += chunk

            while b'\xff\xd8' in buffer and b'\xff\xd9' in buffer:
                start = buffer.find(b'\xff\xd8')  # Start of JPEG frame
                end = buffer.find(b'\xff\xd9') + 2  # End of JPEG frame

                if start < end:
                    frame = buffer[start:end]
                    buffer = buffer[end:]  # Remove the processed frame from the buffer

                    # Send the frame over the WebSocket
                    await websocket.send(frame)
                else:
                    buffer = buffer[end:]

    except websockets.exceptions.ConnectionClosedError:
        print("WebSocket connection closed")
    finally:
        process.terminate()

# Start the WebSocket server
async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())
