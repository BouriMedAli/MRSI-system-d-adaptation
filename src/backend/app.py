
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import pickle
import random
import requests
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

app = FastAPI()

# Variables d'environnement pour l'API Grok
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Chemins dans le conteneur
BASE_DIR = "/app"
MODELS_DIR = "/app/models"
CSV_PATH = "/app/data/dataset_etudiants.csv"

# Charger les modèles et les données
autoencoder = tf.keras.models.load_model(f"{MODELS_DIR}/autoencoder.h5")
encoder = tf.keras.models.load_model(f"{MODELS_DIR}/encoder.h5")
with open(f"{MODELS_DIR}/mlb.pkl", 'rb') as f:
    mlb = pickle.load(f)
with open(f"{MODELS_DIR}/student_embeddings.pkl", 'rb') as f:
    embeddings_df = pickle.load(f)
df = pd.read_csv(CSV_PATH)

# Fonctions placeholders (à remplacer par vos implémentations)
def find_similar_students(student_id, embeddings_df, df):
    return [{"ID_Étudiant": 1, "Nom": "Alice"}, {"ID_Étudiant": 2, "Nom": "Bob"}]

def recommend_courses(skills, interests, learning_styles):
    return [
        {"title": "Python pour le développement de jeux", "description": "Apprenez Python pour créer des jeux"},
        {"title": "Bases de la science des données", "description": "Introduction à l'analyse de données"}
    ]

# Contenu généré par IA
def generate_motivational_message(learning_styles, skills, interests):
    prompt = f"Créez un message motivant pour un étudiant qui préfère l'apprentissage {', '.join(learning_styles)}, a des compétences en {', '.join(skills)}, et s'intéresse à {', '.join(interests)}. Soyez concis et inspirant."
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-3",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        return f"Continuez à progresser avec vos compétences en {skills[0]} et votre passion pour {interests[0]} !"  # Secours

def generate_course_description(course_title, skills, interests):
    prompt = f"Écrivez une description brève et engageante pour un cours intitulé '{course_title}' adapté à un étudiant avec des compétences en {', '.join(skills)} et des intérêts en {', '.join(interests)}."
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-3",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        return f"Explorez {course_title} pour améliorer vos compétences !"  # Secours

# Mettre à jour recommend_courses pour utiliser les descriptions générées par IA
def recommend_courses(skills, interests, learning_styles):
    base_courses = [
        {"title": "Python pour le développement de jeux"},
        {"title": "Bases de la science des données"}
    ]
    for course in base_courses:
        course["description"] = generate_course_description(course["title"], skills, interests)
    return base_courses

@app.get("/recommend/courses/{student_id}")
async def recommend(student_id: int, skills: str = "python", interests: str = "jeux vidéo", learning_styles: str = "Visual"):
    skills_list = skills.split(",")
    interests_list = interests.split(",")
    learning_styles_list = learning_styles.split(",")

    student_idx = df.index[df['ID_Étudiant'] == student_id].tolist()
    if not student_idx:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    student_idx = student_idx[0]
    base_skills = df.iloc[student_idx]["Compétences"]
    base_interests = df.iloc[student_idx]["Centres_d'Intérêt"]

    skills = base_skills + [s.strip() for s in skills_list]
    interests = base_interests + [i.strip() for i in interests_list]
    similar_students = find_similar_students(student_id, embeddings_df, df)
    recommended_courses = recommend_courses(skills, interests, learning_styles_list)
    motivational_message = generate_motivational_message(learning_styles_list, skills, interests)

    return {
        "student_id": int(student_id),
        "teammates": [
            {"ID_Étudiant": int(student["ID_Étudiant"]), "Nom": str(student["Nom"])}
            for student in similar_students
        ],
        "courses": recommended_courses,
        "motivational_message": motivational_message
    }

@app.get("/students/{student_id}")
async def get_student_profile(student_id: int):
    student_idx = df.index[df['ID_Étudiant'] == student_id].tolist()
    if not student_idx:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    student = df.iloc[student_idx[0]]
    return {
        "ID_Étudiant": int(student["ID_Étudiant"]),
        "Nom": str(student["Nom"]),
        "Compétences": student["Compétences"] if isinstance(student["Compétences"], list) else str(student["Compétences"]).split(","),
        "Centres_d_Intérêt": student["Centres_d'Intérêt"] if isinstance(student["Centres_d'Intérêt"], list) else str(student["Centres_d'Intérêt"]).split(",")
    }

class ChatQuery(BaseModel):
    query: str

@app.post("/ai-chat")
async def ai_chat(query: ChatQuery):
    prompt = f"Un étudiant demande : '{query.query}' à propos des cours ou des coéquipiers. Fournissez une réponse utile et concise adaptée à ses objectifs éducatifs."
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-3",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return {"response": response.json()["choices"][0]["message"]["content"]}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="Échec de la génération de la réponse IA")
