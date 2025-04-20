import pandas as pd
import os

# Chemin du fichier CSV local
FICHIER_CSV = 'backend/dataset_etudiants.csv'  # Utilisez un chemin relatif ou configurez un chemin dynamique

# Charger le fichier CSV dans un DataFrame pandas
def charger_donnees():
    try:
        # Vérifiez si le fichier existe
        if not os.path.exists(FICHIER_CSV):
            print(f"Erreur : le fichier '{FICHIER_CSV}' n'existe pas.")
            return None
        
        # Chargement des données à partir du fichier CSV
        etudiants = pd.read_csv(FICHIER_CSV)

        # Affichage des noms de colonnes pour vérification avant renommage
        print(f"Colonnes avant renommage : {etudiants.columns.tolist()}")

        # Renommer la colonne "Centres d'Intérêt" pour éviter l'usage d'apostrophes dans le nom
        etudiants.rename(columns={"Centres_d'Intérêt": "Centres_d_Interet"}, inplace=True)
        etudiants.columns = etudiants.columns.str.strip()

        # Affichage des noms de colonnes après renommage
        print(f"Colonnes après renommage : {etudiants.columns.tolist()}")

        # Vérification des colonnes attendues
        required_columns = ['Nom', 'Compétences', "Centres_d_Interet", 'Travaux_Collaboratifs']
        for col in required_columns:
            if col not in etudiants.columns:
                print(f"Erreur : La colonne '{col}' est manquante dans le fichier CSV.")
                return None

        # Afficher un aperçu des données (les premières lignes)
        print("Aperçu des données :")
        print(etudiants.head())  # Cela affiche les 5 premières lignes du fichier CSV pour vérifier les données

        return etudiants

    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV : {e}")
        return None

# Fonction pour afficher les étudiants
def afficher_etudiants():
    etudiants = charger_donnees()
    if etudiants is not None:
        # Affichage des étudiants
        print("\nListe des étudiants :")
        for index, row in etudiants.iterrows():
            print(f"Nom: {row['Nom']}, Compétences: {row['Compétences']}, Centres d'Intérêt: {row['Centres_d_Interet']}")
    else:
        print("Aucune donnée à afficher.")

# Appeler la fonction pour afficher les étudiants
afficher_etudiants()
