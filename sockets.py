import asyncio
import subprocess
import time
import websockets

camera_device = "/dev/media1"
afterCheckTimeout = 2
afterSendTimeout = 0.02
chunk_size = 1024 * 4
onFrameErrorTimeout = 0.02
bufferSize = 8
start_index_regexp = b'\xFF\xD8'  # JPEG start marker
end_index_regexp = b'\xFF\xD9'  # JPEG end marker
max_retries = 5  # Max retry attempts for camera restart

def release_camera():
    try:
        subprocess.run(['sudo', 'fuser', '-k', camera_device], check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            raise
    time.sleep(afterCheckTimeout)

def terminate_process(process):
    if process:
        process.terminate()
        process.wait()

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

        try:
            release_camera()
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while process.poll() is None:  # Check if process is still running
                chunk = process.stdout.read(chunk_size)
                if not chunk:
                    print("No frame data received. Retrying...")
                    await asyncio.sleep(onFrameErrorTimeout)
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
            await asyncio.sleep(1)  # Wait before retrying

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

async def ping_websocket(websocket):
    """Send WebSocket pings to keep the connection alive."""
    while True:
        try:
            await websocket.ping()
            print("WebSocket ping sent")
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Error sending WebSocket ping: {e}")
            break

async def video_stream(websocket, path):
    """Handle WebSocket connections and stream video."""
    print(f"Client connected: {websocket.remote_address}")

    queue = asyncio.Queue(maxsize=bufferSize)
    producer = asyncio.create_task(capture_frames(queue))
    consumer = asyncio.create_task(send_frames(queue, websocket))
    pinger = asyncio.create_task(ping_websocket(websocket))

    try:
        await asyncio.gather(producer, consumer, pinger)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} disconnected.")
    except Exception as e:
        print(f"Unexpected error in video_stream: {e}")
    finally:
        print(f"Cleaning up tasks for {websocket.remote_address}")
        producer.cancel()
        consumer.cancel()
        pinger.cancel()
        await queue.join()

async def main():
    """Start the WebSocket server."""
    server = await websockets.serve(video_stream, '0.0.0.0', 8765, ping_interval=None, ping_timeout=None)
    print("WebSocket server started on port 8765")
    await asyncio.Future()  # Keep the server running indefinitely

asyncio.run(main())
