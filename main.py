from fastapi import FastAPI
from knn_model import recommander_competences

app = FastAPI()

@app.get("/recommandations/{id_etudiant}")
def get_recommandations(id_etudiant: int):
    recommandations = recommander_competences(id_etudiant)
    return {
        "id": id_etudiant,
        "recommandations": recommandations
    }

