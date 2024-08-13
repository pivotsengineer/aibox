import asyncio
import websockets
import subprocess

async def video_stream(websocket, path):
    command = [
        'libcamera-vid',
        '--codec', 'mjpeg',
        '--width', '320',
        '--height', '240',
        '--framerate', '20',
        '--inline',
        '-o', '-'  # Output to stdout
    ]
    buffer = bytearray()
    chunkSize = 1024*4
    process = None
    try:
        while True:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            chunk = process.stdout.read(chunkSize)
            
            if not chunk:
                print('No frame data received')
                await asyncio.sleep(0.5)
                continue
            
            buffer.extend(chunk)

            start_index = buffer.find(b'\xFF\xD8')  # JPEG start marker
            end_index = buffer.find(b'\xFF\xD9')  # JPEG end marker
            
            while start_index != -1 and end_index != -1 and end_index > start_index:
                end_index += 2  # Move past the end marker
                frame = buffer[start_index:end_index]
                buffer = buffer[end_index:]  # Remaining data
                # Search for next frame
                start_index = buffer.find(b'\xFF\xD8')
                end_index = buffer.find(b'\xFF\xD9')
                await websocket.send(frame)
                # Update buffer to remove the processed frame
                buffer = buffer[end_index:]
                await asyncio.sleep(0.2)

            # Clean up buffer to prevent excessive growth
            if len(buffer) > chunkSize * 10:  # Adjust size threshold as needed
                print("Cleaning up buffer")
                buffer = buffer[-chunkSize * 5:]  # Keep the last 5 chunks worth of data


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if process:
            process.terminate()  # Ensure the process is terminated
            process.wait()  # Wait for the process to terminate
            print("Process terminated")
        print("Connection closed")

async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())
