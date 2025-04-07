# Utiliser une image Python
FROM python:3.9

# Définir le dossier de travail
WORKDIR /app

#  Copier tous les fichiers necessaires dans le conteneur
COPY . .
COPY Dataset/dataset_etudiants.csv /app/Dataset/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# exposer le conteneur
EXPOSE 8000

#  Exécuter le script quand le conteneur démarre
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]


