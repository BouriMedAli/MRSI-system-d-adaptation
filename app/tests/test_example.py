from app.model import RecommandeurKNN  # Assure-toi que c'est bien `app.model` et pas `app.main`

def test_recommandation():
    """Test de la fonction recommander() pour s'assurer qu'elle fonctionne correctement"""
    # Initialisation du modèle avec les données d'entraînement
    recommander_instance = RecommandeurKNN("data/dataset_etudiants.csv")

    # Définition des données d'entrée pour un étudiant fictif
    input_data = {
        "Travaux_Collaboratifs": 3,
        "Coéquipiers": 5,
        "Communautés": 2,
        "Nombre_Interactions": 10,
        "Compétences": "Python, Machine Learning",
        "Centres_d'Intérêt": "IA, Data Science"
    }

    # Exécution de la recommandation
    result = recommander_instance.recommander(input_data)

    # Vérifications
    assert isinstance(result, list), "Le résultat doit être une liste"
    assert len(result) > 0, "La liste de recommandations ne doit pas être vide"
    assert all(isinstance(rec, dict) and "ID_Étudiant" in rec for rec in result), "Chaque recommandation doit être un dictionnaire contenant 'ID_Étudiant'"

    # Optionnel : vérifier un ID attendu si les résultats sont déterministes
    # assert result[0]["ID_Étudiant"] == 42  # Exemple : si l'étudiant 42 est toujours recommandé en premier

