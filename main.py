from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from generate_recommendations import get_recommendations, get_fictitious_recommendations, get_recommended_skills_and_interests
import joblib
import logging
import uvicorn
import webbrowser
import threading
import time
import requests
import ast
import random

app = FastAPI()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les données et le modèle
logger.info("Chargement du modèle et des données...")
model = joblib.load('model.pkl')
df = pd.read_pickle('students_df.pkl')
logger.info(f"Modèle et données chargés. Nombre d'étudiants : {len(df)}")

# Liste statique de compétences et centres d'intérêt programmatiques (copiée depuis generate_recommendations.py)
PROGRAMMATIC_SKILLS = [
    "Machine Learning", "Cloud Computing", "DevOps", "Cybersecurity", "Augmented Reality",
    "Natural Language Processing", "Game Development", "Quantum Computing", "3D Modeling", "Ethical Hacking"
]
PROGRAMMATIC_INTERESTS = [
    "Photography", "Artificial Intelligence Ethics", "Space Exploration", "Virtual Reality", "Sustainable Tech",
    "Digital Art", "Cyberpunk Culture", "Astronomy", "Board Games", "Urban Farming"
]

# Liste statique de ressources pour les cours recommandés (copiée depuis generate_recommendations.py)
RECOMMENDED_COURSES = {
    # Compétences dans la base
    "Python": [
        ("Introduction à Python pour les débutants - YouTube", "https://youtube.com/watch?v=python-intro"),
        ("Cours Python avancé - Udemy", "https://udemy.com/course/python-advanced")
    ],
    "IA": [
        ("Introduction à l'IA - Coursera", "https://coursera.org/learn/intro-to-ai"),
        ("Tutoriel sur l'IA avec Python - YouTube", "https://youtube.com/watch?v=ai-tutorial")
    ],
    "Blockchain": [
        ("Les bases de la Blockchain - Udemy", "https://udemy.com/course/blockchain-basics"),
        ("Comprendre la Blockchain - YouTube", "https://youtube.com/watch?v=blockchain-explained")
    ],
    "Marketing": [
        ("Marketing Digital 101 - Coursera", "https://coursera.org/learn/digital-marketing-101"),
        ("Stratégies de Marketing - YouTube", "https://youtube.com/watch?v=marketing-strategies")
    ],
    "Design": [
        ("Introduction au Design UX/UI - Udemy", "https://udemy.com/course/ux-ui-design"),
        ("Tutoriel de Design Graphique - YouTube", "https://youtube.com/watch?v=design-tutorial")
    ],
    "Data Science": [
        ("Data Science pour débutants - Coursera", "https://coursera.org/learn/data-science-intro"),
        ("Analyse de données avec Python - YouTube", "https://youtube.com/watch?v=data-science-python")
    ],
    "SQL": [
        ("Apprendre SQL pour les débutants - Udemy", "https://udemy.com/course/sql-basics"),
        ("Tutoriel SQL - YouTube", "https://youtube.com/watch?v=sql-tutorial")
    ],
    "Communication": [
        ("Cours de Communication Efficace - Coursera", "https://coursera.org/learn/effective-communication"),
        ("Améliorer ses compétences en communication - YouTube", "https://youtube.com/watch?v=communication-skills")
    ],
    "SEO": [
        ("Introduction au SEO - Udemy", "https://udemy.com/course/seo-basics"),
        ("Tutoriel SEO pour débutants - YouTube", "https://youtube.com/watch?v=seo-tutorial")
    ],
    "Publicité": [
        ("Les bases de la Publicité en ligne - Coursera", "https://coursera.org/learn/online-advertising"),
        ("Créer des campagnes publicitaires - YouTube", "https://youtube.com/watch?v=advertising-campaigns")
    ],
    "UX/UI": [
        ("Introduction au Design UX/UI - Udemy", "https://udemy.com/course/ux-ui-design"),
        ("Principes de UX/UI - YouTube", "https://youtube.com/watch?v=ux-ui-principles")
    ],
    "Graphisme": [
        ("Cours de Graphisme pour débutants - Udemy", "https://udemy.com/course/graphic-design-basics"),
        ("Tutoriel Photoshop - YouTube", "https://youtube.com/watch?v=photoshop-tutorial")
    ],
    "Prototypage": [
        ("Prototypage avec Figma - Udemy", "https://udemy.com/course/prototyping-figma"),
        ("Introduction au prototypage - YouTube", "https://youtube.com/watch?v=prototyping-intro")
    ],
    "Cryptographie": [
        ("Les bases de la Cryptographie - Coursera", "https://coursera.org/learn/cryptography-basics"),
        ("Introduction à la Cryptographie - YouTube", "https://youtube.com/watch?v=cryptography-intro")
    ],
    "Sécurité": [
        ("Introduction à la Cybersécurité - Udemy", "https://udemy.com/course/cybersecurity-basics"),
        ("Les bases de la Sécurité Informatique - YouTube", "https://youtube.com/watch?v=security-basics")
    ],
    "Smart Contracts": [
        ("Créer des Smart Contracts avec Solidity - Udemy", "https://udemy.com/course/smart-contracts-solidity"),
        ("Tutoriel Smart Contracts - YouTube", "https://youtube.com/watch?v=smart-contracts-tutorial")
    ],
    "Statistiques": [
        ("Introduction aux Statistiques - Coursera", "https://coursera.org/learn/statistics-intro"),
        ("Statistiques pour débutants - YouTube", "https://youtube.com/watch?v=statistics-basics")
    ],
    "Big Data": [
        ("Les bases du Big Data - Udemy", "https://udemy.com/course/big-data-basics"),
        ("Introduction au Big Data - YouTube", "https://youtube.com/watch?v=big-data-intro")
    ],
    # Compétences programmatiques (pas dans la base)
    "Machine Learning": [
        ("Introduction au Machine Learning - Coursera", "https://coursera.org/learn/machine-learning-intro"),
        ("Tutoriel Machine Learning - YouTube", "https://youtube.com/watch?v=ml-tutorial"),
        ("Guide ML (PDF)", "https://example.com/ml-guide.pdf")
    ],
    "Cloud Computing": [
        ("Les bases du Cloud Computing - Udemy", "https://udemy.com/course/cloud-computing-basics"),
        ("Introduction au Cloud - YouTube", "https://youtube.com/watch?v=cloud-intro"),
        ("Cloud Computing Guide (PDF)", "https://example.com/cloud-guide.pdf")
    ],
    "DevOps": [
        ("Introduction à DevOps - Coursera", "https://coursera.org/learn/devops-intro"),
        ("Tutoriel DevOps - YouTube", "https://youtube.com/watch?v=devops-tutorial"),
        ("DevOps Essentials (PDF)", "https://example.com/devops-essentials.pdf")
    ],
    "Cybersecurity": [
        ("Introduction à la Cybersécurité - Udemy", "https://udemy.com/course/cybersecurity-basics"),
        ("Les bases de la Cybersécurité - YouTube", "https://youtube.com/watch?v=cybersecurity-basics"),
        ("Cybersecurity Guide (PDF)", "https://example.com/cybersecurity-guide.pdf")
    ],
    "Augmented Reality": [
        ("Introduction à la Réalité Augmentée - Udemy", "https://udemy.com/course/ar-basics"),
        ("Tutoriel AR - YouTube", "https://youtube.com/watch?v=ar-tutorial"),
        ("AR Development Guide (PDF)", "https://example.com/ar-guide.pdf")
    ],
    "Natural Language Processing": [
        ("Introduction au NLP - Coursera", "https://coursera.org/learn/nlp-intro"),
        ("Tutoriel NLP - YouTube", "https://youtube.com/watch?v=nlp-tutorial"),
        ("NLP Basics (PDF)", "https://example.com/nlp-basics.pdf")
    ],
    "Game Development": [
        ("Développement de jeux avec Unity - Udemy", "https://udemy.com/course/game-dev-unity"),
        ("Créer un jeu simple - YouTube", "https://youtube.com/watch?v=game-dev-tutorial"),
        ("Game Dev Guide (PDF)", "https://example.com/game-dev-guide.pdf")
    ],
    "Quantum Computing": [
        ("Introduction au Calcul Quantique - Coursera", "https://coursera.org/learn/quantum-computing-intro"),
        ("Les bases du Calcul Quantique - YouTube", "https://youtube.com/watch?v=quantum-computing-basics"),
        ("Quantum Computing Intro (PDF)", "https://example.com/quantum-computing-intro.pdf")
    ],
    "3D Modeling": [
        ("Introduction à la Modélisation 3D - Udemy", "https://udemy.com/course/3d-modeling-basics"),
        ("Tutoriel Blender - YouTube", "https://youtube.com/watch?v=blender-tutorial"),
        ("3D Modeling Guide (PDF)", "https://example.com/3d-modeling-guide.pdf")
    ],
    "Ethical Hacking": [
        ("Introduction à l'Ethical Hacking - Coursera", "https://coursera.org/learn/ethical-hacking-intro"),
        ("Les bases de l'Ethical Hacking - YouTube", "https://youtube.com/watch?v=ethical-hacking-basics"),
        ("Ethical Hacking Guide (PDF)", "https://example.com/ethical-hacking-guide.pdf")
    ],
    # Centres d'intérêt dans la base
    "Robotique": [
        ("Introduction à la Robotique - YouTube", "https://youtube.com/watch?v=robotics-intro"),
        ("Cours sur la Robotique - edX", "https://edx.org/course/robotics-basics"),
        ("Guide Robotique (PDF)", "https://example.com/robotics-guide.pdf")
    ],
    "Hackathon": [
        ("Comment se préparer pour un Hackathon - Blog", "https://example.com/hackathon-prep"),
        ("Top 10 Astuces pour Hackathons - YouTube", "https://youtube.com/watch?v=hackathon-tips"),
        ("Hackathon Guide (PDF)", "https://example.com/hackathon-guide.pdf")
    ],
    "Musique": [
        ("Apprendre la théorie musicale - YouTube", "https://youtube.com/watch?v=music-theory"),
        ("Cours de piano pour débutants - Udemy", "https://udemy.com/course/piano-basics"),
        ("Théorie Musicale (PDF)", "https://example.com/music-theory.pdf")
    ],
    "Jeux vidéo": [
        ("Développement de jeux vidéo avec Unity - Udemy", "https://udemy.com/course/game-dev-unity"),
        ("Créer un jeu simple - YouTube", "https://youtube.com/watch?v=game-dev-tutorial"),
        ("Guide Jeux Vidéo (PDF)", "https://example.com/game-dev-guide.pdf")
    ],
    "Écologie": [
        ("Introduction au développement durable - Coursera", "https://coursera.org/learn/sustainability"),
        ("Comprendre l'écologie - YouTube", "https://youtube.com/watch?v=ecology-explained"),
        ("Guide Écologie (PDF)", "https://example.com/ecology-guide.pdf")
    ],
    "Technologie": [
        ("Les tendances technologiques 2025 - YouTube", "https://youtube.com/watch?v=tech-trends-2025"),
        ("Introduction à la Technologie - Coursera", "https://coursera.org/learn/intro-to-technology"),
        ("Tendances Tech (PDF)", "https://example.com/tech-trends.pdf")
    ],
    "Entrepreneuriat": [
        ("Les bases de l'Entrepreneuriat - Udemy", "https://udemy.com/course/entrepreneurship-basics"),
        ("Démarrer une startup - YouTube", "https://youtube.com/watch?v=startup-guide"),
        ("Guide Entrepreneuriat (PDF)", "https://example.com/entrepreneurship-guide.pdf")
    ],
    "Innovation": [
        ("Cours sur l'Innovation et la Créativité - Coursera", "https://coursera.org/learn/innovation-creativity"),
        ("Comment innover - YouTube", "https://youtube.com/watch?v=innovation-tips"),
        ("Guide Innovation (PDF)", "https://example.com/innovation-guide.pdf")
    ],
    "Art": [
        ("Introduction à l'Art Contemporain - Udemy", "https://udemy.com/course/contemporary-art"),
        ("Tutoriel de dessin - YouTube", "https://youtube.com/watch?v=drawing-tutorial"),
        ("Guide Art (PDF)", "https://example.com/art-guide.pdf")
    ],
    "Créativité": [
        ("Développer sa Créativité - Coursera", "https://coursera.org/learn/develop-creativity"),
        ("Exercices de Créativité - YouTube", "https://youtube.com/watch?v=creativity-exercises"),
        ("Guide Créativité (PDF)", "https://example.com/creativity-guide.pdf")
    ],
    "Développement": [
        ("Introduction au Développement Web - Udemy", "https://udemy.com/course/web-development-basics"),
        ("Tutoriel de programmation - YouTube", "https://youtube.com/watch?v=programming-tutorial"),
        ("Guide Développement (PDF)", "https://example.com/development-guide.pdf")
    ],
    "E-sport": [
        ("Introduction à l'E-sport - YouTube", "https://youtube.com/watch?v=esport-intro"),
        ("Devenir pro en E-sport - Blog", "https://example.com/esport-guide"),
        ("Guide E-sport (PDF)", "https://example.com/esport-guide.pdf")
    ],
    "Développement Durable": [
        ("Introduction au Développement Durable - Coursera", "https://coursera.org/learn/sustainability"),
        ("Les bases du Développement Durable - YouTube", "https://youtube.com/watch?v=sustainability-basics"),
        ("Guide Développement Durable (PDF)", "https://example.com/sustainability-guide.pdf")
    ],
    "Sciences": [
        ("Introduction aux Sciences - edX", "https://edx.org/course/science-basics"),
        ("Découvrir les Sciences - YouTube", "https://youtube.com/watch?v=science-discovery"),
        ("Guide Sciences (PDF)", "https://example.com/science-guide.pdf")
    ],
    "Nature": [
        ("Explorer la Nature - YouTube", "https://youtube.com/watch?v=nature-exploration"),
        ("Cours sur l'Écologie et la Nature - Coursera", "https://coursera.org/learn/ecology-nature"),
        ("Guide Nature (PDF)", "https://example.com/nature-guide.pdf")
    ],
    # Centres d'intérêt programmatiques (pas dans la base)
    "Photography": [
        ("Introduction à la Photographie - Udemy", "https://udemy.com/course/photography-basics"),
        ("Tutoriel Photographie - YouTube", "https://youtube.com/watch?v=photography-tutorial"),
        ("Guide Photographie (PDF)", "https://example.com/photography-guide.pdf")
    ],
    "Artificial Intelligence Ethics": [
        ("Éthique en IA - Coursera", "https://coursera.org/learn/ai-ethics"),
        ("Introduction à l'Éthique en IA - YouTube", "https://youtube.com/watch?v=ai-ethics-intro"),
        ("Guide Éthique IA (PDF)", "https://example.com/ai-ethics-guide.pdf")
    ],
    "Space Exploration": [
        ("Introduction à l'Exploration Spatiale - edX", "https://edx.org/course/space-exploration"),
        ("L'Exploration Spatiale - YouTube", "https://youtube.com/watch?v=space-exploration"),
        ("Guide Exploration Spatiale (PDF)", "https://example.com/space-exploration-guide.pdf")
    ],
    "Virtual Reality": [
        ("Introduction à la Réalité Virtuelle - Udemy", "https://udemy.com/course/vr-basics"),
        ("Tutoriel VR - YouTube", "https://youtube.com/watch?v=vr-tutorial"),
        ("Guide VR (PDF)", "https://example.com/vr-guide.pdf")
    ],
    "Sustainable Tech": [
        ("Technologies Durables - Coursera", "https://coursera.org/learn/sustainable-tech"),
        ("Introduction aux Tech Durables - YouTube", "https://youtube.com/watch?v=sustainable-tech"),
        ("Guide Tech Durable (PDF)", "https://example.com/sustainable-tech-guide.pdf")
    ],
    "Digital Art": [
        ("Introduction à l'Art Numérique - Udemy", "https://udemy.com/course/digital-art-basics"),
        ("Tutoriel Art Numérique - YouTube", "https://youtube.com/watch?v=digital-art-tutorial"),
        ("Guide Art Numérique (PDF)", "https://example.com/digital-art-guide.pdf")
    ],
    "Cyberpunk Culture": [
        ("Introduction à la Culture Cyberpunk - Blog", "https://example.com/cyberpunk-culture"),
        ("Explorer le Cyberpunk - YouTube", "https://youtube.com/watch?v=cyberpunk-culture"),
        ("Guide Culture Cyberpunk (PDF)", "https://example.com/cyberpunk-culture-guide.pdf")
    ],
    "Astronomy": [
        ("Introduction à l'Astronomie - Coursera", "https://coursera.org/learn/astronomy-intro"),
        ("Les bases de l'Astronomie - YouTube", "https://youtube.com/watch?v=astronomy-basics"),
        ("Guide Astronomie (PDF)", "https://example.com/astronomy-guide.pdf")
    ],
    "Board Games": [
        ("Introduction aux Jeux de Société - Blog", "https://example.com/board-games-intro"),
        ("Découvrir les Jeux de Société - YouTube", "https://youtube.com/watch?v=board-games"),
        ("Guide Jeux de Société (PDF)", "https://example.com/board-games-guide.pdf")
    ],
    "Urban Farming": [
        ("Introduction à l'Agriculture Urbaine - Udemy", "https://udemy.com/course/urban-farming-basics"),
        ("Les bases de l'Agriculture Urbaine - YouTube", "https://youtube.com/watch?v=urban-farming"),
        ("Guide Agriculture Urbaine (PDF)", "https://example.com/urban-farming-guide.pdf")
    ]
}

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
    
    # Étape 1 : Obtenir les coéquipiers recommandés
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
    
    # Étape 2 : Obtenir les compétences et centres d'intérêt actuels de l'étudiant
    student_row = df[df['ID_Étudiant'] == request.student_id]
    if student_row.empty:
        error_msg = f"Étudiant {request.student_id} non trouvé."
        logger.error(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
    
    student_skills = set(ast.literal_eval(student_row['Compétences'].iloc[0]))
    student_interests = set(ast.literal_eval(student_row.get('Centres_d\'Intérêt', pd.Series(['[]'])).iloc[0]))

    # Étape 3 : Obtenir les compétences et centres d'intérêt recommandés basés sur les coéquipiers actuels
    recommended_skills_from_db, recommended_interests_from_db, recommended_skills_programmatic, recommended_interests_programmatic = get_recommended_skills_and_interests(
        student_id=request.student_id,
        student_skills=student_skills,
        student_interests=student_interests,
        df=df,
        potential_teammates=None  # Utilise les coéquipiers actuels
    )

    # Étape 4 : Associer des cours aux compétences et centres d'intérêt recommandés
    recommended_courses = {
        "based_on_skills_from_db": {},
        "based_on_skills_programmatic": {},
        "based_on_interests_from_db": {},
        "based_on_interests_programmatic": {}
    }

    # Cours basés sur les compétences recommandées (de la base)
    for skill in recommended_skills_from_db:
        if skill in RECOMMENDED_COURSES:
            recommended_courses["based_on_skills_from_db"][skill] = RECOMMENDED_COURSES[skill]

    # Cours basés sur les compétences programmatiques
    for skill in recommended_skills_programmatic:
        if skill in RECOMMENDED_COURSES:
            recommended_courses["based_on_skills_programmatic"][skill] = RECOMMENDED_COURSES[skill]

    # Cours basés sur les centres d'intérêt recommandés (de la base)
    for interest in recommended_interests_from_db:
        if interest in RECOMMENDED_COURSES:
            recommended_courses["based_on_interests_from_db"][interest] = RECOMMENDED_COURSES[interest]

    # Cours basés sur les centres d'intérêt programmatiques
    for interest in recommended_interests_programmatic:
        if interest in RECOMMENDED_COURSES:
            recommended_courses["based_on_interests_programmatic"][interest] = RECOMMENDED_COURSES[interest]

    # Étape 5 : Construire la réponse
    response = {
        "teammates": result["teammates"],
        "recommended_skills_from_db": recommended_skills_from_db,
        "recommended_interests_from_db": recommended_interests_from_db,
        "recommended_skills_programmatic": recommended_skills_programmatic,
        "recommended_interests_programmatic": recommended_interests_programmatic,
        "recommended_courses": recommended_courses
    }
    
    logger.info(f"Recommandations générées pour l'étudiant {request.student_id}")
    return response

@app.post("/fictitious_recommendations/")
async def fictitious_recommendations_endpoint(request: FictitiousRecommendationRequest):
    logger.info(f"Requête reçue pour des recommandations fictives pour l'étudiant {request.student_id}")
    
    # Étape 1 : Obtenir les recommandations fictives
    result, error = get_fictitious_recommendations(
        student_id=request.student_id,
        df=df,
        model=model,
        n_recommendations=request.n_recommendations
    )
    
    if error:
        logger.error(f"Erreur pour l'étudiant {request.student_id} : {error}")
        raise HTTPException(status_code=404, detail=error)
    
    # Étape 2 : Associer des cours aux compétences et centres d'intérêt recommandés
    recommended_courses = {
        "based_on_skills_from_db": {},
        "based_on_skills_programmatic": {},
        "based_on_interests_from_db": {},
        "based_on_interests_programmatic": {}
    }

    # Cours basés sur les compétences recommandées (de la base)
    for skill in result["recommended_skills_from_db"]:
        if skill in RECOMMENDED_COURSES:
            recommended_courses["based_on_skills_from_db"][skill] = RECOMMENDED_COURSES[skill]

    # Cours basés sur les compétences programmatiques
    for skill in result["recommended_skills_programmatic"]:
        if skill in RECOMMENDED_COURSES:
            recommended_courses["based_on_skills_programmatic"][skill] = RECOMMENDED_COURSES[skill]

    # Cours basés sur les centres d'intérêt recommandés (de la base)
    for interest in result["recommended_interests_from_db"]:
        if interest in RECOMMENDED_COURSES:
            recommended_courses["based_on_interests_from_db"][interest] = RECOMMENDED_COURSES[interest]

    # Cours basés sur les centres d'intérêt programmatiques
    for interest in result["recommended_interests_programmatic"]:
        if interest in RECOMMENDED_COURSES:
            recommended_courses["based_on_interests_programmatic"][interest] = RECOMMENDED_COURSES[interest]

    # Étape 3 : Ajouter les cours à la réponse
    result["recommended_courses"] = recommended_courses
    
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