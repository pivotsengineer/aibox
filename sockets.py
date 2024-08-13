import asyncio
import websockets
import subprocess

def stop_service(service_name):
    try:
        subprocess.run(['sudo', 'systemctl', 'stop', service_name], check=True)
        print(f"Service {service_name} stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop {service_name}: {e}")

async def video_stream(websocket, path):
    command = [
        'libcamera-vid',
        '--codec', 'mjpeg',
        '--width', '320',
        '--height', '240',
        '--framerate', '15',
        '--inline',
        '-o', '-'  # Output to stdout
    ]
    buffer = bytearray()
    chunk_size = 1024
    process = None

    try:
        # Start the process once
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        while True:
            chunk = process.stdout.read(chunk_size)
            
            if not chunk:
                print('No frame data received')

                # Check for process termination
                return_code = process.poll()
                if return_code is not None:
                    print(f"libcamera-vid terminated with return code: {return_code}")
                    stderr_output = process.stderr.read().decode()
                    print(f"libcamera-vid error: {stderr_output}")
                    break

                await asyncio.sleep(0.5)
                continue
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

                # Search for next frame
                start_index = buffer.find(b'\xFF\xD8')
                end_index = buffer.find(b'\xFF\xD9')

                # Clean up buffer to prevent excessive growth
                if len(buffer) > chunk_size * 2:
                    buffer = buffer[-chunk_size:]  # Keep only the most recent chunk

                await asyncio.sleep(0.2)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if process:
            process.terminate()  # Ensure the process is terminated
            process.wait()  # Wait for the process to terminate
            #demon processes can see by 
            stop_service('pipewire')
            stop_service('wireplumb')
            print("Process terminated")
        print("Connection closed")

async def main():
    server = await websockets.serve(video_stream, '0.0.0.0', 8765)
    await server.wait_closed()

asyncio.run(main())
