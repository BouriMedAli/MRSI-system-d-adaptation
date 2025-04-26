# Étape 1 : image de base
FROM python:3.10-slim

# Étape : installation des dépendances système nécessaires pour scikit-surprise
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Étape 2 : définir le dossier de travail
WORKDIR /app

# Étape 3 : copier les fichiers dans le conteneur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exposer le port
EXPOSE 8000

# Commande pour lancer l'application FastAPI avec uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
