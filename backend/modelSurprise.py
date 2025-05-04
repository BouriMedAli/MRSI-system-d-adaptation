# model.py
import pandas as pd
import ast
from surprise import Dataset, Reader, KNNWithMeans
from surprise.model_selection import train_test_split
from surprise import accuracy

# Load and preprocess the dataset
def load_dataset(path):
    df = pd.read_csv(path)
    df['Compétences'] = df['Compétences'].apply(ast.literal_eval)
    df['Centres_d\'Intérêt'] = df['Centres_d\'Intérêt'].apply(ast.literal_eval)
    return df

# Function to compute similarity rating between two students
def compute_similarity_rating(skills_i, interests_i, skills_j, interests_j):
    skills_i, interests_i = set(skills_i), set(interests_i)
    skills_j, interests_j = set(skills_j), set(interests_j)
    shared_skills = len(skills_i.intersection(skills_j))
    shared_interests = len(interests_i.intersection(interests_j))
    # Rating:
    return 3 * shared_skills + shared_interests # Weight skills higher

# Function to compute complementarity rating for a project
def compute_complementarity_rating(skills_i, interests_i, skills_j, interests_j, project_skills):
    skills_i, interests_i = set(skills_i), set(interests_i)
    skills_j, interests_j = set(skills_j), set(interests_j)
    # Complementary skills: skills_j has project skills that skills_i lacks
    shared_skills = len(skills_i.intersection(skills_j))
    missing_skills = set(project_skills) - skills_i
    complementary_skills = len(missing_skills.intersection(skills_j))
    # Shared interests (to ensure some alignment)
    shared_interests = len(interests_i.intersection(interests_j))
    # Rating
    return 4 * complementary_skills + shared_skills + 0.5 * shared_interests # Emphasize complementary skills

# Create ratings for similarity use case
def create_ratings_similarity (df):
    ratings = []
    for i, row_i in df.iterrows():
        student_i = row_i['ID_Étudiant']
        skills_i = row_i['Compétences']
        interests_i = row_i['Centres_d\'Intérêt']
        for j, row_j in df.iterrows():
            student_j = row_j['ID_Étudiant']
            if student_i != student_j: # Exclude self-rating
                rating = compute_similarity_rating(skills_i, interests_i, row_j['Compétences'], row_j['Centres_d\'Intérêt'])
                if rating > 0:  # Only include non-zero ratings
                    ratings.append((student_i, student_j, rating))
    return ratings

# Create ratings for complementarity use case
def create_ratings_complementarity (project_skills,df):
    ratings= []
    for i, row_i in df.iterrows():
        student_i = row_i['ID_Étudiant']
        skills_i = row_i['Compétences']
        interests_i = row_i['Centres_d\'Intérêt']
        for j, row_j in df.iterrows():
            student_j = row_j['ID_Étudiant']
            if student_i != student_j: # Exclude self-rating
                rating = compute_complementarity_rating(skills_i, interests_i, row_j['Compétences'], row_j['Centres_d\'Intérêt'], project_skills)
                if rating > 0:  # Only include non-zero ratings
                    ratings.append((student_i, student_j, rating))
    return ratings

# Train the recommendation models
def prepare_models(df, project_skills):
    ratings_similarity = create_ratings_similarity(df)
    ratings_complementarity = create_ratings_complementarity(project_skills, df)

    all_skills = set(skill for skills in df['Compétences'] for skill in skills)
    all_interests = set(interest for interests in df['Centres_d\'Intérêt'] for interest in interests)
    max_similarity_rating = len(all_skills) * 3 + len(all_interests)
    max_complementarity_rating = len(all_skills) * 4 + len(all_interests) * 0.5

    similarity_reader = Reader(rating_scale=(0, max_similarity_rating))
    complementarity_reader = Reader(rating_scale=(0, max_complementarity_rating))

    data_similarity = Dataset.load_from_df(pd.DataFrame(ratings_similarity, columns=['user_i', 'user_j', 'rating']), similarity_reader)
    data_complementarity = Dataset.load_from_df(pd.DataFrame(ratings_complementarity, columns=['user_i', 'user_j', 'rating']), complementarity_reader)

    trainset_similarity, _ = train_test_split(data_similarity, test_size=0.2, random_state=42)
    trainset_complementarity, _ = train_test_split(data_complementarity, test_size=0.2, random_state=42)

    sim_options = {'name': 'cosine', 'user_based': True}

    algo_similarity = KNNWithMeans(k=5, sim_options=sim_options)
    algo_complementarity = KNNWithMeans(k=5, sim_options=sim_options)

    algo_similarity.fit(trainset_similarity)
    algo_complementarity.fit(trainset_complementarity)

    return algo_similarity, algo_complementarity, all_skills, all_interests

# Recommend collaborators for a student
def recommend_collaborators(student_id, skills, interests,use_case, algo, df, n=3, project_skills=None):
    # Determine if the student is new (not in the dataset)
    is_new_student = student_id not in df['ID_Étudiant'].values
    
    # Get all student IDs from the dataset
    all_students = df['ID_Étudiant'].unique()
    
    # List to store predictions (student ID, predicted score)
    predictions = []
    
    # Iterate over all students in the dataset
    for other_student in all_students:
        if other_student != student_id:  # Avoid self-recommendation
            # Get the other student's data
            other_student_data = df[df['ID_Étudiant'] == other_student]
            if len(other_student_data) != 1:
                raise ValueError(f"Expected 1 row for student {other_student}, got {len(other_student_data)}")
            
            # Extract skills and interests
            other_skills = other_student_data['Compétences'].iloc[0]
            other_interests = other_student_data['Centres_d\'Intérêt'].iloc[0]
            
            if is_new_student:
                # For new students, compute raw rating as a fallback
                if use_case == "similarity":
                    rating = compute_similarity_rating(skills, interests, other_skills, other_interests)
                elif use_case == "complementarity":
                    rating = compute_complementarity_rating(skills, interests, other_skills, other_interests, project_skills)
                # Use raw rating for new students
                score = rating
            else:
                # For existing students, use KNN prediction
                if use_case == "similarity":
                    rating = compute_similarity_rating(skills, interests, other_skills, other_interests)
                elif use_case == "complementarity":
                    rating = compute_complementarity_rating(skills, interests, other_skills, other_interests, project_skills)
                # Get KNN prediction
                #score = algo.predict(student_id, other_student, r_ui=rating).est
                score = rating
                
            
            # Store the other student's ID and predicted score
            predictions.append((other_student, score))
    
    # Sort by predicted score and return top n
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]
    
    # Build results list with details of recommended students
    results = []
    for other_student_id, score in top_n:
        # Get the recommended student's data
        other_student_data = df[df['ID_Étudiant'] == other_student_id]
        skills = other_student_data['Compétences'].iloc[0]
        interests = other_student_data['Centres_d\'Intérêt'].iloc[0]
        # Append a dictionary with student details
        results.append({
            'Student_ID': other_student_id,
            'Score': score,
            'Skills': skills,
            'Interests': interests
        })
    
    return results
