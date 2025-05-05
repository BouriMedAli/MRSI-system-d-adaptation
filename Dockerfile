FROM python:3.10-slim

# Installer les outils nécessaires pour la compilation, curl et unzip
RUN apt-get update && apt-get install -y gcc g++ build-essential curl unzip

# Créer le dossier app
WORKDIR /app

# Copier tout dans le container
COPY . .

# Télécharger le dataset ml-100k (MovieLens 100k)
RUN mkdir -p /app/ && \
    curl -o /ml-100k.zip http://files.grouplens.org/datasets/movielens/ml-100k.zip && \
    unzip /ml-100k.zip -d /app/data && \
    rm /ml-100k.zip

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install numpy==1.24.4
RUN pip install -r requirements.txt

# Lancer le serveur
CMD ["uvicorn", "backend.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
