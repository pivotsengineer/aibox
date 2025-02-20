# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file and install requirements
COPY requirements.txt requirements.txt
COPY app.py app.py

RUN python -m pip install ultralytics

# Copy the rest of the application files
COPY . .

# Expose the port for the video service
EXPOSE 8765
EXPOSE 8000

# Default command to run the video service
CMD ["python3", "app.py"]

