# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY src/api/requirements.txt .
COPY src/api/main.py .
COPY data/dataset_etudiants.csv /app/data/
COPY models/ /app/models/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port pour FastAPI
EXPOSE 8000

# Commande pour lancer l’API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]