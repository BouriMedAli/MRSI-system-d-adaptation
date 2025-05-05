from fastapi import FastAPI, HTTPException
from flask import Flask
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

# Créer l'application Flask
app = Flask(__name__)

# Autoriser les requêtes depuis toutes les origines
CORS(app)


app = FastAPI()

# Charger les données du modèle
with open("app/models/modele_recommandation.pkl", "rb") as f:
    model_data = pickle.load(f)

mlb_competences = model_data["mlb_competences"]
mlb_interets = model_data["mlb_interets"]
mlb_communautes = model_data["mlb_communautes"]
student_profiles = model_data["student_profiles"]
svd = model_data["svd"]

# Charger les données des étudiants
df = pd.read_csv("app/data/dataset_etudiants.csv")
df.rename(columns={
    "Compétences": "competences",
    "Centres_d'Intérêt": "interets",
    "Communautés": "communaute"
}, inplace=True)

# Nettoyage des colonnes
df["competences"] = df["competences"].apply(lambda x: x.split(","))
df["interets"] = df["interets"].apply(lambda x: x.split(","))
df["communaute"] = df["communaute"].apply(lambda x: x.split(","))

# Modèle de réponse pour les recommandations
class RecommendationResponse(BaseModel):
    ID_Étudiant: int
    Nom: str
    similarity: float


@app.get("/")
async def home():
    return {"message": "🎉 API de recommandation en ligne ! Va sur /docs pour la documentation."}


@app.get("/docs")
async def docs():
    return """
    <h2>📘 Documentation de l'API</h2>
    <p>🔹 <code>/recommendations?id=1</code> : Obtiens les coéquipiers recommandés pour l'étudiant 1.</p>
    """


@app.get("/recommendations", response_model=list[RecommendationResponse])
async def recommend(id: int):
    try:
        if id not in df["ID_Étudiant"].values:
            raise HTTPException(status_code=404, detail="ID étudiant non trouvé")

        # Filtrer les autres étudiants (sauf lui-même)
        others = df[df["ID_Étudiant"] != id]

        # Profil de l'étudiant cible
        idx = df[df["ID_Étudiant"] == id].index[0]
        target_profile = student_profiles[idx]

        # Calcul des similarités cosinus
        similarities = cosine_similarity([target_profile], student_profiles)[0]

        # Ajouter les similarités au DataFrame
        df["similarity"] = similarities
        df_sorted = df[df["ID_Étudiant"] != id].sort_values(by="similarity", ascending=False)

        # Récupérer les 5 coéquipiers les plus proches
        top_5 = df_sorted.head(5)[["ID_Étudiant", "Nom", "similarity"]]
        recommendations = top_5.to_dict(orient="records")

        return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
