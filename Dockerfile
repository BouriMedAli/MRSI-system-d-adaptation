FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y gcc && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

# Commande par défaut (peut être surchargée par docker-compose)
CMD ["python", "generate_recommendations.py"]