import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
import pickle

# Définir les chemins absolus spécifiques
BASE_DIR = r"C:\Users\User\educational_recommendation"
DATA_DIR = r"C:\Users\User\educational_recommendation\data"
MODELS_DIR = r"C:\Users\User\educational_recommendation\models"
CSV_PATH = r"C:\Users\User\educational_recommendation\data\dataset_etudiants.csv"

def preprocess_data(file_path):
    # Charger le dataset
    df = pd.read_csv(file_path)

    # Convertir les colonnes de listes (str) en listes Python
    list_columns = ['Coéquipiers', 'Communautés', 'Compétences', 'Centres_d\'Intérêt']
    for col in list_columns:
        df[col] = df[col].apply(lambda x: eval(x) if isinstance(x, str) else x)

    # Encoder les colonnes catégoriques (listes) avec MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    encoded_data = []
    for col in list_columns:
        encoded = mlb.fit_transform(df[col])
        encoded_df = pd.DataFrame(encoded, columns=[f"{col}_{i}" for i in range(encoded.shape[1])])
        encoded_data.append(encoded_df)

    # Combiner les données encodées
    encoded_df = pd.concat(encoded_data, axis=1)

    # Normaliser la colonne numérique (Nombre_Interactions et Travaux_Collaboratifs)
    scaler = MinMaxScaler()
    df['Nombre_Interactions'] = scaler.fit_transform(df[['Nombre_Interactions']])
    df['Travaux_Collaboratifs'] = scaler.fit_transform(df[['Travaux_Collaboratifs']])

    # Combiner avec les colonnes numériques
    X = pd.concat([encoded_df, df['Nombre_Interactions'], df['Travaux_Collaboratifs']], axis=1)

    return df, mlb, X

def build_autoencoder(input_dim):
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(128, activation='relu')(input_layer)
    encoded = Dense(64, activation='relu')(encoded)
    encoded = Dense(32, activation='relu')(encoded)
    
    decoded = Dense(64, activation='relu')(encoded)
    decoded = Dense(128, activation='relu')(decoded)
    decoded = Dense(input_dim, activation='sigmoid')(decoded)

    autoencoder = Model(input_layer, decoded)
    encoder = Model(input_layer, encoded)

    autoencoder.compile(optimizer='adam', loss='mse')
    return autoencoder, encoder

# Prétraitement des données
df, mlb, X_scaled = preprocess_data(CSV_PATH)

# Construire et entraîner l'autoencodeur
input_dim = X_scaled.shape[1]
autoencoder, encoder = build_autoencoder(input_dim)
autoencoder.fit(X_scaled, X_scaled, epochs=50, batch_size=32, shuffle=True, verbose=1)

# Sauvegarder les modèles et les embeddings
AUTOENCODER_PATH = r"C:\Users\User\educational_recommendation\models\autoencoder.h5"
ENCODER_PATH = r"C:\Users\User\educational_recommendation\models\encoder.h5"
EMBEDDINGS_PATH = r"C:\Users\User\educational_recommendation\models\student_embeddings.pkl"

autoencoder.save(AUTOENCODER_PATH)
encoder.save(ENCODER_PATH)

# Générer les embeddings pour chaque étudiant
embeddings = encoder.predict(X_scaled)

# Sauvegarder les embeddings avec les ID_Étudiant
embeddings_df = pd.DataFrame(embeddings, index=df['ID_Étudiant'])
with open(EMBEDDINGS_PATH, 'wb') as f:
    pickle.dump(embeddings_df, f)

# Sauvegarder le MultiLabelBinarizer pour une utilisation future
with open(r"C:\Users\User\educational_recommendation\models\mlb.pkl", 'wb') as f:
    pickle.dump(mlb, f)

print("Entraînement terminé. Modèles et embeddings sauvegardés.")