# Use a Debian base image for ARM architecture
FROM arm64v8/debian:bookworm

# Enable noninteractive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install gnupg and other necessary packages
RUN apt-get update && apt-get install -y \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Add Raspberry Pi OS repo
RUN echo "deb http://archive.raspberrypi.com/debian bookworm main" > /etc/apt/sources.list.d/raspi.list \
 && apt-key adv --fetch-keys https://archive.raspberrypi.com/debian/raspberrypi.gpg.key \
 && apt-get update

# Install libcamera and dependencies
RUN apt-get install -y \
    libcamera-apps \
    libcamera-tools \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

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