# Use a Raspberry Pi OS base image
FROM arm32v7/python:3.11-slim-buster

# Install system dependencies
RUN sudo apt-get update && apt-get install -y \
    libcamera-apps \
    libcamera-tools \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file and install requirements
COPY video/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY video/sockets.py sockets.py

# Expose the port for the video service
EXPOSE 8765

# Default command to run the video service
CMD ["python3", "sockets.py"]