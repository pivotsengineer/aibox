FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use a custom entrypoint script
CMD ["sh", "entrypoint.sh"]
