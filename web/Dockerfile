# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file and install requirements
COPY web/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY web/app.py app.py
COPY web/templates templates

# Expose the port for the web service
EXPOSE 8000

# Default command to run the web service
CMD ["python3", "app.py"]