from fastapi import FastAPI, Request # type: ignore
from fastapi.responses import HTMLResponse, JSONResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from surprise import Dataset, Reader # type: ignore
from surprise import CoClustering # type: ignore
import matplotlib # type: ignore
matplotlib.use('Agg')
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore # type: ignore
import uuid
import os
import ast
import warnings
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from fastapi.responses import HTMLResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from fastapi import FastAPI, Request # type: ignore
from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter # type: ignore
# Fichier principal 'main.py'
from backend.database import afficher_etudiants # type: ignore

# Afficher les étudiants
afficher_etudiants()

warnings.filterwarnings("ignore", category=UserWarning, message="unknown class")
from fastapi.staticfiles import StaticFiles # type: ignore

# Initialisation de FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Middleware pour CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de requêtes Pydantic
class KNNRequest(BaseModel):
    competences: List[str]
    Centres_d_Interet: List[str]
    travaux: int

class ClusteringRequest(BaseModel):
    k: int

app = FastAPI()
templates = Jinja2Templates(directory="frontend")

# Modèle pour la requête
class KNNRequest(BaseModel):
    competences: list
    Centres_d_Interet: list
    travaux: int

# Chargement et préparation des données
def charger_etudiants():
    try:
        df = pd.read_csv("backend/dataset_etudiants.csv")

        # Correction des noms de colonnes si nécessaire
        if "Centres_d'Intérêt" in df.columns:
            df.rename(columns={"Centres_d'Intérêt": "Centres_d_Interet"}, inplace=True)

        colonnes = ['Compétences', 'Coéquipiers', 'Centres_d_Interet', 'Communautés']
        for col in colonnes:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: ast.literal_eval(str(x)) if pd.notnull(x) else [])

        return df
    except Exception as e:
        print(f"[Erreur] Chargement CSV : {e}")
        return pd.DataFrame()

def clean_data(liste):
    return [item.strip().lower() for item in liste] if isinstance(liste, list) else []

@app.get("/knn", response_class=HTMLResponse)
async def knn_page(request: Request):
    return templates.TemplateResponse("knn.html", {"request": request})

@app.post("/knn", response_class=JSONResponse)
async def recommend_knn(request: KNNRequest):
    print("[INFO] Requête reçue :", request)

    df = charger_etudiants()
    if df.empty:
        return JSONResponse(content={"error": "Erreur de chargement des étudiants"}, status_code=500)

    # Nettoyage
    df['Compétences'] = df['Compétences'].apply(clean_data)
    df['Centres_d_Interet'] = df['Centres_d_Interet'].apply(clean_data)

    # Encodage avec MultiLabelBinarizer
    compétences_possibles = ['Électronique', 'Science', 'Python', 'Marketing', 'IA', 'Design', 'Data', 'Blockchain']
    mlb_comp = MultiLabelBinarizer(classes=compétences_possibles)
    mlb_int = MultiLabelBinarizer()

    X_comp = mlb_comp.fit_transform(df['Compétences'])
    X_int = mlb_int.fit_transform(df['Centres_d_Interet'])

    # Vecteur utilisateur
    user_comp = mlb_comp.transform([request.competences])
    user_int = mlb_int.transform([request.Centres_d_Interet])
    user_travaux = np.array([[request.travaux]])
    user_row = np.hstack([user_comp, user_int, user_travaux])

    X = np.hstack([X_comp, X_int, df[["Travaux_Collaboratifs"]].values])

    # Calcul de la similarité
    sim = cosine_similarity(user_row, X)[0]
    df['similarity'] = sim

    # Top 10
    top_indices = np.argsort(sim)[::-1][:10]
    df_top = df.iloc[top_indices].copy()

    results = [{
        "nom": row["Nom"],
        "competences": row["Compétences"],
        "Centres_d_Interet": row["Centres_d_Interet"],
        "similarity": round(row["similarity"] * 100, 2)
    } for _, row in df_top.iterrows()]

    # Logs
    print("[INFO] Résultats générés :", results)

    # Données pour graphiques
    pie_data = {
        "labels": df_top["Nom"].tolist(),
        "values": df_top["similarity"].tolist()
    }

    scatter_data = {
        "x": list(range(1, len(df_top) + 1)),
        "y": df_top["similarity"].tolist(),
        "labels": df_top["Nom"].tolist()
    }

    histogram_data = {
        "competences": mlb_comp.classes_.tolist(),
        "Centres_d_Interet": mlb_int.classes_.tolist()
    }

    return JSONResponse(content={
        "resultats": results,
        "pie_data": pie_data,
        "scatter_data": scatter_data,
        "histogram_data": histogram_data
    })

"""@app.post("/recommend/knn")
async def recommend_knn(request: KNNRequest):
    df = etudiants.copy()

    # Initialisation du MultiLabelBinarizer pour les compétences possibles
    compétences_possibles = ['Électronique', 'Science', 'Python', 'Marketing', 'IA', 'Design', 'Data', 'Blockchain']
    mlb_comp = MultiLabelBinarizer(classes=compétences_possibles)
    mlb_int = MultiLabelBinarizer()

    # Nettoyage et transformation des colonnes
    df['Compétences'] = df['Compétences'].apply(clean_data)
    df['Centres_d_Interet'] = df['Centres_d_Interet'].apply(clean_data)

    # Transformation des données catégorielles
    X_comp = mlb_comp.fit_transform(df['Compétences'])
    X_int = mlb_int.fit_transform(df['Centres_d_Interet'])

    # Concaténation des données (Compétences, Intérêts, Travaux Collaboratifs)
    X = np.hstack([X_comp, X_int, df[["Travaux_Collaboratifs"]].values])

    # Données de l'utilisateur
    user_row = np.hstack([ 
        mlb_comp.transform([request.competences]), 
        mlb_int.transform([request.interets]), 
        np.array([[request.travaux]]) 
    ])

    # Calcul de la similarité
    sim = cosine_similarity(user_row, X)[0]

    # Ajout de la similarité dans le dataframe
    df['similarity'] = sim

    # Sélection des 10 étudiants les plus similaires
    top_indices = np.argsort(sim)[::-1][:10]
    df_result = df.iloc[top_indices].copy()

    # Création des résultats sous forme de liste de dictionnaires
    results = []
    for _, row in df_result.iterrows():
        results.append({
            "nom": row["Nom"],
            "competences": row["Compétences"],
            "interets": row["Centres_d_Interet"],
            "similarity": round(row["similarity"] * 100, 2)
        })

    # Données pour le graphique de similarité (scatter plot)
    scatter_data = {
        "x": list(range(1, len(df_result)+1)),
        "y": df_result["similarity"].tolist(),
        "labels": df_result["Nom"].tolist()
    }

    # Données pour le graphique des histogrammes
    histogram_data = {
        "competences": mlb_comp.classes_.tolist(),
        "interets": mlb_int.classes_.tolist()
    }

    # Retour de la réponse avec les résultats, les données pour le scatter et histogramme
    return JSONResponse(content={
        "resultats": results,
        "scatter_data": scatter_data,
        "histogram_data": histogram_data
    })
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("frontend/static/select.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={}, status_code=204)

@app.get("/data")
async def get_data():
    df = df.copy()
    return JSONResponse(content=df.to_dict(orient="records"))
templates = Jinja2Templates(directory="frontend/static/template")

app.mount("/static", StaticFiles(directory="static"), name="static")



# Charger les données depuis le fichier CSV
def load_data():
    try:
        # Charger le CSV dans un DataFrame
        df = pd.read_csv("backend/dataset_etudiants.csv")
        return df
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Le fichier de données est introuvable.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors du chargement des données : {str(e)}")

@app.get("/clustering", response_class=HTMLResponse)
async def clustering_page(request: Request):
    return templates.TemplateResponse("co_clustering.html", {"request": request})

@app.post("/clustering", response_class=JSONResponse)
async def recommend_clustering(request: Request):
    # Récupérer k depuis la requête
    k = int(request.query_params.get("k", 3))  # Valeur par défaut de k = 3

    # Vérifier si k est un entier positif
    if not isinstance(k, int) or k <= 0:
        raise HTTPException(status_code=400, detail="Le nombre de clusters (k) doit être un entier positif.")

    # Charger les données depuis le fichier CSV
    df = load_data()

    # Préparer les données pour le modèle
    reader = Reader(rating_scale=(0, 100))
    long_data = []
    for i, row in df.iterrows():
        uid = row["Nom"]
        # Convertir les champs de liste de chaînes en liste d'entiers/chaînes
        coequipiers = eval(row["Coéquipiers"]) if isinstance(row["Coéquipiers"], str) else row["Coéquipiers"]
        communautes = eval(row["Communautés"]) if isinstance(row["Communautés"], str) else row["Communautés"]
        competences = eval(row["Compétences"]) if isinstance(row["Compétences"], str) else row["Compétences"]
        centres_interet = eval(row["Centres_d'Intérêt"]) if isinstance(row["Centres_d'Intérêt"], str) else row["Centres_d'Intérêt"]

        long_data.append((uid, "Travaux_Collaboratifs", row["Travaux_Collaboratifs"]))
        long_data.append((uid, "Coéquipiers", len(coequipiers)))
        long_data.append((uid, "Communautés", len(communautes)))
        long_data.append((uid, "Nombre_Interactions", row["Nombre_Interactions"]))

    # Charger les données dans Surprise Dataset
    data = Dataset.load_from_df(pd.DataFrame(long_data, columns=["userID", "itemID", "rating"]), reader)
    trainset = data.build_full_trainset()

    # Entraînement du modèle CoClustering
    model = CoClustering(n_cltr_u=k, n_cltr_i=k)
    model.fit(trainset)

    # Attribution des clusters aux étudiants
        # Attribution des clusters aux étudiants
    cluster_assignments = {}
    for uid in trainset.all_users():
        raw_uid = trainset.to_raw_uid(uid)
        cluster_u = model.cluster_users[uid]
        cluster_assignments[raw_uid] = cluster_u

    # Ajout des clusters au dataframe
    df["cluster"] = df["Nom"].map(cluster_assignments)

    # Création d'un tableau résumé des clusters
    cluster_summary = df.groupby("cluster").agg({
        "Nom": "count",
        "Travaux_Collaboratifs": "mean",
        "Nombre_Interactions": "mean"
    }).reset_index().rename(columns={"Nom": "Nombre_Etudiants"})

    # Préparation des données à retourner
    results = df.to_dict(orient="records")
    summary = cluster_summary.to_dict(orient="records")

    return JSONResponse(content={
        "clusters": results,
        "summary": summary
    })
