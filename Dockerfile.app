# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies required for scikit-surprise and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Cython first
RUN pip install --no-cache-dir cython==0.29.30

# Install dependencies with increased verbosity
RUN pip install --no-cache-dir --verbose -r requirements.txt

# Copy the application code into the container
COPY app.py .

# Expose the port FastAPI will run on
EXPOSE 8000

# Create model directory
RUN mkdir -p model

# Start the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]