# model.py
import pickle
import numpy as np
from surprise import SVD
from sklearn.preprocessing import MultiLabelBinarizer

class RecommenderSystem:
    def __init__(self):
        self.model_data = None
        self.mlb_competences = None
        self.mlb_interets = None
        self.mlb_communautes = None
        self.student_profiles = None
        self.svd = None

    def load_data_and_model(self, model_path):
        # Chargement du modèle et des données
        with open(model_path, "rb") as f:
            self.model_data = pickle.load(f)

        # Chargement des éléments du modèle
        self.mlb_competences = self.model_data["mlb_competences"]
        self.mlb_interets = self.model_data["mlb_interets"]
        self.mlb_communautes = self.model_data["mlb_communautes"]
        self.student_profiles = self.model_data["student_profiles"]
        self.svd = self.model_data["svd"]  # Chargement du modèle SVD

    def get_recommendations(self, student_id):
        # Exemple d'algorithme de recommandation basé sur la similarité
        student_profile = self.student_profiles[student_id]
        similarities = np.dot(self.student_profiles, student_profile)  # Similarité avec tous les autres étudiants
        recommendations = np.argsort(similarities)[-5:]  # Top 5 recommandations
        return recommendations

# Exemple d'utilisation
recommender = RecommenderSystem()
recommender.load_data_and_model('app/models/modele_recommandation.pkl')
print(recommender.get_recommendations(0))  # Recommandations pour l'étudiant avec l'ID 0
