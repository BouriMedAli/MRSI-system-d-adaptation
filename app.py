from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pickle
import os
import ast
from typing import List, Dict, Any, Optional, Union
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Student Collaboration Recommender API",
              description="API for recommending potential student collaborators")

# Load model and data
MODEL_DIR = "./model"

try:
    with open(os.path.join(MODEL_DIR, 'knn_model.pkl'), 'rb') as f:
        model = pickle.load(f)
    
    with open(os.path.join(MODEL_DIR, 'feature_columns.pkl'), 'rb') as f:
        feature_columns = pickle.load(f)
    
    with open(os.path.join(MODEL_DIR, 'processed_df.pkl'), 'rb') as f:
        df = pickle.load(f)
        
    logger.info("Model and data loaded successfully")
except Exception as e:
    logger.error(f"Error loading model and data: {str(e)}")
    model = None
    feature_columns = None
    df = None

class Student(BaseModel):
    id: int

class RecommendationRequest(BaseModel):
    numeric: List[float] = [7, 50]  # [travaux_collaboratifs, nombre_interactions]
    communautés: List[str] = []
    compétences: List[str] = []
    centres_d_intérêt: List[str] = []  # Using underscore instead of apostrophe
    student_id: Optional[int] = None
    num_recommendations: int = 5

class RegistrationRequest(BaseModel):
    nom: str
    travaux_collaboratifs: int
    nombre_interactions: int
    communautés: List[str]
    compétences: List[str]
    centres_d_intérêt: List[str]  # Using underscore instead of apostrophe

class CategoryResponse(BaseModel):
    communities: List[str]
    skills: List[str]
    interests: List[str]

@app.get("/")
def read_root():
    return {"message": "Student Collaboration Recommender API is running"}

@app.get("/health")
def health_check():
    if model is None or feature_columns is None or df is None:
        raise HTTPException(status_code=500, detail="Model or data not loaded properly")
    return {"status": "healthy"}

@app.get("/categories")
def get_categories():
    """Get all categories for dropdown menus."""
    all_communities = set()
    all_skills = set()
    all_interests = set()
    
    for _, row in df.iterrows():
        all_communities.update(row["Communautés"])
        all_skills.update(row["Compétences"])
        all_interests.update(row["Centres_d'Intérêt"])
    
    return {
        "communities": sorted(list(all_communities)),
        "skills": sorted(list(all_skills)),
        "interests": sorted(list(all_interests))
    }

@app.post("/register")
def register_student(request: RegistrationRequest):
    """Register a new student."""
    global df
    
    if df is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    # Generate a new student ID
    new_id = int(df["ID_Étudiant"].max() + 1)
    
    # Create a new student record
    new_student = {
        "ID_Étudiant": new_id,
        "Nom": request.nom,
        "Travaux_Collaboratifs": request.travaux_collaboratifs,
        "Nombre_Interactions": request.nombre_interactions,
        "Coéquipiers": [],  # New student has no teammates yet
        "Communautés": request.communautés,
        "Compétences": request.compétences,
        "Centres_d'Intérêt": request.centres_d_intérêt
    }
    
    # Add to dataframe
    df = pd.concat([df, pd.DataFrame([new_student])], ignore_index=True)
    
    logger.info(f"Registered new student: {request.nom} with ID {new_id}")
    
    return {"student_id": new_id, "message": "Student registered successfully"}

@app.post("/recommend")
def recommend_collaborators(request: RecommendationRequest):
    """Recommend potential collaborators based on input profile."""
    start_time = time.time()
    
    if model is None or feature_columns is None or df is None:
        raise HTTPException(status_code=500, detail="Model or data not loaded properly")
    
    # Process either existing student or temporary profile
    if request.student_id is not None:
        # Check if student exists
        student = df[df["ID_Étudiant"] == request.student_id]
        if student.empty:
            raise HTTPException(status_code=404, detail=f"Student with ID {request.student_id} not found")
        
        travaux_collaboratifs = student.iloc[0]["Travaux_Collaboratifs"]
        nombre_interactions = student.iloc[0]["Nombre_Interactions"]
        communautes = student.iloc[0]["Communautés"]
        competences = student.iloc[0]["Compétences"]
        interets = student.iloc[0]["Centres_d'Intérêt"]
        exclude_id = request.student_id
    else:
        # Use provided profile data
        travaux_collaboratifs = request.numeric[0]
        nombre_interactions = request.numeric[1]
        communautes = request.communautés
        competences = request.compétences
        interets = request.centres_d_intérêt
        exclude_id = None
    
    # Create feature vector for input profile
    feature_vector = []
    
    # Generate features in the same order as model expects
    for col in feature_columns:
        if col.startswith('skill_'):
            skill = col[6:]  # Remove 'skill_' prefix
            feature_vector.append(1 if skill in competences else 0)
        elif col.startswith('interest_'):
            interest = col[9:]  # Remove 'interest_' prefix
            feature_vector.append(1 if interest in interets else 0)
        elif col.startswith('community_'):
            community = col[10:]  # Remove 'community_' prefix
            feature_vector.append(1 if community in communautes else 0)
        elif col == 'collaboration_score':
            feature_vector.append(travaux_collaboratifs / 10)  # Normalize to 0-1
        elif col == 'interaction_normalized':
            max_interactions = df['Nombre_Interactions'].max()
            if max_interactions > 0:
                feature_vector.append(nombre_interactions / max_interactions)
            else:
                feature_vector.append(0)
    
    # Find nearest neighbors
    input_vector = np.array(feature_vector).reshape(1, -1)
    distances, indices = model.named_steps['knn'].kneighbors(input_vector)
    
    # Process recommendations
    recommendations = []
    processed_count = 0
    
    for i, idx in enumerate(indices[0]):
        if processed_count >= request.num_recommendations:
            break
            
        recommended_student = df.iloc[idx]
        recommended_id = int(recommended_student["ID_Étudiant"])
        
        # Skip the querying student if using an existing ID
        if exclude_id is not None and recommended_id == exclude_id:
            continue
        
        # Calculate similarities
        common_communities = set(communautes).intersection(set(recommended_student["Communautés"]))
        common_skills = set(competences).intersection(set(recommended_student["Compétences"]))
        common_interests = set(interets).intersection(set(recommended_student["Centres_d'Intérêt"]))
        
        recommendations.append({
            "ID_Étudiant": recommended_id,
            "Nom": recommended_student["Nom"],
            "Travaux_Collaboratifs": int(recommended_student["Travaux_Collaboratifs"]),
            "Nombre_Interactions": int(recommended_student["Nombre_Interactions"]),
            "Communautés": recommended_student["Communautés"],
            "Compétences": recommended_student["Compétences"],
            "Centres_d_Intérêt": recommended_student["Centres_d'Intérêt"],
            "similarity_score": float(1.0 - distances[0][i])  # Convert distance to similarity score
        })
        processed_count += 1
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    return {
        "recommended_students": recommendations,
        "metadata": {
            "processing_time_ms": round(processing_time, 2),
            "total_students": len(df),
            "query_type": "existing_student" if request.student_id is not None else "profile_match"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)