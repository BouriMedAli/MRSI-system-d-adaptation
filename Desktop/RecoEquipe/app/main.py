# main.py
from fastapi import FastAPI
from .model import RecommenderSystem

app = FastAPI()
recommender = RecommenderSystem()

# Charger le modèle
recommender.load_data_and_model('app/models/modele_recommandation.pkl')

@app.get("/recommend/{student_id}")
def recommend(student_id: int):
    recommendations = recommender.get_recommendations(student_id)
    return {"recommendations": recommendations.tolist()}
