import pandas as pd
import numpy as np
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from collections import defaultdict

# Initialize FastAPI app
app = FastAPI(title="Student Recommendation API")

# Load and preprocess the dataset
data = pd.read_csv("Dataset/dataset_etudiants.csv")
data['Coéquipiers'] = data['Coéquipiers'].apply(lambda x: eval(x))
data['Communautés'] = data['Communautés'].apply(lambda x: eval(x))
data['Compétences'] = data['Compétences'].apply(lambda x: eval(x))
data['Centres_d\'Intérêt'] = data['Centres_d\'Intérêt'].apply(lambda x: eval(x))

# Create a "ratings" dataset by converting features into implicit ratings
# We'll treat each community, skill, and interest as an "item" with a rating of 1 if present
ratings_data = []

# Add communities as items
for idx, row in data.iterrows():
    student_id = row['ID_Étudiant']
    for community in row['Communautés']:
        ratings_data.append({'user_id': student_id, 'item_id': f"comm_{community}", 'rating': 1})
    for skill in row['Compétences']:
        ratings_data.append({'user_id': student_id, 'item_id': f"skill_{skill}", 'rating': 1})
    for interest in row['Centres_d\'Intérêt']:
        ratings_data.append({'user_id': student_id, 'item_id': f"int_{interest}", 'rating': 1})

ratings_df = pd.DataFrame(ratings_data)

# Define the reader for surprise (ratings are binary: 1 for presence)
reader = Reader(rating_scale=(0, 1))
dataset = Dataset.load_from_df(ratings_df[['user_id', 'item_id', 'rating']], reader)

# Build the full trainset
trainset = dataset.build_full_trainset()

# Train the KNNBasic model (user-based collaborative filtering)
sim_options = {
    'name': 'cosine',  # Use cosine similarity
    'user_based': True  # User-based collaborative filtering
}
model = KNNBasic(k=5, sim_options=sim_options)
model.fit(trainset)

# Pydantic model for request validation
class QueryProfile(BaseModel):
    numeric: list[float]  # [Travaux_Collaboratifs, Nombre_Interactions] - not used directly in surprise
    communautés: list[str]
    compétences: list[str]
    centres_d_intérêt: list[str]

# Function to convert query profile to "ratings"
def profile_to_ratings(query_profile):
    ratings = []
    for comm in query_profile.communautés:
        ratings.append(('query_user', f"comm_{comm}", 1))
    for skill in query_profile.compétences:
        ratings.append(('query_user', f"skill_{skill}", 1))
    for interest in query_profile.centres_d_intérêt:
        ratings.append(('query_user', f"int_{interest}", 1))
    return ratings

# Recommendation endpoint
@app.post("/recommend/")
async def recommend_students(query_profile: QueryProfile):
    # Convert query profile to ratings
    query_ratings = profile_to_ratings(query_profile)
    
    # Build a testset for the query profile
    testset = [(user_id, item_id, rating) for user_id, item_id, rating in query_ratings]
    
    # Predict similarities for all users (students)
    predictions = model.test(testset)
    
    # Aggregate similarities to find most similar students
    similarities = defaultdict(float)
    for pred in predictions:
        # pred.uid is 'query_user', pred.iid is the item, pred.r_ui is the rating, pred.est is the estimated similarity
        # We need to find the actual student (user) associated with the item
        item = pred.iid
        est_similarity = pred.est
        # Find students who have this item
        for student_idx, row in data.iterrows():
            student_id = row['ID_Étudiant']
            if (f"comm_{item}" in [f"comm_{c}" for c in row['Communautés']] or
                f"skill_{item}" in [f"skill_{s}" for s in row['Compétences']] or
                f"int_{item}" in [f"int_{i}" for i in row['Centres_d\'Intérêt']]):
                similarities[student_id] += est_similarity
    
    # Sort students by similarity score and take top 5
    top_students = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
    recommended_student_ids = [student_id for student_id, _ in top_students]
    
    # Get recommended students' details
    similar_students = data[data['ID_Étudiant'].isin(recommended_student_ids)][['ID_Étudiant', 'Nom']].to_dict(orient='records')
    
    return {"recommended_students": similar_students}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)