import streamlit as st
import pandas as pd
import requests
import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

# Set page config
st.set_page_config(
    page_title="Student Collaboration System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define the API URL (either local or from docker-compose)
API_URL = "http://localhost:8000"  # Use backend service name from docker-compose

# Function to load data from API
@st.cache_data(ttl=600)
def load_data():
    try:
        # Get all student data
        response = requests.get(f"{API_URL}/student_network")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error loading data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

@st.cache_data(ttl=600)
def get_metrics():
    try:
        response = requests.get(f"{API_URL}/metrics")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error loading metrics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

def get_student_recommendations(student_id, top_n=5):
    try:
        response = requests.get(f"{API_URL}/recommend_students/{student_id}?top_n={top_n}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error loading recommendations: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

def get_community_recommendations(student_id, top_n=3):
    try:
        response = requests.get(f"{API_URL}/recommend_communities/{student_id}?top_n={top_n}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error loading community recommendations: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

def get_student_details(student_id):
    try:
        response = requests.get(f"{API_URL}/student/{student_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error loading student details: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 10px;
    }
    .recommendation-card {
        background-color: #f7f7f7;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        border-left: 4px solid #1E88E5;
    }
    .student-info {
        padding: 10px;
        background-color: #e9f5fe;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .badge {
        background-color: #1E88E5;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-right: 5px;
        display: inline-block;
    }
    .interest-badge {
        background-color: #4CAF50;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-right: 5px;
        display: inline-block;
    }
    .community-badge {
        background-color: #FF9800;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-right: 5px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Create main header
st.markdown('<div class="main-header">🎓 Student Collaboration Recommendation System</div>', unsafe_allow_html=True)

# Load data
network_data = load_data()
metrics_data = get_metrics()

# Create sidebar for student selection
st.sidebar.markdown('<div class="sub-header">Student Selection</div>', unsafe_allow_html=True)

if network_data:
    # Extract student IDs and names
    student_nodes = network_data["nodes"]
    student_options = {node["id"]: f"{node['name']} (ID: {node['id']})" for node in student_nodes}
    
    # Create a dropdown for student selection
    selected_student_id = st.sidebar.selectbox(
        "Select a student:",
        options=list(student_options.keys()),
        format_func=lambda x: student_options[x]
    )
    
    # Get student details for the selected student
    student_details = get_student_details(selected_student_id)
    
    # Sidebar - Model Metrics
    st.sidebar.markdown('<div class="sub-header">Model Performance</div>', unsafe_allow_html=True)
    
    if metrics_data:
        student_model = metrics_data["student_collaboration_model"]
        community_model = metrics_data["community_recommendation_model"]
        
        with st.sidebar.expander("Student Collaboration Model Metrics", expanded=False):
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            col1.metric("RMSE", f"{student_model['rmse']:.3f}")
            col2.metric("MAE", f"{student_model['mae']:.3f}")
            
            col3, col4 = st.columns(2)
            col3.metric("Precision", f"{student_model['precision']:.3f}")
            col4.metric("Recall", f"{student_model['recall']:.3f}")
            
            st.metric("F1 Score", f"{student_model['f1_score']:.3f}")
            
            # Display confusion matrix image if available
            if "confusion_matrix_img" in student_model and student_model["confusion_matrix_img"]:
                st.markdown("### Confusion Matrix")
                st.image(
                    Image.open(BytesIO(base64.b64decode(student_model["confusion_matrix_img"]))), 
                    caption="Collaboration Compatibility Confusion Matrix"
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with st.sidebar.expander("Community Recommendation Model Metrics", expanded=False):
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            col1.metric("RMSE", f"{community_model['rmse']:.3f}")
            col2.metric("MAE", f"{community_model['mae']:.3f}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Student Dashboard", "Recommendations", "Network Visualization"])
    
    with tab1:
        if student_details:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown('<div class="sub-header">Student Profile</div>', unsafe_allow_html=True)
                st.markdown('<div class="student-info">', unsafe_allow_html=True)
                st.markdown(f"### {student_details['Nom']}")
                st.markdown(f"**ID:** {student_details['ID_Étudiant']}")
                st.markdown(f"**Collaboration Score:** {student_details['Travaux_Collaboratifs']}/10")
                st.markdown(f"**Interaction Count:** {student_details['Nombre_Interactions']}")
                
                st.markdown("#### Skills")
                skills_html = ' '.join([f'<span class="badge">{skill}</span>' for skill in student_details['Compétences']])
                st.markdown(skills_html, unsafe_allow_html=True)
                
                st.markdown("#### Interests")
                interests_html = ' '.join([f'<span class="interest-badge">{interest}</span>' for interest in student_details["Centres_d'Intérêt"]])
                st.markdown(interests_html, unsafe_allow_html=True)
                
                st.markdown("#### Communities")
                communities_html = ' '.join([f'<span class="community-badge">{community}</span>' for community in student_details['Communautés']])
                st.markdown(communities_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
            st.markdown('<div class="sub-header">🌐 Recommended Communities</div>', unsafe_allow_html=True)
            community_recommendations = get_community_recommendations(selected_student_id, top_n=top_n_communities)
            
            if community_recommendations:
                for i, rec in enumerate(community_recommendations):
                    st.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
                    
                    st.markdown(f"### {i+1}. {rec['recommended_community']}")
                    
                    # Show compatibility score
                    compatibility = min(100, round(rec['compatibility_score'] * 20))
                    st.progress(compatibility/100)
                    st.markdown(f"**Compatibility Score:** {compatibility}%")
                    
                    # Show skills to be gained
                    if rec['related_skills']:
                        st.markdown("**Skills You Can Develop:**")
                        skills_html = ' '.join([f'<span class="badge">{skill}</span>' for skill in rec['related_skills']])
                        st.markdown(skills_html, unsafe_allow_html=True)
                        
                    # Show members of this community
                    community_members = [node for node in network_data["nodes"] 
                                       if rec['recommended_community'] in node['communities']]
                    
                    if community_members:
                        with st.expander(f"View {len(community_members)} community members"):
                            for member in community_members[:5]:  # Limit to 5 to keep it clean
                                st.markdown(f"- **{member['name']}** (ID: {member['id']})")
                            if len(community_members) > 5:
                                st.markdown(f"...and {len(community_members) - 5} more")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No community recommendations available")
                st.markdown('<div class="sub-header">Current Collaborations</div>', unsafe_allow_html=True)
                
                if student_details['Coéquipiers']:
                    # Create a radar chart showing skills distribution
                    fig = go.Figure()
                    
                    # Get all unique skills
                    all_skills = set()
                    teammates_data = []
                    
                    # Add student skills
                    all_skills.update(student_details['Compétences'])
                    
                    # Add teammates skills
                    for teammate in student_details['Coéquipiers']:
                        teammate_detail = get_student_details(teammate['id'])
                        if teammate_detail:
                            teammates_data.append(teammate_detail)
                            all_skills.update(teammate_detail['Compétences'])
                    
                    all_skills = list(all_skills)
                    
                    # Create radar chart with student and teammates
                    # Add main student data
                    student_skill_values = [1 if skill in student_details['Compétences'] else 0 for skill in all_skills]
                    fig.add_trace(go.Scatterpolar(
                        r=student_skill_values,
                        theta=all_skills,
                        fill='toself',
                        name=f"{student_details['Nom']} (You)"
                    ))
                    
                    # Add teammate data
                    for teammate in teammates_data:
                        teammate_skill_values = [1 if skill in teammate['Compétences'] else 0 for skill in all_skills]
                        fig.add_trace(go.Scatterpolar(
                            r=teammate_skill_values,
                            theta=all_skills,
                            fill='toself',
                            name=f"{teammate['Nom']}"
                        ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1]
                            )
                        ),
                        title="Skills Distribution Among Collaborators",
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # List teammates
                    st.markdown("#### Current Teammates")
                    for teammate in student_details['Coéquipiers']:
                        st.markdown(f"- **{teammate['name']}** (ID: {teammate['id']})")
                else:
                    st.info("This student has no current collaborators.")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        # Set number of recommendations to display
        top_n_students = st.slider("Number of student recommendations to display", 3, 10, 5)
        top_n_communities = st.slider("Number of community recommendations to display", 2, 5, 3)
        
        with col1:
            st.markdown('<div class="sub-header">🤝 Recommended Study Partners</div>', unsafe_allow_html=True)
            student_recommendations = get_student_recommendations(selected_student_id, top_n=top_n_students)
            
            if student_recommendations:
                for i, rec in enumerate(student_recommendations):
                    st.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
                    
                    # Get recommended student details
                    rec_student = get_student_details(rec['recommended_student_id'])
                    if rec_student:
                        st.markdown(f"### {i+1}. {rec_student['Nom']}")
                        
                        # Show compatibility metric
                        compatibility = min(100, round(rec['compatibility_score'] * 10))
                        st.progress(compatibility/100)
                        st.markdown(f"**Compatibility Score:** {compatibility}%")
                        
                        # Show what they have in common
                        if rec['shared_skills']:
                            st.markdown("**Shared Skills:**")
                            skills_html = ' '.join([f'<span class="badge">{skill}</span>' for skill in rec['shared_skills']])
                            st.markdown(skills_html, unsafe_allow_html=True)
                        
                        if rec['shared_interests']:
                            st.markdown("**Shared Interests:**")
                            interests_html = ' '.join([f'<span class="interest-badge">{interest}</span>' for interest in rec['shared_interests']])
                            st.markdown(interests_html, unsafe_allow_html=True)
                            
                        # Show complementary skills
                        complementary_skills = set(rec_student['Compétences']) - set(student_details['Compétences'])
                        if complementary_skills:
                            st.markdown("**Complementary Skills You Can Learn:**")
                            comp_skills_html = ' '.join([f'<span class="badge">{skill}</span>' for skill in complementary_skills])
                            st.markdown(comp_skills_html, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No student recommendations available")