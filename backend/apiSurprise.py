from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <-- ✅ ADD THIS
from pydantic import BaseModel
from typing import List, Optional
from modelSurprise import (
    load_dataset, prepare_models,
    recommend_collaborators
)

app = FastAPI()
# ✅ Add CORS middleware after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load dataset and prepare models at startup
df = load_dataset("Dataset/dataset_etudiants.csv")
project_skills_default = ["python", "machine learning", "data visualization"]
algo_similarity, algo_complementarity, all_skills, all_interests = prepare_models(df, project_skills_default)

# Convert sets to sorted lists for consistent API responses
all_skills_list = sorted(list(all_skills))
all_interests_list = sorted(list(all_interests))

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
    return {"skills": all_skills_list}

@app.get("/interests")
def get_interests():
    return {"interests": all_interests_list}

@app.post("/recommend/similarity")
def get_similarity_recommendations(req: RecommendationSimilarityRequest):
    # Select the appropriate algorithm based on use_case
    algo = algo_similarity
    
    # Call recommend_collaborators
    results = recommend_collaborators(
        student_id=req.student_id,
        skills=req.skills,
        interests=req.interests,
        use_case="similarity",
        algo=algo,
        df=df,
        n=req.top_n,
    )

    # Format the response to match the desired output
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

    # Select the appropriate algorithm based on use_case
    algo = algo_complementarity
    
    # Call recommend_collaborators
    results = recommend_collaborators(
        student_id=req.student_id,
        skills=req.skills,
        interests=req.interests,
        algo=algo,
        use_case="complementarity",
        df=df,
        n=req.top_n,
        project_skills=req.project_skills
    )

    # Format the response to match the desired output
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