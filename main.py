from fastapi import FastAPI
from knn_function import recommander

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de recommandations KNN"}

@app.get("/recommandations/{id_etudiant}")
def get_recommandations(id_etudiant: int):
    recommandations = recommander(id_etudiant)
    return recommandations
