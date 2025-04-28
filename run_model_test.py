from app.model import train_and_save_model, load_model, make_prediction
import pandas as pd
import os

# Charger les données
data_path = os.path.join("data", "dataset_etudiants.csv")
df = pd.read_csv(data_path)

# Nettoyer les données si nécessaire (on prend un échantillon d'étudiant)
sample_input = df.dropna().iloc[0].drop("student_id").values.tolist()

# Étape 1 : entraîner et sauvegarder le modèle
train_and_save_model()

# Étape 2 : charger le modèle
model = load_model()

# Étape 3 : prédire à partir d'un exemple d'entrée
prediction = make_prediction(sample_input)

print("Prédiction :", prediction)
