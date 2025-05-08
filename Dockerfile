# Étape 1 : image de base
FROM python:3.10-slim

# Étape 2 : installation des dépendances système nécessaires pour scikit-surprise
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Étape 3 : définir le dossier de travail
WORKDIR /app

# Étape 4 : définir un dossier temporaire accessible pour pip
ENV PIP_CACHE_DIR=/app/pip_cache
RUN mkdir -p /app/pip_cache && chmod -R 777 /app/pip_cache

# Étape 5 : copier les fichiers dans le conteneur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn dash

COPY . .

# Exposer le port
EXPOSE 8000

# Commande pour lancer l'application Dash avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:server"]