import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import load_model
import pickle
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
import random

# Définir les chemins absolus spécifiques
BASE_DIR = r"C:\Users\User\educational_recommendation"
DATA_DIR = r"C:\Users\User\educational_recommendation\data"
MODELS_DIR = r"C:\Users\User\educational_recommendation\models"
CSV_PATH = r"C:\Users\User\educational_recommendation\data\dataset_etudiants.csv"

def preprocess_data(file_path, mlb):
    df = pd.read_csv(file_path)
    list_columns = ['Coéquipiers', 'Communautés', 'Compétences', "Centres_d'Intérêt"]
    for col in list_columns:
        df[col] = df[col].apply(lambda x: eval(x) if isinstance(x, str) else x)
    encoded_data = []
    for col in list_columns:
        df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])
        encoded = mlb.transform(df[col])
        expected_classes = mlb.classes_
        if encoded.shape[1] < len(expected_classes):
            padding = np.zeros((encoded.shape[0], len(expected_classes) - encoded.shape[1]))
            encoded = np.hstack((encoded, padding))
        encoded_df = pd.DataFrame(encoded, columns=[f"{col}_{i}" for i in range(len(expected_classes))])
        encoded_data.append(encoded_df)
    encoded_df = pd.concat(encoded_data, axis=1)
    scaler = MinMaxScaler()
    df['Nombre_Interactions'] = scaler.fit_transform(df[['Nombre_Interactions']])
    df['Travaux_Collaboratifs'] = scaler.fit_transform(df[['Travaux_Collaboratifs']])
    X = pd.concat([encoded_df, df['Nombre_Interactions'], df['Travaux_Collaboratifs']], axis=1)
    return df, X

# Charger les modèles et les données
autoencoder = load_model(r"C:\Users\User\educational_recommendation\models\autoencoder.h5")
encoder = load_model(r"C:\Users\User\educational_recommendation\models\encoder.h5")

# Charger le MultiLabelBinarizer sauvegardé
with open(r"C:\Users\User\educational_recommendation\models\mlb.pkl", 'rb') as f:
    mlb = pickle.load(f)

# Prétraitement des données
df, X_scaled = preprocess_data(CSV_PATH, mlb)
print(f"Dimension de X_scaled dans generate.py : {X_scaled.shape}")
if X_scaled.shape[1] != 67:
    padding = np.zeros((X_scaled.shape[0], 67 - X_scaled.shape[1]))
    X_scaled = np.hstack((X_scaled, padding))
    print(f"Ajusté X_scaled à la dimension attendue : {X_scaled.shape}")

# Prédire avec l'autoencodeur
reconstructed = autoencoder.predict(X_scaled)
rmse = math.sqrt(mean_squared_error(X_scaled, reconstructed))
mae = mean_absolute_error(X_scaled, reconstructed)
print(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}")

# Charger les embeddings
with open(r"C:\Users\User\educational_recommendation\models\student_embeddings.pkl", 'rb') as f:
    embeddings_df = pickle.load(f)

# Fonction pour trouver des coéquipiers similaires
def find_similar_students(student_id, embeddings_df, df, top_k=5):
    student_idx = df.index[df['ID_Étudiant'] == student_id].tolist()
    if not student_idx:
        return []
    student_idx = student_idx[0]
    student_embedding = embeddings_df.iloc[student_idx].values
    similarities = embeddings_df.dot(student_embedding) / (np.linalg.norm(embeddings_df, axis=1) * np.linalg.norm(student_embedding))
    similar_indices = similarities.nlargest(top_k + 1).index
    similar_students = []
    for idx in similar_indices:
        if idx != student_idx:
            similar_student_id = df.iloc[idx]['ID_Étudiant']
            similar_student_name = df.iloc[idx]['Nom']
            similar_students.append({'ID_Étudiant': similar_student_id, 'Nom': similar_student_name})
    return similar_students[:top_k]

# Générer des recommandations de cours avec styles d'apprentissage
def recommend_courses(skills, interests, learning_styles, top_k=3):
    course_mapping = {
        "python": {"course": "Cours de Programmation Python", "resources": {
            "Visual": ["Vidéo : Tutoriel Python sur YouTube", "Infographie : Schémas de syntaxe Python"],
            "Auditory": ["Podcast : 'Python Bytes'", "Audio : Cours audio Python"],
            "Reading/Writing": ["Livre : 'Automate the Boring Stuff with Python' par Al Sweigart", "Article : Documentation Python"],
            "Kinesthetic": ["Exercice : Projets pratiques avec Python", "Simulation : Environnement interactif"]
        }},
        "ia": {"course": "Cours d'Intelligence Artificielle", "resources": {
            "Visual": ["Vidéo : Introduction à l'IA sur Coursera", "Diagrammes : Réseaux neuronaux"],
            "Auditory": ["Podcast : 'Lex Fridman AI'", "Audio : Conférences IA"],
            "Reading/Writing": ["Livre : 'Deep Learning' par Goodfellow et al.", "Article : Papiers de recherche"],
            "Kinesthetic": ["Exercice : Modèles TensorFlow", "Simulation : Jeux d'IA"]
        }},
        "blockchain": {"course": "Cours de Blockchain", "resources": {
            "Visual": ["Vidéo : Tutoriel Blockchain sur Udemy", "Infographie : Structure Blockchain"],
            "Auditory": ["Podcast : 'Unchained'", "Audio : Explications Blockchain"],
            "Reading/Writing": ["Livre : 'Mastering Bitcoin' par Andreas Antonopoulos", "Article : Guide Ethereum"],
            "Kinesthetic": ["Exercice : Créer une transaction", "Simulation : Réseau test"]
        }},
        "électronique": {"course": "Cours d'Électronique", "resources": {
            "Visual": ["Vidéo : Tutoriels Arduino", "Schéma : Circuits électroniques"],
            "Auditory": ["Podcast : 'The Amp Hour'", "Audio : Leçons sur les circuits"],
            "Reading/Writing": ["Livre : 'The Art of Electronics' par Horowitz et Hill", "Note : Formules électriques"],
            "Kinesthetic": ["Exercice : Montage de circuits", "Simulation : Logiciels comme LTspice"]
        }},
        "design": {"course": "Cours de Design", "resources": {
            "Visual": ["Vidéo : Tutoriels Figma", "Exemples : Designs UI/UX"],
            "Auditory": ["Podcast : 'Design Better'", "Audio : Conseils de design"],
            "Reading/Writing": ["Livre : 'The Design of Everyday Things' par Don Norman", "Article : Tendances UI"],
            "Kinesthetic": ["Exercice : Créer un prototype", "Simulation : Outils interactifs"]
        }},
        "marketing": {"course": "Cours de Marketing", "resources": {
            "Visual": ["Vidéo : Cours Google Digital Garage", "Graphiques : Campagnes marketing"],
            "Auditory": ["Podcast : 'Marketing Over Coffee'", "Audio : Stratégies marketing"],
            "Reading/Writing": ["Livre : 'Influence: The Psychology of Persuasion' par Robert Cialdini", "Article : Études de cas"],
            "Kinesthetic": ["Exercice : Plan marketing", "Simulation : Campagne publicitaire"]
        }},
        "data science": {"course": "Cours de Data Science", "resources": {
            "Visual": ["Vidéo : Tutoriels Pandas", "Graphiques : Visualisation de données"],
            "Auditory": ["Podcast : 'Data Skeptic'", "Audio : Concepts statistiques"],
            "Reading/Writing": ["Livre : 'Python for Data Analysis' par Wes McKinney", "Article : Méthodes d’analyse"],
            "Kinesthetic": ["Exercice : Analyse de datasets", "Simulation : Modèles prédictifs"]
        }},
        "jeux vidéo": {"course": "Cours de Développement de Jeux Vidéo", "resources": {
            "Visual": ["Vidéo : Tutoriels Unity", "Screenshots : Jeux créés"],
            "Auditory": ["Podcast : 'Game Dev Unchained'", "Audio : Sound design"],
            "Reading/Writing": ["Livre : 'The Art of Game Design' par Jesse Schell", "Article : Développement Unity"],
            "Kinesthetic": ["Exercice : Créer un niveau", "Simulation : Environnement Unity"]
        }},
        "cybersécurité": {"course": "Cours de Cybersécurité", "resources": {
            "Visual": ["Vidéo : Tutoriels Wireshark", "Diagrammes : Attaques réseau"],
            "Auditory": ["Podcast : 'Darknet Diaries'", "Audio : Sécurités réseau"],
            "Reading/Writing": ["Livre : 'Hacking: The Art of Exploitation' par Jon Erickson", "Article : Techniques de hacking"],
            "Kinesthetic": ["Exercice : Analyse de paquets", "Simulation : Environnement sécurisé"]
        }},
        "robotique": {"course": "Cours de Robotique", "resources": {
            "Visual": ["Vidéo : Tutoriels ROS", "Diagrammes : Robots"],
            "Auditory": ["Podcast : 'Robohub'", "Audio : Concepts robotiques"],
            "Reading/Writing": ["Livre : 'Robotics: Modelling, Planning and Control' par Siciliano", "Article : Programmation ROS"],
            "Kinesthetic": ["Exercice : Programmer un robot", "Simulation : Gazebo"]
        }},
        "photographie": {"course": "Cours de Photographie", "resources": {
            "Visual": ["Vidéo : Tutoriels Photoshop", "Exemples : Photos pro"],
            "Auditory": ["Podcast : 'The Photographers'", "Audio : Techniques photo"],
            "Reading/Writing": ["Livre : 'Understanding Exposure' par Bryan Peterson", "Article : Composition photo"],
            "Kinesthetic": ["Exercice : Prise de vue", "Simulation : Édition d’images"]
        }}
    }

    courses = []
    all_items = skills + interests
    for item in all_items:
        item_lower = item.lower()  # Convertir en minuscules pour correspondance insensible à la casse
        if item_lower in course_mapping and course_mapping[item_lower]['course'] not in [c['course'] for c in courses]:
            # Adapter les ressources au style d'apprentissage
            adapted_resources = []
            for style in learning_styles:
                if style in course_mapping[item_lower]["resources"]:
                    adapted_resources.extend(course_mapping[item_lower]["resources"][style])
            if not adapted_resources:  # Si aucun style spécifique, prendre toutes les ressources
                adapted_resources = [res for sublist in course_mapping[item_lower]["resources"].values() for res in sublist]
            courses.append({'course': course_mapping[item_lower]['course'], 'resources': adapted_resources[:3]})  # Limiter à 3 ressources
        else:
            # Générer une recommandation via IA générative si le cours n'existe pas
            generated_course = f"Cours généré : Introduction à {item.capitalize()}"
            generated_resources = {
                "Visual": [f"Vidéo : Tutoriel sur {item.capitalize()}", f"Infographie : Concepts de {item.capitalize()}"],
                "Auditory": [f"Podcast : Exploration de {item.capitalize()}", f"Audio : Guide de {item.capitalize()}"],
                "Reading/Writing": [f"Livre : Manuel de {item.capitalize()}", f"Article : Bases de {item.capitalize()}"],
                "Kinesthetic": [f"Exercice : Projet sur {item.capitalize()}", f"Simulation : Activité {item.capitalize()}"]
            }
            adapted_resources = []
            for style in learning_styles:
                if style in generated_resources:
                    adapted_resources.extend(generated_resources[style])
            if adapted_resources:
                courses.append({'course': generated_course, 'resources': adapted_resources[:3]})

    return courses[:top_k]

# Fonction pour déterminer le style d'apprentissage via des questions
def determine_learning_style():
    print("\n=== Formulaire de Style d'Apprentissage ===")
    print("Répondez aux questions suivantes pour déterminer votre style d'apprentissage (VARK).")
    
    # Initialiser les scores
    visual_score = 0
    auditory_score = 0
    reading_writing_score = 0
    kinesthetic_score = 0

    # Question 1
    print("\nQuestion 1: Quand vous apprenez quelque chose de nouveau, vous préférez :")
    print("a) Regarder des vidéos ou des diagrammes (Visuel)")
    print("b) Écouter des explications ou des podcasts (Auditif)")
    print("c) Lire des textes ou prendre des notes (Lecture/Écriture)")
    print("d) Faire des activités pratiques ou toucher des objets (Kinesthésique)")
    answer = input("Entrez votre choix (a, b, c, d) : ").lower()
    if answer == 'a':
        visual_score += 1
    elif answer == 'b':
        auditory_score += 1
    elif answer == 'c':
        reading_writing_score += 1
    elif answer == 'd':
        kinesthetic_score += 1

    # Question 2
    print("\nQuestion 2: Pour retenir une information, vous trouvez plus facile de :")
    print("a) Visualiser une image ou un graphique dans votre tête (Visuel)")
    print("b) Répéter à voix haute ou écouter une explication (Auditif)")
    print("c) Écrire des résumés ou lire des documents (Lecture/Écriture)")
    print("d) Participer à une activité ou manipuler quelque chose (Kinesthésique)")
    answer = input("Entrez votre choix (a, b, c, d) : ").lower()
    if answer == 'a':
        visual_score += 1
    elif answer == 'b':
        auditory_score += 1
    elif answer == 'c':
        reading_writing_score += 1
    elif answer == 'd':
        kinesthetic_score += 1

    # Question 3
    print("\nQuestion 3: Quand vous suivez des instructions, vous préférez :")
    print("a) Voir une démonstration ou un schéma (Visuel)")
    print("b) Écouter quelqu’un vous expliquer (Auditif)")
    print("c) Lire les instructions écrites (Lecture/Écriture)")
    print("d) Essayer directement et apprendre par l’action (Kinesthésique)")
    answer = input("Entrez votre choix (a, b, c, d) : ").lower()
    if answer == 'a':
        visual_score += 1
    elif answer == 'b':
        auditory_score += 1
    elif answer == 'c':
        reading_writing_score += 1
    elif answer == 'd':
        kinesthetic_score += 1

    # Question 4
    print("\nQuestion 4: Pour résoudre un problème, vous préférez :")
    print("a) Dessiner un plan ou une carte mentale (Visuel)")
    print("b) Discuter avec quelqu’un ou écouter une solution (Auditif)")
    print("c) Lire un manuel ou écrire une liste d’étapes (Lecture/Écriture)")
    print("d) Tester différentes approches par la pratique (Kinesthésique)")
    answer = input("Entrez votre choix (a, b, c, d) : ").lower()
    if answer == 'a':
        visual_score += 1
    elif answer == 'b':
        auditory_score += 1
    elif answer == 'c':
        reading_writing_score += 1
    elif answer == 'd':
        kinesthetic_score += 1

    # Question 5
    print("\nQuestion 5: Quand vous étudiez, vous appréciez le plus :")
    print("a) Regarder des présentations ou des images (Visuel)")
    print("b) Participer à des discussions ou écouter des enregistrements (Auditif)")
    print("c) Prendre des notes détaillées ou lire des livres (Lecture/Écriture)")
    print("d) Faire des exercices pratiques ou des expériences (Kinesthésique)")
    answer = input("Entrez votre choix (a, b, c, d) : ").lower()
    if answer == 'a':
        visual_score += 1
    elif answer == 'b':
        auditory_score += 1
    elif answer == 'c':
        reading_writing_score += 1
    elif answer == 'd':
        kinesthetic_score += 1

    # Question 6
    print("\nQuestion 6: Pour vous motiver, vous préférez :")
    print("a) Voir des exemples visuels de succès (Visuel)")
    print("b) Entendre des encouragements ou des conseils oraux (Auditif)")
    print("c) Lire des articles inspirants ou écrire vos objectifs (Lecture/Écriture)")
    print("d) Agir directement ou participer à une activité (Kinesthésique)")
    answer = input("Entrez votre choix (a, b, c, d) : ").lower()
    if answer == 'a':
        visual_score += 1
    elif answer == 'b':
        auditory_score += 1
    elif answer == 'c':
        reading_writing_score += 1
    elif answer == 'd':
        kinesthetic_score += 1

    # Question 7
    print("\nQuestion 7: Quand vous expliquez quelque chose, vous préférez :")
    print("a) Montrer des images ou des schémas (Visuel)")
    print("b) Parler ou utiliser des sons pour illustrer (Auditif)")
    print("c) Écrire une explication détaillée (Lecture/Écriture)")
    print("d) Démontrer en faisant (Kinesthésique)")
    answer = input("Entrez votre choix (a, b, c, d) : ").lower()
    if answer == 'a':
        visual_score += 1
    elif answer == 'b':
        auditory_score += 1
    elif answer == 'c':
        reading_writing_score += 1
    elif answer == 'd':
        kinesthetic_score += 1

    # Question 8
    print("\nQuestion 8: Pour apprendre une nouvelle compétence, vous préférez :")
    print("a) Observer des tutoriels vidéo (Visuel)")
    print("b) Écouter des instructions ou des discussions (Auditif)")
    print("c) Étudier des guides écrits ou des notes (Lecture/Écriture)")
    print("d) Pratiquer directement avec des exercices (Kinesthésique)")
    answer = input("Entrez votre choix (a, b, c, d) : ").lower()
    if answer == 'a':
        visual_score += 1
    elif answer == 'b':
        auditory_score += 1
    elif answer == 'c':
        reading_writing_score += 1
    elif answer == 'd':
        kinesthetic_score += 1

    # Déterminer le style dominant
    scores = {
        "Visual": visual_score,
        "Auditory": auditory_score,
        "Reading/Writing": reading_writing_score,
        "Kinesthetic": kinesthetic_score
    }
    max_score = max(scores.values())
    dominant_styles = [style for style, score in scores.items() if score == max_score]
    return dominant_styles

# Fonction simple d'IA générative pour un message motivant
def generate_motivational_message(learning_styles, skills, interests):
    style_descriptions = {
        "Visual": "un apprenant visuel qui excelle avec des images et des démonstrations",
        "Auditory": "un apprenant auditif qui brille en écoutant et en discutant",
        "Reading/Writing": "un apprenant qui préfère lire et écrire pour assimiler les connaissances",
        "Kinesthetic": "un apprenant kinesthésique qui apprend mieux par le toucher et l’action"
    }
    style_desc = " et ".join([style_descriptions[style] for style in learning_styles])
    skill_desc = ", ".join(skills)
    interest_desc = ", ".join(interests)

    # Ajouter des suggestions spécifiques
    suggestions = {
        "python": "Pourquoi ne pas explorer des projets avancés en Python, comme un jeu ou une application ?",
        "jeux vidéo": "Tu pourrais créer ton propre jeu avec Unity pour combiner ton intérêt pour les jeux vidéo !",
        "électronique": "Un projet Arduino pourrait être parfait pour mettre en pratique tes compétences en électronique.",
    }
    suggestion_text = ""
    for item in skills + interests:
        item_lower = item.lower()
        if item_lower in suggestions:
            suggestion_text += suggestions[item_lower] + " "

    messages = [
        f"Vous êtes {style_desc} ! Avec vos compétences en {skill_desc} et vos intérêts pour {interest_desc}, tu es prêt(e) à explorer de nouveaux horizons. {suggestion_text}Continue à briller !",
        f"En tant que {style_desc}, tu as un potentiel incroyable avec tes compétences en {skill_desc} et ta passion pour {interest_desc}. {suggestion_text}Lance-toi avec confiance !",
        f"Wow, un(e) {style_desc} avec des compétences en {skill_desc} et des intérêts pour {interest_desc} ! {suggestion_text}Tu es sur la bonne voie pour réussir !"
    ]
    return random.choice(messages)

# Fonction pour collecter les réponses du formulaire
def collect_form_data(df):
    print("=== Formulaire pour l'étudiant ===")
    student_id = int(input("Entrez votre ID étudiant : "))
    
    # Récupérer les compétences et centres d'intérêt de la base
    student_idx = df.index[df['ID_Étudiant'] == student_id].tolist()
    if student_idx:
        student_idx = student_idx[0]
        base_skills = df.iloc[student_idx]["Compétences"]
        base_interests = df.iloc[student_idx]["Centres_d'Intérêt"]
    else:
        print("Étudiant non trouvé dans la base. Utilisation uniquement des données saisies.")
        base_skills = []
        base_interests = []

    # Demander des compétences et centres d'intérêt supplémentaires
    extra_skills = input("Entrez vos compétences (séparées par des virgules, ex. Python, IA) : ").split(",")
    extra_skills = [s.strip() for s in extra_skills]
    extra_interests = input("Entrez vos centres d'intérêt (séparées par des virgules, ex. Jeux vidéo, Photographie) : ").split(",")
    extra_interests = [i.strip() for i in extra_interests]

    # Combiner les données de la base et les entrées supplémentaires
    skills = base_skills + extra_skills
    interests = base_interests + extra_interests

    # Déterminer le style d'apprentissage
    learning_styles = determine_learning_style()
    print(f"\nVotre style d'apprentissage dominant : {', '.join(learning_styles)}")

    return student_id, skills, interests, learning_styles

# Générer des recommandations
student_id, skills, interests, learning_styles = collect_form_data(df)
similar_students = find_similar_students(student_id, embeddings_df, df, top_k=5)
recommended_courses = recommend_courses(skills, interests, learning_styles, top_k=3)

# Générer un message motivant avec IA générative
motivational_message = generate_motivational_message(learning_styles, skills, interests)

# Afficher les recommandations
print(f"\nRecommandations pour étudiant {student_id}:")
print("Coéquipiers:", similar_students)
print("Cours:", recommended_courses)
print("\nMessage motivant :")
print(motivational_message)