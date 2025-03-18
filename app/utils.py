import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler

def preprocess_data(data, encoders=None, scaler=None, is_query=False):
    """
    Prépare les données en encodant les labels et en normalisant les valeurs numériques.
    """
    if not is_query:
        # Convertir les colonnes de listes en vraies listes
        for col in ['Communautés', 'Compétences', "Centres_d'Intérêt"]:
            data[col] = data[col].apply(eval)
        
        # Encoder les valeurs catégoriques multi-labels
        encoders = {
            'Communautés': MultiLabelBinarizer(),
            'Compétences': MultiLabelBinarizer(),
            "Centres_d'Intérêt": MultiLabelBinarizer()
        }
        encoded_features = []
        for col, encoder in encoders.items():
            encoded = encoder.fit_transform(data[col])
            encoded_features.append(encoded)
        
        # Normaliser les caractéristiques numériques
        numeric_features = data[['Travaux_Collaboratifs', 'Nombre_Interactions']].values
        scaler = StandardScaler().fit(numeric_features)
        numeric_scaled = scaler.transform(numeric_features)
        
        # Combiner toutes les caractéristiques
        features = np.hstack([numeric_scaled] + encoded_features)
        return features, encoders, scaler
    
    else:
        # Encoder les données de requête
        encoded_features = [encoders[col].transform([data[col]]) for col in encoders]
        numeric_scaled = scaler.transform([data['numeric']])
        features = np.hstack([numeric_scaled] + encoded_features)
        return features
