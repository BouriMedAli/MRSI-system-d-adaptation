# Utiliser une image Python
FROM python:3.9-slim

# Définir le répertoire
WORKDIR /app

# Copier les fichiers
COPY src/training/requirements.txt .
COPY src/training/train_autoencoder.py .
COPY src/training/generate.py .
COPY data/dataset_etudiants.csv /app/data/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Commande par défaut
CMD ["python", "generate.py"]