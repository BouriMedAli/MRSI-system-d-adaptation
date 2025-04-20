# Utiliser une image Python stable
FROM python:3.13-slim
# Créer et utiliser un dossier de travail
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY backend/fastapi_app.py /app/
COPY etudiants_preprocessed.csv /app/
COPY requirements.txt /app/
COPY frontend /app/frontend

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Lancer l'application
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
