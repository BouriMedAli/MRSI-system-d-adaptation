import pandas as pd
import numpy as np
import pickle
from surprise import Dataset, Reader, KNNBasic, accuracy
from surprise.model_selection import train_test_split, cross_validate
import os
import ast

print("Starting model training with KNN algorithm...")

# Ensure the dataset directory exists
os.makedirs("Dataset", exist_ok=True)

# Load and preprocess the dataset
data_path = os.path.join("Dataset", "dataset_etudiants.csv")
print(f"Loading dataset from {data_path}")

try:
    data = pd.read_csv(data_path)
    print(f"Successfully loaded dataset with {len(data)} students")
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit(1)

# Convert string representations of lists to actual Python lists
print("Converting string columns to Python lists...")
data['Coéquipiers'] = data['Coéquipiers'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
data['Communautés'] = data['Communautés'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
data['Compétences'] = data['Compétences'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
data['Centres_d\'Intérêt'] = data['Centres_d\'Intérêt'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

print("Dataset preprocessed successfully")

# Create implicit ratings for collaborative filtering
print("Creating implicit ratings from student profiles...")
ratings_data = []

for idx, row in data.iterrows():
    student_id = row['ID_Étudiant']
    
    # Add community affiliations as implicit ratings
    for community in row['Communautés']:
        ratings_data.append({'user_id': student_id, 'item_id': f"comm_{community}", 'rating': 1})
        print(f"Added rating: Student {student_id} → Community {community}")
    
    # Add skills as implicit ratings
    for skill in row['Compétences']:
        ratings_data.append({'user_id': student_id, 'item_id': f"skill_{skill}", 'rating': 1})
        print(f"Added rating: Student {student_id} → Skill {skill}")
    
    # Add interests as implicit ratings
    for interest in row['Centres_d\'Intérêt']:
        ratings_data.append({'user_id': student_id, 'item_id': f"int_{interest}", 'rating': 1})
        print(f"Added rating: Student {student_id} → Interest {interest}")

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
    'user_based': True  # User-based collaborative filtering
}
model = KNNBasic(k=5, sim_options=sim_options)
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
    """Return precision and recall at k metrics for each user"""
    print("Calculating precision and recall at k...")
    # Map the predictions to each user
    user_est_true = {}
    for uid, _, true_r, est, _ in predictions:
        if uid not in user_est_true:
            user_est_true[uid] = []
        user_est_true[uid].append((est, true_r))

    precisions = {}
    recalls = {}
    
    for uid, user_ratings in user_est_true.items():
        # Sort user ratings by estimated value
        user_ratings.sort(key=lambda x: x[0], reverse=True)
        
        # Number of relevant items
        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
        
        # Number of recommended items in top k
        n_rec_k = min(k, len(user_ratings))
        
        # Number of relevant and recommended items in top k
        n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold)) 
                              for (est, true_r) in user_ratings[:n_rec_k])
        
        # Precision@K: Proportion of recommended items that are relevant
        precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 0
        
        # Recall@K: Proportion of relevant items that are recommended
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
            predicted_rating = model.predict(student_id, item).est
            recommendations.append((item, predicted_rating))
    
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
rated_items = ratings_df[ratings_df['user_id'] == student_id]['item_id'].unique()
recommend_items(model, student_id, all_items, rated_items, top_n=5)

# Save the model and data for later use
print("\nSaving model and data...")
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('data.pkl', 'wb') as f:
    pickle.dump(data, f)

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
model_size = os.path.getsize('model.pkl') / 1024  # KB
data_size = os.path.getsize('data.pkl') / 1024  # KB
metrics_size = os.path.getsize('accuracy_metrics.pkl') / 1024  # KB

print(f"\nModel saved: model.pkl ({model_size:.2f} KB)")
print(f"Data saved: data.pkl ({data_size:.2f} KB)")
print(f"Accuracy metrics saved: accuracy_metrics.pkl ({metrics_size:.2f} KB)")

print("Model training and evaluation complete!")