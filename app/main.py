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
        # Vérification que toutes les clés attendues sont présentes
        expected_keys = ["Travaux_Collaboratifs", "Coéquipiers", "Communautés", "Nombre_Interactions"]
        for key in expected_keys:
            if key not in data:
                raise HTTPException(status_code=400, detail=f"Clé manquante : {key}")

        # Vérification des types de données
        for key in expected_keys:
            if not isinstance(data[key], (int, float)):
                raise HTTPException(status_code=400, detail=f"Valeur invalide pour {key}. Doit être un nombre.")

        # Obtenir les recommandations
        recommendations = recommandeur.recommander(data)
        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
