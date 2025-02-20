# Use a lightweight Python image
FROM raspbian/stretch

RUN echo "deb http://raspbian.raspberrypi.org/raspbian/ stretch main contrib non-free rpi" > /etc/apt/sources.list
RUN apt-get update && apt-get install -y psmisc
RUN apt-get update && apt-get install -y \
    libcamera-apps \
    libcamera-tools


# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file and install requirements
COPY video/requirements.txt requirements.txt
COPY video/sockets.py sockets.py

RUN pip install -r requirements.txt

# Expose the port for the video service
EXPOSE 8765

# Default command to run the video service
CMD ["python3", "sockets.py"]

