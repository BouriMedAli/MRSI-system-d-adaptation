# Utiliser une image Python
FROM python:3.9

# Définir le dossier de travail
WORKDIR /app/Dataset

#  Copier le code dans le conteneur
COPY model.py .
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

#  Exécuter le script quand le conteneur démarre
CMD ["python", "model.py"]

# exposer le conteneur
EXPOSE 8000

