from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import pandas as pd
import joblib
import pickle
import ast
from generate_recommendations import get_recommendations, model, df

app = FastAPI()

class RecommendationRequest(BaseModel):
    student_id: int
    n_recommendations: int = 5
    skill_filter: Optional[str] = None
    interest_filter: Optional[str] = None
    skill_weight: float = 0.5  # Poids pour les compétences (0.0 à 1.0)
    interest_weight: float = 0.5  # Poids pour les centres d'intérêt (0.0 à 1.0)

@app.post("/recommendations/")
async def get_recommendations_endpoint(request: RecommendationRequest) -> Dict[str, Any]:
    recs, error = get_recommendations(
        request.student_id,
        model,
        df,
        request.n_recommendations,
        request.skill_filter,
        request.interest_filter,
        skill_weight=request.skill_weight,
        interest_weight=request.interest_weight
    )
    if error:
        return {"error": error}
    return recs