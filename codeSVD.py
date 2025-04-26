# --- Imports ---
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from sentence_transformers import SentenceTransformer

# --- 1. Chargement du dataset ---
# Remplace par le bon chemin
df = pd.read_csv('./Dataset/dataset_etudiants.csv')

# --- 2. Construction matrice de collaboration pondérée ---
num_students = df['ID_Étudiant'].nunique()
student_ids = df['ID_Étudiant'].values
student_to_idx = {id_: idx for idx, id_ in enumerate(student_ids)}
idx_to_student = {idx: id_ for id_, idx in student_to_idx.items()}

interaction_matrix = np.zeros((num_students, num_students))

for _, row in df.iterrows():
    src_idx = student_to_idx[row['ID_Étudiant']]
    if pd.isna(row['Coéquipiers']):
        continue
    coequipiers = eval(str(row['Coéquipiers']))
    for coequipier in coequipiers:
        if coequipier in student_to_idx:
            tgt_idx = student_to_idx[coequipier]
            interaction_matrix[src_idx, tgt_idx] += row['Nombre_Interactions'] / 10  # Pondération

# --- 3. SVD sur la matrice ---
svd = TruncatedSVD(n_components=20, random_state=42)
latent_matrix = svd.fit_transform(interaction_matrix)

# --- 4. Embedding des profils (compétences, centres d'intérêt, communautés) ---
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_profile_text(row):
    comp = eval(str(row['Compétences']))
    interets = eval(str(row["Centres_d'Intérêt"]))
    commu = eval(str(row['Communautés']))
    profile = ' '.join(comp + interets + commu)
    return profile

profiles = df.apply(create_profile_text, axis=1)
profile_embeddings = model.encode(profiles.tolist())

# --- 5. Calcul de similarité de profil ---
profile_similarity = cosine_similarity(profile_embeddings)

# --- 6. Fusion SVD latent + Similarité de profil ---
latent_similarity = cosine_similarity(latent_matrix)
final_similarity = 0.7 * latent_similarity + 0.3 * profile_similarity

# --- 7. Fonction de recommandation ---
def recommend(student_id, top_n=5):
    if student_id not in student_to_idx:
        return []
    idx = student_to_idx[student_id]
    scores = final_similarity[idx]
    top_indices = scores.argsort()[::-1][1:top_n+1]
    recommended_ids = [idx_to_student[i] for i in top_indices]
    return recommended_ids

# --- 8. Exemple d'utilisation ---
student_id_to_test = 3
recommendations = recommend(student_id_to_test, top_n=5)
print(f"\n\U0001f680 Recommandations pour l'étudiant {student_id_to_test}: {recommendations}")