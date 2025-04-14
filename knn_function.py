import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

# Charger les données
df = pd.read_csv("etudiants.csv")
df.columns = [col.strip() for col in df.columns]

def explode_features(df, column_name):
    new_rows = []
    for idx, row in df.iterrows():
        try:
            items = eval(row[column_name]) if isinstance(row[column_name], str) else row[column_name]
            if isinstance(items, list):
                for item in items:
                    new_rows.append((row["ID_Étudiant"], f"{column_name}:{str(item).strip()}"))
            else:
                new_rows.append((row["ID_Étudiant"], f"{column_name}:{str(items).strip()}"))
        except:
            continue
    return new_rows

features = []
for col in ["Compétences", "Centres_d'Intérêt", "Communautés"]:
    features.extend(explode_features(df, col))

df_interactions = pd.DataFrame(features, columns=["userID", "itemID"])
df_interactions["rating"] = 1

interaction_matrix = df_interactions.pivot_table(index="userID", columns="itemID", values="rating", fill_value=0)

model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
model_knn.fit(interaction_matrix)

def recommander(etudiant_id, top_n=5):
    try:
        etudiant_id = int(etudiant_id)
        data = interaction_matrix.loc[[etudiant_id]]
        distances, indices = model_knn.kneighbors(data, n_neighbors=top_n + 1)
        voisins = interaction_matrix.index[indices.flatten()[1:]]  # Exclure l'étudiant lui-même

        suggestion_amis = list(voisins)

        etudiant_row = df[df["ID_Étudiant"] == etudiant_id].iloc[0]
        competences_etudiant = set(eval(etudiant_row["Compétences"]))
        interets_etudiant = set(eval(etudiant_row["Centres_d'Intérêt"]))

        suggestions_competences = set()
        suggestions_interets = set()

        for voisin_id in suggestion_amis:
            voisin_row = df[df["ID_Étudiant"] == voisin_id].iloc[0]
            competences_voisin = set(eval(voisin_row["Compétences"]))
            interets_voisin = set(eval(voisin_row["Centres_d'Intérêt"]))

            suggestions_competences.update(competences_voisin - competences_etudiant)
            suggestions_interets.update(interets_voisin - interets_etudiant)

        return {
            "suggestion_amis": suggestion_amis,
            "suggestion_competences": list(suggestions_competences),
            "suggestion_interets": list(suggestions_interets)
        }

    except KeyError:
        return {"error": "Étudiant non trouvé dans les données."}
    except Exception as e:
        return {"error": f"Erreur lors du traitement : {str(e)}"}
