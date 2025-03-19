import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np

class RecommandeurKNN:
    def __init__(self, fichier_donnees):  # Correction du nom __init__
        # Charger le dataset
        self.df = pd.read_csv(fichier_donnees)
        
        # Colonnes utilisées pour la recommandation
        self.features = ["Travaux_Collaboratifs", "Coéquipiers", "Communautés", "Nombre_Interactions", "Compétences", "Centres_d'Intérêt"]

        # Vérifier et corriger les types de données
        for col in self.features:
            self.df[col] = self.df[col].apply(self.convertir_en_nombre)

        # Initialiser et entraîner le modèle KNN
        self.knn = NearestNeighbors(n_neighbors=3, metric="euclidean")
        self.knn.fit(self.df[self.features])

    def convertir_en_nombre(self, valeur):
        """ Convertit une valeur en nombre (ex: transformer une liste en sa longueur). """
        if isinstance(valeur, list):  # Si c'est une liste, on prend sa taille
            return len(valeur)
        try:
            return float(valeur)  # Convertir en float si possible
        except:
            return 0  # Valeur par défaut si conversion impossible

    def recommander(self, donnees_utilisateur):
        # Convertir les données utilisateur en DataFrame
        user_df = pd.DataFrame([donnees_utilisateur])
        
        # Assurer la conversion en nombre
        for col in self.features:
            if col not in donnees_utilisateur:  # Si la clé est manquante
                donnees_utilisateur[col] = 0  # Attribuer une valeur par défaut (0)
            user_df[col] = user_df[col].apply(self.convertir_en_nombre)

        # Trouver les voisins les plus proches
        distances, indices = self.knn.kneighbors(user_df[self.features])

        # Renvoyer les recommandations
        recommandations = self.df.iloc[indices[0]][["ID_Étudiant", "Nom"]].to_dict(orient="records")
        return recommandations
