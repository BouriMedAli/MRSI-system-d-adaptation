# Utiliser une image de base Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Exposer le port 8001
EXPOSE 8001

# Lancer l'application avec Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
