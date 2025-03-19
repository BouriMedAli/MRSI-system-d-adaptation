import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
from app.model import RecommandeurKNN

def charger_donnees(fichier_test):
    """Charge les données de test"""
    return pd.read_csv(fichier_test)

def calculer_rmse_mae(recommendations, recommendations_correctes):
    """Calculer RMSE et MAE"""
    # RMSE (Root Mean Squared Error) : Mesure de l'écart quadratique moyen
    rmse = sqrt(mean_squared_error(recommendations, recommendations_correctes))

    # MAE (Mean Absolute Error) : Mesure de l'erreur absolue moyenne
    mae = mean_absolute_error(recommendations, recommendations_correctes)

    return rmse, mae

def evaluer_model(fichier_donnees, fichier_test):
    """Évaluer le modèle avec RMSE et MAE"""
    # Charger les données de test
    test_data = charger_donnees(fichier_test)

    # Initialiser le modèle
    recommandeur = RecommandeurKNN(fichier_donnees)

    # Stocker les résultats des recommandations du modèle
    recommendations_predites = []

    # Comparer les recommandations pour chaque étudiant du fichier test
    for index, row in test_data.iterrows():
        # Extraire les données pour un étudiant
        data = row.drop('recommandations_correctes')  # Supprimer la colonne des recommandations correctes
        recommendations_correctes = eval(row['recommandations_correctes'])  # Convertir en liste les recommandations correctes
        
        # Obtenir les recommandations du modèle pour cet étudiant
        recommendations = recommandeur.recommander(data.to_dict())

        # Stocker les ID des étudiants recommandés par le modèle
        recommended_ids = [rec['ID_Étudiant'] for rec in recommendations]
        
        # Calculer les métriques RMSE et MAE en fonction de l'ordre de recommandation
        rmse, mae = calculer_rmse_mae(recommended_ids, recommendations_correctes)
        recommendations_predites.append({
            'ID_Étudiant': row['ID_Étudiant'],
            'RMSE': rmse,
            'MAE': mae
        })

    # Afficher les résultats
    df_results = pd.DataFrame(recommendations_predites)
    print(df_results)
    return df_results

if __name__ == '__main__':
    # Nom du fichier de données (train) et du fichier de test
    fichier_donnees = 'data/dataset_etudiants.csv'
    fichier_test = 'data/test_data.csv'
    
    # Évaluer le modèle
    evaluer_model(fichier_donnees, fichier_test)
