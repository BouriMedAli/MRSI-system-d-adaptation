# Use an official lightweight Python image.
FROM python:3.12.6-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code.
COPY . .

# By default, the CMD will evaluate an environment variable TEST.
# If TEST is set to "true", it will run pytest; otherwise, it will launch the FastAPI app.
# We use "sh -c" to enable a conditional command.
CMD ["sh", "-c", "if [ \"$TEST\" = \"true\" ]; then pytest; else uvicorn app:app --host 0.0.0.0 --port 80; fi"]
