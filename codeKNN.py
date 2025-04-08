
import pandas as pd
import ast
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer

# Chargement des données
df = pd.read_csv("Dataset/dataset_etudiants.csv")

# Convertir les colonnes stockant des listes sous forme réelle
df["Coéquipiers"] = df["Coéquipiers"].apply(ast.literal_eval)
df["Communautés"] = df["Communautés"].apply(ast.literal_eval)
df["Compétences"] = df["Compétences"].apply(ast.literal_eval)
df["Centres_d'Intérêt"] = df["Centres_d'Intérêt"].apply(ast.literal_eval)

# Calcul du nombre de coéquipiers uniques
df["Nombre_Coéquipiers"] = df["Coéquipiers"].apply(lambda x: len(set(x)))

# Encodage des attributs catégoriels
mlb = MultiLabelBinarizer()

# Encoder les communautés
communities_encoded = pd.DataFrame(mlb.fit_transform(df["Communautés"]), columns=["Comm_" + label for label in mlb.classes_])
# Encoder les compétences
skills_encoded = pd.DataFrame(mlb.fit_transform(df["Compétences"]), columns=["Skill_" + label for label in mlb.classes_])
# Encoder les centres d'intérêt
interests_encoded = pd.DataFrame(mlb.fit_transform(df["Centres_d'Intérêt"]), columns=["Interest_" + label for label in mlb.classes_])

# Fusionner toutes les features utiles et conserver les noms des colonnes
features = pd.concat([
    df[["Travaux_Collaboratifs", "Nombre_Interactions", "Nombre_Coéquipiers"]],
    communities_encoded, skills_encoded, interests_encoded
], axis=1)

# Entraînement du modèle KNN avec les noms de caractéristiques correctement définis
knn = NearestNeighbors(n_neighbors=5, metric='cosine')
knn.fit(features)


def recommander(id_etudiant):
    # Trouver l'index de l'étudiant
    index = df[df["ID_Étudiant"] == id_etudiant].index[0]
    
    # Obtenir les données pour cet étudiant (et les mettre dans le même format que 'features')
    student_features = features.iloc[index:index+1]  # Prendre une ligne (étudiant)
    
    # Obtenir les voisins les plus proches
    distances, indices = knn.kneighbors(student_features)
    
    # Récupérer les recommandations avec les IDs et les noms, en excluant l'étudiant lui-même
    recommandations = df.iloc[indices[0]]
    recommandations = recommandations[recommandations["ID_Étudiant"] != id_etudiant][["ID_Étudiant", "Nom"]]
    return recommandations.to_dict(orient="records")

# Test avec un étudiant
print(recommander(2))
