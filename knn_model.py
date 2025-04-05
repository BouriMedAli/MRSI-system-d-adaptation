import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
import numpy as np

# --- 1. Chargement des données ---
df = pd.read_csv("dataset_etudiants.csv", sep=';')

# --- 2. Nettoyage et transformation des colonnes en vraies listes ---
colonnes_listes = ['Compétences', "Centres_d'Intérêt", 'Communautés', 'Coéquipiers']
for col in colonnes_listes:
    df[col] = df[col].apply(lambda x: ast.literal_eval(str(x)))

# --- 3. Création d'un vecteur texte par étudiant ---
def concat_features(row):
    return ' '.join(row['Compétences'] + row["Centres_d'Intérêt"] + row['Communautés'])

df['profile_text'] = df.apply(concat_features, axis=1)

# --- 4. Vectorisation (bag of words) ---
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['profile_text'])

# --- 5. Modèle KNN (k plus proches voisins) ---
knn_model = NearestNeighbors(n_neighbors=4, metric='euclidean')
knn_model.fit(X)

# --- 6. Fonction principale de recommandation ---
def recommander_competences(id_etudiant):
    index = df[df['ID_Étudiant'] == id_etudiant].index[0]
    etudiant_vector = X[index]

    # --- KNN ---
    distances, indices = knn_model.kneighbors(etudiant_vector)
    voisins_knn = df.iloc[indices[0][1:]]  # [1:] pour exclure l'étudiant lui-même
    print("\nVoisins KNN :")
    print(voisins_knn[['ID_Étudiant', 'Nom', 'Compétences', 'Communautés', "Centres_d'Intérêt"]].to_string(index=False))

    # --- Compétences des coéquipiers ---
    coequipiers_ids = df.loc[index, 'Coéquipiers']
    coequipiers = df[df['ID_Étudiant'].isin(coequipiers_ids)]

    # --- Compétences à recommander ---
    competences_connues = set(df.loc[index, 'Compétences'])
    competences_voisins = set([c for lst in voisins_knn['Compétences'] for c in lst])
    print(f"competences_voisins :  {competences_voisins} ")
    competences_coequipiers = set([c for lst in coequipiers['Compétences'] for c in lst])
    print(f"competences_connues :  {competences_connues} ")
    toutes_competences = competences_voisins.union(competences_coequipiers)
    competences_a_recommander = list(toutes_competences - competences_connues)

    return competences_a_recommander

# --- Exemple d'utilisation ---
# indice_exemple=1
# recommandations = recommander_competences(indice_exemple)
# ligne_etudiant = df[df['ID_Étudiant'] == indice_exemple]
# print("Profil de l'étudiant : ")
# print(ligne_etudiant.to_string(index=False))
# print(f"\nCompétences recommandées pour l'étudiant : {recommandations}")
