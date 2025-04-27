import pandas as pd
import numpy as np
import pickle
import os
import ast
import logging
import joblib
from surprise import Dataset, Reader, SVD, KNNBasic, accuracy
from surprise.model_selection import train_test_split
from collections import defaultdict
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors
import itertools
from sklearn.neighbors import KNeighborsClassifier


# Exemple d'entraînement
X_train = ...  # Tes données d'entraînement
y_train = ...  # Tes labels d'entraînement

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)

# Enregistrement du modèle
joblib.dump(knn, './model/knn_model.pkl')


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(dataset_path='./Dataset/dataset_etudiants.csv'):
    """Load student dataset and convert string representations of lists to actual lists."""
    logging.info(f"Loading data from {dataset_path}")
    try:
        df = pd.read_csv(dataset_path)
        
        # Convert string representations of lists to actual lists
        for column in ['Coéquipiers', 'Communautés', 'Compétences', "Centres_d'Intérêt"]:
            df[column] = df[column].apply(ast.literal_eval)
            
        logging.info(f"Successfully loaded data with {df.shape[0]} students")
        return df
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        raise

def create_interaction_matrix(df):
    """
    Create a matrix of student-to-student interactions for collaborative filtering.
    
    This creates synthetic ratings based on:
    1. Existing teammate relationships
    2. Shared communities
    3. Skill complementarity
    4. Interest overlap
    """
    logging.info("Creating interaction matrix")
    
    # Generate all possible student pairs
    student_ids = df['ID_Étudiant'].unique()
    ratings_data = []
    
    # Process each student
    for student_id in student_ids:
        student = df[df['ID_Étudiant'] == student_id].iloc[0]
        
        # Create synthetic interactions with other students
        for other_id in student_ids:
            if student_id == other_id:
                continue
                
            other_student = df[df['ID_Étudiant'] == other_id].iloc[0]
            
            # Base rating - neutral
            rating = 3.0
            
            # Factor 1: Existing teammates get a boost
            if other_id in student['Coéquipiers']:
                rating += 1.5
                
            # Factor 2: Shared communities
            shared_communities = set(student['Communautés']).intersection(set(other_student['Communautés']))
            rating += len(shared_communities) * 0.5
            
            # Factor 3: Skill complementarity (skills the other has that I don't)
            complementary_skills = set(other_student['Compétences']).difference(set(student['Compétences']))
            rating += len(complementary_skills) * 0.3
            
            # Factor 4: Shared interests
            shared_interests = set(student["Centres_d'Intérêt"]).intersection(set(other_student["Centres_d'Intérêt"]))
            rating += len(shared_interests) * 0.4
            
            # Factor 5: Other student's collaboration score
            rating += (other_student['Travaux_Collaboratifs'] / 10) * 0.5
            
            # Normalize to 1-5 scale
            rating = min(max(rating, 1.0), 5.0)
            
            # Add to ratings data
            ratings_data.append((student_id, other_id, rating))
    
    # Create DataFrame with ratings
    ratings_df = pd.DataFrame(ratings_data, columns=['studentId', 'partnerId', 'rating'])
    logging.info(f"Created interaction matrix with {len(ratings_df)} ratings")
    
    return ratings_df

def train_surprise_models(ratings_df):
    """Train SVD and KNN models using Surprise library."""
    logging.info("Training recommendation models")
    
    # Create Surprise dataset
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings_df, reader)
    
    # Split data
    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
    
    # Train SVD model (matrix factorization)
    svd_model = SVD(n_factors=20, lr_all=0.005, reg_all=0.02, n_epochs=50, verbose=False)
    svd_model.fit(trainset)
    
    # Train KNN model (item-based collaborative filtering)
    # Compute similarities between items (partners)
    sim_options = {
        'name': 'cosine',
        'user_based': False  # Item-based similarity
    }
    knn_model = KNNBasic(sim_options=sim_options, k=10, min_k=1, verbose=False)
    knn_model.fit(trainset)
    
    # Evaluate models
    svd_predictions = svd_model.test(testset)
    knn_predictions = knn_model.test(testset)
    
    logging.info(f"SVD model RMSE: {accuracy.rmse(svd_predictions):.4f}")
    logging.info(f"KNN model RMSE: {accuracy.rmse(knn_predictions):.4f}")
    
    # Return better model and both predictions
    if accuracy.rmse(svd_predictions) < accuracy.rmse(knn_predictions):
        logging.info("SVD model performed better, using it as primary model")
        primary_model = svd_model
        primary_model_name = "SVD"
    else:
        logging.info("KNN model performed better, using it as primary model")
        primary_model = knn_model
        primary_model_name = "KNN"
    
    return {
        'primary_model': primary_model,
        'primary_model_name': primary_model_name,
        'svd_model': svd_model,
        'knn_model': knn_model,
        'trainset': trainset
    }

def compute_student_similarities(df):
    """Compute student similarities based on profile attributes."""
    logging.info("Computing student similarities")
    
    similarities = {}
    student_ids = df['ID_Étudiant'].unique()
    
    for student_id in student_ids:
        student = df[df['ID_Étudiant'] == student_id].iloc[0]
        student_similarities = {}
        
        for other_id in student_ids:
            if student_id == other_id:
                continue
                
            other_student = df[df['ID_Étudiant'] == other_id].iloc[0]
            
            # Compute similarity components
            # 1. Skill similarity (Jaccard)
            skills_a = set(student['Compétences'])
            skills_b = set(other_student['Compétences'])
            skill_similarity = len(skills_a.intersection(skills_b)) / len(skills_a.union(skills_b)) if skills_a.union(skills_b) else 0
            
            # 2. Interest similarity (Jaccard)
            interests_a = set(student["Centres_d'Intérêt"])
            interests_b = set(other_student["Centres_d'Intérêt"])
            interest_similarity = len(interests_a.intersection(interests_b)) / len(interests_a.union(interests_b)) if interests_a.union(interests_b) else 0
            
            # 3. Community similarity (Jaccard)
            communities_a = set(student['Communautés'])
            communities_b = set(other_student['Communautés'])
            community_similarity = len(communities_a.intersection(communities_b)) / len(communities_a.union(communities_b)) if communities_a.union(communities_b) else 0
            
            # 4. Collaboration score similarity
            collab_similarity = 1 - (abs(student['Travaux_Collaboratifs'] - other_student['Travaux_Collaboratifs']) / 10)
            
            # 5. Interaction count similarity
            max_interactions = df['Nombre_Interactions'].max()
            interaction_similarity = 1 - (abs(student['Nombre_Interactions'] - other_student['Nombre_Interactions']) / max_interactions) if max_interactions > 0 else 0
            
            # Combine similarities
            combined_similarity = (
                skill_similarity * 0.25 +
                interest_similarity * 0.25 +
                community_similarity * 0.2 +
                collab_similarity * 0.15 +
                interaction_similarity * 0.15
            )
            
            student_similarities[other_id] = {
                'combined': combined_similarity,
                'skill': skill_similarity,
                'interest': interest_similarity,
                'community': community_similarity,
                'collaboration': collab_similarity,
                'interaction': interaction_similarity
            }
            
        similarities[student_id] = student_similarities
    
    return similarities

def create_feature_matrix(df):
    """Create a feature matrix for KNN model."""
    logging.info("Creating feature matrix for KNN model")
    
    # Extract skill names, interests, and communities
    all_skills = set()
    all_interests = set()
    all_communities = set()
    
    for _, row in df.iterrows():
        all_skills.update(row['Compétences'])
        all_interests.update(row["Centres_d'Intérêt"])
        all_communities.update(row['Communautés'])
    
    feature_columns = []
    
    # Create one-hot encoding for categorical features
    for skill in sorted(all_skills):
        df[f'skill_{skill}'] = df['Compétences'].apply(lambda x: 1 if skill in x else 0)
        feature_columns.append(f'skill_{skill}')
        
    for interest in sorted(all_interests):
        df[f'interest_{interest}'] = df["Centres_d'Intérêt"].apply(lambda x: 1 if interest in x else 0)
        feature_columns.append(f'interest_{interest}')
        
    for community in sorted(all_communities):
        df[f'community_{community}'] = df['Communautés'].apply(lambda x: 1 if community in x else 0)
        feature_columns.append(f'community_{community}')
    
    # Add numerical features
    df['collaboration_score'] = df['Travaux_Collaboratifs'] / 10  # Normalize to 0-1
    feature_columns.append('collaboration_score')
    
    if df['Nombre_Interactions'].max() > 0:
        df['interaction_normalized'] = df['Nombre_Interactions'] / df['Nombre_Interactions'].max()
    else:
        df['interaction_normalized'] = 0
    feature_columns.append('interaction_normalized')
    
    logging.info(f"Created feature matrix with {len(feature_columns)} features")
    return df, feature_columns

def train_knn_model(df, feature_columns):
    """Train a KNN model for finding similar students."""
    logging.info("Training KNN model for similar students")
    
    X = df[feature_columns].values
    
    # Create and train the KNN model
    knn = NearestNeighbors(n_neighbors=11, algorithm='auto', metric='cosine')
    knn.fit(X)
    
    # Create a pipeline with the KNN model
    pipeline = Pipeline([
        ('knn', knn)
    ])
    
    return pipeline

def save_models(surprise_models, similarities, df, knn_model, feature_columns, output_dir='./model'):
    """Save all trained models and data."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Save Surprise models
    surprise_models_path = os.path.join(output_dir, 'surprise_models.pkl')
    with open(surprise_models_path, 'wb') as f:
        pickle.dump(surprise_models, f)
    logging.info(f"Surprise models saved to {surprise_models_path}")
    
    # Save similarities
    similarities_path = os.path.join(output_dir, 'student_similarities.pkl')
    with open(similarities_path, 'wb') as f:
        pickle.dump(similarities, f)
    logging.info(f"Similarities saved to {similarities_path}")
    
    # Save KNN model
    knn_model_path = os.path.join(output_dir, 'knn_model.pkl')
    with open(knn_model_path, 'wb') as f:
        pickle.dump(knn_model, f)
    logging.info(f"KNN model saved to {knn_model_path}")
    
    # Save feature columns
    feature_columns_path = os.path.join(output_dir, 'feature_columns.pkl')
    with open(feature_columns_path, 'wb') as f:
        pickle.dump(feature_columns, f)
    logging.info(f"Feature columns saved to {feature_columns_path}")
    
    # Save original dataframe
    df_path = os.path.join(output_dir, 'processed_df.pkl')
    with open(df_path, 'wb') as f:
        pickle.dump(df, f)
    logging.info(f"Processed dataframe saved to {df_path}")

def generate_recommendations(models, student_id, n=5):
    """Generate recommendations for a student using the trained model."""
    primary_model = models['primary_model']
    trainset = models['trainset']
    
    # Get inner user id
    try:
        inner_user_id = trainset.to_inner_uid(student_id)
    except ValueError:
        logging.error(f"Student {student_id} not found in training set")
        return []
    
    # Get all items (partners) the user has not interacted with
    user_items = set([j for (j, _) in trainset.ur[inner_user_id]])
    all_items = set(range(trainset.n_items))
    missing = list(all_items - user_items)
    
    # Predict ratings for all missing items
    predictions = []
    for item_id in missing:
        try:
            partner_id = trainset.to_raw_iid(item_id)
            pred = primary_model.predict(student_id, partner_id).est
            predictions.append((partner_id, pred))
        except ValueError:
            continue
    
    # Sort predictions by estimated rating
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N recommendations
    return predictions[:n]

def main():
    logging.info("Starting model training")
    
    # Define paths
    dataset_path = './Dataset/dataset_etudiants.csv'
    output_dir = './model'
    
    # Load data
    df = load_data(dataset_path)
    
    # Create interaction matrix
    ratings_df = create_interaction_matrix(df)
    
    # Train surprise models
    surprise_models = train_surprise_models(ratings_df)
    
    # Compute student similarities
    similarities = compute_student_similarities(df)
    
    # Create feature matrix and train KNN model
    df_features, feature_columns = create_feature_matrix(df)
    knn_model = train_knn_model(df_features, feature_columns)
    
    # Save models and data
    save_models(surprise_models, similarities, df_features, knn_model, feature_columns, output_dir)
    
    # Test model with a sample student
    student_id = 1
    recommendations = generate_recommendations(surprise_models, student_id, n=5)
    
    logging.info(f"Sample recommendations for student {student_id}:")
    for partner_id, score in recommendations:
        partner_name = df[df['ID_Étudiant'] == partner_id].iloc[0]['Nom']
        logging.info(f"  {partner_name} (ID: {partner_id}) - Score: {score:.4f}")
    
    logging.info("Model training completed successfully")

if __name__ == "__main__":
    main()