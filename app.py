import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from surprise import Dataset, Reader, SVD, accuracy, KNNBasic
from surprise.model_selection import train_test_split, cross_validate
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

app = FastAPI(title="Student Collaboration Recommendation System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load and preprocess the data
@app.on_event("startup")
async def startup_event():
    global student_df, model_student, model_community
    
    # Load the CSV file
    if os.path.exists('/app/data/dataset_etudiants.csv'):
        file_path = '/app/data/dataset_etudiants.csv'
    else:
        file_path = 'dataset_etudiants.csv'  # For local development
        
    student_df = pd.read_csv(file_path)
    
    # Process the string representations of lists
    student_df['Coéquipiers'] = student_df['Coéquipiers'].apply(eval)
    student_df['Communautés'] = student_df['Communautés'].apply(eval)
    student_df['Compétences'] = student_df['Compétences'].apply(eval)
    student_df["Centres_d'Intérêt"] = student_df["Centres_d'Intérêt"].apply(eval)
    
    # Create models
    prepare_models()

def prepare_models():
    global model_student, model_community, metrics_student, metrics_community
    
    # Create student-student collaboration data
    collab_data = []
    for _, student in student_df.iterrows():
        student_id = student['ID_Étudiant']
        for teammate_id in student['Coéquipiers']:
            # Add this collaboration with a score based on quality of collaboration
            collab_data.append((student_id, teammate_id, student['Travaux_Collaboratifs']))
    
    # Convert to DataFrame for Surprise
    collab_df = pd.DataFrame(collab_data, columns=['userID', 'itemID', 'rating'])
    
    # Create community participation data
    community_data = []
    for _, student in student_df.iterrows():
        student_id = student['ID_Étudiant']
        for community in student['Communautés']:
            # We rate the participation based on interaction count (scaled)
            rating = min(5, student['Nombre_Interactions'] / 20)
            community_data.append((student_id, community, rating))
    
    # Convert to DataFrame for Surprise
    community_df = pd.DataFrame(community_data, columns=['userID', 'itemID', 'rating'])
    
    # Create reader and datasets
    reader = Reader(rating_scale=(1, 10))
    data_collab = Dataset.load_from_df(collab_df, reader)
    
    reader_community = Reader(rating_scale=(0, 5))
    data_community = Dataset.load_from_df(community_df, reader_community)
    
    # Split the data for evaluation
    trainset_collab, testset_collab = train_test_split(data_collab, test_size=0.2)
    trainset_community, testset_community = train_test_split(data_community, test_size=0.2)
    
    # Train the models
    model_student = SVD(n_factors=5, n_epochs=20, lr_all=0.005, reg_all=0.02)
    model_student.fit(trainset_collab)
    
    # For community recommendations, let's use KNN
    sim_options = {'name': 'pearson_baseline', 'min_support': 1}
    model_community = KNNBasic(sim_options=sim_options)
    model_community.fit(trainset_community)
    
    # Evaluate the models
    predictions_student = model_student.test(testset_collab)
    rmse_student = accuracy.rmse(predictions_student)
    mae_student = accuracy.mae(predictions_student)
    
    predictions_community = model_community.test(testset_community)
    rmse_community = accuracy.rmse(predictions_community)
    mae_community = accuracy.mae(predictions_community)
    
    # Create binary predictions for classification metrics
    actual_ratings = [pred.r_ui for pred in predictions_student]
    predicted_ratings = [pred.est for pred in predictions_student]
    
    # Convert to binary for classification metrics (above/below average)
    avg_rating = np.mean(actual_ratings)
    actual_binary = [1 if rating > avg_rating else 0 for rating in actual_ratings]
    predicted_binary = [1 if rating > avg_rating else 0 for rating in predicted_ratings]
    
    # Create confusion matrix
    cm = confusion_matrix(actual_binary, predicted_binary)
    precision = precision_score(actual_binary, predicted_binary)
    recall = recall_score(actual_binary, predicted_binary)
    f1 = f1_score(actual_binary, predicted_binary)
    
    # Store all metrics
    metrics_student = {
        "rmse": rmse_student,
        "mae": mae_student,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": cm.tolist()
    }
    
    metrics_community = {
        "rmse": rmse_community,
        "mae": mae_community
    }
    
    # Print model metrics
    print("=== Student Collaboration Model Metrics ===")
    print(f"RMSE: {rmse_student:.3f}")
    print(f"MAE: {mae_student:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1 Score: {f1:.3f}")
    print("Confusion Matrix:")
    print(f"[[{cm[0][0]}, {cm[0][1]}], [{cm[1][0]}, {cm[1][1]}]]")
    print("\n=== Community Recommendation Model Metrics ===")
    print(f"RMSE: {rmse_community:.3f}")
    print(f"MAE: {mae_community:.3f}")
    
    # Also create the confusion matrix plot for visualization
    create_confusion_matrix_plot(cm)

def create_confusion_matrix_plot(cm):
    global confusion_matrix_img
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Low Compatibility', 'High Compatibility'],
                yticklabels=['Low Compatibility', 'High Compatibility'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix for Student Collaboration Compatibility')
    
    # Save the plot to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convert the image to base64 for easy transport
    confusion_matrix_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

# Define the response models
class StudentRecommendation(BaseModel):
    student_id: int
    recommended_student_id: int
    compatibility_score: float
    shared_skills: List[str]
    shared_interests: List[str]

class CommunityRecommendation(BaseModel):
    student_id: int
    recommended_community: str
    compatibility_score: float
    related_skills: List[str]

class ModelMetrics(BaseModel):
    rmse: float
    mae: float
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    confusion_matrix: Optional[List[List[int]]] = None
    confusion_matrix_img: Optional[str] = None

# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    return {"message": "Welcome to the Student Collaboration Recommendation System API"}

@app.get("/metrics", response_model=Dict[str, ModelMetrics])
async def get_metrics():
    # Add the confusion matrix image to the student metrics
    student_metrics = metrics_student.copy()
    student_metrics["confusion_matrix_img"] = confusion_matrix_img
    
    return {
        "student_collaboration_model": ModelMetrics(**student_metrics),
        "community_recommendation_model": ModelMetrics(**metrics_community)
    }

@app.get("/recommend_students/{student_id}", response_model=List[StudentRecommendation])
async def recommend_students(student_id: int, top_n: int = Query(5, ge=1, le=20)):
    if student_id not in student_df['ID_Étudiant'].values:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    
    # Get all possible teammates
    potential_teammates = student_df[student_df['ID_Étudiant'] != student_id]['ID_Étudiant'].tolist()
    
    # Predict compatibility scores
    predictions = []
    student_data = student_df[student_df['ID_Étudiant'] == student_id].iloc[0]
    student_skills = set(student_data['Compétences'])
    student_interests = set(student_data["Centres_d'Intérêt"])
    
    for teammate_id in potential_teammates:
        # Skip existing teammates
        if teammate_id in student_data['Coéquipiers']:
            continue
            
        # Get predicted score from model
        score = model_student.predict(student_id, teammate_id).est
        
        # Get teammate data
        teammate_data = student_df[student_df['ID_Étudiant'] == teammate_id].iloc[0]
        
        # Find shared skills and interests to explain recommendation
        teammate_skills = set(teammate_data['Compétences'])
        teammate_interests = set(teammate_data["Centres_d'Intérêt"])
        
        shared_skills = list(student_skills.intersection(teammate_skills))
        shared_interests = list(student_interests.intersection(teammate_interests))
        
        # Add complementary skills factor - more unique skills means more potential for learning
        complementary_skills = len(teammate_skills - student_skills) / max(1, len(student_skills))
        
        # Adjust score based on skill complementarity
        adjusted_score = score * (1 + 0.2 * complementary_skills)
        
        predictions.append({
            "student_id": student_id,
            "recommended_student_id": teammate_id,
            "compatibility_score": adjusted_score,
            "shared_skills": shared_skills,
            "shared_interests": shared_interests
        })
    
    # Sort by score and take top_n
    predictions.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return predictions[:top_n]

@app.get("/recommend_communities/{student_id}", response_model=List[CommunityRecommendation])
async def recommend_communities(student_id: int, top_n: int = Query(3, ge=1, le=10)):
    if student_id not in student_df['ID_Étudiant'].values:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    
    # Get student data
    student_data = student_df[student_df['ID_Étudiant'] == student_id].iloc[0]
    student_communities = set(student_data['Communautés'])
    student_skills = set(student_data['Compétences'])
    
    # Get all unique communities
    all_communities = set()
    for communities in student_df['Communautés']:
        all_communities.update(communities)
    
    # Predict community compatibility for ones the student is not already in
    predictions = []
    for community in all_communities:
        if community in student_communities:
            continue
            
        # Use the model to predict compatibility
        try:
            score = model_community.predict(student_id, community).est
        except:
            # If no data available, estimate based on skills match
            score = 0
            
            # Find students in this community
            community_members = student_df[student_df['Communautés'].apply(lambda x: community in x)]
            
            # Calculate skill overlap with community members
            for _, member in community_members.iterrows():
                member_skills = set(member['Compétences'])
                skill_overlap = len(student_skills.intersection(member_skills)) / max(1, len(student_skills))
                score += skill_overlap
                
            # Normalize score
            score = min(5, score / max(1, len(community_members)))
        
        # Find skills related to this community
        community_members = student_df[student_df['Communautés'].apply(lambda x: community in x)]
        community_skills = set()
        for _, member in community_members.iterrows():
            community_skills.update(member['Compétences'])
        
        # Find skills that would be relevant for the student
        related_skills = list(community_skills - student_skills)
        
        predictions.append({
            "student_id": student_id,
            "recommended_community": community,
            "compatibility_score": score,
            "related_skills": related_skills[:3]  # Just show top 3 most relevant skills
        })
    
    # Sort by score and take top_n
    predictions.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return predictions[:top_n]

@app.get("/student_network")
async def get_student_network():
    """Get a representation of the student collaboration network for visualization"""
    # Create nodes (students)
    nodes = []
    for _, student in student_df.iterrows():
        nodes.append({
            "id": int(student['ID_Étudiant']),
            "name": student['Nom'],
            "skills": student['Compétences'],
            "interests": student["Centres_d'Intérêt"],
            "communities": student['Communautés'],
            "interaction_count": student['Nombre_Interactions']
        })
    
    # Create links (collaborations between students)
    links = []
    for _, student in student_df.iterrows():
        student_id = student['ID_Étudiant']
        for teammate_id in student['Coéquipiers']:
            # Add this collaboration
            links.append({
                "source": int(student_id),
                "target": int(teammate_id),
                "value": student['Travaux_Collaboratifs'] / 2  # Normalize a bit
            })
    
    return {"nodes": nodes, "links": links}

@app.get("/student/{student_id}")
async def get_student(student_id: int):
    """Get detailed information about a specific student"""
    if student_id not in student_df['ID_Étudiant'].values:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    
    student = student_df[student_df['ID_Étudiant'] == student_id].iloc[0].to_dict()
    
    # Get teammates' names
    teammates = []
    for teammate_id in student['Coéquipiers']:
        if teammate_id in student_df['ID_Étudiant'].values:
            teammate_name = student_df[student_df['ID_Étudiant'] == teammate_id].iloc[0]['Nom']
            teammates.append({"id": int(teammate_id), "name": teammate_name})
    
    student['Coéquipiers'] = teammates
    return student

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)