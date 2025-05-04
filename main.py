from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from generate_recommendations import get_recommendations, get_fictitious_recommendations
import joblib
import logging
import uvicorn
import webbrowser
import threading
import time
import requests

app = FastAPI()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les données et le modèle
logger.info("Chargement du modèle et des données...")
model = joblib.load('model.pkl')
df = pd.read_pickle('students_df.pkl')
logger.info(f"Modèle et données chargés. Nombre d'étudiants : {len(df)}")

# Modèle Pydantic pour la requête de recommandations
class RecommendationRequest(BaseModel):
    student_id: int
    n_recommendations: int = 5
    skill_filter: Optional[List[str]] = None
    interest_filter: Optional[List[str]] = None
    skill_weight: float = 0.5
    interest_weight: float = 0.5

# Modèle Pydantic pour la requête de recommandations fictives
class FictitiousRecommendationRequest(BaseModel):
    student_id: int
    n_recommendations: int = 5

@app.post("/recommendations/")
async def recommendations_endpoint(request: RecommendationRequest):
    logger.info(f"Requête reçue pour l'étudiant {request.student_id}")
    
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
        logger.error(f"Erreur pour l'étudiant {request.student_id} : {error}")
        raise HTTPException(status_code=404, detail=error)
    
    logger.info(f"Recommandations générées pour l'étudiant {request.student_id}")
    return result

@app.post("/fictitious_recommendations/")
async def fictitious_recommendations_endpoint(request: FictitiousRecommendationRequest):
    logger.info(f"Requête reçue pour des recommandations fictives pour l'étudiant {request.student_id}")
    
    result, error = get_fictitious_recommendations(
        student_id=request.student_id,
        df=df,
        model=model,
        n_recommendations=request.n_recommendations
    )
    
    if error:
        logger.error(f"Erreur pour l'étudiant {request.student_id} : {error}")
        raise HTTPException(status_code=404, detail=error)
    
    logger.info(f"Recommandations fictives générées pour l'étudiant {request.student_id}")
    return result

# Fonction pour ouvrir le navigateur
def open_browser():
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:8000/docs", timeout=1)
            if response.status_code == 200:
                logger.info("Serveur prêt, ouverture de http://127.0.0.1:8000/docs dans le navigateur...")
                webbrowser.open("http://127.0.0.1:8000/docs")
                return
        except requests.RequestException:
            logger.info(f"Tentative {attempt + 1}/{max_attempts} : Serveur non prêt, attente 1 seconde...")
            time.sleep(1)
    logger.warning(f"Échec d'ouverture du navigateur après {max_attempts} tentatives.")

# Événement de démarrage de FastAPI
@app.on_event("startup")
async def startup_event():
    logger.info("Démarrage du serveur FastAPI...")
    threading.Thread(target=open_browser, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)