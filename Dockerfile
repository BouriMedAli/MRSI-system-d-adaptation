# Stage 1: Training
FROM python:3.9-slim as trainer

WORKDIR /app

# Install system dependencies and update pip first
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir "numpy<2.0.0" && \
    pip install --no-cache-dir -r requirements.txt

# Copy training files
COPY KNN.py .
COPY Dataset/ ./Dataset/

# Create output directory
RUN mkdir -p /app/output

# Run training and save artifacts
RUN python KNN.py && \
    mv model.pkl data.pkl /app/output/

# Stage 2: Runtime
FROM python:3.9-slim

WORKDIR /app

# Install system runtime dependencies and update pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip

# Install runtime dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and trained models
COPY app.py .
COPY --from=trainer /app/output/ ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]