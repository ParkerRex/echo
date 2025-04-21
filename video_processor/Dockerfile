FROM python:3.11-slim

# Install ffmpeg + basic tools
RUN apt-get update &&     apt-get install -y ffmpeg &&     apt-get clean

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY . .

# Expose port Cloud Run expects
EXPOSE 8080
ENV PORT=8080

# Entrypoint (Temporarily reverted for logging test)
CMD ["python", "app.py"]
