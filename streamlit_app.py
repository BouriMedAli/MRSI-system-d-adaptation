import streamlit as st
import requests
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from io import BytesIO
from PIL import Image
import base64

# Set page config
st.set_page_config(
    page_title="Student Collaboration Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define API URL (matches docker-compose service name)
API_URL = "http://api:5000"

# Custom CSS for styling
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

# Load student IDs
@st.cache_data
def load_student_ids():
    df = pd.read_csv('dataset_etudiants.csv')
    return df['ID_Étudiant'].tolist(), df

student_ids, df = load_student_ids()

# Create main header
st.markdown('<div class="main-header">🎓 Student Collaboration Recommender</div>', unsafe_allow_html=True)

# Sidebar for student selection
st.sidebar.markdown('<div class="sub-header">Student Selection</div>', unsafe_allow_html=True)
selected_student_id = st.sidebar.selectbox("Select Student ID", student_ids)
n_recommendations = st.sidebar.slider("Number of Recommendations", 1, 10, 5)
recommendation_type = st.sidebar.radio("Recommendation Type", ["Student-to-Student", "Community/Project"])

# Get student details
student_details = df[df['ID_Étudiant'] == selected_student_id].iloc[0]

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["Student Profile", "Recommendations", "Collaboration Network"])

with tab1:
    st.markdown('<div class="sub-header">Student Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="student-info">', unsafe_allow_html=True)
    st.markdown(f"### {student_details['Nom']}")
    st.markdown(f"**ID:** {student_details['ID_Étudiant']}")
    
    st.markdown("#### Skills")
    skills_html = ' '.join([f'<span class="badge">{skill}</span>' for skill in student_details['Compétences']])
    st.markdown(skills_html, unsafe_allow_html=True)
    
    st.markdown("#### Interests")
    interests_html = ' '.join([f'<span class="interest-badge">{interest}</span>' for interest in student_details['Centres_d_Intérêt']])
    st.markdown(interests_html, unsafe_allow_html=True)
    
    st.markdown("#### Communities")
    communities_html = ' '.join([f'<span class="community-badge">{community}</span>' for community in student_details['Communautés']])
    st.markdown(communities_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="sub-header">Recommendations</div>', unsafe_allow_html=True)
    if st.button("Get Recommendations"):
        try:
            endpoint = "students" if recommendation_type == "Student-to-Student" else "communities"
            response = requests.get(f"{API_URL}/recommend/{endpoint}?student_id={selected_student_id}&n={n_recommendations}")
            if response.status_code == 200:
                recommendations = response.json()
                for rec in recommendations:
                    st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
                    if recommendation_type == "Student-to-Student":
                        st.markdown(f"**{rec['Nom']} (ID: {rec['ID_Étudiant']})**")
                        st.markdown(f"**Compatibility Score:** {rec['Score']}")
                        st.markdown(f"**Skills:** {', '.join(rec['Compétences'])}")
                        st.markdown(f"**Interests:** {', '.join(rec['Centres_d_Intérêt'])}")
                    else:
                        st.markdown(f"**{rec['Communauté']}**")
                        st.markdown(f"**Project:** {rec['Projet']}")
                        st.markdown(f"**Compatibility Score:** {rec['Score']}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error(f"Error fetching recommendations: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab3:
    st.markdown('<div class="sub-header">Collaboration Network</div>', unsafe_allow_html=True)
    
    # Create a network graph
    G = nx.Graph()
    for _, row in df.iterrows():
        student_id = row['ID_Étudiant']
        G.add_node(student_id, label=row['Nom'])
        for coequipier in row['Coéquipiers']:
            G.add_edge(student_id, coequipier)
    
    # Generate positions for nodes
    pos = nx.spring_layout(G)
    
    # Create edge trace
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node]['label'])
        node_color.append('red' if node == selected_student_id else 'blue')
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=False,
            color=node_color,
            size=10,
            line_width=2
        )
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Student Collaboration Network',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    st.plotly_chart(fig, use_container_width=True)