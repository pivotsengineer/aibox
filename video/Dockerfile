# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file and install requirements
COPY requirements.txt requirements.txt
COPY sockets.py sockets.py

RUN pip install -r requiremets.txt

# Expose the port for the video service
EXPOSE 8000

# Default command to run the video service
CMD ["python3", "app.py"]

