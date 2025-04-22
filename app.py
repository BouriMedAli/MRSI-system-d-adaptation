import pickle
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from collections import defaultdict
import time
import os
from surprise import Dataset, Reader, KNNBasic
from typing import List, Dict, Optional

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
        
        # Load student features
        with open('student_features.pkl', 'rb') as f:
            student_features = pickle.load(f)
        
        # Load metadata
        with open('metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
            
        print("Successfully loaded pre-trained model and data")
        return model, data, student_features, metadata
        
    except FileNotFoundError:
        print("Error: Pre-trained model not found. Make sure to run KNN.py first.")
        raise HTTPException(status_code=500, detail="Model files not found. Model training required before API startup.")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

# Load the model and data at startup
model, data, student_features, metadata = load_model_and_data()

# Pre-process data for faster lookups
student_communities = {row['ID_Étudiant']: set(row['Communautés']) for _, row in data.iterrows()}
student_skills = {row['ID_Étudiant']: set(row['Compétences']) for _, row in data.iterrows()}
student_interests = {row['ID_Étudiant']: set(row['Centres_d\'Intérêt']) for _, row in data.iterrows()}
student_collab_work = {row['ID_Étudiant']: row['Travaux_Collaboratifs'] for _, row in data.iterrows()}
student_interactions = {row['ID_Étudiant']: row['Nombre_Interactions'] for _, row in data.iterrows()}

# Pydantic model for request validation
class QueryProfile(BaseModel):
    numeric: list[float]  # [Travaux_Collaboratifs, Nombre_Interactions]
    communautés: list[str]
    compétences: list[str]
    centres_d_intérêt: list[str]
    student_id: Optional[int] = None  # Optional student ID for existing students

# Pydantic model for student registration
class StudentRegistration(BaseModel):
    nom: str
    travaux_collaboratifs: float
    nombre_interactions: float
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

# Function to calculate cosine similarity between two student feature vectors
def calculate_content_similarity(query_features, student_features):
    similarities = {}
    
    for student_id, features in student_features.items():
        # Calculate similarity for numeric features
        query_numeric = [query_features['travaux_collaboratifs'], query_features['nombre_interactions']]
        student_numeric = [features['travaux_collaboratifs'], features['nombre_interactions']]
        
        # Calculate dot product
        dot_product = sum(q * s for q, s in zip(query_numeric, student_numeric))
        
        # Calculate magnitudes
        query_magnitude = (sum(q ** 2 for q in query_numeric)) ** 0.5
        student_magnitude = (sum(s ** 2 for s in student_numeric)) ** 0.5
        
        # Calculate numeric similarity
        numeric_similarity = dot_product / (query_magnitude * student_magnitude) if query_magnitude * student_magnitude > 0 else 0
        
        # Calculate Jaccard similarity for categorical features
        query_communities = set(query_features['communautes'].keys())
        student_communities = set(features['communautes'].keys())
        comm_similarity = len(query_communities & student_communities) / len(query_communities | student_communities) if query_communities | student_communities else 0
        
        query_skills = set(query_features['competences'].keys())
        student_skills = set(features['competences'].keys())
        skill_similarity = len(query_skills & student_skills) / len(query_skills | student_skills) if query_skills | student_skills else 0
        
        query_interests = set(query_features['interets'].keys())
        student_interests = set(features['interets'].keys())
        interest_similarity = len(query_interests & student_interests) / len(query_interests | student_interests) if query_interests | student_interests else 0
        
        # Combine similarities (weighted average)
        combined_similarity = 0.2 * numeric_similarity + 0.3 * comm_similarity + 0.3 * skill_similarity + 0.2 * interest_similarity
        similarities[student_id] = combined_similarity
    
    return similarities

# Recommendation endpoint
@app.post("/recommend/")
async def recommend_students(query_profile: QueryProfile):
    start_time = time.time()
    
    # Create a feature vector for the query profile
    query_features = {
        'travaux_collaboratifs': query_profile.numeric[0] / 10.0,  # Normalize to [0,1]
        'nombre_interactions': query_profile.numeric[1] / 100.0,  # Normalize to [0,1]
        'communautes': {comm: 1.0 for comm in query_profile.communautés},
        'competences': {skill: 1.0 for skill in query_profile.compétences},
        'interets': {interest: 1.0 for interest in query_profile.centres_d_intérêt}
    }
    
    # Check if it's an existing student
    if query_profile.student_id is not None:
        # For existing students, use collaborative filtering
        existing_student_id = query_profile.student_id
        
        # Check if student exists
        if existing_student_id not in student_features:
            raise HTTPException(status_code=404, detail=f"Student with ID {existing_student_id} not found")
        
        # Get the student's existing ratings
        similarities = defaultdict(float)
        for student_id in student_features.keys():
            if student_id != existing_student_id:
                try:
                    sim = model.sim[model.trainset.to_inner_uid(existing_student_id)][model.trainset.to_inner_uid(student_id)]
                    similarities[student_id] = sim
                except:
                    # Fall back to content-based similarity if no collaborative data
                    content_similarities = calculate_content_similarity(query_features, student_features)
                    similarities[student_id] = content_similarities[student_id]
    else:
        # For new students, use content-based filtering with our feature vectors
        # Convert query profile to ratings
        query_ratings = profile_to_ratings(query_profile)
        
        # Build a testset for the query profile
        testset = [(user_id, item_id, rating) for user_id, item_id, rating in query_ratings]
        
        # Try collaborative filtering first
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
        
        # If not enough similarities were found, use content-based approach
        if len(similarities) < 5:
            content_similarities = calculate_content_similarity(query_features, student_features)
            
            # Combine both similarity methods
            for student_id, sim in content_similarities.items():
                similarities[student_id] = similarities[student_id] * 0.7 + sim * 0.3
    
    # Sort students by similarity score and take top 5
    top_students = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
    recommended_student_ids = [student_id for student_id, _ in top_students]
    
    # Get recommended students' details
    similar_students = data[data['ID_Étudiant'].isin(recommended_student_ids)].to_dict(orient='records')
    
    # Add similarity scores and ensure all needed attributes are present
    for student in similar_students:
        student_id = student['ID_Étudiant']
        student['similarity_score'] = float(similarities[student_id])
        student['Travaux_Collaboratifs'] = float(student_collab_work.get(student_id, 0))
        student['Nombre_Interactions'] = float(student_interactions.get(student_id, 0))
        student['Communautés'] = list(student_communities.get(student_id, []))
        student['Compétences'] = list(student_skills.get(student_id, []))
        student['Centres_d_Intérêt'] = list(student_interests.get(student_id, []))
    
    processing_time = time.time() - start_time
    
    return {
        "recommended_students": similar_students,
        "metadata": {
            "processing_time_ms": round(processing_time * 1000, 2)
        }
    }

# Endpoint to register a new student
@app.post("/register/")
async def register_student(student: StudentRegistration):
    global data, student_features, student_communities, student_skills, student_interests
    
    try:
        # Get the next student ID
        next_id = data['ID_Étudiant'].max() + 1
        
        # Create new student record
        new_student = {
            'ID_Étudiant': next_id,
            'Nom': student.nom,
            'Travaux_Collaboratifs': student.travaux_collaboratifs,
            'Coéquipiers': [],  # Start with empty coequipiers
            'Communautés': student.communautés,
            'Nombre_Interactions': student.nombre_interactions,
            'Compétences': student.compétences,
            'Centres_d\'Intérêt': student.centres_d_intérêt
        }
        
        # Add to data DataFrame
        data = pd.concat([data, pd.DataFrame([new_student])], ignore_index=True)
        
        # Update lookup dictionaries
        student_communities[next_id] = set(student.communautés)
        student_skills[next_id] = set(student.compétences)
        student_interests[next_id] = set(student.centres_d_intérêt)
        student_collab_work[next_id] = student.travaux_collaboratifs
        student_interactions[next_id] = student.nombre_interactions
        
        # Create feature vector
        feature_vector = {
            'travaux_collaboratifs': student.travaux_collaboratifs / 10.0,
            'nombre_interactions': student.nombre_interactions / 100.0,
            'communautes': {comm: 1.0 for comm in student.communautés},
            'competences': {skill: 1.0 for skill in student.compétences},
            'interets': {interest: 1.0 for interest in student.centres_d_intérêt}
        }
        
        # Add to student features
        student_features[next_id] = feature_vector
        
        # Save updates to disk
        with open('data.pkl', 'wb') as f:
            pickle.dump(data, f)
            
        with open('student_features.pkl', 'wb') as f:
            pickle.dump(student_features, f)
        
        return {
            "student_id": next_id,
            "message": f"Student {student.nom} registered successfully with ID {next_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering student: {str(e)}")

# Endpoint to get all possible categories
@app.get("/categories/")
async def get_categories():
    return {
        "communities": metadata['all_communities'],
        "skills": metadata['all_skills'],
        "interests": metadata['all_interests']
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_loaded": model is not None, 
        "data_loaded": data is not None,
        "features_loaded": student_features is not None,
        "metadata_loaded": metadata is not None,
        "student_count": len(data),
        "timestamp": time.time()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)