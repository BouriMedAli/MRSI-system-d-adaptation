FROM python:3.10
LABEL authors="Salma"

WORKDIR /knnapp

COPY . /knnapp

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]