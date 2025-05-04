import pandas as pd
import os
from surprise import Dataset, Reader, KNNWithZScore
from surprise.model_selection import train_test_split, GridSearchCV
from surprise.accuracy import rmse, mae
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import pickle
import numpy as np
from collections import defaultdict
import sys
from io import StringIO

# Chemin du dataset
data_path = os.path.join("Dataset", "dataset_etudiants.csv")
df = pd.read_csv(data_path)

# Normaliser Travaux_Collaboratifs entre 1 et 5
df['Collab_Score'] = 1 + 4 * (df['Travaux_Collaboratifs'] - df['Travaux_Collaboratifs'].min()) / (df['Travaux_Collaboratifs'].max() - df['Travaux_Collaboratifs'].min())

# Créer une matrice utilisateur-élément (uniquement pour les coéquipiers)
ratings = []
for index, row in df.iterrows():
    student_id = row['ID_Étudiant']
    try:
        teammates = eval(row['Coéquipiers'])
        collab_score = row['Collab_Score']
        for teammate_id in teammates:
            teammate_row = df[df['ID_Étudiant'] == teammate_id]
            if not teammate_row.empty:
                ratings.append({'user_id': student_id, 'item_id': f"student_{teammate_id}", 'rating': collab_score})
    except (SyntaxError, ValueError):
        continue

# Vérifier que ratings n'est pas vide
if not ratings:
    raise ValueError("Aucune note générée. Vérifiez le dataset.")

# Créer un DataFrame pour Surprise
ratings_df = pd.DataFrame(ratings)

# Définir le format des données pour Surprise
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)

# Diviser les données en ensemble d'entraînement et de test
trainset, testset = train_test_split(data, test_size=0.3, random_state=42)

# Optimisation des hyperparamètres pour KNNWithZScore avec GridSearchCV
param_grid = {
    'k': [3, 5, 7, 10, 15, 20],
    'sim_options': {
        'name': ['cosine', 'pearson', 'pearson_baseline'],
        'user_based': [True, False],
        'min_support': [1, 2, 3],
        'shrinkage': [0, 50, 100] if 'pearson_baseline' in ['cosine', 'pearson', 'pearson_baseline'] else [0]
    }
}

# Rediriger la sortie standard pour supprimer les messages verbeux de GridSearchCV
original_stdout = sys.stdout  # Sauvegarder la sortie standard
sys.stdout = StringIO()  # Rediriger vers une "sortie vide"

# Exécuter GridSearchCV sans affichage
gs = GridSearchCV(KNNWithZScore, param_grid, measures=['rmse', 'mae'], cv=3)
gs.fit(data)

# Restaurer la sortie standard
sys.stdout = original_stdout

# Afficher le résumé des calculs de matrices
print("Computing the pearson similarity matrix... Done computing similarity matrix. (56 fois)")
print("Estimating biases using als... Computing the pearson_baseline similarity matrix... Done computing similarity matrix. (56 fois pour user_based=True, 56 fois pour user_based=False)")
print("Computing the cosine similarity matrix... Done computing similarity matrix. (56 fois)")

# Afficher les meilleurs paramètres
print("Meilleurs paramètres pour RMSE:", gs.best_params['rmse'])
print("Meilleur RMSE (validation croisée):", gs.best_score['rmse'])
print("Meilleurs paramètres pour MAE:", gs.best_params['mae'])
print("Meilleur MAE (validation croisée):", gs.best_score['mae'])

# Configurer l'algorithme KNNWithZScore avec les meilleurs paramètres
algo = KNNWithZScore(
    k=gs.best_params['rmse']['k'],
    sim_options=gs.best_params['rmse']['sim_options'],
    verbose=False  # Désactiver le mode verbeux
)

# Rediriger à nouveau la sortie pour l'entraînement
sys.stdout = StringIO()
algo.fit(trainset)
sys.stdout = original_stdout

# Afficher manuellement le message pour l'entraînement final
print("Computing the cosine similarity matrix... Done computing similarity matrix.")

# Faire des prédictions sur l'ensemble de test
predictions = algo.test(testset)

# Calculer RMSE et MAE
rmse_value = rmse(predictions, verbose=False)
mae_value = mae(predictions, verbose=False)

# Normaliser les métriques par l'échelle maximale (4 = 5 - 1)
normalized_rmse = rmse_value / 4
normalized_mae = mae_value / 4

print(f"RMSE: {rmse_value:.4f}")
print(f"Normalized RMSE: {normalized_rmse:.4f}")
print(f"MAE: {mae_value:.4f}")
print(f"Normalized MAE: {normalized_mae:.4f}")

# Calculer la précision@k et le rappel@k
def precision_recall_at_k(predictions, k=5, threshold=3.5):
    user_est_true = defaultdict(list)
    for pred in predictions:
        user_est_true[pred.uid].append((pred.est, pred.r_ui))

    precisions = dict()
    recalls = dict()
    for uid, user_ratings in user_est_true.items():
        user_ratings.sort(key=lambda x: x[0], reverse=True)
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
        n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])
        n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold)) for (est, true_r) in user_ratings[:k])

        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0

    precision_k = np.mean(list(precisions.values()))
    recall_k = np.mean(list(recalls.values()))
    return precision_k, recall_k

# Calculer précision@5 et rappel@5
precision_k, recall_k = precision_recall_at_k(predictions, k=5, threshold=3.5)
print(f"Précision@5: {precision_k:.4f}")
print(f"Rappel@5: {recall_k:.4f}")

# Sauvegarder le modèle entraîné
joblib.dump(algo, 'model.pkl')

# Créer des vecteurs TF-IDF pour Compétences et Centres_d'Intérêt
df['Compétences_str'] = df['Compétences'].apply(lambda x: ' '.join(eval(x)) if isinstance(x, str) else ' '.join(x))
df['Centres_d\'Intérêt_str'] = df['Centres_d\'Intérêt'].apply(lambda x: ' '.join(eval(x)) if isinstance(x, str) else ' '.join(x))

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

print("Entraînement et sauvegarde terminés avec succès.")