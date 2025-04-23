import pandas as pd
import ast
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
import os

# Chargement des données
df = pd.read_csv(os.path.join("Dataset", "dataset_etudiants.csv"))

# Convertir les colonnes
for col in ["Coéquipiers", "Communautés", "Compétences", "Centres_d'Intérêt"]:
    df[col] = df[col].apply(ast.literal_eval)

df["Nombre_Coéquipiers"] = df["Coéquipiers"].apply(lambda x: len(set(x)))

# Encodage
mlb = MultiLabelBinarizer()
communities_encoded = pd.DataFrame(mlb.fit_transform(df["Communautés"]), columns=["Comm_" + label for label in mlb.classes_])
skills_encoded = pd.DataFrame(mlb.fit_transform(df["Compétences"]), columns=["Skill_" + label for label in mlb.classes_])
interests_encoded = pd.DataFrame(mlb.fit_transform(df["Centres_d'Intérêt"]), columns=["Interest_" + label for label in mlb.classes_])

# Création du vecteur de caractéristiques
features = pd.concat([
    df[["Travaux_Collaboratifs", "Nombre_Interactions", "Nombre_Coéquipiers"]],
    communities_encoded, skills_encoded, interests_encoded
], axis=1)

knn = NearestNeighbors(n_neighbors=5, metric='cosine')
knn.fit(features)

def recommander(id_etudiant: int):
    try:
        index = df[df["ID_Étudiant"] == id_etudiant].index[0]
    except IndexError:
        return None

    student_features = features.iloc[index:index+1]
    distances, indices = knn.kneighbors(student_features)
    recommandations = df.iloc[indices[0]]
    recommandations = recommandations[recommandations["ID_Étudiant"] != id_etudiant][["ID_Étudiant", "Nom"]]
    return recommandations.to_dict(orient="records")
