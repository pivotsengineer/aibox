FROM python:3.11-slim

# Install system dependencies, including libcamera and psmisc (for fuser)
RUN apt-get update && apt-get install -y \
    libcamera-apps \
    psmisc \
    && rm -rf /var/lib/apt/lists/*

# Set up the application
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expose necessary ports
EXPOSE 8765

CMD ["python3", "sockets.py"]
