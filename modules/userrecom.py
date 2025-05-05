# userrecom.py
import os
import json
import re
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from ast import literal_eval
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# Configuration initiale
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.0-flash"


STUDENT_CSV = "dataset/dataset_etudiants.csv"
COURSE_CSV = "dataset/cours.csv"

class StudentRecommender:
    def __init__(self):
        self.df_students = self._preprocess_data()
        self.feature_matrix = self._create_feature_matrix()
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.df_courses = pd.read_csv(COURSE_CSV)

    def _preprocess_data(self):
        """Charge et prétraite les données étudiantes"""
        df = pd.read_csv(STUDENT_CSV)
        
        # Conversion des colonnes stringifiées
        list_cols = ['Coéquipiers', 'Communautés', 'Compétences', 'Centres_d\'Intérêt']
        for col in list_cols:
            df[col] = df[col].apply(lambda x: literal_eval(str(x)) if pd.notnull(x) else [])
        
        # Nettoyage des données
        df['Coéquipiers'] = df['Coéquipiers'].apply(lambda x: x if isinstance(x, list) else [])
        df['Nombre_Interactions'] = df['Nombre_Interactions'].fillna(0)
        
        return df

    def _create_feature_matrix(self):
        """Crée la matrice de caractéristiques combinées"""
        # Encodage des caractéristiques catégorielles
        mlb_skills = MultiLabelBinarizer()
        mlb_interests = MultiLabelBinarizer()
        mlb_communities = MultiLabelBinarizer()
        
        skills_encoded = mlb_skills.fit_transform(self.df_students['Compétences'])
        interests_encoded = mlb_interests.fit_transform(self.df_students['Centres_d\'Intérêt'])
        communities_encoded = mlb_communities.fit_transform(self.df_students['Communautés'])
        
        # Normalisation des caractéristiques numériques
        scaler = MinMaxScaler()
        numerical_features = scaler.fit_transform(
            self.df_students[['Travaux_Collaboratifs', 'Nombre_Interactions']]
        )
        
        return np.hstack([
            numerical_features,
            skills_encoded,
            interests_encoded,
            communities_encoded
        ])

    def _knn_recommendations(self, student_id, top_n=5):
        """Génère les recommandations basées sur KNN et similarité cosinus"""
        try:
            student_idx = self.df_students[self.df_students['ID_Étudiant'] == student_id].index[0]
            similarities = cosine_similarity(
                [self.feature_matrix[student_idx]], 
                self.feature_matrix
            )[0]
            
            similar_indices = np.argsort(similarities)[::-1][1:top_n+1]
            similar_students = self.df_students.iloc[similar_indices]
            
            # Extraction des recommandations
            skills = pd.Series([
                skill for skills in similar_students['Compétences'] for skill in skills
            ]).value_counts().head(3).index.tolist()
            
            communities = pd.Series([
                comm for comms in similar_students['Communautés'] for comm in comms
            ]).value_counts().head(2).index.tolist()
            
            return {
                "skills": skills,
                "communities": communities,
                "similar_peers": similar_students[[
                    'ID_Étudiant', 'Nom', 'Compétences', 'Centres_d\'Intérêt'
                ]].to_dict('records')
            }
        except Exception as e:
            return {"error": str(e)}

    def _llm_recommendations(self, student_id, top_n=5):
        """Génère les recommandations d’étudiants similaires avec Gemini."""
        try:
            student_data = self.df_students[self.df_students['ID_Étudiant'] == student_id].iloc[0]

            # --- MODIFICATION ICI ---
            # Générer la chaîne du DataFrame séparément
            students_string = self.df_students[['ID_Étudiant','Nom','Compétences','Centres_d\'Intérêt']].to_string(index=False)
            # ------------------------

            prompt = f"""
            Voici les données de l'étudiant cible :
            {json.dumps(student_data.to_dict(), indent=2)}

            Parmi l'ensemble des étudiants suivants :
            {students_string} # Utiliser la variable ici

            Propose-moi jusqu'à {top_n} étudiants similaires en JSON, sous la forme :
            {{
              "similar_peers": [
                {{"ID_Étudiant": ..., "Nom": "...", "Compétences": [...], "Centres_d'Intérêt": [...]}},
                …
              ]
            }}
            """
            # ... reste de la méthode
            response = self.model.generate_content(prompt)
            cleaned = re.sub(r'^```json\s*|\s*```$', '', response.text, flags=re.MULTILINE)
            data = json.loads(cleaned)
            return {
                "similar_peers": data.get("similar_peers", [])[:top_n]
            }
        except Exception as e:
            return {"error": str(e)}

    def get_recommendations(self, student_id, reco_type='hybrid'):
        result = {"status": "success", "student_id": student_id, "recommendations": {}}
        try:
            if reco_type in ['knn', 'hybrid']:
                result['recommendations']['knn'] = self._knn_recommendations(student_id)
            if reco_type in ['llm', 'hybrid']:
                # on passe top_n à 5 ou la valeur souhaitée
                result['recommendations']['llm'] = self._llm_recommendations(student_id, top_n=5)
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        return result

# Exemple d'utilisation
if __name__ == "__main__":
    recommender = StudentRecommender()
    
    # Test avec un étudiant existant
    sample_student = 1
    recommendations = recommender.get_recommendations(sample_student,"llm")
    
    print(json.dumps(recommendations, indent=2, ensure_ascii=False))





