import pandas as pd
import joblib
import pickle
import ast
import random
from collections import Counter

print("Chargement du modèle et des données...")
model = joblib.load('model.pkl')
df = pd.read_pickle('students_df.pkl')
print(f"Modèle et données chargés. Nombre d'étudiants : {len(df)}")

# Liste statique de compétences et centres d'intérêt programmatiques (qui ne sont pas dans la base)
PROGRAMMATIC_SKILLS = [
    "Machine Learning", "Cloud Computing", "DevOps", "Cybersecurity", "Augmented Reality",
    "Natural Language Processing", "Game Development", "Quantum Computing", "3D Modeling", "Ethical Hacking"
]
PROGRAMMATIC_INTERESTS = [
    "Photography", "Artificial Intelligence Ethics", "Space Exploration", "Virtual Reality", "Sustainable Tech",
    "Digital Art", "Cyberpunk Culture", "Astronomy", "Board Games", "Urban Farming"
]

# Liste statique de ressources pour les cours recommandés (copiée depuis streamlit_app.py)
RECOMMENDED_COURSES = {
    # Compétences dans la base
    "Python": [
        ("Introduction à Python pour les débutants - YouTube", "https://youtube.com/watch?v=python-intro"),
        ("Cours Python avancé - Udemy", "https://udemy.com/course/python-advanced")
    ],
    "IA": [
        ("Introduction à l'IA - Coursera", "https://coursera.org/learn/intro-to-ai"),
        ("Tutoriel sur l'IA avec Python - YouTube", "https://youtube.com/watch?v=ai-tutorial")
    ],
    "Blockchain": [
        ("Les bases de la Blockchain - Udemy", "https://udemy.com/course/blockchain-basics"),
        ("Comprendre la Blockchain - YouTube", "https://youtube.com/watch?v=blockchain-explained")
    ],
    "Marketing": [
        ("Marketing Digital 101 - Coursera", "https://coursera.org/learn/digital-marketing-101"),
        ("Stratégies de Marketing - YouTube", "https://youtube.com/watch?v=marketing-strategies")
    ],
    "Design": [
        ("Introduction au Design UX/UI - Udemy", "https://udemy.com/course/ux-ui-design"),
        ("Tutoriel de Design Graphique - YouTube", "https://youtube.com/watch?v=design-tutorial")
    ],
    "Data Science": [
        ("Data Science pour débutants - Coursera", "https://coursera.org/learn/data-science-intro"),
        ("Analyse de données avec Python - YouTube", "https://youtube.com/watch?v=data-science-python")
    ],
    "SQL": [
        ("Apprendre SQL pour les débutants - Udemy", "https://udemy.com/course/sql-basics"),
        ("Tutoriel SQL - YouTube", "https://youtube.com/watch?v=sql-tutorial")
    ],
    "Communication": [
        ("Cours de Communication Efficace - Coursera", "https://coursera.org/learn/effective-communication"),
        ("Améliorer ses compétences en communication - YouTube", "https://youtube.com/watch?v=communication-skills")
    ],
    "SEO": [
        ("Introduction au SEO - Udemy", "https://udemy.com/course/seo-basics"),
        ("Tutoriel SEO pour débutants - YouTube", "https://youtube.com/watch?v=seo-tutorial")
    ],
    "Publicité": [
        ("Les bases de la Publicité en ligne - Coursera", "https://coursera.org/learn/online-advertising"),
        ("Créer des campagnes publicitaires - YouTube", "https://youtube.com/watch?v=advertising-campaigns")
    ],
    "UX/UI": [
        ("Introduction au Design UX/UI - Udemy", "https://udemy.com/course/ux-ui-design"),
        ("Principes de UX/UI - YouTube", "https://youtube.com/watch?v=ux-ui-principles")
    ],
    "Graphisme": [
        ("Cours de Graphisme pour débutants - Udemy", "https://udemy.com/course/graphic-design-basics"),
        ("Tutoriel Photoshop - YouTube", "https://youtube.com/watch?v=photoshop-tutorial")
    ],
    "Prototypage": [
        ("Prototypage avec Figma - Udemy", "https://udemy.com/course/prototyping-figma"),
        ("Introduction au prototypage - YouTube", "https://youtube.com/watch?v=prototyping-intro")
    ],
    "Cryptographie": [
        ("Les bases de la Cryptographie - Coursera", "https://coursera.org/learn/cryptography-basics"),
        ("Introduction à la Cryptographie - YouTube", "https://youtube.com/watch?v=cryptography-intro")
    ],
    "Sécurité": [
        ("Introduction à la Cybersécurité - Udemy", "https://udemy.com/course/cybersecurity-basics"),
        ("Les bases de la Sécurité Informatique - YouTube", "https://youtube.com/watch?v=security-basics")
    ],
    "Smart Contracts": [
        ("Créer des Smart Contracts avec Solidity - Udemy", "https://udemy.com/course/smart-contracts-solidity"),
        ("Tutoriel Smart Contracts - YouTube", "https://youtube.com/watch?v=smart-contracts-tutorial")
    ],
    "Statistiques": [
        ("Introduction aux Statistiques - Coursera", "https://coursera.org/learn/statistics-intro"),
        ("Statistiques pour débutants - YouTube", "https://youtube.com/watch?v=statistics-basics")
    ],
    "Big Data": [
        ("Les bases du Big Data - Udemy", "https://udemy.com/course/big-data-basics"),
        ("Introduction au Big Data - YouTube", "https://youtube.com/watch?v=big-data-intro")
    ],
    # Compétences programmatiques (pas dans la base)
    "Machine Learning": [
        ("Introduction au Machine Learning - Coursera", "https://coursera.org/learn/machine-learning-intro"),
        ("Tutoriel Machine Learning - YouTube", "https://youtube.com/watch?v=ml-tutorial"),
        ("Guide ML (PDF)", "https://example.com/ml-guide.pdf")
    ],
    "Cloud Computing": [
        ("Les bases du Cloud Computing - Udemy", "https://udemy.com/course/cloud-computing-basics"),
        ("Introduction au Cloud - YouTube", "https://youtube.com/watch?v=cloud-intro"),
        ("Cloud Computing Guide (PDF)", "https://example.com/cloud-guide.pdf")
    ],
    "DevOps": [
        ("Introduction à DevOps - Coursera", "https://coursera.org/learn/devops-intro"),
        ("Tutoriel DevOps - YouTube", "https://youtube.com/watch?v=devops-tutorial"),
        ("DevOps Essentials (PDF)", "https://example.com/devops-essentials.pdf")
    ],
    "Cybersecurity": [
        ("Introduction à la Cybersécurité - Udemy", "https://udemy.com/course/cybersecurity-basics"),
        ("Les bases de la Cybersécurité - YouTube", "https://youtube.com/watch?v=cybersecurity-basics"),
        ("Cybersecurity Guide (PDF)", "https://example.com/cybersecurity-guide.pdf")
    ],
    "Augmented Reality": [
        ("Introduction à la Réalité Augmentée - Udemy", "https://udemy.com/course/ar-basics"),
        ("Tutoriel AR - YouTube", "https://youtube.com/watch?v=ar-tutorial"),
        ("AR Development Guide (PDF)", "https://example.com/ar-guide.pdf")
    ],
    "Natural Language Processing": [
        ("Introduction au NLP - Coursera", "https://coursera.org/learn/nlp-intro"),
        ("Tutoriel NLP - YouTube", "https://youtube.com/watch?v=nlp-tutorial"),
        ("NLP Basics (PDF)", "https://example.com/nlp-basics.pdf")
    ],
    "Game Development": [
        ("Développement de jeux avec Unity - Udemy", "https://udemy.com/course/game-dev-unity"),
        ("Créer un jeu simple - YouTube", "https://youtube.com/watch?v=game-dev-tutorial"),
        ("Game Dev Guide (PDF)", "https://example.com/game-dev-guide.pdf")
    ],
    "Quantum Computing": [
        ("Introduction au Calcul Quantique - Coursera", "https://coursera.org/learn/quantum-computing-intro"),
        ("Les bases du Calcul Quantique - YouTube", "https://youtube.com/watch?v=quantum-computing-basics"),
        ("Quantum Computing Intro (PDF)", "https://example.com/quantum-computing-intro.pdf")
    ],
    "3D Modeling": [
        ("Introduction à la Modélisation 3D - Udemy", "https://udemy.com/course/3d-modeling-basics"),
        ("Tutoriel Blender - YouTube", "https://youtube.com/watch?v=blender-tutorial"),
        ("3D Modeling Guide (PDF)", "https://example.com/3d-modeling-guide.pdf")
    ],
    "Ethical Hacking": [
        ("Introduction à l'Ethical Hacking - Coursera", "https://coursera.org/learn/ethical-hacking-intro"),
        ("Les bases de l'Ethical Hacking - YouTube", "https://youtube.com/watch?v=ethical-hacking-basics"),
        ("Ethical Hacking Guide (PDF)", "https://example.com/ethical-hacking-guide.pdf")
    ],
    # Centres d'intérêt dans la base
    "Robotique": [
        ("Introduction à la Robotique - YouTube", "https://youtube.com/watch?v=robotics-intro"),
        ("Cours sur la Robotique - edX", "https://edx.org/course/robotics-basics"),
        ("Guide Robotique (PDF)", "https://example.com/robotics-guide.pdf")
    ],
    "Hackathon": [
        ("Comment se préparer pour un Hackathon - Blog", "https://example.com/hackathon-prep"),
        ("Top 10 Astuces pour Hackathons - YouTube", "https://youtube.com/watch?v=hackathon-tips"),
        ("Hackathon Guide (PDF)", "https://example.com/hackathon-guide.pdf")
    ],
    "Musique": [
        ("Apprendre la théorie musicale - YouTube", "https://youtube.com/watch?v=music-theory"),
        ("Cours de piano pour débutants - Udemy", "https://udemy.com/course/piano-basics"),
        ("Théorie Musicale (PDF)", "https://example.com/music-theory.pdf")
    ],
    "Jeux vidéo": [
        ("Développement de jeux vidéo avec Unity - Udemy", "https://udemy.com/course/game-dev-unity"),
        ("Créer un jeu simple - YouTube", "https://youtube.com/watch?v=game-dev-tutorial"),
        ("Guide Jeux Vidéo (PDF)", "https://example.com/game-dev-guide.pdf")
    ],
    "Écologie": [
        ("Introduction au développement durable - Coursera", "https://coursera.org/learn/sustainability"),
        ("Comprendre l'écologie - YouTube", "https://youtube.com/watch?v=ecology-explained"),
        ("Guide Écologie (PDF)", "https://example.com/ecology-guide.pdf")
    ],
    "Technologie": [
        ("Les tendances technologiques 2025 - YouTube", "https://youtube.com/watch?v=tech-trends-2025"),
        ("Introduction à la Technologie - Coursera", "https://coursera.org/learn/intro-to-technology"),
        ("Tendances Tech (PDF)", "https://example.com/tech-trends.pdf")
    ],
    "Entrepreneuriat": [
        ("Les bases de l'Entrepreneuriat - Udemy", "https://udemy.com/course/entrepreneurship-basics"),
        ("Démarrer une startup - YouTube", "https://youtube.com/watch?v=startup-guide"),
        ("Guide Entrepreneuriat (PDF)", "https://example.com/entrepreneurship-guide.pdf")
    ],
    "Innovation": [
        ("Cours sur l'Innovation et la Créativité - Coursera", "https://coursera.org/learn/innovation-creativity"),
        ("Comment innover - YouTube", "https://youtube.com/watch?v=innovation-tips"),
        ("Guide Innovation (PDF)", "https://example.com/innovation-guide.pdf")
    ],
    "Art": [
        ("Introduction à l'Art Contemporain - Udemy", "https://udemy.com/course/contemporary-art"),
        ("Tutoriel de dessin - YouTube", "https://youtube.com/watch?v=drawing-tutorial"),
        ("Guide Art (PDF)", "https://example.com/art-guide.pdf")
    ],
    "Créativité": [
        ("Développer sa Créativité - Coursera", "https://coursera.org/learn/develop-creativity"),
        ("Exercices de Créativité - YouTube", "https://youtube.com/watch?v=creativity-exercises"),
        ("Guide Créativité (PDF)", "https://example.com/creativity-guide.pdf")
    ],
    "Développement": [
        ("Introduction au Développement Web - Udemy", "https://udemy.com/course/web-development-basics"),
        ("Tutoriel de programmation - YouTube", "https://youtube.com/watch?v=programming-tutorial"),
        ("Guide Développement (PDF)", "https://example.com/development-guide.pdf")
    ],
    "E-sport": [
        ("Introduction à l'E-sport - YouTube", "https://youtube.com/watch?v=esport-intro"),
        ("Devenir pro en E-sport - Blog", "https://example.com/esport-guide"),
        ("Guide E-sport (PDF)", "https://example.com/esport-guide.pdf")
    ],
    "Développement Durable": [
        ("Introduction au Développement Durable - Coursera", "https://coursera.org/learn/sustainability"),
        ("Les bases du Développement Durable - YouTube", "https://youtube.com/watch?v=sustainability-basics"),
        ("Guide Développement Durable (PDF)", "https://example.com/sustainability-guide.pdf")
    ],
    "Sciences": [
        ("Introduction aux Sciences - edX", "https://edx.org/course/science-basics"),
        ("Découvrir les Sciences - YouTube", "https://youtube.com/watch?v=science-discovery"),
        ("Guide Sciences (PDF)", "https://example.com/science-guide.pdf")
    ],
    "Nature": [
        ("Explorer la Nature - YouTube", "https://youtube.com/watch?v=nature-exploration"),
        ("Cours sur l'Écologie et la Nature - Coursera", "https://coursera.org/learn/ecology-nature"),
        ("Guide Nature (PDF)", "https://example.com/nature-guide.pdf")
    ],
    # Centres d'intérêt programmatiques (pas dans la base)
    "Photography": [
        ("Introduction à la Photographie - Udemy", "https://udemy.com/course/photography-basics"),
        ("Tutoriel Photographie - YouTube", "https://youtube.com/watch?v=photography-tutorial"),
        ("Guide Photographie (PDF)", "https://example.com/photography-guide.pdf")
    ],
    "Artificial Intelligence Ethics": [
        ("Éthique en IA - Coursera", "https://coursera.org/learn/ai-ethics"),
        ("Introduction à l'Éthique en IA - YouTube", "https://youtube.com/watch?v=ai-ethics-intro"),
        ("Guide Éthique IA (PDF)", "https://example.com/ai-ethics-guide.pdf")
    ],
    "Space Exploration": [
        ("Introduction à l'Exploration Spatiale - edX", "https://edx.org/course/space-exploration"),
        ("L'Exploration Spatiale - YouTube", "https://youtube.com/watch?v=space-exploration"),
        ("Guide Exploration Spatiale (PDF)", "https://example.com/space-exploration-guide.pdf")
    ],
    "Virtual Reality": [
        ("Introduction à la Réalité Virtuelle - Udemy", "https://udemy.com/course/vr-basics"),
        ("Tutoriel VR - YouTube", "https://youtube.com/watch?v=vr-tutorial"),
        ("Guide VR (PDF)", "https://example.com/vr-guide.pdf")
    ],
    "Sustainable Tech": [
        ("Technologies Durables - Coursera", "https://coursera.org/learn/sustainable-tech"),
        ("Introduction aux Tech Durables - YouTube", "https://youtube.com/watch?v=sustainable-tech"),
        ("Guide Tech Durable (PDF)", "https://example.com/sustainable-tech-guide.pdf")
    ],
    "Digital Art": [
        ("Introduction à l'Art Numérique - Udemy", "https://udemy.com/course/digital-art-basics"),
        ("Tutoriel Art Numérique - YouTube", "https://youtube.com/watch?v=digital-art-tutorial"),
        ("Guide Art Numérique (PDF)", "https://example.com/digital-art-guide.pdf")
    ],
    "Cyberpunk Culture": [
        ("Introduction à la Culture Cyberpunk - Blog", "https://example.com/cyberpunk-culture"),
        ("Explorer le Cyberpunk - YouTube", "https://youtube.com/watch?v=cyberpunk-culture"),
        ("Guide Culture Cyberpunk (PDF)", "https://example.com/cyberpunk-culture-guide.pdf")
    ],
    "Astronomy": [
        ("Introduction à l'Astronomie - Coursera", "https://coursera.org/learn/astronomy-intro"),
        ("Les bases de l'Astronomie - YouTube", "https://youtube.com/watch?v=astronomy-basics"),
        ("Guide Astronomie (PDF)", "https://example.com/astronomy-guide.pdf")
    ],
    "Board Games": [
        ("Introduction aux Jeux de Société - Blog", "https://example.com/board-games-intro"),
        ("Découvrir les Jeux de Société - YouTube", "https://youtube.com/watch?v=board-games"),
        ("Guide Jeux de Société (PDF)", "https://example.com/board-games-guide.pdf")
    ],
    "Urban Farming": [
        ("Introduction à l'Agriculture Urbaine - Udemy", "https://udemy.com/course/urban-farming-basics"),
        ("Les bases de l'Agriculture Urbaine - YouTube", "https://youtube.com/watch?v=urban-farming"),
        ("Guide Agriculture Urbaine (PDF)", "https://example.com/urban-farming-guide.pdf")
    ]
}

def normalize_score(score, min_score=1, max_score=5):
    """Normalise un score pour qu'il soit dans [min_score, max_score]."""
    if score > max_score:
        return max_score
    if score < min_score:
        return min_score
    return score

def get_recommended_skills_and_interests(student_id, student_skills, student_interests, df, potential_teammates=None):
    """Recommande des compétences et centres d'intérêt en fonction des coéquipiers identifiés par KNNWithZScore."""
    recommended_skills_from_db = []
    recommended_interests_from_db = []

    # Étape 1 : Recommandations basées sur les coéquipiers (actuels ou prédits)
    if potential_teammates is not None:
        current_teammates = [int(teammate.replace("student_", "")) for teammate in potential_teammates]
    else:
        student_row = df[df['ID_Étudiant'] == student_id]
        if student_row.empty:
            return [], [], [], []
        current_teammates = ast.literal_eval(student_row['Coéquipiers'].iloc[0])

    teammates_skills = []
    teammates_interests = []
    for teammate_id in current_teammates:
        teammate_row = df[df['ID_Étudiant'] == teammate_id]
        if not teammate_row.empty:
            teammate_skills = ast.literal_eval(teammate_row['Compétences'].iloc[0])
            teammate_interests = ast.literal_eval(teammate_row['Centres_d\'Intérêt'].iloc[0] if 'Centres_d\'Intérêt' in teammate_row.columns else '[]')
            teammates_skills.extend(teammate_skills)
            teammates_interests.extend(teammate_interests)

    skill_counts = Counter(teammates_skills)
    interest_counts = Counter(teammates_interests)

    recommended_skills_from_db = [skill for skill, count in skill_counts.most_common() if skill not in student_skills][:3]
    recommended_interests_from_db = [interest for interest, count in interest_counts.most_common() if interest not in student_interests][:3]

    # Étape 2 : Recommandations programmatiques
    all_skills_in_db = set([skill for skills in df['Compétences'].apply(ast.literal_eval) for skill in skills])
    all_interests_in_db = set([interest for interests in df.get('Centres_d\'Intérêt', pd.Series(['[]'] * len(df))).apply(ast.literal_eval) for interest in interests])
    
    available_programmatic_skills = [skill for skill in PROGRAMMATIC_SKILLS if skill not in all_skills_in_db and skill not in student_skills]
    available_programmatic_interests = [interest for interest in PROGRAMMATIC_INTERESTS if interest not in all_interests_in_db and interest not in student_interests]
    
    recommended_skills_programmatic = random.sample(available_programmatic_skills, min(3, len(available_programmatic_skills))) if available_programmatic_skills else []
    recommended_interests_programmatic = random.sample(available_programmatic_interests, min(2, len(available_programmatic_interests))) if available_programmatic_interests else []

    return recommended_skills_from_db, recommended_interests_from_db, recommended_skills_programmatic, recommended_interests_programmatic

def get_fictitious_recommendations(student_id, df, model, n_recommendations=5):
    """Génère des recommandations de compétences et centres d'intérêt en utilisant uniquement KNNWithZScore."""
    student_row = df[df['ID_Étudiant'] == student_id]
    if student_row.empty:
        error_msg = f"Étudiant {student_id} non trouvé."
        print(error_msg)
        return None, error_msg

    student_skills = set(ast.literal_eval(student_row['Compétences'].iloc[0]))
    student_interests = set(ast.literal_eval(student_row.get('Centres_d\'Intérêt', pd.Series(['[]'])).iloc[0]))

    # Étape 1 : Utiliser KNNWithZScore pour prédire les coéquipiers potentiels
    all_teammates = set()
    for index, row in df.iterrows():
        teammates = ast.literal_eval(row['Coéquipiers'])
        for teammate_id in teammates:
            all_teammates.add(f"student_{teammate_id}")

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
        pred = model.predict(student_id, item)
        predictions.append((item, pred.est))

    predictions.sort(key=lambda x: x[1], reverse=True)
    top_teammates = [item for item, score in predictions[:n_recommendations]]

    # Étape 2 : Recommander des compétences et centres d'intérêt basées uniquement sur les coéquipiers prédits
    recommended_skills_from_db, recommended_interests_from_db, recommended_skills_programmatic, recommended_interests_programmatic = get_recommended_skills_and_interests(
        student_id, student_skills, student_interests, df, potential_teammates=top_teammates
    )

    return {
        "recommended_skills_from_db": recommended_skills_from_db,
        "recommended_interests_from_db": recommended_interests_from_db,
        "recommended_skills_programmatic": recommended_skills_programmatic,
        "recommended_interests_programmatic": recommended_interests_programmatic
    }, None

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
    student_interests = set(ast.literal_eval(student_row.get('Centres_d\'Intérêt', pd.Series(['[]'])).iloc[0]))
    
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

    # Convertir skill_filter et interest_filter en listes si ce sont des chaînes
    skill_filter = [skill_filter] if isinstance(skill_filter, str) else (skill_filter if skill_filter else [])
    interest_filter = [interest_filter] if isinstance(skill_filter, str) else (interest_filter if interest_filter else [])

    predictions = []
    for item in potential_teammates:
        teammate_id = int(item.replace("student_", ""))
        teammate_row = df[df['ID_Étudiant'] == teammate_id]
        if not teammate_row.empty:
            teammate_skills = set(ast.literal_eval(teammate_row['Compétences'].iloc[0]))
            teammate_interests = set(ast.literal_eval(teammate_row['Centres_d\'Intérêt'].iloc[0] if 'Centres_d\'Intérêt' in teammate_row.columns else '[]'))
            
            skill_match = True
            if skill_filter:
                skill_match = any(skill in teammate_skills for skill in skill_filter)
            
            interest_match = True
            if interest_filter:
                interest_match = any(interest in teammate_interests for interest in interest_filter)
            
            if (skill_match or interest_match) or (not skill_filter and not interest_filter):
                pred = model.predict(student_id, item)
                skill_score = 0.5
                if skill_filter:
                    matching_skills = sum(1 for skill in skill_filter if skill in teammate_skills)
                    skill_score = 0.5 + 0.5 * (matching_skills / len(skill_filter))
                interest_score = 0.5
                if interest_filter:
                    matching_interests = sum(1 for interest in interest_filter if interest in teammate_interests)
                    interest_score = 0.5 + 0.5 * (matching_interests / len(interest_filter))
                skill_diversity_bonus = 0.2 * len(teammate_skills - student_skills)
                interest_diversity_bonus = 0.1 * len(teammate_interests - student_interests)
                weighted_score = pred.est * (skill_weight * skill_score + interest_weight * interest_score) + skill_diversity_bonus + interest_diversity_bonus
                weighted_score = normalize_score(weighted_score)
                predictions.append((item, weighted_score))

    if not predictions:
        print(f"Aucun coéquipier ne correspond aux critères pour l'étudiant {student_id}. Ignorer les filtres...")
        predictions = []
        for item in potential_teammates:
            teammate_id = int(item.replace("student_", ""))
            teammate_row = df[df['ID_Étudiant'] == teammate_id]
            if not teammate_row.empty:
                teammate_skills = set(ast.literal_eval(teammate_row['Compétences'].iloc[0]))
                teammate_interests = set(ast.literal_eval(teammate_row['Centres_d\'Intérêt'].iloc[0] if 'Centres_d\'Intérêt' in teammate_row.columns else '[]'))
                pred = model.predict(student_id, item)
                skill_score = 0.5
                interest_score = 0.5
                skill_diversity_bonus = 0.2 * len(teammate_skills - student_skills)
                interest_diversity_bonus = 0.1 * len(teammate_interests - student_interests)
                weighted_score = pred.est * (skill_weight * skill_score + interest_weight * interest_score) + skill_diversity_bonus + interest_diversity_bonus
                weighted_score = normalize_score(weighted_score)
                predictions.append((item, weighted_score))

    if not predictions:
        error_msg = f"Aucun coéquipier disponible après suppression des filtres pour l'étudiant {student_id}."
        print(error_msg)
        return None, error_msg

    predictions.sort(key=lambda x: x[1], reverse=True)

    recommended_teammates = []
    for item, score in predictions[:n_recommendations]:
        teammate_id = int(item.replace("student_", ""))
        if teammate_id != student_id:
            recommended_teammates.append((teammate_id, score))

    student_info["teammates"] = recommended_teammates
    return {"teammates": recommended_teammates}, None

if __name__ == "__main__":
    n_recommendations = 5
    skill_filter = ["Python", "Blockchain"]
    interest_filter = ["Robotique", "Hackathon"]
    skill_weight = 0.7
    interest_weight = 0.3

    # Test pour l'étudiant 2 avec recommandations de compétences, centres d'intérêt et cours
    student_id = 2
    print(f"\nLancement des recommandations pour l'étudiant {student_id}...")
    
    # Obtenir les recommandations de coéquipiers (comme avant)
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
        print(f"\nRecommandations pour l'étudiant {student_id} :")
        for teammate_id, score in result["teammates"]:
            teammate_row = df[df['ID_Étudiant'] == teammate_id]
            teammate_skills = ast.literal_eval(teammate_row['Compétences'].iloc[0]) if not teammate_row.empty else []
            teammate_interests = ast.literal_eval(teammate_row['Centres_d\'Intérêt'].iloc[0] if 'Centres_d\'Intérêt' in teammate_row.columns else '[]') if not teammate_row.empty else []
            print(f"- Étudiant {teammate_id} : Score {score:.2f}")
            print(f"  Compétences : {teammate_skills}")
            print(f"  Centres d'intérêt : {teammate_interests}")
        
        # Obtenir les compétences et centres d'intérêt actuels et recommandés
        student_row = df[df['ID_Étudiant'] == student_id]
        current_skills = ast.literal_eval(student_row['Compétences'].iloc[0]) if not student_row.empty else []
        current_interests = ast.literal_eval(student_row['Centres_d\'Intérêt'].iloc[0] if 'Centres_d\'Intérêt' in student_row.columns else '[]') if not student_row.empty else []
        
        print("\nProfil de l'étudiant :")
        print(f"  Compétences actuelles : {', '.join(current_skills) if current_skills else 'Aucune'}")
        print(f"  Centres d'intérêt actuels : {', '.join(current_interests) if current_interests else 'Aucun'}")
        
        # Obtenir les recommandations de compétences et centres d'intérêt (comme dans l'onglet 2)
        fictitious_result, fictitious_error = get_fictitious_recommendations(
            student_id=student_id,
            df=df,
            model=model,
            n_recommendations=n_recommendations
        )
        
        if fictitious_error:
            print(f"Erreur pour les recommandations fictives de l'étudiant {student_id} : {fictitious_error}")
        else:
            print("\nCompétences et centres d'intérêt recommandés (Basés sur la base) :")
            print(f"  Compétences recommandées : {', '.join(fictitious_result['recommended_skills_from_db']) if fictitious_result['recommended_skills_from_db'] else 'Aucune'}")
            print(f"  Centres d'intérêt recommandés : {', '.join(fictitious_result['recommended_interests_from_db']) if fictitious_result['recommended_interests_from_db'] else 'Aucun'}")
            
            print("\nCompétences et centres d'intérêt recommandés (Programmatiques - Non présents dans la base) :")
            print(f"  Compétences recommandées : {', '.join(fictitious_result['recommended_skills_programmatic']) if fictitious_result['recommended_skills_programmatic'] else 'Aucune'}")
            print(f"  Centres d'intérêt recommandés : {', '.join(fictitious_result['recommended_interests_programmatic']) if fictitious_result['recommended_interests_programmatic'] else 'Aucun'}")
            
            # Afficher les cours recommandés
            print("\nCours recommandés :")
            print("  Basé sur les compétences recommandées (de la base) :")
            for skill in fictitious_result['recommended_skills_from_db']:
                if skill in RECOMMENDED_COURSES:
                    print(f"    - {skill} :")
                    for course_name, course_url in RECOMMENDED_COURSES[skill]:
                        print(f"      - {course_name} ({course_url})")
            
            print("  Basé sur les compétences recommandées (programmatiques) :")
            for skill in fictitious_result['recommended_skills_programmatic']:
                if skill in RECOMMENDED_COURSES:
                    print(f"    - {skill} :")
                    for course_name, course_url in RECOMMENDED_COURSES[skill]:
                        print(f"      - {course_name} ({course_url})")
            
            print("  Basé sur les centres d'intérêt recommandés (de la base) :")
            for interest in fictitious_result['recommended_interests_from_db']:
                if interest in RECOMMENDED_COURSES:
                    print(f"    - {interest} :")
                    for course_name, course_url in RECOMMENDED_COURSES[interest]:
                        print(f"      - {course_name} ({course_url})")
            
            print("  Basé sur les centres d'intérêt recommandés (programmatiques) :")
            for interest in fictitious_result['recommended_interests_programmatic']:
                if interest in RECOMMENDED_COURSES:
                    print(f"    - {interest} :")
                    for course_name, course_url in RECOMMENDED_COURSES[interest]:
                        print(f"      - {course_name} ({course_url})")
        
        print("Recommandations générées avec succès.")

    # Test pour l'étudiant 15 avec recommandations de compétences, centres d'intérêt et cours
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
        print(f"\nRecommandations pour l'étudiant {student_id} :")
        for teammate_id, score in result["teammates"]:
            teammate_row = df[df['ID_Étudiant'] == teammate_id]
            teammate_skills = ast.literal_eval(teammate_row['Compétences'].iloc[0]) if not teammate_row.empty else []
            teammate_interests = ast.literal_eval(teammate_row['Centres_d\'Intérêt'].iloc[0] if 'Centres_d\'Intérêt' in teammate_row.columns else '[]') if not teammate_row.empty else []
            print(f"- Étudiant {teammate_id} : Score {score:.2f}")
            print(f"  Compétences : {teammate_skills}")
            print(f"  Centres d'intérêt : {teammate_interests}")
        
        # Obtenir les compétences et centres d'intérêt actuels et recommandés
        student_row = df[df['ID_Étudiant'] == student_id]
        current_skills = ast.literal_eval(student_row['Compétences'].iloc[0]) if not student_row.empty else []
        current_interests = ast.literal_eval(student_row['Centres_d\'Intérêt'].iloc[0] if 'Centres_d\'Intérêt' in student_row.columns else '[]') if not student_row.empty else []
        
        print("\nProfil de l'étudiant :")
        print(f"  Compétences actuelles : {', '.join(current_skills) if current_skills else 'Aucune'}")
        print(f"  Centres d'intérêt actuels : {', '.join(current_interests) if current_interests else 'Aucun'}")
        
        # Obtenir les recommandations de compétences et centres d'intérêt
        fictitious_result, fictitious_error = get_fictitious_recommendations(
            student_id=student_id,
            df=df,
            model=model,
            n_recommendations=n_recommendations
        )
        
        if fictitious_error:
            print(f"Erreur pour les recommandations fictives de l'étudiant {student_id} : {fictitious_error}")
        else:
            print("\nCompétences et centres d'intérêt recommandés (Basés sur la base) :")
            print(f"  Compétences recommandées : {', '.join(fictitious_result['recommended_skills_from_db']) if fictitious_result['recommended_skills_from_db'] else 'Aucune'}")
            print(f"  Centres d'intérêt recommandés : {', '.join(fictitious_result['recommended_interests_from_db']) if fictitious_result['recommended_interests_from_db'] else 'Aucun'}")
            
            print("\nCompétences et centres d'intérêt recommandés (Programmatiques - Non présents dans la base) :")
            print(f"  Compétences recommandées : {', '.join(fictitious_result['recommended_skills_programmatic']) if fictitious_result['recommended_skills_programmatic'] else 'Aucune'}")
            print(f"  Centres d'intérêt recommandés : {', '.join(fictitious_result['recommended_interests_programmatic']) if fictitious_result['recommended_interests_programmatic'] else 'Aucune'}")
            
            # Afficher les cours recommandés
            print("\nCours recommandés :")
            print("  Basé sur les compétences recommandées (de la base) :")
            for skill in fictitious_result['recommended_skills_from_db']:
                if skill in RECOMMENDED_COURSES:
                    print(f"    - {skill} :")
                    for course_name, course_url in RECOMMENDED_COURSES[skill]:
                        print(f"      - {course_name} ({course_url})")
            
            print("  Basé sur les compétences recommandées (programmatiques) :")
            for skill in fictitious_result['recommended_skills_programmatic']:
                if skill in RECOMMENDED_COURSES:
                    print(f"    - {skill} :")
                    for course_name, course_url in RECOMMENDED_COURSES[skill]:
                        print(f"      - {course_name} ({course_url})")
            
            print("  Basé sur les centres d'intérêt recommandés (de la base) :")
            for interest in fictitious_result['recommended_interests_from_db']:
                if interest in RECOMMENDED_COURSES:
                    print(f"    - {interest} :")
                    for course_name, course_url in RECOMMENDED_COURSES[interest]:
                        print(f"      - {course_name} ({course_url})")
            
            print("  Basé sur les centres d'intérêt recommandés (programmatiques) :")
            for interest in fictitious_result['recommended_interests_programmatic']:
                if interest in RECOMMENDED_COURSES:
                    print(f"    - {interest} :")
                    for course_name, course_url in RECOMMENDED_COURSES[interest]:
                        print(f"      - {course_name} ({course_url})")
        
        print("Recommandations générées avec succès.")

    # Test pour tous les étudiants (inchangé)
    print("\nRecommandations pour tous les étudiants :")
    for student_id in range(1, 51):
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