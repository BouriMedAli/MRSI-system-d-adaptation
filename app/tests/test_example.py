from app.main import RecommandeurKNN  # Assure-toi d'importer correctement la classe

def test_recommandation():
    recommander_instance = RecommandeurKNN("data/dataset_etudiants.csv")  # Instanciation de la classe
    result = recommander_instance.recommander({
        "Travaux_Collaboratifs": 3,
        "Coéquipiers": 5,
        "Communautés": 2,
        "Nombre_Interactions": 10,
        "Compétences": "Python, Machine Learning",
        "Centres_d'Intérêt": "IA, Data Science"
    })
    assert result is not None  # Exemple de validation, tu peux ajuster ce test en fonction des résultats attendus
