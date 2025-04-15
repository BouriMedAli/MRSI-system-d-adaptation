import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from collections import defaultdict
import time
import os
from surprise import Dataset, Reader, KNNBasic

# Initialize FastAPI app
app = FastAPI(title="Student Recommendation API")

# Load the trained model and data
def load_model_and_data():
    print("Loading pre-trained model and data...")
    
    try:
        # Load the model
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
            
        # Load the data
        with open('data.pkl', 'rb') as f:
            data = pickle.load(f)
            
        print("Successfully loaded pre-trained model and data")
        return model, data
        
    except FileNotFoundError:
        print("Error: Pre-trained model not found. Make sure to run KNN.py first.")
        raise HTTPException(status_code=500, detail="Model files not found. Model training required before API startup.")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

# Load the model and data at startup
model, data = load_model_and_data()

# Pre-process data for faster lookups
student_communities = {row['ID_Étudiant']: set(row['Communautés']) for _, row in data.iterrows()}
student_skills = {row['ID_Étudiant']: set(row['Compétences']) for _, row in data.iterrows()}
student_interests = {row['ID_Étudiant']: set(row['Centres_d\'Intérêt']) for _, row in data.iterrows()}

# Pydantic model for request validation
class QueryProfile(BaseModel):
    numeric: list[float]  # [Travaux_Collaboratifs, Nombre_Interactions]
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
    start_time = time.time()
    
    # Convert query profile to ratings
    query_ratings = profile_to_ratings(query_profile)
    
    # Build a testset for the query profile
    testset = [(user_id, item_id, rating) for user_id, item_id, rating in query_ratings]
    
    # Predict similarities for all users (students)
    predictions = model.test(testset)
    
    # Aggregate similarities to find most similar students
    similarities = defaultdict(float)
    for pred in predictions:
        item = pred.iid
        est_similarity = pred.est
        
        # Parse the item type and actual value
        if '_' in item:
            item_type, item_value = item.split('_', 1)
            
            # Find students who have this item - using pre-processed sets for faster lookup
            if item_type == 'comm':
                for student_id, communities in student_communities.items():
                    if item_value in communities:
                        similarities[student_id] += est_similarity
            elif item_type == 'skill':
                for student_id, skills in student_skills.items():
                    if item_value in skills:
                        similarities[student_id] += est_similarity
            elif item_type == 'int':
                for student_id, interests in student_interests.items():
                    if item_value in interests:
                        similarities[student_id] += est_similarity
    
    # Sort students by similarity score and take top 5
    top_students = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
    recommended_student_ids = [student_id for student_id, _ in top_students]
    
    # Get recommended students' details
    similar_students = data[data['ID_Étudiant'].isin(recommended_student_ids)][['ID_Étudiant', 'Nom']].to_dict(orient='records')
    
    # Add similarity scores to results
    for student in similar_students:
        student_id = student['ID_Étudiant']
        student['similarity_score'] = similarities[student_id]
    
    processing_time = time.time() - start_time
    
    return {
        "recommended_students": similar_students,
        "metadata": {
            "processing_time_ms": round(processing_time * 1000, 2)
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None, "data_loaded": data is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)