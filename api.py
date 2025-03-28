from model import recommend_collaborators,evaluate_recommendations_cosine
from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neighbors import NearestNeighbors

# Charger les données et le modèle
df = pd.read_csv("Dataset/dataset_etudiants.csv")

# Prétraitement des données
mlb_skills = MultiLabelBinarizer()
skills_encoded = mlb_skills.fit_transform(df['Compétences'])
skills_df = pd.DataFrame(skills_encoded, columns=mlb_skills.classes_)

mlb_interests = MultiLabelBinarizer()
interests_encoded = mlb_interests.fit_transform(df["Centres_d'Intérêt"])
interests_df = pd.DataFrame(interests_encoded, columns=mlb_interests.classes_)

df['Nombre_Interactions'] = (df['Nombre_Interactions'] - df['Nombre_Interactions'].min()) / (df['Nombre_Interactions'].max() - df['Nombre_Interactions'].min())

features = pd.concat([skills_df, interests_df, df[['Nombre_Interactions']]], axis=1)

# Construction du modèle KNN
k = 3
knn = NearestNeighbors(n_neighbors=k, metric='euclidean')
knn.fit(features)

# FastAPI Setup
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de recommandation KNN"}

class RequestBody(BaseModel):
    student_id: int
    k: int = 3  # Par défaut, k=3

# Endpoint de recommandation
@app.get("/recommend_collaborators/")
def recommend_collaborators_api(student_id: int = Query(...), k: int = Query(3)):
    recommendations = recommend_collaborators(student_id, k)
    return {"recommended_students": recommendations}

# Endpoint d'évaluation avec la similarité cosinus
@app.get("/evaluate_recommendations/")
def evaluate_recommendations_api(k: int = 3):
    avg_similarity = evaluate_recommendations_cosine(k)

    return {"average_similarity": avg_similarity}
