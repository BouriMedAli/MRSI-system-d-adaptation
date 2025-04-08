import streamlit as st
import requests
import json

# Streamlit app configuration
st.set_page_config(page_title="Student Recommendation System", layout="wide")

# API endpoint
API_URL = "http://localhost:8000/recommend/"

# Title
st.title("Student Recommendation System")

# Input form
with st.form(key="recommendation_form"):
    st.subheader("Enter Student Profile")
    
    travaux_collaboratifs = st.number_input("Travaux Collaboratifs", min_value=0, max_value=10, value=7)
    nombre_interactions = st.number_input("Nombre Interactions", min_value=0, max_value=100, value=50)
    
    communautés_options = [
        "Club Robotique", "Groupe IA", "Club Entrepreneurs", "Association Écologie", "Club Data Science"
    ]
    compétences_options = [
        "Blockchain", "IA", "Data Science", "Python", "Design", "Électronique", "Marketing"
    ]
    centres_d_intérêt_options = [
        "Jeux vidéo", "Musique", "Robotique", "Entrepreneuriat", "Écologie", "Hackathon"
    ]
    
    communautés = st.multiselect("Communautés", options=communautés_options, default=["Club Robotique"])
    compétences = st.multiselect("Compétences", options=compétences_options, default=["IA"])
    centres_d_intérêt = st.multiselect("Centres d'Intérêt", options=centres_d_intérêt_options, default=["Musique"])
    
    submit_button = st.form_submit_button(label="Get Recommendations")

# Process form submission
if submit_button:
    query_profile = {
        "numeric": [float(travaux_collaboratifs), float(nombre_interactions)],
        "communautés": communautés,
        "compétences": compétences,
        "centres_d_intérêt": centres_d_intérêt
    }
    
    try:
        response = requests.post(API_URL, json=query_profile)
        if response.status_code == 200:
            recommendations = response.json()["recommended_students"]
            st.success("Recommendations retrieved successfully!")
            st.subheader("Recommended Students")
            st.table(recommendations)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")