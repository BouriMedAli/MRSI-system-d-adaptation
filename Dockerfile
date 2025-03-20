# Étape 1 : Utiliser une image de base Python
FROM python:3.9-slim

# Étape 2 : Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3 : Copier les fichiers de votre projet dans le conteneur
COPY . /app

# Étape 4 : Installer les dépendances depuis requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Étape 5 : Exposer le port 8001 pour accéder à l'application FastAPI
EXPOSE 8001

# Étape 6 : Lancer l'application FastAPI avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
