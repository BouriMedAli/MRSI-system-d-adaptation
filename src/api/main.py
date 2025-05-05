from fastapi import FastAPI
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import pickle
import random

app = FastAPI()

# Chemins absolus
BASE_DIR = r"C:\Users\User\educational_recommendation"
MODELS_DIR = r"C:\Users\User\educational_recommendation\models"
CSV_PATH = r"C:\Users\User\educational_recommendation\data\dataset_etudiants.csv"

# Charger les modèles et données
autoencoder = tf.keras.models.load_model(f"{MODELS_DIR}/autoencoder.h5")
encoder = tf.keras.models.load_model(f"{MODELS_DIR}/encoder.h5")
with open(f"{MODELS_DIR}/mlb.pkl", 'rb') as f:
    mlb = pickle.load(f)
with open(f"{MODELS_DIR}/student_embeddings.pkl", 'rb') as f:
    embeddings_df = pickle.load(f)
df = pd.read_csv(CSV_PATH)

def preprocess_data(df, mlb):
    list_columns = ['Coéquipiers', 'Communautés', 'Compétences', "Centres_d'Intérêt"]
    for col in list_columns:
        df[col] = df[col].apply(lambda x: eval(x) if isinstance(x, str) else x)
    encoded_data = []
    for col in list_columns:
        df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])
        encoded = mlb.transform(df[col])
        expected_classes = mlb.classes_
        if encoded.shape[1] < len(expected_classes):
            padding = np.zeros((encoded.shape[0], len(expected_classes) - encoded.shape[1]))
            encoded = np.hstack((encoded, padding))
        encoded_df = pd.DataFrame(encoded, columns=[f"{col}_{i}" for i in range(len(expected_classes))])
        encoded_data.append(encoded_df)
    encoded_df = pd.concat(encoded_data, axis=1)
    scaler = MinMaxScaler()
    df['Nombre_Interactions'] = scaler.fit_transform(df[['Nombre_Interactions']])
    df['Travaux_Collaboratifs'] = scaler.fit_transform(df[['Travaux_Collaboratifs']])
    X = pd.concat([encoded_df, df['Nombre_Interactions'], df['Travaux_Collaboratifs']], axis=1)
    return df, X

df, X_scaled = preprocess_data(df, mlb)
if X_scaled.shape[1] != 67:
    padding = np.zeros((X_scaled.shape[0], 67 - X_scaled.shape[1]))
    X_scaled = np.hstack((X_scaled, padding))

def find_similar_students(student_id, embeddings_df, df, top_k=5):
    student_idx = df.index[df['ID_Étudiant'] == student_id].tolist()
    if not student_idx:
        return []
    student_idx = student_idx[0]
    student_embedding = embeddings_df.iloc[student_idx].values
    similarities = embeddings_df.dot(student_embedding) / (np.linalg.norm(embeddings_df, axis=1) * np.linalg.norm(student_embedding))
    similar_indices = similarities.nlargest(top_k + 1).index
    similar_students = []
    for idx in similar_indices:
        if idx != student_idx:
            similar_student_id = int(df.iloc[idx]['ID_Étudiant'])  # Convert to Python int
            similar_student_name = str(df.iloc[idx]['Nom'])  # Ensure string
            similar_students.append({'ID_Étudiant': similar_student_id, 'Nom': similar_student_name})
    return similar_students[:top_k]

def recommend_courses(skills, interests, learning_styles, top_k=3):
    course_mapping = {
        "python": {"course": "Cours de Programmation Python", "resources": {
            "Visual": ["Vidéo : Tutoriel Python sur YouTube", "Infographie : Schémas de syntaxe Python"],
            "Auditory": ["Podcast : 'Python Bytes'", "Audio : Cours audio Python"],
            "Reading/Writing": ["Livre : 'Automate the Boring Stuff with Python' par Al Sweigart", "Article : Documentation Python"],
            "Kinesthetic": ["Exercice : Projets pratiques avec Python", "Simulation : Environnement interactif"]
        }},
        # ... (rest of course_mapping remains unchanged)
    }

    courses = []
    all_items = skills + interests
    for item in all_items:
        item_lower = item.lower()
        if item_lower in course_mapping and course_mapping[item_lower]['course'] not in [c['course'] for c in courses]:
            adapted_resources = []
            for style in learning_styles:
                if style in course_mapping[item_lower]["resources"]:
                    adapted_resources.extend(course_mapping[item_lower]["resources"][style])
            if not adapted_resources:
                adapted_resources = [res for sublist in course_mapping[item_lower]["resources"].values() for res in sublist]
            courses.append({
                'course': course_mapping[item_lower]['course'],
                'resources': adapted_resources[:3],
                'description': generate_course_description(course_mapping[item_lower]['course'], learning_styles)
            })
        else:
            generated_course = f"Cours généré : Introduction à {item.capitalize()}"
            generated_resources = {
                "Visual": [f"Vidéo : Tutoriel sur {item.capitalize()}", f"Infographie : Concepts de {item.capitalize()}"],
                "Auditory": [f"Podcast : Exploration de {item.capitalize()}", f"Audio : Guide de {item.capitalize()}"],
                "Reading/Writing": [f"Livre : Manuel de {item.capitalize()}", f"Article : Bases de {item.capitalize()}"],
                "Kinesthetic": [f"Exercice : Projet sur {item.capitalize()}", f"Simulation : Activité {item.capitalize()}"]
            }
            adapted_resources = []
            for style in learning_styles:
                if style in generated_resources:
                    adapted_resources.extend(generated_resources[style])
            if adapted_resources:
                courses.append({
                    'course': generated_course,
                    'resources': adapted_resources[:3],
                    'description': generate_course_description(generated_course, learning_styles)
                })

    return courses[:top_k]

def generate_motivational_message(learning_styles, skills, interests):
    style_descriptions = {
        "Visual": "un apprenant visuel qui excelle avec des images et des démonstrations",
        "Auditory": "un apprenant auditif qui brille en écoutant et en discutant",
        "Reading/Writing": "un apprenant qui préfère lire et écrire pour assimiler les connaissances",
        "Kinesthetic": "un apprenant kinesthésique qui apprend mieux par le toucher et l’action"
    }
    style_desc = " et ".join([style_descriptions[style] for style in learning_styles])
    skill_desc = ", ".join(skills)
    interest_desc = ", ".join(interests)

    suggestions = {
        "python": "Pourquoi ne pas explorer des projets avancés comme une application ou un algorithme innovant ?",
        "jeux vidéo": "Tu pourrais développer ton propre jeu avec Unity ou Unreal Engine pour mettre tes idées en pratique.",
        "électronique": "Un projet DIY avec Arduino ou Raspberry Pi pourrait booster tes compétences.",
        "musique": "Essaie de composer une piste ou d’apprendre un instrument pour enrichir ton parcours.",
        "photographie": "Expérimente avec des techniques avancées comme la retouche ou la photographie de nuit."
    }
    suggestion_text = " ".join([suggestions.get(item.lower(), f"Explore des projets créatifs liés à {item}!") for item in skills + interests])

    messages = [
        f"Tu es {style_desc} ! Avec tes talents en {skill_desc} et ta passion pour {interest_desc}, tu as tout pour réussir. {suggestion_text} Continue à te dépasser !",
        f"En tant que {style_desc}, tu portes en toi un potentiel unique avec {skill_desc} et {interest_desc}. {suggestion_text} Ose franchir la prochaine étape !",
        f"Bravo, {style_desc} avec {skill_desc} et {interest_desc} ! {suggestion_text} Ton chemin vers l’excellence est déjà tracé, avance avec audace !"
    ]
    return random.choice(messages)

def generate_course_description(course_name, learning_styles):
    base_description = f"Ce cours {course_name} est conçu pour développer tes compétences à travers une approche personnalisée."
    style_details = {
        "Visual": "Tu apprendras via des vidéos captivantes, des infographies détaillées et des démonstrations visuelles.",
        "Auditory": "Des podcasts inspirants, des discussions audio et des explications orales enrichiront ton expérience.",
        "Reading/Writing": "Tu plongeras dans des livres, des articles et des exercices d’écriture pour maîtriser les concepts.",
        "Kinesthetic": "Des projets pratiques, des simulations interactives et des activités physiques te permettront de progresser."
    }
    style_text = " ".join([style_details[style] for style in learning_styles if style in style_details])
    return f"{base_description} {style_text} Prépare-toi à une aventure éducative sur mesure !"

@app.get("/recommend/courses/{student_id}")
async def recommend(student_id: int, skills: str = "python", interests: str = "jeux vidéo", learning_styles: str = "Visual"):
    skills_list = skills.split(",")
    interests_list = interests.split(",")
    learning_styles_list = learning_styles.split(",")

    student_idx = df.index[df['ID_Étudiant'] == student_id].tolist()
    if student_idx:
        student_idx = student_idx[0]
        base_skills = df.iloc[student_idx]["Compétences"]
        base_interests = df.iloc[student_idx]["Centres_d'Intérêt"]
    else:
        base_skills = []
        base_interests = []

    skills = base_skills + [s.strip() for s in skills_list]
    interests = base_interests + [i.strip() for i in interests_list]
    similar_students = find_similar_students(student_id, embeddings_df, df)
    recommended_courses = recommend_courses(skills, interests, learning_styles_list)
    motivational_message = generate_motivational_message(learning_styles_list, skills, interests)

    # Ensure all values are JSON-serializable
    return {
        "student_id": int(student_id),  # Convert to Python int
        "teammates": [
            {"ID_Étudiant": int(student["ID_Étudiant"]), "Nom": str(student["Nom"])}  # Ensure int and str
            for student in similar_students
        ],
        "courses": recommended_courses,
        "motivational_message": motivational_message
    }