# Use a slim Python image
FROM python:3.11-slim

# Install LibreOffice and clean up to keep the image small
RUN apt-get update && apt-get install -y \
    libreoffice \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# Start the server using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]