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
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    buffer = bytearray()
    chunkSize = 1024*4
    
    try:
        while True:
            chunk = process.stdout.read(chunkSize)  # Read a chunk of data
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
                
                await websocket.send(frame)
                
                # Search for next frame
                start_index = buffer.find(b'\xFF\xD8')
                end_index = buffer.find(b'\xFF\xD9')

            await asyncio.sleep(0.02)  # Adjust delay as needed
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
