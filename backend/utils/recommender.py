# backend/utils/recommender.py

import pandas as pd
import ast
from sklearn.neighbors import NearestNeighbors

def preprocess_data(filepath):
    df = pd.read_csv(filepath)

    # Nettoyer les colonnes JSON
    for col in ['Compétences', "Centres_d'Intérêt"]:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

    # Extraire les compétences et centres d'intérêt uniques
    all_competences = sorted(set(sum(df['Compétences'], [])))
    all_interets = sorted(set(sum(df["Centres_d'Intérêt"], [])))

    for comp in all_competences:
        df[f'Comp_{comp}'] = df['Compétences'].apply(lambda x: 1 if comp in x else 0)

    for interet in all_interets:
        df[f'Interet_{interet}'] = df["Centres_d'Intérêt"].apply(lambda x: 1 if interet in x else 0)

    df['Travaux_Collaboratifs'] = df['Travaux_Collaboratifs'].astype(float)
    df['Nombre_Interactions'] = df['Nombre_Interactions'].astype(float)

    return df, all_competences, all_interets

def recommend_students(nom_etudiant, nb_interactions, top_n=10):
    filepath = "backend/data/dataset_etudiants.csv"
    df, all_competences, all_interets = preprocess_data(filepath)

    features = [f'Comp_{c}' for c in all_competences] + [f'Interet_{i}' for i in all_interets] + ['Travaux_Collaboratifs']
    df_features = df[features].copy()

    # Entrée utilisateur
    target_student = df[df['Nom'] == nom_etudiant]
    if target_student.empty:
        return [], []

    input_vector = target_student[features].values

    # KNN
    knn = NearestNeighbors(n_neighbors=top_n + 1, metric='euclidean')
    knn.fit(df_features)
    distances, indices = knn.kneighbors(input_vector)

    result_df = df.iloc[indices[0][1:]].copy()
    result_df['Distance'] = distances[0][1:]

    return result_df.to_dict(orient='records'), features
