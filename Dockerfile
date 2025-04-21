# Use an official Python runtime as the base image
FROM python:3.11-slim

# Install ffmpeg system package and other tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port Cloud Run expects
EXPOSE 8080
ENV PORT=8080

# Command to run the main script using Gunicorn, evaluating $PORT via shell
CMD exec sh -c 'gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 video_processor.main:app'
