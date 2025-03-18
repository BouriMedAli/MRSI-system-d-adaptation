from fastapi import FastAPI
from pydantic import BaseModel
from app.model import RecommenderSystem

# Initialisation de l'API
app = FastAPI()
recommender = RecommenderSystem("data/dataset_etudiants.csv")

# Schéma de la requête
class ProfilUtilisateur(BaseModel):
    numerique: list
    groupes: list
    competences: list
    interets: list

@app.post("/recommend")
def get_recommendations(profil: ProfilUtilisateur):
    recommendations = recommender.recommander_etudiants(profil.dict())
    return recommendations[['ID_Étudiant', 'Nom']].to_dict(orient="records")

@app.get("/")
def read_root():
    return {"message": "API de recommandation sociale avec FastAPI"}
