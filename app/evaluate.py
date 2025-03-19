import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from app.model import RecommenderSystem

def evaluate_system():
    recommender = RecommenderSystem("data/dataset_etudiants.csv")
    test_profiles = [
        {"numeric": [5, 30], "groupes": ["Club Robotique"], "competences": ["IA"], "interets": ["Musique"]},
        {"numeric": [8, 50], "groupes": ["Groupe IA"], "competences": ["Blockchain"], "interets": ["Jeux vidéo"]}
    ]
    
    actual_ratings = []  # Hypothétiques scores réels d'affinité
    predicted_ratings = []
    
    for i, profile in enumerate(test_profiles):
        recommendations = recommender.recommander_etudiants(profile)
        print(f"Profil {i+1}: Recommandations")
        print(recommendations[['ID_Étudiant', 'Nom']])
        print("-"*40)
        
        # Simuler des scores d'affinité (hypothétiques)
        actual_ratings.extend([1] * len(recommendations))  # Supposons que toutes les recommandations sont bonnes
        predicted_ratings.extend(np.random.uniform(0.5, 1, len(recommendations)))  # Simulons des prédictions
    
    # Calculer RMSE et MAE
    rmse = np.sqrt(mean_squared_error(actual_ratings, predicted_ratings))
    mae = mean_absolute_error(actual_ratings, predicted_ratings)
    
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")

if __name__ == "__main__":
    evaluate_system()
