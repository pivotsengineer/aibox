import asyncio
import websockets
import subprocess
import time
import os
import requests
from io import BytesIO

camera_device = "/dev/media1"
afterCheckTimeout = 2
afterSendTimeout = 0.25
chunk_size = 1024 * 4
onFrameErrorTimeout = 0.02
bufferSize = 8
start_index_regexp = b'\xFF\xD8'  # JPEG start marker
end_index_regexp = b'\xFF\xD9'  # JPEG end marker
ping_interval = 30  # Ping every 30 seconds to keep the connection alive
recognition_server_url = 'http://192.168.0.152:8001/predict'  # Your recognition server
recognition_interval = 1  # Time interval to send frames for recognition (in seconds)

def check_and_release_camera():
    release_camera()
    result = subprocess.run(['lsof', camera_device], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        for line in lines[1:]:
            parts = line.split()
            pid = int(parts[1])
            command = parts[0]
            print(f"Killing process {command} with PID {pid} using {camera_device}")
            try:
                os.kill(pid, 9)
                time.sleep(0.5)
            except Exception as e:
                print(f"Error killing process {pid}: {e}")

def release_camera():
    try:
        subprocess.run(['sudo', 'fuser', '-k', camera_device], check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            raise
    time.sleep(afterCheckTimeout)

def terminateProcess(process):
    if process:
        process.terminate()
        process.wait()

async def capture_frames(queue: asyncio.Queue):
    command = [
        'libcamera-vid',
        '--codec', 'mjpeg',
        '--width', '640',
        '--height', '480',
        '--framerate', '60',
        '--roi', '0.0,0.0,1.0,1.0',
        '-t', '0',
        '--inline',
        '-o', '-'
    ]
    buffer = bytearray()
    process = None
    retry_attempts = 0
    max_retries = 5

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

                if start_index != -1 and end_index != -1 and end_index > start_index:
                    end_index += len(end_index_regexp)
                    frame_data = buffer[start_index:end_index]
                    buffer = buffer[end_index:]

                    await queue.put(frame_data)

                if len(buffer) > chunk_size * 8:
                    buffer = buffer[-chunk_size:]

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            terminateProcess(process)
            await asyncio.sleep(afterCheckTimeout)
            retry_attempts += 1

            if retry_attempts >= max_retries:
                print(f"Reached max retry attempts ({max_retries}). Exiting capture loop.")
                break

            print(f"Retrying... ({retry_attempts}/{max_retries})")

async def send_frames(queue: asyncio.Queue, websocket):
    while True:
        frame_data = await queue.get()
        await websocket.send(frame_data)
        queue.task_done()

async def ping_websocket(websocket):
    while True:
        try:
            await websocket.ping()
            print("WebSocket ping sent")
            await asyncio.sleep(ping_interval)
        except Exception as e:
            print(f"Error sending WebSocket ping: {e}")
            break

async def video_stream(websocket, path):
    queue = asyncio.Queue(maxsize=bufferSize)
    producer = asyncio.create_task(capture_frames(queue))
    consumer = asyncio.create_task(send_frames(queue, websocket))
    pinger = asyncio.create_task(ping_websocket(websocket))

    await asyncio.gather(producer, consumer, pinger)

async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())
