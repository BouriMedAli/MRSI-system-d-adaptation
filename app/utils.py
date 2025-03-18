import pandas as pd
import ast

def preprocess_data(df, is_query=False):
    print("Colonnes disponibles :", df.columns)  # Debug

    # Vérifier la présence des colonnes attendues
    required_columns = ["Compétences", "Centres_d'Intérêt", "Coéquipiers", "Communautés"]
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Erreur: La colonne '{col}' est absente. Colonnes trouvées : {df.columns}")

    # Parser les colonnes contenant des listes stockées en string
    def parse_list(value):
        try:
            return ast.literal_eval(value) if isinstance(value, str) else value
        except Exception:
            return []

    df["Compétences"] = df["Compétences"].apply(parse_list)
    df["Centres_d'Intérêt"] = df["Centres_d'Intérêt"].apply(parse_list)
    df["Coéquipiers"] = df["Coéquipiers"].apply(parse_list)
    df["Communautés"] = df["Communautés"].apply(parse_list)

    return df
