FROM arm64v8/debian:bookworm

# Enable noninteractive mode
ENV DEBIAN_FRONTEND=noninteractive

# Add Raspberry Pi OS repo
RUN echo "deb http://archive.raspberrypi.com/debian bookworm main" > /etc/apt/sources.list.d/raspi.list \
 && apt-key adv --fetch-keys https://archive.raspberrypi.com/debian/raspberrypi.gpg.key \
 && apt-get update

# Install libcamera and dependencies
RUN apt-get install -y \
    libcamera-apps \
    libcamera-tools \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY video/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY video/sockets.py sockets.py

EXPOSE 8765
CMD ["python3", "sockets.py"]
