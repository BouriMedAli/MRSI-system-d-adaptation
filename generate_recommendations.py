import pandas as pd
import joblib
import pickle
import ast

print("Chargement du modèle et des données...")
model = joblib.load('model.pkl')
df = pd.read_pickle('students_df.pkl')
print(f"Modèle et données chargés. Nombre d'étudiants : {len(df)}")

def normalize_score(score, min_score=1, max_score=5):
    """Normalise un score pour qu'il soit dans [min_score, max_score]."""
    if score > max_score:
        return max_score
    if score < min_score:
        return min_score
    return score

def get_recommendations(student_id, model, df, n_recommendations=5, skill_filter=None, interest_filter=None, skill_weight=0.5, interest_weight=0.5):
    all_teammates = set()
    for index, row in df.iterrows():
        teammates = ast.literal_eval(row['Coéquipiers'])
        for teammate_id in teammates:
            all_teammates.add(f"student_{teammate_id}")

    student_row = df[df['ID_Étudiant'] == student_id]
    if student_row.empty:
        error_msg = f"Étudiant {student_id} non trouvé."
        print(error_msg)
        return None, error_msg
    
    student_skills = set(ast.literal_eval(student_row['Compétences'].iloc[0]))
    student_interests = set(ast.literal_eval(student_row.get('Centres_d\'Intérêt', ['[]']).iloc[0]))
    
    # Afficher les compétences et centres d'intérêt uniquement si demandé (par exemple, pour les étudiants 2 et 15)
    student_info = {
        "skills": student_skills,
        "interests": student_interests,
        "teammates": None
    }
    
    known_teammates = set()
    current_teammates = ast.literal_eval(student_row['Coéquipiers'].iloc[0])
    for teammate_id in current_teammates:
        known_teammates.add(f"student_{teammate_id}")

    potential_teammates = all_teammates - known_teammates
    if not potential_teammates:
        error_msg = f"Aucun nouveau coéquipier à recommander pour l'étudiant {student_id}."
        print(error_msg)
        return None, error_msg

    predictions = []
    for item in potential_teammates:
        teammate_id = int(item.replace("student_", ""))
        teammate_row = df[df['ID_Étudiant'] == teammate_id]
        if not teammate_row.empty:
            teammate_skills = set(ast.literal_eval(teammate_row['Compétences'].iloc[0]))
            teammate_interests = set(ast.literal_eval(teammate_row.get('Centres_d\'Intérêt', ['[]']).iloc[0]))
            
            # Vérifier si au moins une compétence du filtre est dans teammate_skills
            skill_match = True
            if skill_filter:  # Si skill_filter est une liste non vide
                skill_match = any(skill in teammate_skills for skill in skill_filter)
            
            # Vérifier si au moins un centre d'intérêt du filtre est dans teammate_interests
            interest_match = True
            if interest_filter:  # Si interest_filter est une liste non vide
                interest_match = any(interest in teammate_interests for interest in interest_filter)
            
            if skill_match or interest_match:
                pred = model.predict(student_id, item)
                # Calculer skill_score en fonction du nombre de compétences correspondantes
                skill_score = 0.5
                if skill_filter:
                    matching_skills = sum(1 for skill in skill_filter if skill in teammate_skills)
                    skill_score = 0.5 + 0.5 * (matching_skills / len(skill_filter))  # Bonus proportionnel
                # Calculer interest_score en fonction du nombre de centres d'intérêt correspondants
                interest_score = 0.5
                if interest_filter:
                    matching_interests = sum(1 for interest in interest_filter if interest in teammate_interests)
                    interest_score = 0.5 + 0.5 * (matching_interests / len(interest_filter))  # Bonus proportionnel
                skill_diversity_bonus = 0.2 * len(teammate_skills - student_skills)
                interest_diversity_bonus = 0.1 * len(teammate_interests - student_interests)
                weighted_score = pred.est * (skill_weight * skill_score + interest_weight * interest_score) + skill_diversity_bonus + interest_diversity_bonus
                # Normaliser le score à [1, 5]
                weighted_score = normalize_score(weighted_score)
                predictions.append((item, weighted_score))

    if not predictions:
        error_msg = f"Aucun coéquipier correspondant aux critères pour l'étudiant {student_id}."
        print(error_msg)
        return None, error_msg

    predictions.sort(key=lambda x: x[1], reverse=True)

    recommended_teammates = []
    for item, score in predictions[:n_recommendations]:
        teammate_id = int(item.replace("student_", ""))
        if teammate_id != student_id:
            recommended_teammates.append((teammate_id, score))

    student_info["teammates"] = recommended_teammates
    return student_info, None

# Exécuter get_recommendations pour des étudiants spécifiques et pour tous les étudiants
if __name__ == "__main__":
    n_recommendations = 5
    skill_filter = ["Python", "Blockchain"]
    interest_filter = ["Robotique", "Hackathon"]
    skill_weight = 0.7
    interest_weight = 0.3

    # Exemple détaillé pour l'Étudiant 2
    student_id = 2
    print(f"\nLancement des recommandations pour l'étudiant {student_id}...")
    result, error = get_recommendations(
        student_id=student_id,
        model=model,
        df=df,
        n_recommendations=n_recommendations,
        skill_filter=skill_filter,
        interest_filter=interest_filter,
        skill_weight=skill_weight,
        interest_weight=interest_weight
    )
    
    if error:
        print(f"Erreur pour l'étudiant {student_id} : {error}")
    else:
        print(f"\nCompétences de l'étudiant {student_id} : {result['skills']}")
        print(f"Centres d'intérêt de l'étudiant {student_id} : {result['interests']}")
        print(f"\nRecommandations pour l'étudiant {student_id} :")
        for teammate_id, score in result["teammates"]:
            teammate_row = df[df['ID_Étudiant'] == teammate_id]
            teammate_skills = ast.literal_eval(teammate_row['Compétences'].iloc[0]) if not teammate_row.empty else []
            teammate_interests = ast.literal_eval(teammate_row.get('Centres_d\'Intérêt', ['[]']).iloc[0]) if not teammate_row.empty else []
            print(f"- Étudiant {teammate_id} : Score {score:.2f}")
            print(f"  Compétences : {teammate_skills}")
            print(f"  Centres d'intérêt : {teammate_interests}")
        print("Recommandations générées avec succès.")

    # Exemple détaillé pour l'Étudiant 15
    student_id = 15
    print(f"\nLancement des recommandations pour l'étudiant {student_id}...")
    result, error = get_recommendations(
        student_id=student_id,
        model=model,
        df=df,
        n_recommendations=n_recommendations,
        skill_filter=skill_filter,
        interest_filter=interest_filter,
        skill_weight=skill_weight,
        interest_weight=interest_weight
    )
    
    if error:
        print(f"Erreur pour l'étudiant {student_id} : {error}")
    else:
        print(f"\nCompétences de l'étudiant {student_id} : {result['skills']}")
        print(f"Centres d'intérêt de l'étudiant {student_id} : {result['interests']}")
        print(f"\nRecommandations pour l'étudiant {student_id} :")
        for teammate_id, score in result["teammates"]:
            teammate_row = df[df['ID_Étudiant'] == teammate_id]
            teammate_skills = ast.literal_eval(teammate_row['Compétences'].iloc[0]) if not teammate_row.empty else []
            teammate_interests = ast.literal_eval(teammate_row.get('Centres_d\'Intérêt', ['[]']).iloc[0]) if not teammate_row.empty else []
            print(f"- Étudiant {teammate_id} : Score {score:.2f}")
            print(f"  Compétences : {teammate_skills}")
            print(f"  Centres d'intérêt : {teammate_interests}")
        print("Recommandations générées avec succès.")

    # Recommandations pour tous les étudiants (ID et score uniquement)
    print("\nRecommandations pour tous les étudiants  :")
    for student_id in range(1, 51):  # Parcourir les étudiants de 1 à 50
        print(f"\nÉtudiant {student_id} :")
        result, error = get_recommendations(
            student_id=student_id,
            model=model,
            df=df,
            n_recommendations=n_recommendations,
            skill_filter=skill_filter,
            interest_filter=interest_filter,
            skill_weight=skill_weight,
            interest_weight=interest_weight
        )
        
        if error:
            print(f"Erreur : {error}")
        else:
            for teammate_id, score in result["teammates"]:
                print(f"- Étudiant {teammate_id} : Score {score:.2f}")