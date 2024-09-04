import asyncio
import websockets
import subprocess
import time
import os
import cv2
import numpy as np

camera_device = "/dev/media1"
afterCheckTimeuot = 0.5
afterSendTimeuot = 0.25
chunk_size = 1024 * 4
onFrameErrorTimeout = 0.02
bufferSize = 8
start_index_regexp = b'\xFF\xD8'  # JPEG start marker
end_index_regexp = b'\xFF\xD9'  # JPEG end marker

def release_camera():
    # Kill any lingering processes that might be using the camera
    try:
        subprocess.run(['sudo', 'fuser', '-k', camera_device], check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            # If the error is for another reason, re-raise it
            raise 
    # Give the system time to release the camera
    time.sleep(afterCheckTimeuot)

def check_and_release_camera():
    release_camera()
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

def terminateProcess(process):
    if process:
        process.terminate()  # Ensure the process is terminated
        process.wait()  # Wait for the process to terminate

async def capture_frames(queue: asyncio.Queue):
    command = [
        'libcamera-vid',
        '--codec', 'mjpeg',
        '--width', '640',
        '--height', '480',
        '--framerate', '60',
        '--roi', '0.0,0.0,1.0,1.0',  # Full sensor readout (no crop)
        '-t', '0',
        '--inline',
        '-o', '-'  # Output to stdout
    ]
    buffer = bytearray()
    process = None

    while True:
        try:
            check_and_release_camera()
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while True:
                chunk = process.stdout.read(chunk_size)
                if not chunk:
                    print('No frame data received')
                    await asyncio.sleep(onFrameErrorTimeout)
                    return_code = process.poll()
                    if return_code is not None:
                        print(f"libcamera-vid terminated with return code: {return_code}")
                        stderr_output = process.stderr.read().decode()
                        print(f"libcamera-vid error: {stderr_output}")
                        break
                else:
                    buffer.extend(chunk)

                start_index = buffer.find(start_index_regexp)
                end_index = buffer.find(end_index_regexp)

                while True:
                    start_index = buffer.find(start_index_regexp)
                    end_index = buffer.find(end_index_regexp)
                    if start_index != -1 and end_index != -1 and end_index > start_index:
                        end_index += len(end_index_regexp)
                        frame_data = buffer[start_index:end_index]
                        buffer = buffer[end_index:]
                        await queue.put(frame_data)
                    else:
                        break   

                if len(buffer) > chunk_size * 8:
                    buffer = buffer[-chunk_size:]

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            terminateProcess(process)
            await asyncio.sleep(afterCheckTimeuot)

async def send_frames(queue: asyncio.Queue, websocket):
    while True:
        frame_data = await queue.get()
        await websocket.send(frame_data)
        print('Frame data sent')
        queue.task_done()

async def video_stream(websocket, path):
    queue = asyncio.Queue(maxsize=bufferSize)
    producer = asyncio.create_task(capture_frames(queue))
    consumer = asyncio.create_task(send_frames(queue, websocket))

    await asyncio.gather(producer, consumer)


async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())