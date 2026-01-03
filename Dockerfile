# Dockerfile for RAG API Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY rag_pipeline.py .
COPY rag_api.py .

# Create directory for temporary uploads
RUN mkdir -p /tmp/uploads

# Expose port
EXPOSE 5002

# Set environment variables
ENV FLASK_APP=rag_api.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5002/health')" || exit 1

# Run the application
CMD ["python", "rag_api.py"]

