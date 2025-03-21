# Use a Debian base image for ARM architecture
FROM arm64v8/debian:bookworm

# Enable noninteractive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install gnupg, wget, python3, python3-pip, and other necessary packages
RUN apt-get update && apt-get install -y \
    gnupg \
    wget \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Add Raspberry Pi OS repo and fetch the GPG key
RUN echo "deb http://archive.raspberrypi.com/debian bookworm main" > /etc/apt/sources.list.d/raspi.list \
 && wget -O - https://archive.raspberrypi.com/debian/raspberrypi.gpg.key | apt-key add - \
 && apt-get update

# Install libcamera and dependencies
RUN apt-get install -y \
    libcamera-apps \
    libcamera-tools \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Create a virtual environment and install requirements
RUN python3 -m venv venv
COPY video/requirements.txt requirements.txt
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY video/sockets.py sockets.py

# Expose the port for the video service
EXPOSE 8765

# Default command to run the video service
CMD ["./venv/bin/python", "sockets.py"]