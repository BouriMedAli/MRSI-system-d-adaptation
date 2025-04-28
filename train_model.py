import pandas as pd
import os
from surprise import Dataset, Reader, KNNWithZScore
from surprise.model_selection import train_test_split, GridSearchCV
from surprise.accuracy import rmse, mae
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import pickle

# Chemin du dataset
data_path = os.path.join("Dataset", "dataset_etudiants.csv")
df = pd.read_csv(data_path)

# Normaliser Travaux_Collaboratifs et Nombre_Interactions entre 1 et 5
df['Collab_Score'] = 1 + 4 * (df['Travaux_Collaboratifs'] - df['Travaux_Collaboratifs'].min()) / (df['Travaux_Collaboratifs'].max() - df['Travaux_Collaboratifs'].min())
df['Interaction_Score'] = 1 + 4 * (df['Nombre_Interactions'] - df['Nombre_Interactions'].min()) / (df['Nombre_Interactions'].max() - df['Nombre_Interactions'].min())

# Créer une matrice utilisateur-élément (sans pondération)
ratings = []
for index, row in df.iterrows():
    student_id = row['ID_Étudiant']
    
    # Coéquipiers : utiliser Collab_Score directement
    teammates = eval(row['Coéquipiers'])
    collab_score = row['Collab_Score']
    for teammate_id in teammates:
        teammate_row = df[df['ID_Étudiant'] == teammate_id]
        if not teammate_row.empty:
            ratings.append({'user_id': student_id, 'item_id': f"student_{teammate_id}", 'rating': collab_score})
    
    # Compétences : utiliser Interaction_Score directement
    skills = eval(row['Compétences'])
    interaction_score = row['Interaction_Score']
    for skill in skills:
        ratings.append({'user_id': student_id, 'item_id': f"skill_{skill}", 'rating': interaction_score})
    
    # Centres d'Intérêt : utiliser Interaction_Score directement
    interests = eval(row['Centres_d\'Intérêt'])
    for interest in interests:
        ratings.append({'user_id': student_id, 'item_id': f"interest_{interest}", 'rating': interaction_score})

# Vérifier que ratings n'est pas vide
if not ratings:
    raise ValueError("Aucune note générée. Vérifiez le dataset.")

# Créer un DataFrame pour Surprise
ratings_df = pd.DataFrame(ratings)

# Analyser la distribution des scores
print("Distribution des scores dans ratings_df :")
print(ratings_df['rating'].describe())

# Vérifier les coéquipiers invalides
for index, row in df.iterrows():
    teammates = eval(row['Coéquipiers'])
    for teammate_id in teammates:
        if teammate_id not in df['ID_Étudiant'].values:
            print(f"ID coéquipier invalide : {teammate_id} pour étudiant {row['ID_Étudiant']}")

# Définir le format des données pour Surprise
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)

# Diviser les données en ensemble d'entraînement et de test
trainset, testset = train_test_split(data, test_size=0.3, random_state=42)

# Optimisation des hyperparamètres pour KNNWithZScore avec GridSearchCV
param_grid = {
    'k': [3, 5, 7, 10, 15, 20],  # Plus de valeurs petites pour k
    'sim_options': {
        'name': ['cosine', 'pearson', 'pearson_baseline'],
        'user_based': [True, False],
        'min_support': [1, 2, 3],
        'shrinkage': [0, 50, 100] if 'pearson_baseline' in ['cosine', 'pearson', 'pearson_baseline'] else [0]
    }
}
gs = GridSearchCV(KNNWithZScore, param_grid, measures=['rmse', 'mae'], cv=3)
gs.fit(data)

# Afficher les meilleurs paramètres
print("Meilleurs paramètres pour RMSE:", gs.best_params['rmse'])
print("Meilleur RMSE (validation croisée):", gs.best_score['rmse'])
print("Meilleurs paramètres pour MAE:", gs.best_params['mae'])
print("Meilleur MAE (validation croisée):", gs.best_score['mae'])

# Configurer l'algorithme KNNWithZScore avec les meilleurs paramètres
algo = KNNWithZScore(
    k=gs.best_params['rmse']['k'],
    sim_options=gs.best_params['rmse']['sim_options'],
    verbose=True
)

# Entraîner le modèle
algo.fit(trainset)

# Faire des prédictions sur l'ensemble de test
predictions = algo.test(testset)

# Calculer RMSE et MAE
rmse_value = rmse(predictions)
mae_value = mae(predictions)

# Normaliser les métriques par l'échelle maximale (4 = 5 - 1)
normalized_rmse = rmse_value / 4
normalized_mae = mae_value / 4

print(f"RMSE: {rmse_value:.4f}")
print(f"Normalized RMSE: {normalized_rmse:.4f}")
print(f"MAE: {mae_value:.4f}")
print(f"Normalized MAE: {normalized_mae:.4f}")

# Sauvegarder le modèle entraîné
joblib.dump(algo, 'model.pkl')

# Créer des vecteurs TF-IDF pour Compétences et Centres_d'Intérêt
df['Compétences_str'] = df['Compétences'].apply(lambda x: ' '.join(eval(x)))
df['Centres_d\'Intérêt_str'] = df['Centres_d\'Intérêt'].apply(lambda x: ' '.join(eval(x)))

tfidf_skills = TfidfVectorizer()
skills_matrix = tfidf_skills.fit_transform(df['Compétences_str'])
tfidf_interests = TfidfVectorizer()
interests_matrix = tfidf_interests.fit_transform(df['Centres_d\'Intérêt_str'])

# Sauvegarder les matrices et vectorizers
with open('tfidf_skills.pkl', 'wb') as f:
    pickle.dump(tfidf_skills, f)
with open('tfidf_interests.pkl', 'wb') as f:
    pickle.dump(tfidf_interests, f)
with open('skills_matrix.pkl', 'wb') as f:
    pickle.dump(skills_matrix, f)
with open('interests_matrix.pkl', 'wb') as f:
    pickle.dump(interests_matrix, f)

# Sauvegarder le DataFrame pour référence
df.to_pickle('students_df.pkl')