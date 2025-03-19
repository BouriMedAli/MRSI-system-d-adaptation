import pandas as pd
from app.utils import preprocess_data

class RecommandeurKNN:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path, encoding="utf-8")
        self.df = preprocess_data(self.df)

    def afficher_donnees(self, n=5):
        print(self.df.head(n))

# Test du modèle
if __name__ == "__main__":
    recommandeur = RecommandeurKNN("data/dataset_etudiants.csv")
    recommandeur.afficher_donnees()
