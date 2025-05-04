from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import joblib
from generate_recommendations import get_recommendations, get_fictitious_recommendations

app = FastAPI()

# Charger les données et le modèle
model = joblib.load('model.pkl')
df = pd.read_pickle('students_df.pkl')

class RecommendationRequest(BaseModel):
    student_id: int
    n_recommendations: int = 5
    skill_filter: Optional[List[str]] = None
    interest_filter: Optional[List[str]] = None
    skill_weight: float = 0.5
    interest_weight: float = 0.5

class FictitiousRecommendationRequest(BaseModel):
    student_id: int
    n_recommendations: int = 5

@app.post("/recommendations/")
async def recommend(request: RecommendationRequest):
    result, error = get_recommendations(
        student_id=request.student_id,
        model=model,
        df=df,
        n_recommendations=request.n_recommendations,
        skill_filter=request.skill_filter,
        interest_filter=request.interest_filter,
        skill_weight=request.skill_weight,
        interest_weight=request.interest_weight
    )
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    return result

@app.post("/fictitious_recommendations/")
async def fictitious_recommend(request: FictitiousRecommendationRequest):
    result, error = get_fictitious_recommendations(
        student_id=request.student_id,
        df=df,
        n_recommendations=request.n_recommendations
    )
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    return result

@app.get("/health/")
async def health_check():
    return {"status": "API is running"}