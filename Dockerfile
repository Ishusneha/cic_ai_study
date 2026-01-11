# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Create necessary directories
RUN mkdir -p backend/uploads backend/progress_data backend/vector_store

# Set environment variables
ENV PYTHONPATH=/app
ENV UPLOAD_DIR=/app/backend/uploads
ENV VECTOR_STORE_PATH=/app/backend/vector_store

# Expose port 8000
EXPOSE 8000

# Run the application with reload for development
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

