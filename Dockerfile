# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
# Pin numpy to version 1.x for compatibility with surprise library
RUN pip install --no-cache-dir numpy<2.0.0 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create directory for model files if they're not mounted as volumes
RUN mkdir -p /app/Dataset

# Copy model files if they exist locally (will be overridden by volumes if used)
COPY model.pkl data.pkl ./

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]