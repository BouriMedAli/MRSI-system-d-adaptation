import pandas as pd
import ast
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader

# Load and preprocess the dataset
def load_dataset(path):
    df = pd.read_csv(path)
    df['Compétences'] = df['Compétences'].apply(ast.literal_eval)
    df['Centres_d\'Intérêt'] = df['Centres_d\'Intérêt'].apply(ast.literal_eval)
    return df

# Function to compute similarity rating between two students
def compute_similarity_rating(skills_i, interests_i, skills_j, interests_j):
    skills_i, interests_i = set(skills_i), set(interests_i)
    skills_j, interests_j = set(skills_j), set(interests_j)
    shared_skills = len(skills_i.intersection(skills_j))
    shared_interests = len(interests_i.intersection(interests_j))
    return 3 * shared_skills + shared_interests  # Weight skills higher

# Function to compute complementarity rating for a project
def compute_complementarity_rating(skills_i, interests_i, skills_j, interests_j, project_skills):
    skills_i, interests_i = set(skills_i), set(interests_i)
    skills_j, interests_j = set(skills_j), set(interests_j)
    shared_skills = len(skills_i.intersection(skills_j))
    missing_skills = set(project_skills) - skills_i
    complementary_skills = len(missing_skills.intersection(skills_j))
    shared_interests = len(interests_i.intersection(interests_j))
    return 4 * complementary_skills + shared_skills + 0.5 * shared_interests  # Emphasize complementary skills

# Create ratings for similarity use case
def create_ratings_similarity(df):
    ratings = []
    for i, row_i in df.iterrows():
        student_i = row_i['ID_Étudiant']
        skills_i = row_i['Compétences']
        interests_i = row_i['Centres_d\'Intérêt']
        for j, row_j in df.iterrows():
            student_j = row_j['ID_Étudiant']
            if student_i != student_j:
                rating = compute_similarity_rating(skills_i, interests_i, row_j['Compétences'], row_j['Centres_d\'Intérêt'])
                if rating > 0:
                    ratings.append((student_i, student_j, rating))
    return ratings

# Create ratings for complementarity use case
def create_ratings_complementarity(project_skills, df):
    ratings = []
    for i, row_i in df.iterrows():
        student_i = row_i['ID_Étudiant']
        skills_i = row_i['Compétences']
        interests_i = row_i['Centres_d\'Intérêt']
        for j, row_j in df.iterrows():
            student_j = row_j['ID_Étudiant']
            if student_i != student_j:
                rating = compute_complementarity_rating(skills_i, interests_i, row_j['Compétences'], row_j['Centres_d\'Intérêt'], project_skills)
                if rating > 0:
                    ratings.append((student_i, student_j, rating))
    return ratings

# Encode skills and interests into feature vectors
def encode_features(df):
    all_skills = set(skill for skills in df['Compétences'] for skill in skills)
    all_interests = set(interest for interests in df['Centres_d\'Intérêt'] for interest in interests)
    
    skill_encoder = MultiLabelBinarizer()
    interest_encoder = MultiLabelBinarizer()
    
    skill_encoder.fit([list(all_skills)])
    interest_encoder.fit([list(all_interests)])
    
    skill_vectors = skill_encoder.transform(df['Compétences'])
    interest_vectors = interest_encoder.transform(df['Centres_d\'Intérêt'])
    
    feature_vectors = np.concatenate([skill_vectors, interest_vectors], axis=1)
    
    return feature_vectors, skill_encoder, interest_encoder, all_skills, all_interests

# Custom Dataset for training the MLP
class RatingsDataset(Dataset):
    def __init__(self, ratings, feature_vectors, max_rating):
        self.ratings = ratings
        self.feature_vectors = feature_vectors
        self.max_rating = max_rating
        self.student_id_to_idx = {id: idx for idx, id in enumerate(np.unique([r[0] for r in ratings] + [r[1] for r in ratings]))}
    
    def __len__(self):
        return len(self.ratings)
    
    def __getitem__(self, idx):
        student_i, student_j, rating = self.ratings[idx]
        i_idx = self.student_id_to_idx[student_i]
        j_idx = self.student_id_to_idx[student_j]
        
        feature_i = self.feature_vectors[i_idx]
        feature_j = self.feature_vectors[j_idx]
        
        combined_features = np.concatenate([feature_i, feature_j])
        normalized_rating = rating / self.max_rating
        
        return torch.tensor(combined_features, dtype=torch.float32), torch.tensor(normalized_rating, dtype=torch.float32)

# MLP model
class MLP(nn.Module):
    def __init__(self, input_dim, hidden_dims=[128, 64, 32]):
        super(MLP, self).__init__()
        layers = []
        prev_dim = input_dim
        for dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_dim = dim
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())  # Output normalized rating [0, 1]
        self.model = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.model(x)

# Train the MLP
def train_mlp(model, train_loader, num_epochs=100, learning_rate=0.001):
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for features, rating in train_loader:
            optimizer.zero_grad()
            output = model(features).squeeze()
            loss = criterion(output, rating)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
    
    return model

# Prepare and train the recommendation models
def prepare_models(df, project_skills):
    # Encode features
    feature_vectors, skill_encoder, interest_encoder, all_skills, all_interests = encode_features(df)
    
    # Create ratings
    ratings_similarity = create_ratings_similarity(df)
    ratings_complementarity = create_ratings_complementarity(project_skills, df)
    
    # Calculate max ratings for normalization
    max_similarity_rating = len(all_skills) * 3 + len(all_interests)
    max_complementarity_rating = len(all_skills) * 4 + len(all_interests) * 0.5
    
    # Prepare datasets
    similarity_dataset = RatingsDataset(ratings_similarity, feature_vectors, max_similarity_rating)
    complementarity_dataset = RatingsDataset(ratings_complementarity, feature_vectors, max_complementarity_rating)
    
    # Create data loaders
    similarity_loader = DataLoader(similarity_dataset, batch_size=32, shuffle=True)
    complementarity_loader = DataLoader(complementarity_dataset, batch_size=32, shuffle=True)
    
    # Initialize models
    input_dim = feature_vectors.shape[1] * 2  # Concatenated features for two students
    similarity_model = MLP(input_dim)
    complementarity_model = MLP(input_dim)
    
    # Train models
    similarity_model = train_mlp(similarity_model, similarity_loader)
    complementarity_model = train_mlp(complementarity_model, complementarity_loader)
    
    return (similarity_model, complementarity_model, skill_encoder, interest_encoder, all_skills, all_interests, max_similarity_rating, max_complementarity_rating)

# Recommend collaborators for a student
def recommend_collaborators(student_id, skills, interests, use_case, model_data, df, n=3, project_skills=None):
    model, skill_encoder, interest_encoder, max_rating = model_data
    is_new_student = student_id not in df['ID_Étudiant'].values
    
    # Encode input student features
    skill_vector = skill_encoder.transform([skills])[0]
    interest_vector = interest_encoder.transform([interests])[0]
    student_features = np.concatenate([skill_vector, interest_vector])
    
    all_students = df['ID_Étudiant'].unique()
    predictions = []
    
    for other_student in all_students:
        if other_student != student_id:
            other_student_data = df[df['ID_Étudiant'] == other_student]
            other_skills = other_student_data['Compétences'].iloc[0]
            other_interests = other_student_data['Centres_d\'Intérêt'].iloc[0]
            
            if is_new_student:
                # For new students, use raw rating
                if use_case == "similarity":
                    predicted_rating = compute_similarity_rating(skills, interests, other_skills, other_interests)
                else:
                    predicted_rating = compute_complementarity_rating(skills, interests, other_skills, other_interests, project_skills)
            else:
                # Encode other student features
                other_skill_vector = skill_encoder.transform([other_skills])[0]
                other_interest_vector = interest_encoder.transform([other_interests])[0]
                other_features = np.concatenate([other_skill_vector, other_interest_vector])
                
                # Combine features
                combined_features = np.concatenate([student_features, other_features])
                input_tensor = torch.tensor(combined_features, dtype=torch.float32).unsqueeze(0)
                
                # Predict rating using MLP
                model.eval()
                with torch.no_grad():
                    predicted_rating = model(input_tensor).item() * max_rating
            
            predictions.append((other_student, predicted_rating, other_skills, other_interests))
    
    # Sort and get top n
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]
    
    # Format results to match apiNN.py expectations (no Score)
    results = []
    for other_student_id, _, skills, interests in top_n:
        results.append({
            'Student_ID': int(other_student_id),
            'Skills': list(skills),
            'Interests': list(interests)
        })
    
    return results

# Wrapper function to handle model selection
def prepare_and_recommend(df, project_skills, student_id, skills, interests, use_case, n=3):
    models = prepare_models(df, project_skills)
    similarity_model, complementarity_model, skill_encoder, interest_encoder, all_skills, all_interests, max_similarity_rating, max_complementarity_rating = models
    
    if use_case == "similarity":
        model_data = (similarity_model, skill_encoder, interest_encoder, max_similarity_rating)
    else:
        model_data = (complementarity_model, skill_encoder, interest_encoder, max_complementarity_rating)
    
    return recommend_collaborators(student_id, skills, interests, use_case, model_data, df, n, project_skills)