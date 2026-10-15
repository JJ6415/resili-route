# ResiliRoute Dockerfile for Google Cloud Run
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Environment variables for Cloud Run
ENV HOST=0.0.0.0
ENV PORT=8080
ENV DEBUG=false

# Expose standard container port
EXPOSE 8080

# Run entry point
CMD ["python", "run_server.py"]
