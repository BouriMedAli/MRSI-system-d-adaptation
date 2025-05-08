import pandas as pd
import ast
import os
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.impute import SimpleImputer

# Chargement du dataset
try:
    df = pd.read_csv(os.path.join("Dataset", "dataset_etudiants.csv"))
except Exception as e:
    raise RuntimeError(f"Erreur de lecture du fichier dataset_etudiants.csv : {e}")

# Colonnes à parser comme listes
columns_to_parse = ["Coéquipiers", "Communautés", "Compétences", "Centres_d'Intérêt"]
for col in columns_to_parse:
    df[col] = df[col].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])

# Ajout d'une colonne : nombre de coéquipiers uniques
df["Nombre_Coéquipiers"] = df["Coéquipiers"].apply(lambda x: len(set(x)))

# Encodage One-hot avec MultiLabelBinarizer
def encode_column(col_name, prefix):
    mlb = MultiLabelBinarizer()
    encoded = mlb.fit_transform(df[col_name])
    return pd.DataFrame(encoded, columns=[f"{prefix}_{label}" for label in mlb.classes_])

communities_encoded = encode_column("Communautés", "Comm")
skills_encoded = encode_column("Compétences", "Skill")
interests_encoded = encode_column("Centres_d'Intérêt", "Interest")

# Construction du vecteur de caractéristiques
features = pd.concat([
    df[["Travaux_Collaboratifs", "Nombre_Interactions", "Nombre_Coéquipiers"]],
    communities_encoded, skills_encoded, interests_encoded
], axis=1)

# Imputation des NaN (par sécurité)
imputer = SimpleImputer(strategy="mean")
features_imputed = imputer.fit_transform(features)

# Vérification qu'il ne reste aucun NaN
assert not np.isnan(features_imputed).any(), "Des NaN subsistent après imputation"

# Initialisation et entraînement du modèle KNN
knn = NearestNeighbors(n_neighbors=5, metric='cosine')
knn.fit(features_imputed)

# Fonction de recommandation
def recommander(id_etudiant: int):
    try:
        index = df[df["ID_Étudiant"] == id_etudiant].index[0]
    except IndexError:
        return {"erreur": "ID_Étudiant non trouvé."}

    student_features = imputer.transform([features.iloc[index]])
    distances, indices = knn.kneighbors(student_features)

    recommandations = df.iloc[indices[0]]
    recommandations = recommandations[recommandations["ID_Étudiant"] != id_etudiant][["ID_Étudiant", "Nom"]]
    return recommandations.to_dict(orient="records")
