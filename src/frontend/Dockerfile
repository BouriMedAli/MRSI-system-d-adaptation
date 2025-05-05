# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY src/frontend/requirements.txt .
COPY src/frontend/app.py .
COPY data/dataset_etudiants.csv /app/data/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port pour Streamlit
EXPOSE 8501

# Commande pour lancer Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]