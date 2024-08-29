import asyncio
import websockets
import subprocess
import time
import os
import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
camera_device = "/dev/media1"
afterCheckTimeuot = 0.5
aftercleanUpTimeuot = 0.3
afterSendTimeuot = 0.25
chunk_size = 1024 * 128
# basically the higher the number, the bigger the buffer array. 2 is a minimum # not sure here
bufferMarker = 2
# how many images in buffer
bufferSize = 4

def check_and_release_camera():
    # Check which process is using the camera device
    result = subprocess.run(['lsof', camera_device], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    
    # Skip the header and get process info
    for line in lines[1:]:
        parts = line.split()
        pid = int(parts[1])
        command = parts[0]
        print(f"Killing process {command} with PID {pid} using {camera_device}")
        try:
            os.kill(pid, 9)
        except Exception as e:
            print(f"Error killing process {pid}: {e}")

    time.sleep(afterCheckTimeuot)  # Give the system a moment to release the camera

def cleanUp(process):
    if process:
        process.terminate()  # Ensure the process is terminated
        process.wait()  # Wait for the process to terminate

    # Ensure all camera-related processes are killed
    try:
        subprocess.run(['sudo', 'killall', 'pipewire', 'wireplumber'], check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            raise  # Re-raise if the error was due to another reason
        else:
            print("No 'libcamera-vid' process found to kill.")

    time.sleep(aftercleanUpTimeuot)

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
    process = None

    try:
        while True:

            # Check and release camera if it's in use
            check_and_release_camera()

            # Start the process
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                chunk = process.stdout.read(chunk_size)
                
                if not chunk:
                    print('No frame data received')
                    # await asyncio.sleep(0.02)
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
                    end_index += bufferMarker  # Move past the end marker
                    frame_data = buffer[start_index:end_index]
                    buffer = buffer[end_index:]  # Remaining data

                    #### face recognition ####
                    # Convert frame to numpy array
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    # Detect faces in the frame
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    # Draw rectangles around faces
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    # Encode frame back to JPEG
                    _, jpeg = cv2.imencode('.jpg', frame)
                    frame_data = jpeg.tobytes()

                    # Send the frame to the client
                    await websocket.send(frame_data)

                    start_index = buffer.find(b'\xFF\xD8')
                    end_index = buffer.find(b'\xFF\xD9')

                    if len(buffer) > chunk_size * bufferSize:
                        buffer = buffer[-chunk_size:]

                    await asyncio.sleep(afterSendTimeuot)
            
            # Clean up after process terminates
            cleanUp(process)
            
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())