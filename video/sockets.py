import asyncio
import subprocess
import time
import websockets
import psutil

camera_device = "/dev/media1"
afterCheckTimeout = 3
chunk_size = 1024 * 4
bufferSize = 8
start_index_regexp = b'\xFF\xD8'  # JPEG start marker
end_index_regexp = b'\xFF\xD9'  # JPEG end marker
max_retries = 5  # Max retry attempts for camera restart

def release_camera():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any(camera_device in cmd for cmd in cmdline):
                print(f"Terminating process {proc.info['pid']} using camera device")
                proc.terminate()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
            print(f"Error terminating process: {e}")
            continue
    time.sleep(afterCheckTimeout)

async def capture_frames(queue: asyncio.Queue):
    """Capture frames from libcamera-vid and put them into the queue."""
    print("Starting frame capture...")
    command = [
        'libcamera-vid',
        '--codec', 'mjpeg',
        '--width', '640',
        '--height', '480',
        '--framerate', '30',
        '--roi', '0.0,0.0,1.0,1.0',
        '-t', '0',
        '--inline',
        '-o', '-'
    ]

    buffer = bytearray()
    retry_attempts = 0

    while retry_attempts < max_retries:
        print(f"Attempt {retry_attempts + 1} to start libcamera-vid...")

        process = None
        try:
            release_camera()
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while process.poll() is None:
                chunk = process.stdout.read(chunk_size)
                if not chunk:
                    stderr_output = process.stderr.read().decode()
                    print(f"No frame data received. Retrying... stderr: {stderr_output}")
                    await asyncio.sleep(0.02)
                    continue

                buffer.extend(chunk)

                start_index = buffer.find(start_index_regexp)
                end_index = buffer.find(end_index_regexp)

                if start_index != -1 and end_index != -1 and end_index > start_index:
                    end_index += len(end_index_regexp)
                    frame_data = buffer[start_index:end_index]
                    buffer = buffer[end_index:]

                    await queue.put(frame_data)
                    print(f"Captured frame of size: {len(frame_data)} bytes")

                if len(buffer) > chunk_size * 8:
                    buffer = buffer[-chunk_size:]

        except Exception as e:
            print(f"Error in capture_frames: {e}")

        finally:
            if process:
                process.terminate()
                process.wait()

            retry_attempts += 1
            await asyncio.sleep(1)

    print("Max retries reached. Exiting frame capture.")

async def send_frames(queue: asyncio.Queue, websocket):
    """Send frames from the queue to the WebSocket client."""
    try:
        while True:
            frame_data = await queue.get()
            try:
                await websocket.send(frame_data)
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected while sending frames.")
                break
            queue.task_done()
    except Exception as e:
        print(f"Unexpected error in send_frames: {e}")

async def video_stream(websocket, path=""):
    """Handle WebSocket connections and stream video."""
    print(f"Client connected: {websocket.remote_address}")

    queue = asyncio.Queue(maxsize=bufferSize)
    producer = asyncio.create_task(capture_frames(queue))
    consumer = asyncio.create_task(send_frames(queue, websocket))

    try:
        await asyncio.gather(producer, consumer)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} disconnected.")
    except Exception as e:
        print(f"Unexpected error in video_stream: {e}")
    finally:
        print(f"Cleaning up tasks for {websocket.remote_address}")
        producer.cancel()
        consumer.cancel()
        await queue.join()

async def main():
    """Start the WebSocket server."""
    server = await websockets.serve(video_stream, '0.0.0.0', 8765, ping_interval=None, ping_timeout=None, max_size=2**23)
    print("WebSocket server started on port 8765")
    await asyncio.Future()  # Keep the server running indefinitely

asyncio.run(main())