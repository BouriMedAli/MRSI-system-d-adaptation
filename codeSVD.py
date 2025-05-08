# import pandas as pd
# import numpy as np
# from surprise import Dataset, Reader, SVD
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import ast
# import logging
# import os

# # Configuration des journaux
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Variables globales
# df = None
# svd_model = None
# text_embeddings = None
# content_similarity_matrix = None
# student_ids = []
# student_to_idx = {}
# idx_to_student = {}
# vectorizer = None
# ratings_df = None  # Initialisation de la variable à None au début


# def init_model():
#     """
#     Initialise le modèle de recommandation en chargeant les données, entraînant SVD et calculant les similarités textuelles.
#     Raises:
#         FileNotFoundError: Si le fichier CSV est introuvable.
#         ValueError: Si les données sont invalides ou incohérentes.
#     """
#     global df, svd_model, text_embeddings, content_similarity_matrix
#     global student_ids, student_to_idx, idx_to_student, vectorizer
#     global ratings_df 

#     logger.info("Initialisation du modèle...")

#     # Chargement des données
#     csv_path = "./Dataset/dataset_etudiants.csv"
#     if not os.path.exists(csv_path):
#         logger.error(f"Fichier {csv_path} introuvable.")
#         raise FileNotFoundError(f"Le fichier {csv_path} est introuvable.")
    
#     try:
#         df = pd.read_csv(csv_path)
#     except pd.errors.EmptyDataError:
#         logger.error("Le fichier CSV est vide.")
#         raise ValueError("Le fichier CSV est vide.")

#     # Vérification des colonnes requises
#     required_columns = ["ID_Étudiant", "Coéquipiers", "Communautés", "Compétences", "Centres_d'Intérêt"]
#     if not all(col in df.columns for col in required_columns):
#         missing_cols = [col for col in required_columns if col not in df.columns]
#         logger.error(f"Colonnes manquantes : {missing_cols}")
#         raise ValueError(f"Colonnes manquantes dans le dataset : {missing_cols}")

#     # Vérification de l'unicité des ID_Étudiant
#     if df["ID_Étudiant"].duplicated().any():
#         logger.error("Les ID_Étudiant doivent être uniques.")
#         raise ValueError("Les ID_Étudiant doivent être uniques.")

#     # Conversion des colonnes en listes
#     for col in ["Coéquipiers", "Communautés", "Compétences", "Centres_d'Intérêt"]:
#         try:
#             df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x if isinstance(x, list) else [])
#         except (ValueError, SyntaxError) as e:
#             logger.error(f"Erreur lors de la conversion de la colonne {col} : {e}")
#             raise ValueError(f"Erreur de formatage dans la colonne {col} : {e}")

#     # Construction des interactions
#     interactions = []
#     interaction_counts = {}
#     all_teammates = set()
#     for _, row in df.iterrows():
#         student_id = row["ID_Étudiant"]
#         teammates = row["Coéquipiers"]
#         interaction_counts[student_id] = len(teammates)
#         for teammate in teammates:
#             interactions.append((student_id, teammate, 1.0))
#             all_teammates.add(teammate)

#     # Vérification de la validité des coéquipiers
#     invalid_teammates = all_teammates - set(df["ID_Étudiant"])
#     if invalid_teammates:
#         logger.error(f"Identifiants de coéquipiers invalides : {invalid_teammates}")
#         raise ValueError(f"Identifiants de coéquipiers invalides : {invalid_teammates}")

#     if not interactions:
#         logger.error("Aucune interaction trouvée dans les données.")
#         raise ValueError("Aucune interaction trouvée dans les données.")

#     df["Nombre_Interactions"] = df["ID_Étudiant"].map(interaction_counts).fillna(0).astype(int)

#     # Entraînement SVD
#     logger.info("Entraînement du modèle SVD...")
#     reader = Reader(rating_scale=(0, 1))
#     data = Dataset.load_from_df(pd.DataFrame(interactions, columns=["userID", "itemID", "rating"]), reader)
#     trainset = data.build_full_trainset()
#     svd_model = SVD(n_factors=20)
#     svd_model.fit(trainset)

#     # Profil textuel pour contenu
#     df["profil_textuel"] = df["Compétences"].apply(lambda x: " ".join(map(str, x))) + " " + \
#                            df["Centres_d'Intérêt"].apply(lambda x: " ".join(map(str, x))) + " " + \
#                            df["Communautés"].apply(lambda x: " ".join(map(str, x)))

#     # Vérification des profils textuels
#     if df["profil_textuel"].str.strip().eq("").all():
#         logger.error("Tous les profils textuels sont vides.")
#         raise ValueError("Tous les profils textuels sont vides.")

#     vectorizer = TfidfVectorizer()
#     text_embeddings = vectorizer.fit_transform(df["profil_textuel"])
#     content_similarity_matrix = cosine_similarity(text_embeddings)
#     logger.info("Matrice de similarité textuelle calculée.")

#     # Indexation des étudiants
#     student_ids.clear()
#     student_ids.extend(df["ID_Étudiant"].tolist())
#     student_to_idx.clear()
#     student_to_idx.update({id_: i for i, id_ in enumerate(student_ids)})
#     idx_to_student.clear()
#     idx_to_student.update({i: id_ for i, id_ in enumerate(student_ids)})
#     logger.info("Initialisation terminée avec succès.")

#     ratings_df = pd.DataFrame(interactions, columns=["userID", "itemID", "rating"])

# def recommend(student_id, top_n=5, use_surprise=False, use_hybrid=False):
#     """
#     Génère des recommandations de coéquipiers pour un étudiant donné.
#     Args:
#         student_id: ID de l'étudiant.
#         top_n: Nombre de recommandations à retourner (défaut : 5).
#         use_surprise: Si True, utilise SVD (filtrage collaboratif).
#         use_hybrid: Si True, utilise l'approche hybride (SVD + contenu).
#     Returns:
#         Liste des top_n identifiants d'étudiants recommandés.
#     """
#     if student_id not in student_to_idx:
#         logger.warning(f"ID étudiant {student_id} non trouvé.")
#         return []

#     logger.info(f"Génération de recommandations pour l'étudiant {student_id}...")
#     if use_hybrid:
#         return hybrid_predict(student_id, student_ids, top_n)
#     elif use_surprise:
#         return svd_predict(student_id, student_ids, top_n)
#     else:
#         return content_predict(student_id, top_n)

# def svd_predict(student_id, all_student_ids, top_n):
#     """
#     Prédit les coéquipiers à l'aide du modèle SVD.
#     Args:
#         student_id: ID de l'étudiant.
#         all_student_ids: Liste de tous les ID d'étudiants.
#         top_n: Nombre de recommandations.
#     Returns:
#         Liste des top_n identifiants d'étudiants.
#     """
#     predictions = np.array([(other_id, svd_model.predict(student_id, other_id).est)
#                            for other_id in all_student_ids if other_id != student_id])
#     if predictions.size == 0:
#         return []
#     top_indices = np.argsort(predictions[:, 1])[::-1][:top_n]
#     return predictions[top_indices, 0].astype(int).tolist()

# def content_predict(student_id, top_n):
#     """
#     Prédit les coéquipiers à l'aide de la similarité textuelle.
#     Args:
#         student_id: ID de l'étudiant.
#         top_n: Nombre de recommandations.
#     Returns:
#         Liste des top_n identifiants d'étudiants.
#     """
#     idx = student_to_idx[student_id]
#     scores = content_similarity_matrix[idx]
#     top_indices = np.argsort(scores)[::-1][1:top_n+1]
#     return [idx_to_student[i] for i in top_indices]

# def hybrid_predict(student_id, all_student_ids, top_n):
#     """
#     Prédit les coéquipiers en combinant SVD et similarité textuelle.
#     Args:
#         student_id: ID de l'étudiant.
#         all_student_ids: Liste de tous les ID d'étudiants.
#         top_n: Nombre de recommandations.
#     Returns:
#         Liste des top_n identifiants d'étudiants.
#     """
#     if student_id not in student_to_idx:
#         logger.warning(f"ID étudiant {student_id} non trouvé dans hybrid_predict.")
#         return []

#     profile_idx = student_to_idx[student_id]
#     nb_interactions = df.loc[df['ID_Étudiant'] == student_id, 'Nombre_Interactions'].values[0]
#     max_interactions = df['Nombre_Interactions'].max()
#     alpha = min(max(nb_interactions / max_interactions if max_interactions > 0 else 0.5, 0.1), 0.9)

#     predictions = np.array([(other_id,
#                             alpha * svd_model.predict(student_id, other_id).est +
#                             (1 - alpha) * content_similarity_matrix[profile_idx][student_to_idx[other_id]])
#                            for other_id in all_student_ids if other_id != student_id])
#     if predictions.size == 0:
#         return []
#     top_indices = np.argsort(predictions[:, 1])[::-1][:top_n]
#     return predictions[top_indices, 0].astype(int).tolist()

# if __name__ == "__main__":
#     # Exemple de test
#     try:
#         init_model()
#         print("Recommandations par contenu pour l'étudiant :", recommend(5, top_n=5))
#         print("Recommandations SVD pour l'étudiant 5:", recommend(5, top_n=5, use_surprise=True))
#         print("Recommandations hybrides pour l'étudiant 5:", recommend(5, top_n=5, use_hybrid=True))
#         print("Recommandations pour ID invalide:", recommend(999))
#     except Exception as e:
#         logger.error(f"Erreur lors de l'exécution : {e}")
import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import logging
import os

# Configuration des journaux
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variables globales
df = None
svd_model = None
text_embeddings = None
content_similarity_matrix = None
student_ids = []
student_to_idx = {}
idx_to_student = {}
vectorizer = None
ratings_df = None

def init_model():
    """
    Initialise le modèle de recommandation en chargeant les données, entraînant SVD et calculant les similarités textuelles.
    Raises:
        FileNotFoundError: Si le fichier CSV est introuvable.
        ValueError: Si les données sont invalides ou incohérentes.
    """
    global df, svd_model, text_embeddings, content_similarity_matrix
    global student_ids, student_to_idx, idx_to_student, vectorizer
    global ratings_df

    logger.info("Initialisation du modèle...")

    # Chargement des données
    csv_path = "./Dataset/dataset_etudiants.csv"
    if not os.path.exists(csv_path):
        logger.error(f"Fichier {csv_path} introuvable.")
        raise FileNotFoundError(f"Le fichier {csv_path} est introuvable.")
    
    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        logger.error("Le fichier CSV est vide.")
        raise ValueError("Le fichier CSV est vide.")

    # Vérification des colonnes requises
    required_columns = ["ID_Étudiant", "Coéquipiers", "Communautés", "Compétences", "Centres_d'Intérêt", "Nom"]
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        logger.error(f"Colonnes manquantes : {missing_cols}")
        raise ValueError(f"Colonnes manquantes dans le dataset : {missing_cols}")

    # Vérification de l'unicité des ID_Étudiant
    if df["ID_Étudiant"].duplicated().any():
        logger.error("Les ID_Étudiant doivent être uniques.")
        raise ValueError("Les ID_Étudiant doivent être uniques.")

    # Conversion des colonnes en listes
    for col in ["Coéquipiers", "Communautés", "Compétences", "Centres_d'Intérêt"]:
        try:
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x if isinstance(x, list) else [])
        except (ValueError, SyntaxError) as e:
            logger.error(f"Erreur lors de la conversion de la colonne {col} : {e}")
            raise ValueError(f"Erreur de formatage dans la colonne {col} : {e}")

    # Construction des interactions
    interactions = []
    interaction_counts = {}
    all_teammates = set()
    for _, row in df.iterrows():
        student_id = row["ID_Étudiant"]
        teammates = row["Coéquipiers"]
        interaction_counts[student_id] = len(teammates)
        for teammate in teammates:
            interactions.append((student_id, teammate, 1.0))
            all_teammates.add(teammate)

    # Vérification de la validité des coéquipiers
    invalid_teammates = all_teammates - set(df["ID_Étudiant"])
    if invalid_teammates:
        logger.error(f"Identifiants de coéquipiers invalides : {invalid_teammates}")
        raise ValueError(f"Identifiants de coéquipiers invalides : {invalid_teammates}")

    if not interactions:
        logger.error("Aucune interaction trouvée dans les données.")
        raise ValueError("Aucune interaction trouvée dans les données.")

    df["Nombre_Interactions"] = df["ID_Étudiant"].map(interaction_counts).fillna(0).astype(int)

    # Entraînement SVD
    logger.info("Entraînement du modèle SVD...")
    reader = Reader(rating_scale=(0, 1))
    data = Dataset.load_from_df(pd.DataFrame(interactions, columns=["userID", "itemID", "rating"]), reader)
    trainset = data.build_full_trainset()
    svd_model = SVD(n_factors=20)
    svd_model.fit(trainset)

    # Profil textuel pour contenu
    df["profil_textuel"] = df["Compétences"].apply(lambda x: " ".join(map(str, x))) + " " + \
                           df["Centres_d'Intérêt"].apply(lambda x: " ".join(map(str, x))) + " " + \
                           df["Communautés"].apply(lambda x: " ".join(map(str, x)))

    # Vérification des profils textuels
    if df["profil_textuel"].str.strip().eq("").all():
        logger.error("Tous les profils textuels sont vides.")
        raise ValueError("Tous les profils textuels sont vides.")

    vectorizer = TfidfVectorizer()
    text_embeddings = vectorizer.fit_transform(df["profil_textuel"])
    content_similarity_matrix = cosine_similarity(text_embeddings)
    logger.info("Matrice de similarité textuelle calculée.")

    # Indexation des étudiants
    student_ids.clear()
    student_ids.extend(df["ID_Étudiant"].tolist())
    student_to_idx.clear()
    student_to_idx.update({id_: i for i, id_ in enumerate(student_ids)})
    idx_to_student.clear()
    idx_to_student.update({i: id_ for i, id_ in enumerate(student_ids)})
    logger.info("Initialisation terminée avec succès.")

    ratings_df = pd.DataFrame(interactions, columns=["userID", "itemID", "rating"])

def recommend(student_id, top_n=5, use_surprise=False, use_hybrid=False):
    """
    Génère des recommandations de coéquipiers pour un étudiant donné.
    Args:
        student_id: ID de l'étudiant.
        top_n: Nombre de recommandations à retourner (défaut : 5).
        use_surprise: Si True, utilise SVD (filtrage collaboratif).
        use_hybrid: Si True, utilise l'approche hybride (SVD + contenu).
    Returns:
        Liste de dictionnaires contenant ID_Étudiant et Nom des étudiants recommandés.
    """
    if student_id not in student_to_idx:
        logger.warning(f"ID étudiant {student_id} non trouvé.")
        return []

    logger.info(f"Génération de recommandations pour l'étudiant {student_id}...")
    if use_hybrid:
        ids = hybrid_predict(student_id, student_ids, top_n)
    elif use_surprise:
        ids = svd_predict(student_id, student_ids, top_n)
    else:
        ids = content_predict(student_id, top_n)

    # Retourner une liste de dictionnaires avec ID et Nom
    result = [
        {"ID_Étudiant": id_, "Nom": df[df["ID_Étudiant"] == id_]["Nom"].iloc[0]}
        for id_ in ids if id_ in df["ID_Étudiant"].values
    ]
    return result

def svd_predict(student_id, all_student_ids, top_n):
    """
    Prédit les coéquipiers à l'aide du modèle SVD.
    Args:
        student_id: ID de l'étudiant.
        all_student_ids: Liste de tous les ID d'étudiants.
        top_n: Nombre de recommandations.
    Returns:
        Liste des top_n identifiants d'étudiants.
    """
    predictions = np.array([(other_id, svd_model.predict(student_id, other_id).est)
                           for other_id in all_student_ids if other_id != student_id])
    if predictions.size == 0:
        return []
    top_indices = np.argsort(predictions[:, 1])[::-1][:top_n]
    return predictions[top_indices, 0].astype(int).tolist()

def content_predict(student_id, top_n):
    """
    Prédit les coéquipiers à l'aide de la similarité textuelle.
    Args:
        student_id: ID de l'étudiant.
        top_n: Nombre de recommandations.
    Returns:
        Liste des top_n identifiants d'étudiants.
    """
    idx = student_to_idx[student_id]
    scores = content_similarity_matrix[idx]
    top_indices = np.argsort(scores)[::-1][1:top_n+1]
    return [idx_to_student[i] for i in top_indices]

def hybrid_predict(student_id, all_student_ids, top_n):
    """
    Prédit les coéquipiers en combinant SVD et similarité textuelle.
    Args:
        student_id: ID de l'étudiant.
        all_student_ids: Liste de tous les ID d'étudiants.
        top_n: Nombre de recommandations.
    Returns:
        Liste des top_n identifiants d'étudiants.
    """
    if student_id not in student_to_idx:
        logger.warning(f"ID étudiant {student_id} non trouvé dans hybrid_predict.")
        return []

    profile_idx = student_to_idx[student_id]
    nb_interactions = df.loc[df['ID_Étudiant'] == student_id, 'Nombre_Interactions'].values[0]
    max_interactions = df['Nombre_Interactions'].max()
    alpha = min(max(nb_interactions / max_interactions if max_interactions > 0 else 0.5, 0.1), 0.9)

    predictions = np.array([(other_id,
                            alpha * svd_model.predict(student_id, other_id).est +
                            (1 - alpha) * content_similarity_matrix[profile_idx][student_to_idx[other_id]])
                           for other_id in all_student_ids if other_id != student_id])
    if predictions.size == 0:
        return []
    top_indices = np.argsort(predictions[:, 1])[::-1][:top_n]
    return predictions[top_indices, 0].astype(int).tolist()

if __name__ == "__main__":
    # Exemple de test
    try:
        init_model()
        print("Recommandations par contenu pour l'étudiant 5:", recommend(5, top_n=5))
        print("Recommandations SVD pour l'étudiant 5:", recommend(5, top_n=5, use_surprise=True))
        print("Recommandations hybrides pour l'étudiant 5:", recommend(5, top_n=5, use_hybrid=True))
        print("Recommandations pour ID invalide:", recommend(999))
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution : {e}")