from fastapi import FastAPI, HTTPException
import pickle
import pandas as pd
from recommendation_system import load_data, get_student_recommendations, get_community_recommendations

app = FastAPI()

# Load models and data
student_model = pickle.load(open('svd_student_model.pkl', 'rb'))
community_model = pickle.load(open('svd_community_model.pkl', 'rb'))
df = load_data('dataset_etudiants.csv')
all_communities = set()
for communities in df['Communautés']:
    all_communities.update(communities)
all_communities = list(all_communities)

@app.get("/recommend/students")
async def recommend_students(student_id: int, n: int = 5):
    try:
        recommendations = get_student_recommendations(student_id, student_model, df, n)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/recommend/communities")
async def recommend_communities(student_id: int, n: int = 5):
    try:
        recommendations = get_community_recommendations(student_id, community_model, df, all_communities, n)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)