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

# Create tabs
recommend_tab, register_tab, about_tab = st.tabs(["Get Recommendations", "Register New Student", "About"])

# --- Recommendation Tab ---
with recommend_tab:
    st.title("Student Recommendation System")

    with st.form(key="recommendation_form"):
        st.subheader("Enter Student Profile")

        col1, col2 = st.columns(2)

        with col1:
            travaux_collaboratifs = st.slider("Travaux Collaboratifs", 0, 10, 7)
            nombre_interactions = st.slider("Nombre Interactions", 0, 100, 50)
            is_existing = st.checkbox("Existing Student")
            student_id = None
            if is_existing:
                student_id = st.number_input("Student ID", min_value=1, value=1)

        with col2:
            categories = st.session_state.categories
            communautes = st.multiselect("Communautés", categories.get("communities", []))
            competences = st.multiselect("Compétences", categories.get("skills", []))
            interets = st.multiselect("Centres d'Intérêt", categories.get("interests", []))

        submit_button = st.form_submit_button(label="Get Recommendations")

    if submit_button:
        # Ensure at least one option is selected from each category
        if not communautes:
            communautes = categories.get("communities", [])[:1]  # Select first option as default
        if not competences:
            competences = categories.get("skills", [])[:1]  # Select first option as default
        if not interets:
            interets = categories.get("interests", [])[:1]  # Select first option as default
            
        query_profile = {
            "numeric": [float(travaux_collaboratifs), float(nombre_interactions)],
            "communautés": communautes,
            "compétences": competences,
            "centres_d_intérêt": interets  # Using underscore instead of apostrophe
        }
        if is_existing and student_id:
            query_profile["student_id"] = student_id

        try:
            with st.spinner("Getting recommendations..."):
                response = requests.post(API_URL, json=query_profile)
                if response.status_code == 200:
                    data = response.json()
                    recommendations = data["recommended_students"]
                    st.success(f"Recommendations retrieved in {data['metadata']['processing_time_ms']} ms")

                    st.subheader("Recommended Students")
                    for student in recommendations:
                        # Ensure we have lists for all student attributes (not None)
                        student_communities = student.get("Communautés", []) or []
                        student_skills = student.get("Compétences", []) or []
                        student_interests = student.get("Centres_d_Intérêt", []) or []
                        
                        common_communities = set(communautes).intersection(set(student_communities))
                        common_skills = set(competences).intersection(set(student_skills))
                        common_interests = set(interets).intersection(set(student_interests))
                        
                        # Get numerical attributes with defaults
                        student_collab = student.get("Travaux_Collaboratifs", 5)
                        student_interact = student.get("Nombre_Interactions", 50)
                        
                        collab_diff = abs(travaux_collaboratifs - student_collab)
                        interact_diff = abs(nombre_interactions - student_interact)

                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.write(f"**{student['Nom']}** (ID: {student['ID_Étudiant']})")
                        with col2:
                            # Ensure similarity score is between 0 and 1 for progress bar
                            normalized_score = min(max(student.get('similarity_score', 0.5), 0), 1.0)
                            st.progress(normalized_score)
                            st.write(f"Similarity: {normalized_score:.2f}")

                        with st.expander(f"Details for {student['Nom']}"):
                            st.write(f"**Collaborative Work Score:** {student_collab}")
                            st.write(f"**Number of Interactions:** {student_interact}")
                            
                            # Display communities, skills, and interests (ensure we never show "None")
                            st.write("**Communities:**", ", ".join(student_communities) if student_communities else "No communities")
                            st.write("**Skills:**", ", ".join(student_skills) if student_skills else "No skills")
                            st.write("**Interests:**", ", ".join(student_interests) if student_interests else "No interests")
                            
                            st.write("**Why this student is recommended:**")
                            summary_parts = []
                            if common_communities:
                                summary_parts.append(f"shares {len(common_communities)} community(ies): {', '.join(common_communities)}")
                            if common_skills:
                                summary_parts.append(f"has {len(common_skills)} skill(s) in common: {', '.join(common_skills)}")
                            if common_interests:
                                summary_parts.append(f"shares {len(common_interests)} interest(s): {', '.join(common_interests)}")
                            if collab_diff <= 2:
                                summary_parts.append("has a similar collaborative work style")
                            if interact_diff <= 10:
                                summary_parts.append("has a similar level of interaction")
                                
                            # Ensure we always have something to say about the recommendation
                            if not summary_parts:
                                if len(student_communities) > 0:
                                    summary_parts.append(f"is part of the {student_communities[0]} community")
                                elif len(student_skills) > 0:
                                    summary_parts.append(f"has {student_skills[0]} skills")
                                elif len(student_interests) > 0:
                                    summary_parts.append(f"is interested in {student_interests[0]}")
                                else:
                                    summary_parts.append("has a complementary profile")
                                    
                            st.write("This student " + (", ".join(summary_parts) + "."))

                            st.write("**Similarity Breakdown:**")
                            st.write(f"- Common Communities: {len(common_communities)} ({', '.join(common_communities) if common_communities else 'Different communities'})")
                            st.write(f"- Common Skills: {len(common_skills)} ({', '.join(common_skills) if common_skills else 'Different skills'})")
                            st.write(f"- Common Interests: {len(common_interests)} ({', '.join(common_interests) if common_interests else 'Different interests'})")
                            st.write(f"- Collaborative Work Difference: {collab_diff}")
                            st.write(f"- Interactions Difference: {interact_diff}")

                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")

# --- Registration Tab ---
with register_tab:
    st.title("Register New Student")
    with st.form(key="registration_form"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Student Name")
            travaux_collaboratifs = st.slider("Travaux Collaboratifs", 0, 10, 5, key="reg_tc")
            nombre_interactions = st.slider("Nombre Interactions", 0, 100, 50, key="reg_ni")

        with col2:
            communautes = st.multiselect("Communautés", st.session_state.categories.get("communities", []), key="reg_comm")
            competences = st.multiselect("Compétences", st.session_state.categories.get("skills", []), key="reg_comp")
            interets = st.multiselect("Centres d'Intérêt", st.session_state.categories.get("interests", []), key="reg_int")

        submit_registration = st.form_submit_button(label="Register Student")

    if submit_registration:
        if not nom:
            st.error("Student name is required")
        else:
            # Ensure at least one option is selected from each category for new students
            if not communautes:
                communautes = st.session_state.categories.get("communities", [])[:1]
            if not competences:
                competences = st.session_state.categories.get("skills", [])[:1]
            if not interets:
                interets = st.session_state.categories.get("interests", [])[:1]
                
            student_data = {
                "nom": nom,
                "travaux_collaboratifs": travaux_collaboratifs,
                "nombre_interactions": nombre_interactions,
                "communautés": communautes,
                "compétences": competences,
                "centres_d_intérêt": interets  # Using underscore instead of apostrophe
            }
            try:
                with st.spinner("Registering student..."):
                    response = requests.post(REGISTER_URL, json=student_data)
                    if response.status_code == 200:
                        st.success(f"Student registered! ID: {response.json()['student_id']}")
                        st.balloons()
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")

# --- About Tab ---
with about_tab:
    st.title("About the Student Recommendation System")
    st.markdown("""
    ## How it Works
    This system uses a hybrid recommendation approach:
    - **Collaborative Filtering**: Based on shared attributes and past interactions
    - **Content-Based Filtering**: Based on similarity of profile attributes
    - **Cold-Start Handling**: Supports new users without prior history

    ## Features
    - Get personalized student recommendations
    - Register new students into the system
    - Detailed explanation of why students are recommended
    - View common attributes and differences between profiles

    ## Data Used for Matching
    - **Collaborative Work Style**: How well students work in teams (0-10)
    - **Interaction Level**: How socially active they are (0-100)
    - **Communities**: Clubs and groups they belong to
    - **Skills**: Technical and soft skills they possess
    - **Interests**: Personal and academic interests

    ## Technologies
    - FastAPI backend with Scikit-Surprise recommendation algorithms
    - Streamlit interactive frontend
    - Docker containerization for easy deployment
    """)