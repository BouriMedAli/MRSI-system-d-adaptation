import pandas as pd
import ast
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MultiLabelBinarizer
from torch.utils.data import Dataset, DataLoader
from scipy.spatial.distance import cosine

# Load and preprocess the dataset
def load_dataset(path):
    df = pd.read_csv(path)
    df['Compétences'] = df['Compétences'].apply(ast.literal_eval)
    df['Centres_d\'Intérêt'] = df['Centres_d\'Intérêt'].apply(ast.literal_eval)
    return df

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

# Custom Dataset for training the autoencoder
class StudentDataset(Dataset):
    def __init__(self, feature_vectors):
        self.feature_vectors = feature_vectors
    
    def __len__(self):
        return len(self.feature_vectors)
    
    def __getitem__(self, idx):
        return torch.tensor(self.feature_vectors[idx], dtype=torch.float32)

# Autoencoder model
class Autoencoder(nn.Module):
    def __init__(self, input_dim, latent_dim=16):
        super(Autoencoder, self).__init__()
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, latent_dim),
            nn.ReLU()
        )
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, input_dim),
            nn.Sigmoid()  # Binary features (0 or 1)
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return encoded, decoded

# Train the autoencoder
def train_autoencoder(model, train_loader, num_epochs=100, learning_rate=0.001):
    criterion = nn.BCELoss()  # Binary cross-entropy for binary features
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for features in train_loader:
            optimizer.zero_grad()
            _, decoded = model(features)
            loss = criterion(decoded, features)  # Reconstruct input
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
    
    return model

# Compute similarity score in latent space
def compute_latent_similarity(embedding_i, embedding_j):
    # Cosine similarity (1 - cosine distance)
    return 1 - cosine(embedding_i, embedding_j)

# Compute complementarity score in latent space
def compute_latent_complementarity(embedding_i, embedding_j, project_skills_embedding):
    # Similarity to project skills (how well student_j complements student_i's needs)
    complementarity_score = compute_latent_similarity(embedding_j, project_skills_embedding)
    # Penalize if students are too similar (to encourage diversity)
    similarity_penalty = 0.5 * compute_latent_similarity(embedding_i, embedding_j)
    return complementarity_score - similarity_penalty

# Prepare and train the autoencoder model
def prepare_models(df, project_skills):
    # Encode features
    feature_vectors, skill_encoder, interest_encoder, all_skills, all_interests = encode_features(df)
    
    # Prepare dataset
    dataset = StudentDataset(feature_vectors)
    data_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Initialize and train autoencoder
    input_dim = feature_vectors.shape[1]
    model = Autoencoder(input_dim, latent_dim=16)
    model = train_autoencoder(model, data_loader)
    
    # Generate embeddings for all students
    model.eval()
    with torch.no_grad():
        embeddings = model.encoder(torch.tensor(feature_vectors, dtype=torch.float32)).detach().numpy()
    
    # Encode project skills as a feature vector
    project_skills_vector = skill_encoder.transform([project_skills])[0]
    project_interests_vector = interest_encoder.transform([[]])[0]  # No interests for project
    project_features = np.concatenate([project_skills_vector, project_interests_vector])
    project_embedding = model.encoder(torch.tensor(project_features, dtype=torch.float32)).detach().numpy()
    
    # Return model data (no max_rating for unsupervised)
    return (model, embeddings, project_embedding, skill_encoder, interest_encoder, all_skills, all_interests, None)

# Recommend collaborators for a student
def recommend_collaborators(student_id, skills, interests, use_case, model_data, df, n=3, project_skills=None):
    model, embeddings, project_embedding, skill_encoder, interest_encoder, all_skills, all_interests, _ = model_data
    is_new_student = student_id not in df['ID_Étudiant'].values
    
    # Encode input student features
    skill_vector = skill_encoder.transform([skills])[0]
    interest_vector = interest_encoder.transform([interests])[0]
    student_features = np.concatenate([skill_vector, interest_vector])
    
    # Get student embedding
    if is_new_student:
        model.eval()
        with torch.no_grad():
            student_embedding = model.encoder(torch.tensor(student_features, dtype=torch.float32)).detach().numpy()
    else:
        student_idx = df[df['ID_Étudiant'] == student_id].index[0]
        student_embedding = embeddings[student_idx]
    
    all_students = df['ID_Étudiant'].unique()
    predictions = []
    
    for other_student in all_students:
        if other_student != student_id:
            other_idx = df[df['ID_Étudiant'] == other_student].index[0]
            other_embedding = embeddings[other_idx]
            other_student_data = df[df['ID_Étudiant'] == other_student]
            other_skills = other_student_data['Compétences'].iloc[0]
            other_interests = other_student_data['Centres_d\'Intérêt'].iloc[0]
            
            if use_case == "similarity":
                score = compute_latent_similarity(student_embedding, other_embedding)
            else:
                score = compute_latent_complementarity(student_embedding, other_embedding, project_embedding)
            
            predictions.append((other_student, score, other_skills, other_interests))
    
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

# Wrapper function to handle model preparation and recommendation
def prepare_and_recommend(df, project_skills, student_id, skills, interests, use_case, n=3):
    model_data = prepare_models(df, project_skills)
    return recommend_collaborators(student_id, skills, interests, use_case, model_data, df, n, project_skills)