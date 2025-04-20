import pandas as pd
import ast
import os
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

# Charger le dataset
df = pd.read_csv(os.path.join("Dataset", "dataset_etudiants.csv"))

# S'assurer que la colonne 'Coéquipiers' est bien une liste
df["Coéquipiers"] = df["Coéquipiers"].apply(ast.literal_eval)

# Création de la matrice étudiant-étudiant (coéquipiers)
student_ids = df["ID_Étudiant"].tolist()
collab_matrix = pd.DataFrame(0, index=student_ids, columns=student_ids)
valid_ids = set(student_ids)

for i, row in df.iterrows():
    for teammate in row["Coéquipiers"]:
        if teammate in valid_ids:
            collab_matrix.at[row["ID_Étudiant"], teammate] = 1
            collab_matrix.at[teammate, row["ID_Étudiant"]] = 1  # Assure la symétrie

# Appliquer SVD
n_components = min(10, len(collab_matrix.columns) - 1)
svd = TruncatedSVD(n_components=n_components)
svd_matrix = svd.fit_transform(collab_matrix)

# Calcul de la similarité cosinus
similarity = cosine_similarity(svd_matrix)

# Mapping index <-> ID étudiant
index_to_id = dict(enumerate(collab_matrix.index))
id_to_index = {v: k for k, v in index_to_id.items()}

def recommander_svd(id_etudiant: int, top_n=5):
    if id_etudiant not in id_to_index:
        return None
    
    idx = id_to_index[id_etudiant]
    sim_scores = similarity[idx]
    
    # Trier par similarité (exclure l'étudiant lui-même)
    similar_indices = sim_scores.argsort()[::-1]
    similar_ids = [
        index_to_id[i] for i in similar_indices
        if index_to_id[i] != id_etudiant
    ][:top_n]
    
    # Retourner les noms et ID
    recommandations = df[df["ID_Étudiant"].isin(similar_ids)][["ID_Étudiant", "Nom"]]
    return recommandations.to_dict(orient="records")
