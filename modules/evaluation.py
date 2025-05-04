# modules/evaluation.py
import pandas as pd
import ast
from surprise import Dataset, Reader, KNNBasic, SVD
from surprise.model_selection import cross_validate


def create_ratings_df(csv_path: str = "dataset/dataset_etudiants.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    try:
        df["Compétences"] = df["Compétences"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
    except Exception as e:
        print("Error parsing 'Compétences' column:", e)
        return pd.DataFrame()

    ratings = []
    for _, row in df.iterrows():
        student_id = row["ID_Étudiant"]
        num_interactions = row["Nombre_Interactions"]
        compétences = row["Compétences"]  # <-- Ajoutez cette ligne
        
        # Normalize interactions to 0-5 scale
        #normalized_score = min((num_interactions / 100.0) * 5, 5)  # Plafonner à 5
        normalized_score = min((num_interactions / 100.0) * 5, 5) * (1 + len(compétences)/10)  

        for competence in compétences:
            ratings.append((str(student_id), competence, float(normalized_score)))
    
    return pd.DataFrame(ratings, columns=["user", "item", "rating"])




def evaluate_surprise_models(csv_path: str = "dataset/dataset_etudiants.csv") -> dict:
    try:
        ratings_df = create_ratings_df(csv_path)
        if ratings_df.empty:
            return {"error": "No valid ratings data available"}

        reader = Reader(rating_scale=(0, 5))  # Changed scale to 0-5
        data = Dataset.load_from_df(ratings_df[["user", "item", "rating"]], reader)
        
        # Use fewer folds and handle empty results
        knn_results = cross_validate(KNNBasic(), data, measures=["RMSE", "MAE"], cv=5, verbose=False)
        svd_results = cross_validate(SVD(), data, measures=["RMSE", "MAE"], cv=5, verbose=False)
        

        return {
            "KNN": {
                "RMSE": round(float(sum(knn_results["test_rmse"]) / len(knn_results["test_rmse"])), 2),
                "MAE": round(float(sum(knn_results["test_mae"]) / len(knn_results["test_mae"])), 2)
            },
            "SVD": {
                "RMSE": round(float(sum(svd_results["test_rmse"]) / len(svd_results["test_rmse"])), 2),
                "MAE": round(float(sum(svd_results["test_mae"]) / len(svd_results["test_mae"])), 2)
            }
        }
    except Exception as e:
        print(f"Error in evaluate_surprise_models: {str(e)}")
        return {"error": str(e)}

def train_knn_model():
    ratings_df = create_ratings_df()
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(ratings_df[["user", "item", "rating"]], reader)
    trainset = data.build_full_trainset()
    model = KNNBasic(sim_options={'name': 'cosine', 'user_based': True})
    model.fit(trainset)
    return trainset, model

def train_svd_model():
    ratings_df = create_ratings_df()
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(ratings_df[["user", "item", "rating"]], reader)
    trainset = data.build_full_trainset()
    model = SVD()
    model.fit(trainset)
    return trainset, model