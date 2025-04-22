import pandas as pd
import numpy as np
import pickle
from surprise import Dataset, Reader, KNNBasic, accuracy
from surprise.model_selection import train_test_split, cross_validate
import os
import ast

print("Starting model training with KNN algorithm...")

# Create Dataset directory if it doesn't exist
os.makedirs("Dataset", exist_ok=True)

# Define the data path
data_path = os.path.join("Dataset", "dataset_etudiants.csv")
print(f"Looking for dataset at {data_path}")

# Check if the dataset file exists, if not, create it from the provided data
if not os.path.exists(data_path):
    print(f"Dataset not found at {data_path}. Creating it from the provided data...")
    
    # This is the data from the document
    data = pd.DataFrame({
        'ID_Étudiant': list(range(1, 51)),
        'Nom': [f'Etudiant_{i}' for i in range(1, 51)],
        'Travaux_Collaboratifs': [8, 5, 10, 9, 7, 5, 5, 2, 9, 5, 2, 8, 1, 7, 5, 5, 4, 7, 10, 5, 2, 7, 2, 8, 6, 3, 2, 4, 3, 1, 2, 3, 10, 2, 1, 4, 9, 4, 2, 5, 9, 8, 9, 9, 9, 4, 1, 7, 1, 4],
        'Coéquipiers': ["[49, 36, 30]", "[16, 5]", "[22, 9, 41, 34]", "[36]", "[10]", "[47, 35, 30]", "[12, 35, 20, 43, 17]", "[19, 33, 24]", "[3, 37, 28, 23, 43]", "[43, 14, 25]", "[33, 46, 14, 37]", "[8, 26, 43]", "[41, 42, 47, 31, 12]", "[29, 28, 47, 50, 42]", "[9, 45, 29, 41, 16]", "[3]", "[7]", "[19, 10, 2, 41]", "[9, 27]", "[39, 10, 41, 6, 49]", "[50, 27, 44]", "[18, 14, 6, 30, 24]", "[32, 49]", "[41]", "[19, 8, 50, 49]", "[48, 49, 14, 9]", "[40, 43, 17]", "[10, 40, 3, 42, 9]", "[50, 42, 27, 21]", "[25]", "[17, 29, 24, 34]", "[31]", "[25]", "[44, 15, 28, 17]", "[34]", "[7, 44, 1, 30]", "[27]", "[14, 45, 12, 28, 2]", "[43]", "[15, 26, 9]", "[36, 17, 27]", "[20, 35, 4]", "[14]", "[46, 19, 43, 5]", "[31, 44, 46, 39, 25]", "[4, 47, 49]", "[46, 26, 31, 16]", "[20, 29, 40]", "[20, 37, 17]", "[36, 6, 18]"],
        'Communautés': ["['Club Robotique', 'Groupe IA']", "['Club Entrepreneurs', 'Groupe IA']", "['Groupe IA', 'Club Robotique']", "['Association Écologie']", "['Association Écologie', 'Club Entrepreneurs']", "['Association Écologie']", "['Club Data Science']", "['Club Robotique']", "['Club Data Science', 'Association Écologie']", "['Association Écologie']", "['Club Data Science']", "['Club Data Science', 'Association Écologie']", "['Club Entrepreneurs']", "['Club Data Science']", "['Association Écologie', 'Groupe IA']", "['Association Écologie']", "['Groupe IA', 'Club Robotique']", "['Club Entrepreneurs']", "['Club Data Science']", "['Club Entrepreneurs']", "['Club Robotique', 'Groupe IA']", "['Groupe IA', 'Club Robotique']", "['Association Écologie']", "['Club Robotique', 'Groupe IA']", "['Club Robotique', 'Club Entrepreneurs']", "['Club Robotique', 'Groupe IA']", "['Club Data Science', 'Groupe IA']", "['Groupe IA']", "['Club Data Science']", "['Club Robotique', 'Club Data Science']", "['Association Écologie', 'Club Entrepreneurs']", "['Club Data Science', 'Club Robotique']", "['Association Écologie', 'Club Robotique']", "['Club Robotique', 'Club Entrepreneurs']", "['Club Entrepreneurs']", "['Club Robotique']", "['Association Écologie', 'Groupe IA']", "['Club Robotique']", "['Association Écologie']", "['Club Entrepreneurs', 'Association Écologie']", "['Association Écologie', 'Club Entrepreneurs']", "['Club Entrepreneurs', 'Groupe IA']", "['Groupe IA', 'Club Data Science']", "['Club Robotique', 'Club Entrepreneurs']", "['Club Data Science']", "['Club Entrepreneurs', 'Groupe IA']", "['Association Écologie']", "['Club Data Science', 'Club Robotique']", "['Groupe IA', 'Club Robotique']", "['Association Écologie', 'Groupe IA']"],
        'Nombre_Interactions': [91, 63, 23, 23, 64, 9, 29, 82, 8, 72, 88, 39, 89, 71, 83, 7, 80, 45, 48, 81, 100, 38, 34, 73, 89, 68, 64, 70, 98, 93, 16, 88, 26, 38, 90, 68, 87, 20, 32, 53, 64, 35, 57, 56, 89, 68, 58, 68, 32, 11],
        'Compétences': ["['Blockchain', 'IA', 'Data Science']", "['IA', 'Blockchain', 'Python']", "['Design', 'Python', 'Blockchain']", "['Blockchain', 'Data Science']", "['Électronique', 'Design']", "['Blockchain']", "['Blockchain', 'Marketing', 'Électronique']", "['Électronique', 'Marketing']", "['Blockchain', 'Marketing', 'IA']", "['Design', 'IA']", "['IA', 'Électronique', 'Data Science']", "['Design', 'Électronique']", "['IA', 'Électronique']", "['IA']", "['Python']", "['Blockchain']", "['Électronique']", "['Blockchain', 'Électronique', 'Design']", "['Marketing', 'Blockchain', 'Électronique']", "['IA', 'Blockchain']", "['Data Science', 'Électronique', 'Marketing']", "['IA', 'Blockchain']", "['Blockchain']", "['Blockchain', 'Design', 'Marketing']", "['IA', 'Design', 'Python']", "['Python', 'Design']", "['Design']", "['Data Science']", "['Marketing', 'Data Science', 'IA']", "['Blockchain']", "['Python', 'Blockchain', 'Marketing']", "['Blockchain', 'Design']", "['Blockchain']", "['Marketing', 'Data Science', 'Blockchain']", "['Python']", "['Data Science']", "['IA']", "['Data Science', 'Python']", "['Marketing', 'Data Science']", "['IA']", "['Blockchain']", "['Électronique']", "['Design', 'Data Science']", "['Data Science']", "['Design']", "['IA']", "['Blockchain', 'Marketing', 'Data Science']", "['Data Science', 'Blockchain']", "['Data Science', 'Blockchain']", "['IA', 'Blockchain', 'Data Science']"],
        'Centres_d\'Intérêt': ["['Jeux vidéo', 'Musique']", "['Musique']", "['Jeux vidéo', 'Robotique']", "['Robotique']", "['Musique']", "['Entrepreneuriat', 'Musique']", "['Écologie', 'Jeux vidéo']", "['Écologie']", "['Jeux vidéo', 'Écologie', 'Robotique']", "['Jeux vidéo']", "['Musique']", "['Musique']", "['Robotique']", "['Hackathon', 'Entrepreneuriat']", "['Musique']", "['Robotique', 'Entrepreneuriat']", "['Écologie', 'Hackathon', 'Robotique']", "['Jeux vidéo', 'Musique']", "['Jeux vidéo']", "['Musique', 'Entrepreneuriat', 'Écologie']", "['Robotique']", "['Musique', 'Hackathon', 'Entrepreneuriat']", "['Hackathon', 'Entrepreneuriat']", "['Jeux vidéo']", "['Robotique', 'Hackathon']", "['Musique']", "['Entrepreneuriat']", "['Écologie', 'Musique']", "['Écologie', 'Jeux vidéo']", "['Musique', 'Robotique']", "['Hackathon', 'Robotique', 'Écologie']", "['Musique', 'Hackathon']", "['Jeux vidéo', 'Hackathon']", "['Musique', 'Robotique']", "['Robotique', 'Musique', 'Écologie']", "['Entrepreneuriat', 'Musique']", "['Jeux vidéo', 'Robotique']", "['Hackathon', 'Entrepreneuriat']", "['Hackathon', 'Jeux vidéo']", "['Entrepreneuriat', 'Musique', 'Hackathon']", "['Musique', 'Entrepreneuriat', 'Robotique']", "['Musique']", "['Entrepreneuriat']", "['Jeux vidéo', 'Entrepreneuriat', 'Robotique']", "['Musique', 'Jeux vidéo', 'Entrepreneuriat']", "['Hackathon', 'Écologie']", "['Écologie', 'Robotique']", "['Jeux vidéo', 'Robotique']", "['Jeux vidéo', 'Hackathon', 'Écologie']", "['Hackathon']"]
    })
    
    # Save the dataset to CSV
    data.to_csv(data_path, index=False)
    print(f"Created dataset file at {data_path}")

# Now try to load the dataset
try:
    data = pd.read_csv(data_path)
    print(f"Successfully loaded dataset with {len(data)} students")
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit(1)

# Convert string representations of lists to actual Python lists
print("Converting string columns to Python lists...")
try:
    data['Coéquipiers'] = data['Coéquipiers'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    data['Communautés'] = data['Communautés'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    data['Compétences'] = data['Compétences'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    data['Centres_d\'Intérêt'] = data['Centres_d\'Intérêt'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    print("Dataset preprocessed successfully")
except Exception as e:
    print(f"Error preprocessing dataset: {e}. Attempting to fix the formatting...")
    try:
        # Manual fixing for common format issues
        for col in ['Coéquipiers', 'Communautés', 'Compétences', 'Centres_d\'Intérêt']:
            # Handle any potential formatting issues
            data[col] = data[col].apply(lambda x: 
                ast.literal_eval(x) if isinstance(x, str) else 
                ([] if pd.isna(x) else x))
        print("Dataset fixed and preprocessed successfully")
    except Exception as e:
        print(f"Failed to fix dataset: {e}")
        exit(1)

# Extract all unique communities, skills, and interests for cross-validation
print("Extracting unique attributes...")
all_communities = set()
all_skills = set()
all_interests = set()

for _, row in data.iterrows():
    all_communities.update(row['Communautés'])
    all_skills.update(row['Compétences'])
    all_interests.update(row['Centres_d\'Intérêt'])

print(f"Found {len(all_communities)} unique communities, {len(all_skills)} unique skills, and {len(all_interests)} unique interests")

# Create implicit ratings for collaborative filtering with weighted ratings
print("Creating implicit ratings from student profiles...")
ratings_data = []

# Add some negative samples for better evaluation
for idx, row in data.iterrows():
    student_id = row['ID_Étudiant']
    
    # Add community affiliations as implicit ratings
    for community in row['Communautés']:
        # Positive rating with weight based on interaction count
        weight = min(1.0, 0.5 + row['Nombre_Interactions'] / 200)
        ratings_data.append({'user_id': student_id, 'item_id': f"comm_{community}", 'rating': weight})
    
    # Add negative samples for communities
    other_communities = all_communities - set(row['Communautés'])
    for community in list(other_communities)[:2]:  # Add 2 negative samples
        ratings_data.append({'user_id': student_id, 'item_id': f"comm_{community}", 'rating': 0.1})
    
    # Add skills as implicit ratings
    for skill in row['Compétences']:
        # Weight by travaux_collaboratifs score
        weight = min(1.0, 0.4 + row['Travaux_Collaboratifs'] / 20)
        ratings_data.append({'user_id': student_id, 'item_id': f"skill_{skill}", 'rating': weight})
    
    # Add negative samples for skills
    other_skills = all_skills - set(row['Compétences'])
    for skill in list(other_skills)[:2]:  # Add 2 negative samples
        ratings_data.append({'user_id': student_id, 'item_id': f"skill_{skill}", 'rating': 0.2})
    
    # Add interests as implicit ratings
    for interest in row['Centres_d\'Intérêt']:
        ratings_data.append({'user_id': student_id, 'item_id': f"int_{interest}", 'rating': 0.9})
    
    # Add negative samples for interests
    other_interests = all_interests - set(row['Centres_d\'Intérêt'])
    for interest in list(other_interests)[:2]:  # Add 2 negative samples
        ratings_data.append({'user_id': student_id, 'item_id': f"int_{interest}", 'rating': 0.3})

ratings_df = pd.DataFrame(ratings_data)
print(f"Created {len(ratings_df)} implicit ratings from student profiles")

# Define the reader for Surprise
reader = Reader(rating_scale=(0, 1))
dataset = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)

# Split data into training and test sets (80% train, 20% test)
print("Splitting data into training and test sets...")
trainset, testset = train_test_split(dataset, test_size=0.2, random_state=42)
print(f"Data split into training set ({len(trainset.build_testset())}) and test set ({len(testset)})")

# Train the KNNBasic model
print("Training KNN model...")
sim_options = {
    'name': 'cosine',  # Use cosine similarity
    'user_based': True,  # User-based collaborative filtering
    'min_support': 3,   # Minimum number of common items
}
model = KNNBasic(k=10, sim_options=sim_options)
model.fit(trainset)
print("KNN model training complete")

# Evaluate the model's accuracy on the test set
print("Evaluating model accuracy on the test set...")
predictions = model.test(testset)
rmse = accuracy.rmse(predictions)
mae = accuracy.mae(predictions)
print(f"Model accuracy on test set: RMSE = {rmse:.4f}, MAE = {mae:.4f}")

# Perform cross-validation to avoid overfitting
print("Performing cross-validation...")
cross_validation_results = cross_validate(
    model, dataset, measures=['RMSE', 'MAE'], cv=5, verbose=True
)
print("Cross-validation results:")
print(cross_validation_results)

# Function to calculate precision and recall for recommendations
def precision_recall_at_k(predictions, k=5, threshold=0.5):
    user_est_true = {}
    for uid, _, true_r, est, _ in predictions:
        if uid not in user_est_true:
            user_est_true[uid] = []
        user_est_true[uid].append((est, true_r))
    
    precisions = {}
    recalls = {}
    for uid, user_ratings in user_est_true.items():
        user_ratings.sort(key=lambda x: x[0], reverse=True)
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
        n_rec_k = min(k, len(user_ratings))
        n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold)) 
                              for (est, true_r) in user_ratings[:n_rec_k])
        
        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0
        recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 0
    
    return precisions, recalls

# Calculate precision and recall
precisions, recalls = precision_recall_at_k(predictions, k=5, threshold=0.5)

# Average precision and recall
avg_precision = sum(prec for prec in precisions.values()) / len(precisions) if precisions else 0
avg_recall = sum(rec for rec in recalls.values()) / len(recalls) if recalls else 0
print(f"Recommendation metrics: Precision@5 = {avg_precision:.4f}, Recall@5 = {avg_recall:.4f}")

# Function to recommend items (communities, skills, interests) for a given student
def recommend_items(model, student_id, all_items, rated_items, top_n=5):
    """Recommend top-N items for a student based on the trained model."""
    print(f"\nGenerating recommendations for Student {student_id}...")
    recommendations = []
    
    # Predict ratings for all unrated items
    for item in all_items:
        if item not in rated_items:
            try:
                predicted_rating = model.predict(student_id, item).est
                recommendations.append((item, predicted_rating))
            except Exception as e:
                print(f"Error predicting rating for {student_id}, {item}: {e}")
                continue
    
    # Sort recommendations by predicted rating
    recommendations.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top-N recommendations
    top_recommendations = recommendations[:top_n]
    print(f"Top {top_n} recommendations for Student {student_id}:")
    for item, score in top_recommendations:
        print(f"  - {item} (Predicted Rating: {score:.4f})")
    
    return top_recommendations

# Get all unique items (communities, skills, interests)
all_items = set(ratings_df['item_id'])

# Example: Recommend items for a specific student (e.g., Student 1)
student_id = 1
try:
    rated_items = ratings_df[ratings_df['user_id'] == student_id]['item_id'].unique()
    recommend_items(model, student_id, all_items, rated_items, top_n=5)
except Exception as e:
    print(f"Error generating recommendations for student {student_id}: {e}")

# Add student feature vectors for cold-start recommendations
print("\nCreating feature vectors for students...")
student_features = {}

for idx, row in data.iterrows():
    student_id = row['ID_Étudiant']
    
    # Create a feature vector for the student
    feature_vector = {
        'travaux_collaboratifs': row['Travaux_Collaboratifs'] / 10.0,  # Normalize to [0,1]
        'nombre_interactions': row['Nombre_Interactions'] / 100.0,  # Normalize to [0,1]
        'communautes': {comm: 1.0 for comm in row['Communautés']},
        'competences': {skill: 1.0 for skill in row['Compétences']},
        'interets': {interest: 1.0 for interest in row['Centres_d\'Intérêt']}
    }
    
    student_features[student_id] = feature_vector

# Save the model, data, and feature vectors for later use
print("\nSaving model and data...")
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('data.pkl', 'wb') as f:
    pickle.dump(data, f)

with open('student_features.pkl', 'wb') as f:
    pickle.dump(student_features, f)

# Save metadata about all possible categories
metadata = {
    'all_communities': list(all_communities),
    'all_skills': list(all_skills),
    'all_interests': list(all_interests)
}

with open('metadata.pkl', 'wb') as f:
    pickle.dump(metadata, f)

# Save accuracy metrics for reference
accuracy_metrics = {
    'rmse': rmse,
    'mae': mae,
    'precision@5': avg_precision,
    'recall@5': avg_recall
}

with open('accuracy_metrics.pkl', 'wb') as f:
    pickle.dump(accuracy_metrics, f)

# Verify the files were created and show their sizes
try:
    model_size = os.path.getsize('model.pkl') / 1024  # KB
    data_size = os.path.getsize('data.pkl') / 1024  # KB
    metrics_size = os.path.getsize('accuracy_metrics.pkl') / 1024  # KB
    features_size = os.path.getsize('student_features.pkl') / 1024  # KB
    metadata_size = os.path.getsize('metadata.pkl') / 1024  # KB

    print(f"\nModel saved: model.pkl ({model_size:.2f} KB)")
    print(f"Data saved: data.pkl ({data_size:.2f} KB)")
    print(f"Student features saved: student_features.pkl ({features_size:.2f} KB)")
    print(f"Metadata saved: metadata.pkl ({metadata_size:.2f} KB)")
    print(f"Accuracy metrics saved: accuracy_metrics.pkl ({metrics_size:.2f} KB)")
except Exception as e:
    print(f"Error checking file sizes: {e}")

print("Model training and evaluation complete!")