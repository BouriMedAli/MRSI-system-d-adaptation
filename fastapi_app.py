from fastapi import FastAPI, HTTPException
import pickle
import pandas as pd
from recommendation_system import load_data, get_student_recommendations, get_community_recommendations
import os

app = FastAPI()

# Path configuration
MODELS_DIR = "models"
DATA_FILE = "dataset_etudiants.csv"

# Load models and data
def load_models_and_data():
    try:
        # Ensure models directory exists
        os.makedirs(MODELS_DIR, exist_ok=True)
        
        # Load data
        df = load_data(DATA_FILE)
        
        # Load or create models
        student_model_path = os.path.join(MODELS_DIR, 'svd_student_model.pkl')
        community_model_path = os.path.join(MODELS_DIR, 'svd_community_model.pkl')
        
        if not os.path.exists(student_model_path) or not os.path.exists(community_model_path):
            from recommendation_system import train_model, create_student_interaction_data, create_community_interaction_data
            print("Models not found, training new ones...")
            
            # Train student model
            student_interaction_df = create_student_interaction_data(df)
            student_model, _ = train_model(student_interaction_df, student_model_path)
            
            # Train community model
            community_interaction_df, all_communities = create_community_interaction_data(df)
            community_model, _ = train_model(community_interaction_df, community_model_path)
        else:
            print("Loading existing models...")
            student_model = pickle.load(open(student_model_path, 'rb'))
            community_model = pickle.load(open(community_model_path, 'rb'))
            _, all_communities = create_community_interaction_data(df)
            
        return student_model, community_model, df, all_communities
        
    except Exception as e:
        raise RuntimeError(f"Failed to load models and data: {str(e)}")

try:
    student_model, community_model, df, all_communities = load_models_and_data()
except Exception as e:
    print(f"Initialization error: {str(e)}")
    raise

@app.get("/recommend/students")
async def recommend_students(student_id: int, n: int = 5):
    try:
        recommendations = get_student_recommendations(student_id, student_model, df, n)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/recommend/communities")
async def recommend_communities(student_id: int, n: int = 5):
    try:
        recommendations = get_community_recommendations(student_id, community_model, df, all_communities, n)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)