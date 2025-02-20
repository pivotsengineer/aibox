# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file and install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose both ports
EXPOSE 8000 
EXPOSE 8765 

# Default command (this will be overridden by docker-compose)
CMD ["python3", "app.py"]
