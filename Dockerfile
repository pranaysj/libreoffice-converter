# Use Python 3.11 slim as the foundation
FROM python:3.11-slim

# Install system binaries for conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Render provides the $PORT environment variable automatically
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
