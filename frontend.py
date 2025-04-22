import streamlit as st
import requests
import json
import pandas as pd

# Streamlit app configuration
st.set_page_config(page_title="Student Recommendation System", layout="wide")

# API endpoints
API_URL = "http://localhost:8000/recommend/"
REGISTER_URL = "http://localhost:8000/register/"
CATEGORIES_URL = "http://localhost:8000/categories/"

# Initialize session state
if 'categories' not in st.session_state:
    try:
        response = requests.get(CATEGORIES_URL)
        if response.status_code == 200:
            st.session_state.categories = response.json()
        else:
            st.session_state.categories = {
                "communities": ["Club Robotique", "Groupe IA", "Club Entrepreneurs", "Association Écologie", "Club Data Science"],
                "skills": ["Blockchain", "IA", "Data Science", "Python", "Design", "Électronique", "Marketing"],
                "interests": ["Jeux vidéo", "Musique", "Robotique", "Entrepreneuriat", "Écologie", "Hackathon"]
            }
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")
        st.session_state.categories = {
            "communities": ["Club Robotique", "Groupe IA", "Club Entrepreneurs", "Association Écologie", "Club Data Science"],
            "skills": ["Blockchain", "IA", "Data Science", "Python", "Design", "Électronique", "Marketing"],
            "interests": ["Jeux vidéo", "Musique", "Robotique", "Entrepreneuriat", "Écologie", "Hackathon"]
        }

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Get Recommendations", "Register New Student", "About"])

# Tab 1: Get Recommendations
with tab1:
    st.title("Student Recommendation System")
    
    with st.form(key="recommendation_form"):
        st.subheader("Enter Student Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            travaux_collaboratifs = st.slider("Travaux Collaboratifs", min_value=0, max_value=10, value=7)
            nombre_interactions = st.slider("Nombre Interactions", min_value=0, max_value=100, value=50)
            
            # Add option for existing student
            is_existing = st.checkbox("Existing Student")
            student_id = None
            if is_existing:
                student_id = st.number_input("Student ID", min_value=1, value=1)
        
        with col2:
            communautés_options = st.session_state.categories.get("communities", [])
            compétences_options = st.session_state.categories.get("skills", [])
            centres_d_intérêt_options = st.session_state.categories.get("interests", [])
            
            communautés = st.multiselect("Communautés", options=communautés_options, default=[communautés_options[0]] if communautés_options else [])
            compétences = st.multiselect("Compétences", options=compétences_options, default=[compétences_options[0]] if compétences_options else [])
            centres_d_intérêt = st.multiselect("Centres d'Intérêt", options=centres_d_intérêt_options, default=[centres_d_intérêt_options[0]] if centres_d_intérêt_options else [])
        
        submit_button = st.form_submit_button(label="Get Recommendations")
    
    # Process form submission
    if submit_button:
        query_profile = {
            "numeric": [float(travaux_collaboratifs), float(nombre_interactions)],
            "communautés": communautés,
            "compétences": compétences,
            "centres_d_intérêt": centres_d_intérêt
        }
        
        if is_existing and student_id:
            query_profile["student_id"] = student_id
        
        try:
            with st.spinner("Getting recommendations..."):
                response = requests.post(API_URL, json=query_profile)
                if response.status_code == 200:
                    recommendations = response.json()["recommended_students"]
                    processing_time = response.json()["metadata"]["processing_time_ms"]
                    
                    st.success(f"Recommendations retrieved successfully in {processing_time} ms!")
                    
                    # Convert to DataFrame for better display
                    if recommendations:
                        df = pd.DataFrame(recommendations)
                        
                        # Display similarity scores with progress bars
                        st.subheader("Recommended Students")
                        
                        for i, row in df.iterrows():
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.write(f"**{row['Nom']}** (ID: {row['ID_Étudiant']})")
                            with col2:
                                st.progress(min(row['similarity_score'], 1.0))
                                st.write(f"Similarity: {row['similarity_score']:.2f}")
                            
                            # Show student details in an expander
                            with st.expander(f"Details for {row['Nom']}"):
                                st.write("**Communities:**", ", ".join(row.get('communautés', [])))
                                st.write("**Skills:**", ", ".join(row.get('compétences', [])))
                                st.write("**Interests:**", ", ".join(row.get('centres_d_intérêt', [])))
                    else:
                        st.warning("No recommendations found")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API: {str(e)}")

# Tab 2: Register New Student
with tab2:
    st.title("Register New Student")
    
    with st.form(key="registration_form"):
        st.subheader("Student Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Student Name")
            travaux_collaboratifs = st.slider("Travaux Collaboratifs", min_value=0, max_value=10, value=5, key="reg_tc")
            nombre_interactions = st.slider("Nombre Interactions", min_value=0, max_value=100, value=50, key="reg_ni")
        
        with col2:
            communautés_options = st.session_state.categories.get("communities", [])
            compétences_options = st.session_state.categories.get("skills", [])
            centres_d_intérêt_options = st.session_state.categories.get("interests", [])
            
            communautés = st.multiselect("Communautés", options=communautés_options, default=[], key="reg_comm")
            compétences = st.multiselect("Compétences", options=compétences_options, default=[], key="reg_comp")
            centres_d_intérêt = st.multiselect("Centres d'Intérêt", options=centres_d_intérêt_options, default=[], key="reg_int")
        
        submit_registration = st.form_submit_button(label="Register Student")
    
    if submit_registration:
        if not nom:
            st.error("Student name is required")
        else:
            student_data = {
                "nom": nom,
                "travaux_collaboratifs": travaux_collaboratifs,
                "nombre_interactions": nombre_interactions,
                "communautés": communautés,
                "compétences": compétences,
                "centres_d_intérêt": centres_d_intérêt
            }
            
            try:
                with st.spinner("Registering student..."):
                    response = requests.post(REGISTER_URL, json=student_data)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Student registered successfully! Student ID: {result['student_id']}")
                        st.balloons()
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

# Tab 3: About
with tab3:
    st.title("About the Student Recommendation System")
    
    st.markdown("""
    ## How it Works
    
    This system uses a hybrid recommendation approach that combines:
    
    1. **Collaborative Filtering**: Recommends students based on shared interests, communities, and skills
    2. **Content-Based Filtering**: Uses student profile attributes to find similar students
    3. **Cold-Start Handling**: Special handling for new students with no prior interactions
    
    ## Features
    
    - **Get Recommendations**: Find similar students based on profile data
    - **Register New Student**: Add new students to the system
    - **Existing Student Mode**: Get recommendations for students already in the system
    
    ## Technologies Used
    
    - FastAPI for backend API
    - Streamlit for frontend
    - Scikit-Surprise for recommendation algorithms
    - Docker for containerization
    
    ## Dataset
    
    The system uses a dataset of student profiles with the following attributes:
    
    - Travaux Collaboratifs (Collaborative Work Score)
    - Nombre Interactions (Number of Interactions)
    - Communautés (Communities/Clubs)
    - Compétences (Skills)
    - Centres d'Intérêt (Interests)
    """)
    
    st.info("For more information, contact the system administrator.")