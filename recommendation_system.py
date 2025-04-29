import pandas as pd
import numpy as np
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate
from sklearn.metrics import confusion_matrix
import json
import ast
import pickle
import re

# Load and preprocess data
def load_data(file_path):
    # Read the CSV with proper encoding
    df = pd.read_csv(file_path, encoding='latin1')
    
    # Print column names to debug
    print("Original columns in CSV:", df.columns.tolist())
    
    # Create a mapping from original column names to expected column names
    column_mapping = {
        'ID_Étudiant': 'IDEtudiant',
        'ID_Ã\x89tudiant': 'IDEtudiant',
        'ID_tudiant': 'IDEtudiant',
        'Coéquipiers': 'Coequipiers',
        'CoÃ©quipiers': 'Coequipiers',
        'Coquipiers': 'Coequipiers',
        'Communautés': 'Communautes',
        'CommunautÃ©s': 'Communautes',
        'Communauts': 'Communautes',
        'Compétences': 'Competences',
        'CompÃ©tences': 'Competences',
        'Comptences': 'Competences',
        "Centres_d'Intérêt": 'CentresdInteret',
        "Centres_d'IntÃ©rÃªt": 'CentresdInteret',
        'Centres_dIntrt': 'CentresdInteret'
    }
    
    # Apply the mapping based on what's available in the dataframe
    for orig_col, new_col in column_mapping.items():
        if orig_col in df.columns:
            df = df.rename(columns={orig_col: new_col})
    
    print("Renamed columns:", df.columns.tolist())
    
    # Check for any missing expected columns
    expected_columns = ['IDEtudiant', 'Nom', 'Coequipiers', 'Communautes', 
                        'Nombre_Interactions', 'Competences', 'CentresdInteret']
    
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing expected columns: {missing_columns}")
        
        # If Coequipiers is missing but we have an alternative column format
        if 'Coequipiers' in missing_columns:
            possible_alternatives = [col for col in df.columns if 'quip' in col.lower()]
            if possible_alternatives:
                print(f"Found possible alternatives for Coequipiers: {possible_alternatives}")
                df = df.rename(columns={possible_alternatives[0]: 'Coequipiers'})
                
        # Similarly for other missing columns
        for missing_col in missing_columns:
            if missing_col == 'IDEtudiant' and any('ID' in col for col in df.columns):
                id_cols = [col for col in df.columns if 'ID' in col or 'Id' in col]
                if id_cols:
                    df = df.rename(columns={id_cols[0]: 'IDEtudiant'})
            elif missing_col == 'Communautes' and any('commun' in col.lower() for col in df.columns):
                comm_cols = [col for col in df.columns if 'commun' in col.lower()]
                if comm_cols:
                    df = df.rename(columns={comm_cols[0]: 'Communautes'})
            elif missing_col == 'Competences' and any('comp' in col.lower() for col in df.columns):
                comp_cols = [col for col in df.columns if 'comp' in col.lower()]
                if comp_cols:
                    df = df.rename(columns={comp_cols[0]: 'Competences'})
            elif missing_col == 'CentresdInteret' and any('int' in col.lower() for col in df.columns):
                int_cols = [col for col in df.columns if 'int' in col.lower()]
                if int_cols:
                    df = df.rename(columns={int_cols[0]: 'CentresdInteret'})
                    
    print("Final columns after fixes:", df.columns.tolist())
    
    # Now parse the list columns with robust error handling
    list_columns = ['Coequipiers', 'Competences', 'CentresdInteret', 'Communautes']
    
    for col in list_columns:
        if col in df.columns:
            try:
                # Check if the column already contains list objects
                if df[col].dtype == 'object' and all(isinstance(x, list) for x in df[col].dropna()):
                    print(f"Column {col} already contains list objects")
                    continue
                
                # Try direct parsing first
                try:
                    df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
                except (ValueError, SyntaxError):
                    # If direct parsing fails, try cleaning the strings first
                    df[col] = df[col].apply(lambda x: 
                                          ast.literal_eval(str(x).replace("'", '"')
                                                          .replace('[', '[')
                                                          .replace(']', ']')) 
                                          if isinstance(x, str) else x)
            except Exception as e:
                print(f"Error parsing {col}: {str(e)}")
                print(f"Sample data for {col}:", df[col].head(3).tolist())
                
                # Try to fix the column if we have specific handling for it
                if col == 'Coequipiers':
                    try:
                        # Try to extract lists from string representation
                        def extract_list(x):
                            if isinstance(x, list):
                                return x
                            elif isinstance(x, str):
                                # Extract numbers using regex
                                numbers = re.findall(r'\d+', x)
                                return [int(num) for num in numbers]
                            else:
                                return []
                        
                        df[col] = df[col].apply(extract_list)
                        print(f"Applied custom parsing for {col}")
                    except Exception as inner_e:
                        print(f"Failed to apply custom parsing for {col}: {str(inner_e)}")
                        # Last resort: create empty lists
                        df[col] = df[col].apply(lambda x: [])
    
    return df

# Create student-student interaction data
def create_student_interaction_data(df):
    interactions = []
    for _, row in df.iterrows():
        student_id = int(row['IDEtudiant'])  # Convert to standard Python int
        coequipiers = row['Coequipiers']
        if not isinstance(coequipiers, list):
            coequipiers = []
        
        interactions_count = int(row['Nombre_Interactions'])  # Convert to standard Python int
        rating = min(5, max(1, interactions_count // 20))  # Normalize to 1-5
        
        for coequipier in coequipiers:
            interactions.append((student_id, int(coequipier), rating))  # Convert to standard Python int
    
    return pd.DataFrame(interactions, columns=['student_id', 'coequipier_id', 'rating'])

# Create student-community interaction data
def create_community_interaction_data(df):
    interactions = []
    all_communities = set()
    
    for _, row in df.iterrows():
        communities = row['Communautes']
        if isinstance(communities, list):
            all_communities.update(communities)
    
    all_communities = list(all_communities)
    
    for _, row in df.iterrows():
        student_id = int(row['IDEtudiant'])  # Convert to standard Python int
        student_communities = row['Communautes'] if isinstance(row['Communautes'], list) else []
        
        for community in all_communities:
            rating = 5 if community in student_communities else 1  # Binary-like rating
            interactions.append((student_id, community, rating))
    
    return pd.DataFrame(interactions, columns=['student_id', 'community', 'rating']), all_communities

# Train SVD model
def train_model(interaction_df, model_file):
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(interaction_df[['student_id', 'coequipier_id' if 'coequipier_id' in interaction_df else 'community', 'rating']], reader)
    model = SVD(n_factors=20, n_epochs=20, random_state=42)
    trainset = data.build_full_trainset()
    model.fit(trainset)
    
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    
    results = cross_validate(model, data, measures=['RMSE', 'MAE'], cv=5, verbose=False)
    return model, results

# Compute confusion matrix
def compute_confusion_matrix(model, interaction_df, is_student=True):
    predictions = []
    actuals = []
    for _, row in interaction_df.iterrows():
        pred = model.predict(row['student_id'], row['coequipier_id' if is_student else 'community']).est
        predictions.append(1 if pred >= 3 else 0)
        actuals.append(1 if row['rating'] >= 3 else 0)
    return confusion_matrix(actuals, predictions)

# Helper function to convert numpy types to Python native types
def convert_to_serializable(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

# Get student-to-student recommendations
def get_student_recommendations(student_id, model, df, n=5):
    all_students = df['IDEtudiant'].unique()
    predictions = []
    
    # Get current student's skills and interests
    student_data = df[df['IDEtudiant'] == student_id]
    if len(student_data) == 0:
        print(f"Warning: Student {student_id} not found in dataset")
        return []
    
    student_skills = set(student_data['Competences'].iloc[0]) if isinstance(student_data['Competences'].iloc[0], list) else set()
    student_interests = set(student_data['CentresdInteret'].iloc[0]) if isinstance(student_data['CentresdInteret'].iloc[0], list) else set()
    
    for other_id in all_students:
        if other_id != student_id:
            pred = model.predict(int(student_id), int(other_id)).est
            
            # Get other student's skills and interests
            other_data = df[df['IDEtudiant'] == other_id]
            if len(other_data) == 0:
                continue
                
            other_skills = set(other_data['Competences'].iloc[0]) if isinstance(other_data['Competences'].iloc[0], list) else set()
            other_interests = set(other_data['CentresdInteret'].iloc[0]) if isinstance(other_data['CentresdInteret'].iloc[0], list) else set()
            
            # Filter by shared skills or interests
            if student_skills & other_skills or student_interests & other_interests:
                predictions.append((other_id, pred))
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]
    
    recommendations = []
    for other_id, score in top_n:
        student_data = df[df['IDEtudiant'] == other_id].iloc[0]
        # Convert data to be JSON serializable
        other_id_int = convert_to_serializable(other_id)
        competences = [convert_to_serializable(comp) for comp in student_data['Competences']] if isinstance(student_data['Competences'], list) else []
        interests = [convert_to_serializable(interest) for interest in student_data['CentresdInteret']] if isinstance(student_data['CentresdInteret'], list) else []
        
        recommendations.append({
            'ID_Étudiant': other_id_int,
            'Nom': student_data['Nom'],
            'Compétences': competences,
            'Centres_d_Intérêt': interests,
            'Score': round(float(score), 2)  # Convert to float for JSON
        })
    return recommendations

# Get community/project recommendations
def get_community_recommendations(student_id, model, df, all_communities, n=5):
    predictions = []
    
    student_data = df[df['IDEtudiant'] == student_id]
    if len(student_data) == 0:
        print(f"Warning: Student {student_id} not found in dataset")
        return []
        
    student_communities = student_data['Communautes'].iloc[0] if isinstance(student_data['Communautes'].iloc[0], list) else []
    
    for community in all_communities:
        if community not in student_communities:  # Recommend new communities
            pred = model.predict(int(student_id), community).est
            predictions.append((community, pred))
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]
    
    recommendations = []
    for community, score in top_n:
        recommendations.append({
            'Communauté': community,
            'Projet': f"{community} Project",  # Infer project from community
            'Score': round(float(score), 2)  # Convert to float for JSON
        })
    return recommendations

# Custom JSON encoder class to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        return convert_to_serializable(obj)

if __name__ == '__main__':
    try:
        # Load data with error handling
        print("Loading data...")
        df = load_data('dataset_etudiants.csv')
        
        print("Data loaded successfully!")
        print(f"Dataset has {len(df)} rows and {len(df.columns)} columns")
        
        # Student-to-student recommendations
        print("Creating student interaction data...")
        student_interaction_df = create_student_interaction_data(df)
        print(f"Created {len(student_interaction_df)} student interactions")
        
        print("Training student recommendation model...")
        student_model, student_results = train_model(student_interaction_df, 'svd_student_model.pkl')
        student_cm = compute_confusion_matrix(student_model, student_interaction_df, is_student=True)
        
        # Community/project recommendations
        print("Creating community interaction data...")
        community_interaction_df, all_communities = create_community_interaction_data(df)
        print(f"Created {len(community_interaction_df)} community interactions across {len(all_communities)} communities")
        
        print("Training community recommendation model...")
        community_model, community_results = train_model(community_interaction_df, 'svd_community_model.pkl')
        community_cm = compute_confusion_matrix(community_model, community_interaction_df, is_student=False)
        
        # Print results
        print("\nStudent-to-Student Recommendations:")
        print(f"RMSE: {np.mean(student_results['test_rmse']):.4f}")
        print(f"MAE: {np.mean(student_results['test_mae']):.4f}")
        print("Confusion Matrix:")
        print(student_cm)
        
        print("\nCommunity/Project Recommendations:")
        print(f"RMSE: {np.mean(community_results['test_rmse']):.4f}")
        print(f"MAE: {np.mean(community_results['test_mae']):.4f}")
        print("Confusion Matrix:")
        print(community_cm)
        
        # Example recommendations for student 1
        print("\nGenerating example recommendations...")
        student_id = 1
        student_recs = get_student_recommendations(student_id, student_model, df)
        community_recs = get_community_recommendations(student_id, community_model, df, all_communities)
        
        print(f"\nStudent Recommendations for {df[df['IDEtudiant'] == student_id]['Nom'].iloc[0]}:")
        print(json.dumps(student_recs, indent=2, cls=NumpyEncoder))
        
        print(f"\nCommunity Recommendations for {df[df['IDEtudiant'] == student_id]['Nom'].iloc[0]}:")
        print(json.dumps(community_recs, indent=2, cls=NumpyEncoder))
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()