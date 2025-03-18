from fastapi import FastAPI, HTTPException
import pandas as pd
from app.model import RecommandeurKNN

app = FastAPI()

# Chargement du modèle de recommandation
recommandeur = RecommandeurKNN("data/dataset_etudiants.csv")

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de recommandation KNN"}

@app.post("/recommander/")
def obtenir_recommandation(data: dict):
    try:
        query_df = pd.DataFrame([data])
        recommendations = recommandeur.recommander(query_df)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
