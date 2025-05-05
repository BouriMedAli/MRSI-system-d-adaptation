from fastapi import FastAPI, Request, Query, HTTPException # type: ignore
from fastapi.responses import HTMLResponse, JSONResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
from sklearn.preprocessing import MultiLabelBinarizer # type: ignore
from surprise import Dataset, Reader, CoClustering, KNNBasic # type: ignore
import matplotlib # type: ignore
matplotlib.use('Agg')
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import ast
import warnings
import os
from sklearn.cluster import SpectralCoclustering
from sklearn.feature_extraction.text import CountVectorizer
warnings.filterwarnings("ignore", category=UserWarning, message="unknown class")
from surprise.model_selection import train_test_split # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from sklearn.preprocessing import LabelEncoder

# Charger les données
data = Dataset.load_builtin('ml-100k') # type: ignore
trainset, testset = train_test_split(data, test_size=0.25) # type: ignore

algo = CoClustering() # type: ignore
algo.fit(trainset) # type: ignore

# Accès aux  utilisateurs/items (non officiel)

# Initialisation FastAPI
app = FastAPI() # type: ignore

app.add_middleware( # type: ignore
      CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configs
FICHIER_CSV = 'backend/dataset_etudiants.csv'
templates = Jinja2Templates(directory="static/template") # type: ignore
app.mount("/static", StaticFiles(directory="static"), name="static") # type: ignore

# Charger les données
def charger_donnees1():
    try:
        if not os.path.exists(FICHIER_CSV):
            print(f"❌ Erreur : fichier '{FICHIER_CSV}' introuvable.")
            return None

        etudiants = pd.read_csv(FICHIER_CSV, encoding="utf-8")
        etudiants.rename(columns={"Centres_d'Intérêt": "Centres_d_Interet"}, inplace=True)
        etudiants.columns = etudiants.columns.str.strip()

        colonnes_requises = ['Nom', 'Compétences', 'Centres_d_Interet', 'Travaux_Collaboratifs', 'Coéquipiers', 'Communautés', 'Nombre_Interactions']
        for col in colonnes_requises:
            if col not in etudiants.columns:
                print(f"❌ Erreur : colonne '{col}' manquante.")
                return None

        colonnes_a_convertir = ['Compétences', 'Centres_d_Interet', 'Coéquipiers', 'Communautés']
        for col in colonnes_a_convertir:
            etudiants[col] = etudiants[col].apply(convertir_en_liste)

        print("✅ Données chargées !")
        return etudiants

    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return None

def convertir_en_liste(chaine): # type: ignore
    try:
        return ast.literal_eval(chaine) if isinstance(chaine, str) else [] # type: ignore
    except Exception as e:
        print(f"❌ Erreur conversion en liste : {e}")
        return []# type: ignore

# Frontend page
@app.get("/knn", response_class=HTMLResponse) # type: ignore
async def afficher_page_knn(request: Request): # type: ignore
    return templates.TemplateResponse("knn.html", {"request": request}) # type: ignore


class KNNRequest(BaseModel): # type: ignore
    Compétences: List[str]
    Communautés: List[str]

# Recommandation
@app.post("/api/knn", response_class=JSONResponse) # type: ignore
async def api_knn_post(payload: KNNRequest): # type: ignore
    Competences_input = payload.Compétences
    Communautes_input = payload.Communautés

    if not Competences_input or not Communautes_input:
        return JSONResponse(content={"message": "Veuillez spécifier au moins une compétence et une communauté."}, status_code=400) # type: ignore

    df = charger_donnees1()
    if df is None:
        return {"message": "Erreur chargement données."}

    try:
        # Fusionner compétences + communautés en une seule chaîne
        df['features'] = df.apply(lambda x: " ".join(x['Compétences'] + x['Communautés']), axis=1) # type: ignore

        # Ajouter l'utilisateur temporaire
        utilisateur_temp_features = " ".join(Competences_input + Communautes_input)

        # Construire la matrice
        corpus = list(df['features']) + [utilisateur_temp_features] # type: ignore
        vectorizer = CountVectorizer()
        vecteurs = vectorizer.fit_transform(corpus) # type: ignore

        # Calcul de la similarité
        similarity_matrix = cosine_similarity(vecteurs)# type: ignore

        # La dernière ligne est celle de l'utilisateur temporaire
        similarities = similarity_matrix[-1][:-1]  # Exclure lui-même

        similarites = []
        for i, sim in enumerate(similarities):
            similarites.append({# type: ignore
                "Nom": df.iloc[i]['Nom'],
                "Compétences": df.iloc[i]['Compétences'],
                "Communautés": df.iloc[i]['Communautés'],
                "Similarité": round(sim * 100, 2)
            })

   # Trier par similarité décroissante
        similarites.sort(key=lambda x: x["Similarité"], reverse=True)# type: ignore

# Prendre seulement les 10 premiers
        top_10 = similarites[:10]# type: ignore

# Normaliser pour que le total fasse 100%
        total_sim = sum([s["Similarité"] for s in top_10])# type: ignore

        if total_sim > 0:
            for s in top_10:# type: ignore
                s["Similarité"] = round((s["Similarité"] / total_sim) * 100, 2)# type: ignore

        return {"resultats": top_10}# type: ignore

    except Exception as e:
        print(f"❌ Erreur traitement : {e}")
        return JSONResponse(content={"message": "Erreur traitement."}, status_code=500)# type: ignore



# Route page principale
@app.get("/", response_class=HTMLResponse)# type: ignore
async def home():# type: ignore
    with open("static/select.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())# type: ignore
    
# --------- Affichage de l'interface ----------
@app.get("/co_clustering_interface")# type: ignore
def afficher_page(request: Request):# type: ignore
    return templates.TemplateResponse("co_clustering.html", {"request": request})# type: ignore

# --------- Chargement des données ----------
def charger_donnees():
    df = pd.read_csv("backend/dataset_etudiants.csv")# type: ignore
    df["Communautés"] = df["Communautés"].apply(eval)# type: ignore
    df["Nom"] = df["Nom"].astype(str)
    df["Coéquipiers"] = df["Coéquipiers"].apply(lambda x: ast.literal_eval(str(x)))# type: ignore
    return df

# --------- Création du dataset pour CoClustering ----------
def creer_dataset_surprise(df):# type: ignore
    df_surprise = df[["ID_Étudiant", "Nom", "Nombre_Interactions"]]# type: ignore
    reader = Reader(rating_scale=(df_surprise["Nombre_Interactions"].min(), df_surprise["Nombre_Interactions"].max()))# type: ignore
    data = Dataset.load_from_df(df_surprise[["ID_Étudiant", "Nom", "Nombre_Interactions"]], reader)# type: ignore
    return data# type: ignore


# --------- Entraîner le modèle CoClustering ----------
def entrainer_coclustering(data):# type: ignore
    trainset = data.build_full_trainset()# type: ignore
    algo = CoClustering()# type: ignore
    algo.fit(trainset)# type: ignore
    return algo, trainset# type: ignore

# --------- Ajouter les clusters aux étudiants ----------
def generer_predictions(df, algo, communaute):# type: ignore
    df_filtre = filtrer_par_communaute(df, communaute)# type: ignore
    resultats = []

    for index, row_source in df_filtre.iterrows():# type: ignore
        uid = str(row_source["ID_Étudiant"])# type: ignore
        for index2, row_cible in df.iterrows():# type: ignore
            iid = str(row_cible["Nom"])# type: ignore
            prediction = algo.predict(uid, iid)# type: ignore
            resultats.append({# type: ignore
                "ID_Étudiant": row_source["ID_Étudiant"],
                "Nom": row_source["Nom"],
                "Nom_Cible": row_cible["Nom"],
                "Interaction_Prédit": round(prediction.est, 2)# type: ignore
            })

    return pd.DataFrame(resultats)


from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
import ast

app = FastAPI()

# CORS (pour permettre l'accès depuis le frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------- Affichage de l'interface ----------
@app.get("/co_clustering_interface")# type: ignore
def afficher_page(request: Request):# type: ignore
    return templates.TemplateResponse("co_clustering.html", {"request": request})# type: ignore
@app.get("/co_clustering/")# type: ignore
def co_clustering(communaute: str = Query(...)):# type: ignore
    df = pd.read_csv("backend/dataset_etudiants.csv")# type: ignore
    multi_cols = ['Coéquipiers', 'Communautés', 'Compétences', "Centres_d'Intérêt"]
    for col in multi_cols:
        df[col] = df[col].apply(lambda x: ast.literal_eval(str(x)))# type: ignore

    # Filtrage
    df_filtered = df[df["Communautés"].apply(lambda x: communaute in x)].reset_index(drop=True)# type: ignore

    if df_filtered.empty:
        return JSONResponse(content={"message": "Aucun étudiant trouvé"}, status_code=404)# type: ignore
    print(df.head())
    encoded_parts = []
    for col in multi_cols:
        mlb = MultiLabelBinarizer()
        binarized = pd.DataFrame(mlb.fit_transform(df_filtered[col]), columns=[f"{col}_{v}" for v in mlb.classes_])# type: ignore
        encoded_parts.append(binarized)# type: ignore

    numeric_df = df_filtered[['Travaux_Collaboratifs', 'Nombre_Interactions']].reset_index(drop=True)
    X = pd.concat([numeric_df] + encoded_parts, axis=1)
    X = (X > 0).astype(int)# type: ignore

    n_students, n_features = X.shape
    n_row_clusters = 2
    n_col_clusters = 2
    np.random.seed(0)
    row_clusters = np.random.randint(0, n_row_clusters, size=n_students)
    col_clusters = np.random.randint(0, n_col_clusters, size=n_features)

    def compute_surprise(matrix, row_clusters, col_clusters, n_row_clusters, n_col_clusters):# type: ignore
        total = matrix.sum()# type: ignore
        surprise = 0
        for i in range(n_row_clusters):# type: ignore
            for j in range(n_col_clusters):# type: ignore
                block = matrix[(row_clusters == i)][:, (col_clusters == j)]# type: ignore
                o = block.sum()# type: ignore
                e = block.shape[0] * block.shape[1] * (total / (matrix.shape[0] * matrix.shape[1]))# type: ignore
                if o > 0 and e > 0:
                    surprise += o * np.log(o / (e + 1e-10))# type: ignore
        return surprise# type: ignore

    max_iter = 10
    for _ in range(max_iter):
        changed = False
        for i in range(n_students):
            best_cluster = row_clusters[i]
            best_surprise = compute_surprise(X.values, row_clusters, col_clusters, n_row_clusters, n_col_clusters)# type: ignore
            for k in range(n_row_clusters):
                row_clusters[i] = k
                s = compute_surprise(X.values, row_clusters, col_clusters, n_row_clusters, n_col_clusters)# type: ignore
                if s > best_surprise:
                    best_cluster = k
                    best_surprise = s
            if row_clusters[i] != best_cluster:
                changed = True
            row_clusters[i] = best_cluster

        for j in range(n_features):
            best_cluster = col_clusters[j]
            best_surprise = compute_surprise(X.values, row_clusters, col_clusters, n_row_clusters, n_col_clusters)# type: ignore
            for l in range(n_col_clusters):
                col_clusters[j] = l
                s = compute_surprise(X.values, row_clusters, col_clusters, n_row_clusters, n_col_clusters)# type: ignore
                if s > best_surprise:
                    best_cluster = l
                    best_surprise = s
            if col_clusters[j] != best_cluster:
                changed = True
            col_clusters[j] = best_cluster

        if not changed:
            break

    df_filtered["Cluster_Etudiant"] = row_clusters
    df_filtered["Pred"] = df_filtered["Nombre_Interactions"] + np.random.randint(-2, 3, size=len(df_filtered))

    tableau_par_nom = df_filtered[["ID_Étudiant", "Nom", "Nombre_Interactions", "Cluster_Etudiant", "Pred"]].to_dict(orient="records")# type: ignore
    tableau_par_cluster = df_filtered.sort_values("Cluster_Etudiant")[["ID_Étudiant", "Nom", "Nombre_Interactions", "Cluster_Etudiant", "Pred"]].to_dict(orient="records")# type: ignore
    # Matrice X après tri par clusters (ligne = étudiant, colonne = attribut)
    X_sorted = X.iloc[np.argsort(row_clusters), :]
    X_sorted = X_sorted.iloc[:, np.argsort(col_clusters)]
   
    return {
        "tableau_par_nom": tableau_par_nom,
        "tableau_par_cluster": tableau_par_cluster,
    }
