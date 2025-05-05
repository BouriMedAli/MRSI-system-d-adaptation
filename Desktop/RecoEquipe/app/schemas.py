from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    student_name: str
    n_recommendations: int = 5

class RecommendationResult(BaseModel):
    nom: str
    score: float
    competences: list[str]