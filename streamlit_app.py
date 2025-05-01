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
API_URL = os.getenv("API_URL", "http://api:8000")

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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<h2 class='subheader'>{student['name']} (ID: {student['id']})</h2>", unsafe_allow_html=True)
        
        # Display main metrics
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            st.metric("Collaboration Score", student['collab_score'], f"{student['collab_score']/10:.1f}/1.0")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with metrics_col2:
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            st.metric("Interactions", student['interactions'])
            st.markdown("</div>", unsafe_allow_html=True)
            
        with metrics_col3:
            st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
            st.metric("Communities", len(student['communities']))
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Display skills
        st.markdown("<h3>Skills</h3>", unsafe_allow_html=True)
        skill_html = ""
        for skill in student['skills']:
            skill_html += f"<span class='badge'>{skill}</span>"
        st.markdown(skill_html, unsafe_allow_html=True)
        
        # Display interests
        st.markdown("<h3>Interests</h3>", unsafe_allow_html=True)
        interest_html = ""
        for interest in student['interests']:
            interest_html += f"<span class='badge'>{interest}</span>"
        st.markdown(interest_html, unsafe_allow_html=True)
        
        # Display communities
        st.markdown("<h3>Communities</h3>", unsafe_allow_html=True)
        community_html = ""
        for community in student['communities']:
            community_html += f"<span class='badge'>{community}</span>"
        st.markdown(community_html, unsafe_allow_html=True)

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
            
            # Fetch and display detailed info about the recommended student
            if st.button(f"View details for {rec['name']}", key=f"details_{rec['id']}"):
                recommended_student = fetch_student_info(rec['id'])
                if recommended_student:
                    st.subheader(f"Details for {recommended_student['name']}")
                    display_student_info(recommended_student)

def create_network_visualization(student_id, recommendations):
    """Create a network visualization of the student and their recommendations"""
    if not recommendations:
        return None
    
    # Create a graph
    G = nx.Graph()
    
    # Add the selected student
    G.add_node(student_id, size=20, color='#D81B60')
    
    # Add the recommended students
    for rec in recommendations:
        G.add_node(rec['id'], size=15, color='#1E88E5')
        # Add edge with weight based on similarity
        G.add_edge(student_id, rec['id'], weight=rec['similarity'] * 10)
    
    # Get positions for nodes using a spring layout
    pos = nx.spring_layout(G)
    
    # Create edges
    edge_x = []
    edge_y = []
    edge_widths = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_widths.append(edge[2]['weight'])
    
    # Create nodes
    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
    node_text = []
    
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_colors.append(node[1]['color'])
        node_sizes.append(node[1]['size'])
        node_text.append(f"Student ID: {node[0]}")
    
    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create node trace
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
    
    # Create the figure
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

def main():
    st.markdown("<h1 class='main-header'>🎓 Student Recommendation System</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    This application uses graph theory and natural language understanding to recommend students 
    for collaboration based on their interests, skills, communities, and social connections.
    """)
    
    # Fetch all students
    all_students = fetch_all_students()
    
    if not all_students:
        st.error("Failed to load student data. Please check the API connection.")
        st.info(f"Trying to connect to API at: {API_URL}")
        return
    
    # Create a sidebar for selection
    st.sidebar.title("Select a Student")
    
    # Convert to DataFrame for selection
    students_df = pd.DataFrame(all_students)
    selected_student_id = st.sidebar.selectbox(
        "Choose a student to get recommendations for:",
        options=students_df['id'].tolist(),
        format_func=lambda x: f"{students_df[students_df['id'] == x]['name'].iloc[0]} (ID: {x})"
    )
    
    # Number of recommendations
    top_n = st.sidebar.slider(
        "Number of recommendations:",
        min_value=1,
        max_value=10,
        value=5
    )
    
    # Advanced options
    with st.sidebar.expander("Advanced Options"):
        show_network = st.checkbox("Show Network Visualization", value=True)
    
    # Fetch student info
    selected_student = fetch_student_info(selected_student_id)
    
    if selected_student:
        # Display student info
        display_student_info(selected_student)
        
        # Fetch recommendations
        recommendations = fetch_recommendations(selected_student_id, top_n)
        
        # Display recommendations
        if recommendations:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                display_recommendations(recommendations, selected_student)
            
            with col2:
                if show_network:
                    fig = create_network_visualization(selected_student_id, recommendations)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recommendations available for this student.")

if __name__ == "__main__":
    main()