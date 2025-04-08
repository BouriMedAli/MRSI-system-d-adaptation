# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies required for scikit-surprise
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and dataset into the container
COPY KNN.py .
COPY Dataset/dataset_etudiants.csv Dataset/

# Expose the port FastAPI will run on
EXPOSE 8000

# Define the command to run the FastAPI app
CMD ["python", "KNN.py"]