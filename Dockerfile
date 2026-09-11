FROM python:3.11-slim

# Install Tesseract OCR and required system libraries
RUN apt-get update && apt-get install -y \
  tesseract-ocr \
  libgl1 \
  libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker caching
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the complete project
COPY . /app

# Backend working directory
WORKDIR /app/backend

# Render provides PORT automatically
ENV PORT=10000

# Start FastAPI
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]