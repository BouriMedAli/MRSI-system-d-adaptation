import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

# Étape 1 : Charger la dataset
df = pd.read_csv("Dataset/dataset_etudiants.csv")

# Étape 2 : Prétraitement des données
mlb_skills = MultiLabelBinarizer()
skills_encoded = mlb_skills.fit_transform(df['Compétences'])
skills_df = pd.DataFrame(skills_encoded, columns=mlb_skills.classes_)

mlb_interests = MultiLabelBinarizer()
interests_encoded = mlb_interests.fit_transform(df["Centres_d'Intérêt"])
interests_df = pd.DataFrame(interests_encoded, columns=mlb_interests.classes_)

df['Nombre_Interactions'] = (df['Nombre_Interactions'] - df['Nombre_Interactions'].min()) / (df['Nombre_Interactions'].max() - df['Nombre_Interactions'].min())

features = pd.concat([skills_df, interests_df, df[['Nombre_Interactions']]], axis=1)

# Étape 3 : Construire la matrice de collaborations
n_students = len(df)
collaboration_matrix = np.zeros((n_students, n_students), dtype=int)

for i in range(n_students):
    for j in range(i + 1, n_students):
        # Vérifie s'il y a AU MOINS UN projet commun (split par virgule si plusieurs)
        projects_i = set(str(df.iloc[i]['Travaux_Collaboratifs']).split(','))
        projects_j = set(str(df.iloc[j]['Travaux_Collaboratifs']).split(','))
        if projects_i & projects_j:
            collaboration_matrix[i, j] = 1
            collaboration_matrix[j, i] = 1

# Étape 4 : Modèle KNN
k = 3
knn = NearestNeighbors(n_neighbors=k, metric='euclidean')
knn.fit(features)

# Étape 5 : Fonction de recommandation
def recommend_collaborators(student_id, k=3):
    student_idx = df.index[df['ID_Étudiant'] == student_id].tolist()[0]
    distances, indices = knn.kneighbors(features.iloc[[student_idx]], n_neighbors=k + 1)
    recommended_indices = indices[0][1:]

    recommendations = []
    print(f"\nRecommandations pour {df.iloc[student_idx]['Nom']} :")
    print(f"  Compétences : {df.iloc[student_idx]['Compétences']}")
    print(f"  Centres d'Intérêt : {df.iloc[student_idx]['Centres_d\'Intérêt']}\n")
    print("Étudiants recommandés pour collaboration :")
    for idx in recommended_indices:
        student_info = {
            "Nom": df.iloc[idx]['Nom'],
            "ID_Étudiant": int(df.iloc[idx]['ID_Étudiant']),
            "Compétences": df.iloc[idx]['Compétences'],
            "Centres_d'Intérêt": df.iloc[idx]['Centres_d\'Intérêt'],
            "Distance": distances[0][list(recommended_indices).index(idx)]
        }
        recommendations.append(student_info)
        print(f"- {df.iloc[idx]['Nom']} (ID: {df.iloc[idx]['ID_Étudiant']})")
        print(f"  Compétences : {df.iloc[idx]['Compétences']}")
        print(f"  Centres d'Intérêt : {df.iloc[idx]['Centres_d\'Intérêt']}")
        print(f"  Distance : {distances[0][list(recommended_indices).index(idx)]:.4f}\n")

    return recommendations


# Étape 6 : Évaluation
def evaluate_recommendations_cosine(k=3):
    y_true = []
    y_pred = []

    # Calcul de la Similarité Cosinus pour chaque étudiant
    for i in range(len(df)):
        student_features = features.iloc[i].values.reshape(1, -1)
        student_features = pd.DataFrame(student_features, columns=features.columns)
        # Trouver les voisins de l'étudiant
        _, indices = knn.kneighbors(student_features, n_neighbors=k + 1)  # Ne pas mettre un tableau de 3D
        recommended_indices = indices[0][1:]  # Exclure l'étudiant lui-même

        # Comparer la similarité entre l'étudiant et ses voisins recommandés
        for j in range(len(df)):
            if i == j:
                continue
            # Calcul de la similarité cosinus entre l'étudiant i et l'étudiant j
            similarity = cosine_similarity([student_features.iloc[0].values], [features.iloc[j].values])[0][0]
            y_true.append(1 if j in recommended_indices else 0)
            y_pred.append(similarity)

    # Calculer la moyenne des scores de similarité
    avg_similarity = np.mean(y_pred)

    print("\nÉvaluation avec Cosine Similarity :")
    print(f" - Similarité moyenne des recommandations : {avg_similarity:.2f}")
    return avg_similarity

# Étape 7 : Tester la recommandation
student_id_to_test = 1
recommend_collaborators(student_id_to_test, k=3)

# Étape 8 : Évaluer
evaluate_recommendations_cosine(k=3)