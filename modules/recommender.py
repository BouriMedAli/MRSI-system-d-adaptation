#recommender.py
import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from . import evaluation


from .evaluation import train_knn_model, train_svd_model

# 1. Load the dataset.
import os


def load_data():
    csv_path = os.path.join("dataset", "dataset_etudiants.csv")
    df = pd.read_csv(csv_path)
    
    # Vérification des colonnes essentielles
    required_columns = ["ID_Étudiant", "Nom", "Compétences", "Nombre_Interactions"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Colonne manquante: {col}")
    
    return df

# 2. Preprocess the features: convert list-like columns and create a combined textual feature.
def preprocess_features(df):
    for col in ["Coéquipiers", "Communautés", "Compétences", "Centres_d'Intérêt"]:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    def combine_features(row):
        features = []
        if isinstance(row["Communautés"], list):
            features.extend(row["Communautés"])
        if isinstance(row["Compétences"], list):
            features.extend(row["Compétences"])
        if isinstance(row["Centres_d'Intérêt"], list):
            features.extend(row["Centres_d'Intérêt"])
        features.append(str(row["Travaux_Collaboratifs"]))
        features.append(str(row["Nombre_Interactions"]))
        return " ".join(features)
    
    df["combined_features"] = df.apply(combine_features, axis=1)
    return df

# 3. Compute the cosine similarity matrix.
def compute_similarity_matrix(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df["combined_features"])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim



# Global preprocessing.
df = load_data()
df = preprocess_features(df)
cosine_sim = compute_similarity_matrix(df)

# 4. Global recommendations based on 'Nombre_Interactions'.
def get_global_recommendations():
    top_students = df.sort_values("Nombre_Interactions", ascending=False).head(6)
    recommendations = []
    for _, row in top_students.iterrows():
        recommendations.append({
            "ID": row["ID_Étudiant"],
            "Nom": row["Nom"],
            "Nombre_Interactions": row["Nombre_Interactions"]
        })
    return recommendations

# 5. Personalized recommendations using cosine similarity.
def get_user_recommendations(user_id, top_n=6):
    df = preprocess_features(load_data())  # Recharger à chaque requête
    cosine_sim = compute_similarity_matrix(df)
    # Find the index of the user in the DataFrame
    idx_list = df.index[df["ID_Étudiant"] == user_id].tolist()
    if not idx_list:
        return []  # If student not found.
    idx = idx_list[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [score for score in sim_scores if score[0] != idx][:top_n]
    
    recommendations = []
    for i, score in sim_scores:
        student = df.iloc[i]
        recommendations.append({
            "ID": student["ID_Étudiant"],
            "Nom": student["Nom"],
            "Similarity": score
        })
    return recommendations

# 6. Compare models by calling the evaluation module.
def compare_models():
    results = evaluation.evaluate_surprise_models("dataset/dataset_etudiants.csv")
    return results





def add_user_to_dataset(new_user):
    try:
        # Charger les données fraîches
        global_df = load_data()
        
        # Générer l'ID
        new_id = 1 if global_df.empty else global_df["ID_Étudiant"].max() + 1
        new_user["ID_Étudiant"] = new_id
        
        # Ajouter le nouvel utilisateur
        updated_df = pd.concat([global_df, pd.DataFrame([new_user])], ignore_index=True)
        
        # Sauvegarder de manière atomique
        temp_path = "dataset/temp.csv"
        final_path = "dataset/dataset_etudiants.csv"
        updated_df.to_csv(temp_path, index=False)
        os.replace(temp_path, final_path)
        
        # Mettre à jour les variables globales
        global df, cosine_sim
        df = preprocess_features(updated_df)
        cosine_sim = compute_similarity_matrix(df)
        
    except Exception as e:
        print(f"Error in add_user_to_dataset: {str(e)}")
        raise




def get_knn_recommendations(user_id, top_n=5):
    try:
        trainset, model = evaluation.train_knn_model()
        testset = trainset.build_anti_testset()
        predictions = model.test(testset)
        
        # Récupérer les compétences prédites pour l'utilisateur
        user_skills = [p.iid for p in predictions if p.uid == str(user_id)]
        user_skills = sorted(user_skills, key=lambda x: x.est, reverse=True)[:top_n]
        
        # Trouver les étudiants ayant ces compétences
        df = preprocess_features(load_data())
        recommendations = []
        for skill in user_skills:
            skilled_students = df[df["Compétences"].apply(lambda x: skill in x)]
            for _, student in skilled_students.iterrows():
                recommendations.append({
                    "Nom": student["Nom"],
                    "Compétence": skill,
                    "Score": student["Nombre_Interactions"] / 100  # Score basé sur les interactions
                })
        
        return sorted(recommendations, key=lambda x: x["Score"], reverse=True)[:top_n]

    except Exception as e:
        print(f"KNN Error: {str(e)}")
        return []

def get_svd_recommendations(user_id, top_n=5):
    try:
        trainset, model = evaluation.train_svd_model()
        testset = trainset.build_anti_testset()
        predictions = model.test(testset)
        
        
        user_preds = [p for p in predictions if p.uid == str(user_id)]
        user_preds.sort(key=lambda x: x.est, reverse=True)
        
        return [{
            "Nom": df[df["ID_Étudiant"] == int(p.iid)]["Nom"].values[0],
            "Score": p.est
        } for p in user_preds[:top_n]]
    except Exception as e:
        print(f"SVD Error: {str(e)}")
        return []