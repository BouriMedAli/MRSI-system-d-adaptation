import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import os

# API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Set page config
st.set_page_config(
    page_title="Student Recommender System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .recommendation-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 10px;
    }
    .reason-item {
        margin-left: 20px;
        color: #4b7bec;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #3498db;
        margin-bottom: 20px;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2980b9;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .metric-container {
        background-color: #e8f4f8;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .badge {
        background-color: #3498db;
        color: white;
        padding: 5px 10px;
        border-radius: 10px;
        margin-right: 5px;
        margin-bottom: 5px;
        display: inline-block;
    }
    .form-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .rec-details {
        background-color: #eaf6ff;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def fetch_all_students():
    """Fetch all students from the API"""
    try:
        response = requests.get(f"{API_URL}/students")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch students: {e}")
        return []

def fetch_student_info(student_id):
    """Fetch information about a specific student"""
    try:
        response = requests.get(f"{API_URL}/students/{student_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch student info: {e}")
        return None

def fetch_recommendations(student_id, top_n=5):
    """Fetch recommendations for a specific student"""
    try:
        response = requests.get(f"{API_URL}/recommendations/{student_id}?top_n={top_n}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch recommendations: {e}")
        return []

def display_student_info(student):
    """Display information about a student"""
    if not student:
        return
    
    st.markdown(f"<h2 class='subheader'>{student['name']} (ID: {student['id']})</h2>", unsafe_allow_html=True)
    
    # Display main metrics
    cols = st.columns(3)
    with cols[0]:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("Collaboration Score", student.get('collab_score', 'N/A'), 
                 f"{student.get('collab_score', 0)/10:.1f}/1.0" if student.get('collab_score') else "N/A")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("Interactions", student.get('interactions', 'N/A'))
        st.markdown("</div>", unsafe_allow_html=True)
        
    with cols[2]:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("Communities", len(student.get('communities', [])))
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display skills, interests, and communities
    for section in ['skills', 'interests', 'communities']:
        st.markdown(f"<h3>{section.capitalize()}</h3>", unsafe_allow_html=True)
        items_html = "".join([f"<span class='badge'>{item}</span>" for item in student.get(section, [])])
        st.markdown(items_html, unsafe_allow_html=True)

def display_recommendation_detail(student):
    """Display a simplified version of student info for recommendations"""
    if not student:
        return
    
    st.markdown("<div class='rec-details'>", unsafe_allow_html=True)
    st.markdown(f"<h4>{student['name']} - Quick Profile</h4>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"**Collaboration Score:** {student.get('collab_score', 'N/A')}/10")
        st.markdown(f"**Interactions:** {student.get('interactions', 'N/A')}")
    
    with cols[1]:
        st.markdown(f"**Communities:** {', '.join(student.get('communities', []))}")
    
    st.markdown("**Skills:** " + ", ".join(student.get('skills', [])))
    st.markdown("**Interests:** " + ", ".join(student.get('interests', [])))
    st.markdown("</div>", unsafe_allow_html=True)

def display_recommendations(recommendations, selected_student):
    """Display recommendations for a student"""
    if not recommendations:
        st.info("No recommendations available.")
        return
    
    st.markdown(f"<h2 class='subheader'>Top Recommendations for {selected_student['name']}</h2>", unsafe_allow_html=True)
    
    for i, rec in enumerate(recommendations):
        with st.container():
            st.markdown(f"""
            <div class='recommendation-card'>
                <h3>{rec['name']} (ID: {rec['id']})</h3>
                <p>Similarity Score: {rec['similarity']:.2f}</p>
                <h4>Why we recommend:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for reason in rec['reasons']:
                st.markdown(f"<p class='reason-item'>• {reason}</p>", unsafe_allow_html=True)
            
            if 'similarity_breakdown' in rec:
                breakdown = rec['similarity_breakdown']
                st.markdown("#### Similarity Breakdown")
                
                cols = st.columns(5)
                metrics = [
                    ("Interest", "interest"),
                    ("Competence", "competence"),
                    ("Community", "community"),
                    ("Network", "network"),
                    ("Collab", "collab")
                ]
                
                for idx, (label, key) in enumerate(metrics):
                    with cols[idx]:
                        st.metric(label, f"{breakdown.get(key, 0):.2f}")
            
            if st.button(f"View profile for {rec['name']}", key=f"details_{rec['id']}"):
                recommended_student = fetch_student_info(rec['id'])
                if recommended_student:
                    display_recommendation_detail(recommended_student)

def create_network_visualization(student_id, recommendations):
    """Create a network visualization of the student and their recommendations"""
    if not recommendations:
        return None
    
    G = nx.Graph()
    G.add_node(student_id, size=20, color='#D81B60')
    
    for rec in recommendations:
        G.add_node(rec['id'], size=15, color='#1E88E5')
        G.add_edge(student_id, rec['id'], weight=rec['similarity'] * 10)
    
    pos = nx.spring_layout(G)
    
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    node_x, node_y, node_colors, node_sizes, node_text = [], [], [], [], []
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_colors.append(node[1]['color'])
        node_sizes.append(node[1]['size'])
        node_text.append(f"Student ID: {node[0]}")
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            color=node_colors,
            size=node_sizes,
            line=dict(width=2, color='#FFF')
        )
    )
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title='Student Recommendation Network',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=400
        )
    )
    
    return fig

def create_similarity_radar_chart(student_id, recommendations):
    """Create a radar chart showing similarity factors for recommendations"""
    if not recommendations:
        return None
    
    categories = ['Interest', 'Competence', 'Community', 'Network', 'Collab']
    fig = go.Figure()
    
    for rec in recommendations[:3]:  # Limit to top 3 for readability
        breakdown = rec.get('similarity_breakdown', {})
        values = [
            breakdown.get('interest', 0),
            breakdown.get('competence', 0),
            breakdown.get('community', 0),
            breakdown.get('network', 0),
            breakdown.get('collab', 0)
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=f"{rec['name']}"
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 0.4])),
        title="Similarity Factors Comparison",
        showlegend=True,
        height=400
    )
    
    return fig

def new_student_form():
    """Form to create a new student and get recommendations"""
    st.markdown("<h2 class='subheader'>Find Collaboration Partners</h2>", unsafe_allow_html=True)
    st.markdown("Fill out this form to find the best collaborators based on your profile.")
    
    with st.form("collaboration_form", clear_on_submit=False):
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        
        # Basic information
        name = st.text_input("Your Name", placeholder="Enter your name")
        project_name = st.text_input("Project Name", placeholder="What are you working on?")
        
        # Project details
        project_description = st.text_area("Project Description", 
                                         placeholder="Briefly describe your project and what you're looking for in collaborators")
        
        # Skills and interests
        all_skills = ["Python", "AI", "Data Science", "Blockchain", "Design", 
                     "Marketing", "Electronics", "Web Development", "Mobile Development"]
        your_skills = st.multiselect("Your Skills", options=all_skills)
        needed_skills = st.multiselect("Skills Needed", options=all_skills)
        
        all_interests = ["Video Games", "Music", "Robotics", "Ecology", 
                        "Entrepreneurship", "Hackathons", "Art", "Sports"]
        your_interests = st.multiselect("Your Interests", options=all_interests)
        
        all_communities = ["Robotics Club", "AI Group", "Ecology Association", 
                          "Entrepreneurs Club", "Data Science Club", "Art Society"]
        your_communities = st.multiselect("Your Communities", options=all_communities)
        
        # Collaboration preferences
        collab_preference = st.selectbox("Collaboration Style", 
                                       ["Casual", "Regular Meetings", "Intensive", "Remote", "In-person"])
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Find Collaborators")
    
    if submitted:
        if not name or not project_name:
            st.error("Please enter your name and project name")
            return None
            
        return {
            "id": 9999,  # Special ID for new students
            "name": name,
            "collab_score": 7,  # Default score
            "interactions": 50,  # Default interactions
            "skills": your_skills + needed_skills,
            "interests": your_interests,
            "communities": your_communities,
            "project": {
                "name": project_name,
                "description": project_description,
                "needed_skills": needed_skills,
                "collab_preference": collab_preference
            }
        }
    
    return None

def main():
    st.markdown("<h1 class='main-header'>🤝 Collaboration Partner Finder</h1>", unsafe_allow_html=True)
    st.markdown("""
    Find the perfect collaborators for your projects based on shared interests, 
    complementary skills, and community connections using our advanced recommendation system.
    """)
    
    # Create tabs
    tab1, tab2 = st.tabs(["Browse Students", "Find Collaborators"])
    
    with tab1:
        st.markdown("<h2 class='subheader'>Browse Existing Students</h2>", unsafe_allow_html=True)
        students = fetch_all_students()
        
        if students:
            student_ids = [f"{s['name']} (ID: {s['id']})" for s in students]
            selected_student = st.selectbox("Select a student", student_ids)
            
            if selected_student:
                student_id = int(selected_student.split("ID: ")[1].strip(")"))
                student_info = fetch_student_info(student_id)
                
                if student_info:
                    display_student_info(student_info)
                    
                    top_n = st.slider("Number of recommendations:", 1, 10, 5, key="existing_student_top_n")
                    
                    if st.button("Get Recommendations"):
                        recommendations = fetch_recommendations(student_id, top_n)
                        
                        if recommendations:
                            col1, col2 = st.columns([2, 1], gap="large")
                            
                            with col1:
                                display_recommendations(recommendations, student_info)
                            
                            with col2:
                                st.markdown("""
                                <div class='metric-container'>
                                <h3>Recommendation Factors</h3>
                                <ul>
                                <li><strong>Interest similarity (35%)</strong></li>
                                <li><strong>Skill complementarity (25%)</strong></li>
                                <li><strong>Community overlap (20%)</strong></li>
                                <li><strong>Network proximity (10%)</strong></li>
                                <li><strong>Collaboration style (10%)</strong></li>
                                </ul>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                fig = create_network_visualization(student_id, recommendations)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                radar_fig = create_similarity_radar_chart(student_id, recommendations)
                                if radar_fig:
                                    st.plotly_chart(radar_fig, use_container_width=True)
                        else:
                            st.info("No recommendations available for this student.")
        else:
            st.warning("No students found in the database.")
    
    with tab2:
        st.sidebar.title("Recommendation Settings")
        top_n = st.sidebar.slider(
            "Number of recommendations:",
            min_value=1,
            max_value=10,
            value=5,
            key="new_student_top_n"  # Unique key
        )
        
        with st.sidebar.expander("Visualization Options"):
            show_network = st.checkbox("Show Network Graph", value=True)
            show_radar = st.checkbox("Show Radar Chart", value=True)
        
        new_student = new_student_form()
        
        if new_student:
            st.success(f"Searching for collaborators for {new_student['name']}'s project: {new_student['project']['name']}")
            
            # Display project info
            st.markdown(f"### Project: {new_student['project']['name']}")
            st.markdown(new_student['project']['description'])
            
            st.markdown("#### Looking for collaborators with:")
            if new_student['project']['needed_skills']:
                st.markdown("**Skills:** " + ", ".join(new_student['project']['needed_skills']))
            st.markdown(f"**Collaboration Style:** {new_student['project']['collab_preference']}")
            
            with st.spinner("Finding the best collaborators for your project..."):
                try:
                    api_payload = {
                        "name": new_student["name"],
                        "collab_score": new_student["collab_score"],
                        "interactions": new_student["interactions"],
                        "communities": new_student["communities"],
                        "skills": new_student["skills"],
                        "interests": new_student["interests"]
                    }
                    
                    response = requests.post(
                        f"{API_URL}/recommend-new?top_n={top_n}",
                        json=api_payload
                    )
                    response.raise_for_status()
                    recommendations = response.json()
                    
                    if recommendations:
                        col1, col2 = st.columns([2, 1], gap="large")
                        
                        with col1:
                            display_recommendations(recommendations, new_student)
                        
                        with col2:
                            st.markdown("""
                            <div class='metric-container'>
                            <h3>Recommendation Factors</h3>
                            <ul>
                            <li><strong>Interest similarity (35%)</strong></li>
                            <li><strong>Skill complementarity (25%)</strong></li>
                            <li><strong>Community overlap (20%)</strong></li>
                            <li><strong>Network proximity (10%)</strong></li>
                            <li><strong>Collaboration style (10%)</strong></li>
                            </ul>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if show_network:
                                fig = create_network_visualization(new_student["id"], recommendations)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                            
                            if show_radar and recommendations:
                                radar_fig = create_similarity_radar_chart(new_student["id"], recommendations)
                                if radar_fig:
                                    st.plotly_chart(radar_fig, use_container_width=True)
                    else:
                        st.info("No recommendations available. Try broadening your search criteria.")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"Error finding collaborators: {e}")
                    st.warning("""
                    If you're seeing this error, the API endpoint for new student recommendations
                    might not be implemented yet. Make sure the API is running and the endpoint is available.
                    """)

if __name__ == "__main__":
    main()