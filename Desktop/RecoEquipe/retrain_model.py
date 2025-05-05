# retrain_model.py
import pandas as pd
import pickle
import os
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from surprise import SVD, Dataset, Reader

# Chargement des données
df = pd.read_csv("app/data/dataset_etudiants.csv")
print("Colonnes disponibles :", df.columns.tolist())

# Renommage des colonnes pour uniformiser
df.rename(columns={
    "Compétences": "competences",
    "Centres_d'Intérêt": "interets",
    "Communautés": "communaute"
}, inplace=True)

# Nettoyage des colonnes multi-labels
# On vérifie si les colonnes existent avant de les transformer
for col in ["competences", "interets", "communaute"]:
    if col in df.columns:
        df[col] = df[col].fillna("").apply(lambda x: [item.strip() for item in x.split(",") if item.strip()])

# Affichage pour vérification
print("✅ Exemple de données nettoyées :")
print(df[["competences", "interets", "communaute"]].head())

# Encodage multi-label
mlb_competences = MultiLabelBinarizer()
mlb_interets = MultiLabelBinarizer()
mlb_communautes = MultiLabelBinarizer()

X_comp = mlb_competences.fit_transform(df["competences"])
X_int = mlb_interets.fit_transform(df["interets"])
X_com = mlb_communautes.fit_transform(df["communaute"])

# Création du profil vectorisé des étudiants
student_profiles = np.hstack([X_comp, X_int, X_com])

# Vérification des colonnes de notation pour SVD
required_cols = ["ID_Étudiant", "Coéquipiers", "Nombre_Interactions"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Colonne manquante dans le fichier CSV : {col}")

# Préparation des données pour Surprise
reader = Reader(rating_scale=(1, 5))  # Tu peux ajuster selon ta logique
df_ratings = df[["ID_Étudiant", "Coéquipiers", "Nombre_Interactions"]]

# Dataset pour Surprise
data = Dataset.load_from_df(df_ratings, reader)
trainset = data.build_full_trainset()

# Entraînement du modèle SVD
svd = SVD()
svd.fit(trainset)

# Dictionnaire à sauvegarder
model_data = {
    "mlb_competences": mlb_competences,
    "mlb_interets": mlb_interets,
    "mlb_communautes": mlb_communautes,
    "student_profiles": student_profiles,
    "svd": svd
}

# Sauvegarde du modèle
os.makedirs("app/models", exist_ok=True)
with open("app/models/modele_recommandation.pkl", "wb") as f:
    pickle.dump(model_data, f)

print("✅ Modèle SVD entraîné et sauvegardé avec succès.")
