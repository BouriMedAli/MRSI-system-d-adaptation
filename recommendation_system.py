import pandas as pd
import numpy as np
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate
from sklearn.metrics import confusion_matrix
import json
import ast
import pickle

# Load and preprocess data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Coéquipiers'] = df['Coéquipiers'].apply(ast.literal_eval)
    df['Compétences'] = df['Compétences'].apply(ast.literal_eval)
    df['Centres_d_Intérêt'] = df['Centres_d_Intérêt'].apply(ast.literal_eval)
    df['Communautés'] = df['Communautés'].apply(ast.literal_eval)
    return df

# Create student-student interaction data
def create_student_interaction_data(df):
    interactions = []
    for _, row in df.iterrows():
        student_id = row['ID_Étudiant']
        coequipiers = row['Coéquipiers']
        interactions_count = row['Nombre_Interactions']
        rating = min(5, max(1, interactions_count // 20))  # Normalize to 1-5
        for coequipier in coequipiers:
            interactions.append((student_id, coequipier, rating))
    return pd.DataFrame(interactions, columns=['student_id', 'coequipier_id', 'rating'])

# Create student-community interaction data
def create_community_interaction_data(df):
    interactions = []
    all_communities = set()
    for _, row in df.iterrows():
        communities = row['Communautés']
        all_communities.update(communities)
    all_communities = list(all_communities)
    
    for _, row in df.iterrows():
        student_id = row['ID_Étudiant']
        student_communities = row['Communautés']
        for community in all_communities:
            rating = 5 if community in student_communities else 1  # Binary-like rating
            interactions.append((student_id, community, rating))
    return pd.DataFrame(interactions, columns=['student_id', 'community', 'rating']), all_communities

# Train SVD model
def train_model(interaction_df, model_file):
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(interaction_df[['student_id', 'coequipier_id' if 'coequipier_id' in interaction_df else 'community', 'rating']], reader)
    model = SVD(n_factors=20, n_epochs=20, random_state=42)
    trainset = data.build_full_trainset()
    model.fit(trainset)
    
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    
    results = cross_validate(model, data, measures=['RMSE', 'MAE'], cv=5, verbose=False)
    return model, results

# Compute confusion matrix
def compute_confusion_matrix(model, interaction_df, is_student=True):
    predictions = []
    actuals = []
    for _, row in interaction_df.iterrows():
        pred = model.predict(row['student_id'], row['coequipier_id' if is_student else 'community']).est
        predictions.append(1 if pred >= 3 else 0)
        actuals.append(1 if row['rating'] >= 3 else 0)
    return confusion_matrix(actuals, predictions)

# Get student-to-student recommendations
def get_student_recommendations(student_id, model, df, n=5):
    all_students = df['ID_Étudiant'].unique()
    predictions = []
    for other_id in all_students:
        if other_id != student_id:
            pred = model.predict(student_id, other_id).est
            # Filter by shared skills or interests
            student_skills = set(df[df['ID_Étudiant'] == student_id]['Compétences'].iloc[0])
            student_interests = set(df[df['ID_Étudiant'] == student_id]['Centres_d_Intérêt'].iloc[0])
            other_skills = set(df[df['ID_Étudiant'] == other_id]['Compétences'].iloc[0])
            other_interests = set(df[df['ID_Étudiant'] == other_id]['Centres_d_Intérêt'].iloc[0])
            if student_skills & other_skills or student_interests & other_interests:
                predictions.append((other_id, pred))
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]
    
    recommendations = []
    for other_id, score in top_n:
        student_data = df[df['ID_Étudiant'] == other_id].iloc[0]
        recommendations.append({
            'ID_Étudiant': other_id,
            'Nom': student_data['Nom'],
            'Compétences': student_data['Compétences'],
            'Centres_d_Intérêt': student_data['Centres_d_Intérêt'],
            'Score': round(score, 2)
        })
    return recommendations

# Get community/project recommendations
def get_community_recommendations(student_id, model, df, all_communities, n=5):
    predictions = []
    student_communities = df[df['ID_Étudiant'] == student_id]['Communautés'].iloc[0]
    for community in all_communities:
        if community not in student_communities:  # Recommend new communities
            pred = model.predict(student_id, community).est
            predictions.append((community, pred))
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]
    
    recommendations = []
    for community, score in top_n:
        recommendations.append({
            'Communauté': community,
            'Projet': f"{community} Project",  # Infer project from community
            'Score': round(score, 2)
        })
    return recommendations

if __name__ == '__main__':
    df = load_data('dataset_etudiants.csv')
    
    # Student-to-student recommendations
    student_interaction_df = create_student_interaction_data(df)
    student_model, student_results = train_model(student_interaction_df, 'svd_student_model.pkl')
    student_cm = compute_confusion_matrix(student_model, student_interaction_df, is_student=True)
    
    # Community/project recommendations
    community_interaction_df, all_communities = create_community_interaction_data(df)
    community_model, community_results = train_model(community_interaction_df, 'svd_community_model.pkl')
    community_cm = compute_confusion_matrix(community_model, community_interaction_df, is_student=False)
    
    # Print results
    print("Student-to-Student Recommendations:")
    print(f"RMSE: {np.mean(student_results['test_rmse']):.4f}")
    print(f"MAE: {np.mean(student_results['test_mae']):.4f}")
    print("Confusion Matrix:")
    print(student_cm)
    
    print("\nCommunity/Project Recommendations:")
    print(f"RMSE: {np.mean(community_results['test_rmse']):.4f}")
    print(f"MAE: {np.mean(community_results['test_mae']):.4f}")
    print("Confusion Matrix:")
    print(community_cm)
    
    # Example recommendations
    student_recs = get_student_recommendations(1, student_model, df)
    community_recs = get_community_recommendations(1, community_model, df, all_communities)
    print("\nStudent Recommendations for Etudiant_1:")
    print(json.dumps(student_recs, indent=2))
    print("\nCommunity Recommendations for Etudiant_1:")
    print(json.dumps(community_recs, indent=2))