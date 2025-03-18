import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from sklearn.neighbors import NearestNeighbors

# Step 1: Load the dataset
data = pd.read_csv("Dataset/dataset_etudiants.csv")

# Step 2: Preprocess the dataset
# Convert string representations of lists into actual lists
data['Coéquipiers'] = data['Coéquipiers'].apply(lambda x: eval(x))
data['Communautés'] = data['Communautés'].apply(lambda x: eval(x))
data['Compétences'] = data['Compétences'].apply(lambda x: eval(x))
data['Centres_d\'Intérêt'] = data['Centres_d\'Intérêt'].apply(lambda x: eval(x))

# Step 3: One-hot encode categorical columns
mlb_communautés = MultiLabelBinarizer()
communautés_encoded = mlb_communautés.fit_transform(data['Communautés'])

mlb_compétences = MultiLabelBinarizer()
compétences_encoded = mlb_compétences.fit_transform(data['Compétences'])

mlb_centres_d_intérêt = MultiLabelBinarizer()
centres_d_intérêt_encoded = mlb_centres_d_intérêt.fit_transform(data['Centres_d\'Intérêt'])

# Combine all encoded features with numeric features
numeric_features = data[['Travaux_Collaboratifs', 'Nombre_Interactions']].values
features = np.hstack([numeric_features, communautés_encoded, compétences_encoded, centres_d_intérêt_encoded])

# Normalize the full feature set
scaler_full = MinMaxScaler()
features_normalized = scaler_full.fit_transform(features)

# Normalize individual feature subsets
scaler_numeric = MinMaxScaler().fit(numeric_features)
scaler_communautés = MinMaxScaler().fit(communautés_encoded)
scaler_compétences = MinMaxScaler().fit(compétences_encoded)
scaler_centres_d_intérêt = MinMaxScaler().fit(centres_d_intérêt_encoded)

# Apply KNN algorithm
k = 5  # Number of neighbors to recommend
knn_full = NearestNeighbors(n_neighbors=k, metric='euclidean')
knn_full.fit(features_normalized)

knn_skills = NearestNeighbors(n_neighbors=k, metric='euclidean')
knn_skills.fit(scaler_compétences.transform(compétences_encoded))

knn_interests = NearestNeighbors(n_neighbors=k, metric='euclidean')
knn_interests.fit(scaler_centres_d_intérêt.transform(centres_d_intérêt_encoded))

knn_communities = NearestNeighbors(n_neighbors=k, metric='euclidean')
knn_communities.fit(scaler_communautés.transform(communautés_encoded))

# Function to recommend students based on a hybrid query profile
def recommend_students_by_profile(query_profile, knn_model, scaler, mlb_communautés, mlb_compétences, mlb_centres_d_intérêt):
    # Create a feature vector for the query profile
    query_numeric = np.array(query_profile['numeric']).reshape(1, -1)  # Reshape to 2D array
    query_communautés = mlb_communautés.transform([query_profile['communautés']])
    query_compétences = mlb_compétences.transform([query_profile['compétences']])
    query_centres_d_intérêt = mlb_centres_d_intérêt.transform([query_profile['centres_d_intérêt']])
    
    # Combine all features
    query_features = np.hstack([query_numeric, query_communautés, query_compétences, query_centres_d_intérêt])
    
    # Normalize the query features
    query_features_normalized = scaler.transform(query_features)
    
    # Find the k nearest neighbors
    distances, indices = knn_model.kneighbors(query_features_normalized)
    
    # Get the recommended students
    similar_students_indices = indices.flatten()
    similar_students = data.iloc[similar_students_indices]
    
    return similar_students

# Function to recommend students based on skills
def recommend_students_by_skills(query_skills, knn_model, scaler, mlb_compétences):
    # Encode the query skills
    query_encoded = mlb_compétences.transform([query_skills])
    
    # Normalize the query features
    query_normalized = scaler.transform(query_encoded)
    
    # Find the k nearest neighbors
    distances, indices = knn_model.kneighbors(query_normalized)
    
    # Get the recommended students
    similar_students_indices = indices.flatten()
    similar_students = data.iloc[similar_students_indices]
    
    return similar_students

# Function to recommend students based on interests
def recommend_students_by_interests(query_interests, knn_model, scaler, mlb_centres_d_intérêt):
    # Encode the query interests
    query_encoded = mlb_centres_d_intérêt.transform([query_interests])
    
    # Normalize the query features
    query_normalized = scaler.transform(query_encoded)
    
    # Find the k nearest neighbors
    distances, indices = knn_model.kneighbors(query_normalized)
    
    # Get the recommended students
    similar_students_indices = indices.flatten()
    similar_students = data.iloc[similar_students_indices]
    
    return similar_students

# Function to recommend students based on community memberships
def recommend_students_by_communities(query_communities, knn_model, scaler, mlb_communautés):
    # Encode the query communities
    query_encoded = mlb_communautés.transform([query_communities])
    
    # Normalize the query features
    query_normalized = scaler.transform(query_encoded)
    
    # Find the k nearest neighbors
    distances, indices = knn_model.kneighbors(query_normalized)
    
    # Get the recommended students
    similar_students_indices = indices.flatten()
    similar_students = data.iloc[similar_students_indices]
    
    return similar_students

# Example usage for each type of recommendation
# Define a query profile (hypothetical student)
query_profile = {
    'numeric': [7, 50],  # Travaux_Collaboratifs, Nombre_Interactions
    'communautés': ['Club Robotique', 'Groupe IA'],  # Communities
    'compétences': ['Blockchain', 'IA'],  # Skills
    'centres_d_intérêt': ['Jeux vidéo', 'Musique']  # Interests
}

# General hybrid recommendation
recommended_students = recommend_students_by_profile(query_profile, knn_full, scaler_full, mlb_communautés, mlb_compétences, mlb_centres_d_intérêt)
print("Recommended students based on hybrid query profile:")
print(recommended_students[['ID_Étudiant', 'Nom']])

# Skills-based recommendation
query_skills = ['Blockchain', 'Data Science']  # Query profile: Skills
recommended_students_skills = recommend_students_by_skills(query_skills, knn_skills, scaler_compétences, mlb_compétences)
print("\nRecommended students with similar skills:")
print(recommended_students_skills[['ID_Étudiant', 'Nom', 'Compétences']])

# Interests-based recommendation
query_interests = ['Jeux vidéo', 'Musique']  # Query profile: Interests
recommended_students_interests = recommend_students_by_interests(query_interests, knn_interests, scaler_centres_d_intérêt, mlb_centres_d_intérêt)
print("\nRecommended students with similar interests:")
print(recommended_students_interests[['ID_Étudiant', 'Nom', 'Centres_d\'Intérêt']])

# Community-based recommendation
query_communities = ['Club Robotique', 'Groupe IA']  # Query profile: Communities
recommended_students_communities = recommend_students_by_communities(query_communities, knn_communities, scaler_communautés, mlb_communautés)
print("\nRecommended students in similar communities:")
print(recommended_students_communities[['ID_Étudiant', 'Nom', 'Communautés']])