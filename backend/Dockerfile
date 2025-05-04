# Dockerfile
FROM python:3.9

WORKDIR /app

# Copy all code and dataset
COPY . .
COPY Dataset/dataset_etudiants.csv /app/Dataset/

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "apiSurprise:app", "--host", "0.0.0.0", "--port", "8000"]
