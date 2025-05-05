from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from modelMLP import load_dataset, prepare_and_recommend

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset at startup
df = load_dataset("Dataset/dataset_etudiants.csv")
project_skills_default = ["python", "machine learning", "data visualization"]

# Pydantic model for recommendation request
class RecommendationSimilarityRequest(BaseModel):
    student_id: int
    skills: List[str]
    interests: List[str]
    top_n: Optional[int] = 3

class RecommendationComplementarityRequest(BaseModel):
    student_id: int
    skills: List[str]
    interests: List[str]
    project_skills: Optional[List[str]] = None
    top_n: Optional[int] = 3

@app.get("/")
def read_root():
    return {"message": "Student Collaboration Recommendation API is running."}

@app.get("/skills")
def get_skills():
    # Extract all skills from the dataset
    all_skills = set(skill for skills in df['Compétences'] for skill in skills)
    return {"skills": sorted(list(all_skills))}

@app.get("/interests")
def get_interests():
    # Extract all interests from the dataset
    all_interests = set(interest for interests in df['Centres_d\'Intérêt'] for interest in interests)
    return {"interests": sorted(list(all_interests))}

@app.post("/recommend/similarity")
def get_similarity_recommendations(req: RecommendationSimilarityRequest):
    # Call prepare_and_recommend for similarity use case
    results = prepare_and_recommend(
        df=df,
        project_skills=project_skills_default,  # Default project skills
        student_id=req.student_id,
        skills=req.skills,
        interests=req.interests,
        use_case="similarity",
        n=req.top_n
    )

    # Format the response
    formatted_results = []
    for res in results:
        formatted_results.append({
            "student_id": int(res["Student_ID"]),
            "skills": res["Skills"],
            "interests": res["Interests"]
        })

    return {
        "recommendations": formatted_results
    }

@app.post("/recommend/complementarity")
def get_complementarity_recommendations(req: RecommendationComplementarityRequest):
    # Enforce project_skills for complementarity
    if not req.project_skills:
        raise HTTPException(status_code=400, detail="project_skills must be provided for complementarity use case")

    # Call prepare_and_recommend for complementarity use case
    results = prepare_and_recommend(
        df=df,
        project_skills=req.project_skills,
        student_id=req.student_id,
        skills=req.skills,
        interests=req.interests,
        use_case="complementarity",
        n=req.top_n
    )

    # Format the response
    formatted_results = []
    for res in results:
        formatted_results.append({
            "student_id": int(res["Student_ID"]),
            "skills": res["Skills"],
            "interests": res["Interests"]
        })

    return {
        "recommendations": formatted_results
    }