from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
from recommender import InterestCompetenceGraphRecommender
import os
import pandas as pd
import numpy as np
import copy

# Initialize the app
app = FastAPI(
    title="Student Recommender API",
    description="API for getting personalized student recommendations based on interests, competencies, and social network",
    version="1.0.0"
)

# Initialize the recommender
data_path = os.getenv("DATA_PATH", "Dataset/dataset_etudiants.csv")
recommender = InterestCompetenceGraphRecommender(data_path)

@app.on_event("startup")
async def startup():
    """Train the recommender on startup"""
    recommender.train()
    print("Recommender system trained and ready!")

# Request and response models
class StudentInfo(BaseModel):
    id: int
    name: str
    collab_score: Optional[int] = None
    interactions: Optional[int] = None
    communities: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None

class NewStudentRequest(BaseModel):
    name: str
    collab_score: int
    interactions: int
    communities: List[str]
    skills: List[str]
    interests: List[str]

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
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint that returns API info"""
    return {
        "message": "Student Recommender API is running",
        "version": "1.0.0",
        "endpoints": {
            "/students": "Get all students",
            "/students/{student_id}": "Get information about a specific student",
            "/recommendations/{student_id}": "Get recommendations for a specific student",
            "/recommend-new": "Get recommendations for a new student (not in dataset)"
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
        recommendations = recommender.get_recommendations(student_id, top_n=top_n)
        # Ensure the recommendations conform to the expected structure
        validated_recommendations = []
        for rec in recommendations:
            # Convert all values in similarity breakdown to float to avoid validation errors
            if "similarity_breakdown" in rec:
                breakdown = rec["similarity_breakdown"]
                validated_breakdown = SimilarityBreakdown(
                    interest=float(breakdown.get("interest", 0.0)),
                    competence=float(breakdown.get("competence", 0.0)),
                    community=float(breakdown.get("community", 0.0)),
                    network=float(breakdown.get("network", 0.0)),
                    collab=float(breakdown.get("collab", 0.0))
                )
                
                # Create a properly validated recommendation object
                validated_rec = Recommendation(
                    id=int(rec["id"]),
                    name=str(rec["name"]),
                    similarity=float(rec["similarity"]),
                    similarity_breakdown=validated_breakdown,
                    reasons=rec["reasons"]
                )
                validated_recommendations.append(validated_rec.dict())
            else:
                # If no similarity breakdown exists (should not happen), create a default one
                default_breakdown = SimilarityBreakdown(
                    interest=0.0,
                    competence=0.0,
                    community=0.0,
                    network=0.0,
                    collab=0.0
                )
                validated_rec = Recommendation(
                    id=int(rec["id"]),
                    name=str(rec["name"]),
                    similarity=float(rec["similarity"]),
                    similarity_breakdown=default_breakdown,
                    reasons=rec["reasons"]
                )
                validated_recommendations.append(validated_rec.dict())
                
        return validated_recommendations
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/recommend-new", response_model=List[Recommendation])
async def recommend_for_new_student(
    student: NewStudentRequest = Body(...),
    top_n: int = Query(5, description="Number of recommendations to return", ge=1, le=10)
):
    """Get recommendations for a new student not in the dataset"""
    try:
        # Create a copy of the recommender to avoid modifying the original
        temp_recommender = copy.deepcopy(recommender)
        
        # Add the new student to the dataframe temporarily
        new_student_id = 9999  # Use a special ID for the new student
        
        # Create a new row for the student
        new_row = pd.DataFrame({
            'ID_Étudiant': [new_student_id],
            'Nom': [student.name],
            'Travaux_Collaboratifs': [student.collab_score],
            'Coéquipiers': [[]],  # Empty list as they don't have teammates yet
            'Communautés': [student.communities],
            'Nombre_Interactions': [student.interactions],
            'Compétences': [student.skills],
            "Centres_d'Intérêt": [student.interests]
        })
        
        # Append to the dataframe
        temp_recommender.df = pd.concat([temp_recommender.df, new_row], ignore_index=True)
        
        # Rebuild the graph and matrices with the new student
        temp_recommender.build_graph()
        temp_recommender.create_feature_matrices()
        temp_recommender.generate_embeddings()
        
        # Get recommendations for the new student
        recommendations = temp_recommender.get_recommendations(new_student_id, top_n=top_n)
        
        # Ensure the recommendations conform to the expected structure
        validated_recommendations = []
        for rec in recommendations:
            # Convert all values in similarity breakdown to float to avoid validation errors
            if "similarity_breakdown" in rec:
                breakdown = rec["similarity_breakdown"]
                validated_breakdown = SimilarityBreakdown(
                    interest=float(breakdown.get("interest", 0.0)),
                    competence=float(breakdown.get("competence", 0.0)),
                    community=float(breakdown.get("community", 0.0)),
                    network=float(breakdown.get("network", 0.0)),
                    collab=float(breakdown.get("collab", 0.0))
                )
                
                # Create a properly validated recommendation object
                validated_rec = Recommendation(
                    id=int(rec["id"]),
                    name=str(rec["name"]),
                    similarity=float(rec["similarity"]),
                    similarity_breakdown=validated_breakdown,
                    reasons=rec["reasons"]
                )
                validated_recommendations.append(validated_rec.dict())
            else:
                # If no similarity breakdown exists (should not happen), create a default one
                default_breakdown = SimilarityBreakdown(
                    interest=0.0,
                    competence=0.0,
                    community=0.0,
                    network=0.0,
                    collab=0.0
                )
                validated_rec = Recommendation(
                    id=int(rec["id"]),
                    name=str(rec["name"]),
                    similarity=float(rec["similarity"]),
                    similarity_breakdown=default_breakdown,
                    reasons=rec["reasons"]
                )
                validated_recommendations.append(validated_rec.dict())
        
        return validated_recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

# Run the server if executed directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)