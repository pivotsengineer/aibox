# Use a lightweight Python image
FROM python:3.11-slim

# Set environment variable to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    psmisc lsof cmake git g++ \
    libboost-program-options-dev \
    libdrm-dev libexif-dev libjpeg-dev libpng-dev libtiff-dev \
    libudev-dev libx11-dev libxcomposite-dev libxdamage-dev \
    libxext-dev libxfixes-dev libxrandr-dev libxrender-dev \
    meson ninja-build pkg-config \
    python3-dev python3-pip python3-setuptools python3-wheel \
    libcamera-dev libcamera-tools \
    && rm -rf /var/lib/apt/lists/*

# Install required Python modules
RUN pip install --no-cache-dir jinja2 pyyaml ply

# Clone and build libcamera (use a stable version)
RUN git clone --depth 1 --branch v0.0.5 https://git.libcamera.org/libcamera/libcamera.git /libcamera \
    && cd /libcamera \
    && meson build \
    && ninja -C build \
    && ninja -C build install

# Clone and build libcamera-apps (use a compatible stable version)
RUN git clone --depth 1 --branch stable-2023-09-14 https://github.com/raspberrypi/libcamera-apps.git /libcamera-apps \
    && cd /libcamera-apps \
    && mkdir build && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && make install

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file and install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port for the video service
EXPOSE 8765

# Default command to run the video service
CMD ["python3", "sockets.py"]
