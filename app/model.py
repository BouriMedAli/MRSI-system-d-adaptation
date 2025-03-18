import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.neighbors import NearestNeighbors
from app.utils import preprocess_data

class RecommenderSystem:
    def __init__(self, data_path, k_neighbors=5):
        self.df = pd.read_csv(data_path)
        self.k_neighbors = k_neighbors
        self.features_scaled, self.encoders, self.scaler = preprocess_data(self.df)
        self._train_knn()
    
    def _train_knn(self):
        self.knn_model = NearestNeighbors(n_neighbors=self.k_neighbors, metric='euclidean')
        self.knn_model.fit(self.features_scaled)
    
    def recommander_etudiants(self, profil):
        profil_vecteur = preprocess_data(profil, self.encoders, self.scaler, is_query=True)
        distances, indices = self.knn_model.kneighbors(profil_vecteur)
        return self.df.iloc[indices.flatten()]
