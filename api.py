from model import recommend_collaborators,evaluate_recommendations_cosine
from fastapi import FastAPI, Query
from pydantic import BaseModel

# FastAPI Setup
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de recommandation KNN"}

class RequestBody(BaseModel):
    student_id: int
    k: int = 3  # Par défaut, k=3

# Endpoint de recommandation
@app.get("/recommend_collaborators/")
def recommend_collaborators_api(student_id: int = Query(...), k: int = Query(3)):
    recommendations = recommend_collaborators(student_id, k)
    return {"recommended_students": recommendations}

# Endpoint d'évaluation avec la similarité cosinus
@app.get("/evaluate_recommendations/")
def evaluate_recommendations_api(k: int = 3):
    avg_similarity = evaluate_recommendations_cosine(k)

    return {"average_similarity": avg_similarity}
