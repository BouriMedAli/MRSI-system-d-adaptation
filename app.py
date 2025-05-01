from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from recommender import InterestCompetenceGraphRecommender
import os

# Initialize the app
app = FastAPI(
    title="Student Recommender API",
    description="API for getting personalized student recommendations based on interests, competencies, and social network",
    version="1.0.0"
)

# Initialize the recommender
data_path = os.getenv("DATA_PATH", "dataset_etudiants.csv")
recommender = InterestCompetenceGraphRecommender(data_path)

@app.on_event("startup")
async def startup():
    """Train the recommender on startup"""
    recommender.train()
    print("Recommender system trained and ready!")

# Response models
class StudentInfo(BaseModel):
    id: int
    name: str
    collab_score: Optional[int] = None
    interactions: Optional[int] = None
    communities: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None

class SimilarityBreakdown(BaseModel):
    interest: float
    competence: float
    community: float
    network: float
    collab: float
    
class Recommendation(BaseModel):
    id: int
    name: str
    similarity: float
    similarity_breakdown: SimilarityBreakdown
    reasons: List[str]

# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint that returns API info"""
    return {
        "message": "Student Recommender API is running",
        "version": "1.0.0",
        "endpoints": {
            "/students": "Get all students",
            "/students/{student_id}": "Get information about a specific student",
            "/recommendations/{student_id}": "Get recommendations for a specific student"
        }
    }

@app.get("/students", response_model=List[StudentInfo])
async def get_all_students():
    """Get a list of all students"""
    return recommender.get_all_students()

@app.get("/students/{student_id}", response_model=StudentInfo)
async def get_student_info(student_id: int):
    """Get detailed information about a specific student"""
    try:
        return recommender.get_student_info(student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/recommendations/{student_id}", response_model=List[Recommendation])
async def get_recommendations(
    student_id: int, 
    top_n: int = Query(5, description="Number of recommendations to return", ge=1, le=10)
):
    """Get personalized recommendations for a specific student"""
    try:
        return recommender.get_recommendations(student_id, top_n=top_n)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Run the server if executed directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)