import asyncio
import websockets
import subprocess
import time

def cleanUp(process):
    if process:
        process.terminate()  # Ensure the process is terminated
        process.wait()  # Wait for the process to terminate

    # Ensure all camera-related processes are killed
    try:
        subprocess.run(['sudo', 'pkill', 'libcamera-vid'], check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            raise  # Re-raise if the error was due to another reason
        else:
            print("No 'libcamera-vid' process found to kill.")

    time.sleep(1)

async def video_stream(websocket, path):
    command = [
        'libcamera-vid',
        '--codec', 'mjpeg',
        '--width', '640',
        '--height', '480',
        '--framerate', '30',
        '-t', '10000',
        '--inline',
        '-o', '-'  # Output to stdout
    ]
    buffer = bytearray()
    chunk_size = 1024 * 1024
    process = None

    try:
        while True:
            # Start the process
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                chunk = process.stdout.read(chunk_size)
                
                if not chunk:
                    print('No frame data received')
                    await asyncio.sleep(0.3)
                    return_code = process.poll()
                    if return_code is not None:
                        print(f"libcamera-vid terminated with return code: {return_code}")
                        stderr_output = process.stderr.read().decode()
                        print(f"libcamera-vid error: {stderr_output}")
                        break
                else:
                    buffer.extend(chunk)

                start_index = buffer.find(b'\xFF\xD8')  # JPEG start marker
                end_index = buffer.find(b'\xFF\xD9')  # JPEG end marker
                
                while start_index != -1 and end_index != -1 and end_index > start_index:
                    end_index += 2  # Move past the end marker
                    frame = buffer[start_index:end_index]
                    buffer = buffer[end_index:]  # Remaining data

                    # Send the frame to the client
                    await websocket.send(frame)

                    start_index = buffer.find(b'\xFF\xD8')
                    end_index = buffer.find(b'\xFF\xD9')

                    if len(buffer) > chunk_size * 4:
                        buffer = buffer[-chunk_size:]

                    await asyncio.sleep(0.5)
            
            # Clean up after process terminates
            cleanUp(process)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        cleanUp(process)

async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())