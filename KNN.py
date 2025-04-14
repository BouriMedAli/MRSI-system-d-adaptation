import pandas as pd
import numpy as np
import pickle
from surprise import Dataset, Reader, KNNBasic
import os

print("Starting model training with KNN algorithm...")

# Load and preprocess your dataset
data_path = os.path.join("Dataset", "dataset_etudiants.csv")
print(f"Loading dataset from {data_path}")

try:
    data = pd.read_csv(data_path)
    print(f"Successfully loaded dataset with {len(data)} students")
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit(1)

# Convert string representations of lists to actual Python lists
data['Coéquipiers'] = data['Coéquipiers'].apply(lambda x: eval(x) if isinstance(x, str) else x)
data['Communautés'] = data['Communautés'].apply(lambda x: eval(x) if isinstance(x, str) else x)
data['Compétences'] = data['Compétences'].apply(lambda x: eval(x) if isinstance(x, str) else x)
data['Centres_d\'Intérêt'] = data['Centres_d\'Intérêt'].apply(lambda x: eval(x) if isinstance(x, str) else x)

print("Dataset preprocessed successfully")

# Create a "ratings" dataset for KNN collaborative filtering
ratings_data = []

for idx, row in data.iterrows():
    student_id = row['ID_Étudiant']
    
    # Add community affiliations as implicit ratings
    for community in row['Communautés']:
        ratings_data.append({'user_id': student_id, 'item_id': f"comm_{community}", 'rating': 1})
    
    # Add skills as implicit ratings
    for skill in row['Compétences']:
        ratings_data.append({'user_id': student_id, 'item_id': f"skill_{skill}", 'rating': 1})
    
    # Add interests as implicit ratings
    for interest in row['Centres_d\'Intérêt']:
        ratings_data.append({'user_id': student_id, 'item_id': f"int_{interest}", 'rating': 1})

ratings_df = pd.DataFrame(ratings_data)
print(f"Created {len(ratings_df)} implicit ratings from student profiles")

# Define the reader for surprise
reader = Reader(rating_scale=(0, 1))
dataset = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)

# Build the full trainset
trainset = dataset.build_full_trainset()

# Train the KNNBasic model
print("Training KNN model...")
sim_options = {
    'name': 'cosine',  # Use cosine similarity
    'user_based': True  # User-based collaborative filtering
}
model = KNNBasic(k=5, sim_options=sim_options)
model.fit(trainset)
print("KNN model training complete")

# Save the model and data for later use
print("Saving model and data...")
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('data.pkl', 'wb') as f:
    pickle.dump(data, f)

print("Model and data saved successfully!")