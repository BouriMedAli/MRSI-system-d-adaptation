import streamlit as st
import pandas as pd
import requests
import ast
import plotly.graph_objects as go
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuration de la page
st.set_page_config(page_title="Réseau de Collaboration MRSI", layout="wide", page_icon="🌐")

# Styles CSS pour un design moderne
st.markdown("""
    <style>
    .main { background-color: #f8fafc; padding: 20px; }
    .dark-mode { background-color: #1f2937; color: white; }
    .dark-mode .card { background-color: #374151; color: white; }
    .dark-mode h1, .dark-mode h3 { color: #60a5fa; }
    .stButton>button {
        background-color: #3b82f6; color: white; border-radius: 8px; padding: 10px 20px;
        font-weight: bold; border: none; transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2563eb; transform: scale(1.05);
    }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>select {
        border-radius: 8px; border: 1px solid #d1d5db; padding: 10px;
    }
    .card {
        background-color: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px;
        transition: all 0.3s;
    }
    .card:hover {
        transform: translateY(-5px); box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .error { color: #dc2626; font-weight: bold; padding: 10px; background-color: #fee2e2; border-radius: 8px; }
    .success { color: #15803d; font-weight: bold; padding: 10px; background-color: #dcfce7; border-radius: 8px; }
    .sidebar .sidebar-content { background-color: #ffffff; border-right: 1px solid #e5e7eb; }
    h1 { color: #1e3a8a; font-size: 2.5em; }
    h3 { color: #1f2937; }
    </style>
""", unsafe_allow_html=True)

# Gestion du thème
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Charger les données
@st.cache_data
def load_data():
    df = pd.read_pickle("students_df.pkl")
    skills = sorted(set([skill for skills in df['Compétences'].apply(ast.literal_eval) for skill in skills]))
    interests = sorted(set([interest for interests in df.get('Centres_d\'Intérêt', pd.Series(['[]'] * len(df))).apply(ast.literal_eval) for interest in interests]))
    return df, skills, interests

df, skills, interests = load_data()

# Gestion de l'historique
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar pour le formulaire
with st.sidebar:
    st.markdown("<h2 style='color: #1e3a8a;'>Réseau de Collaboration</h2>", unsafe_allow_html=True)
    
    student_id = st.number_input("ID Étudiant (1-50)", min_value=1, max_value=50, value=1)
    n_recommendations = st.number_input("Nombre de recommandations", min_value=1, max_value=10, value=5)
    
    skill_filter = st.multiselect("Compétences", skills, default=["Python"])
    interest_filter = st.multiselect("Centres d'intérêt", interests, default=["Robotique"])
    
    skill_weight = st.slider("Poids des compétences", 0.0, 1.0, 0.5, 0.1)
    interest_weight = st.slider("Poids des centres d'intérêt", 0.0, 1.0, 0.5, 0.1)
    
    submit_button = st.button("Obtenir les recommandations")
    reset_button = st.button("Réinitialiser")
    theme_button = st.button("Changer de thème", on_click=toggle_theme)

# Appliquer le thème
theme_class = "dark-mode" if st.session_state.theme == 'dark' else ""
st.markdown(f"<div class='{theme_class}'>", unsafe_allow_html=True)

# Titre principal
st.markdown("<h1>Systéme de recommandation</h1>", unsafe_allow_html=True)

# Réinitialisation
if reset_button:
    st.session_state.clear()
    st.experimental_rerun()

# Traitement de la soumission
if submit_button:
    # Créer la requête JSON (première compétence/intérêt pour simplifier)
    request_data = {
        "student_id": student_id,
        "n_recommendations": n_recommendations,
        "skill_filter": skill_filter[0] if skill_filter else None,
        "interest_filter": interest_filter[0] if interest_filter else None,
        "skill_weight": skill_weight,
        "interest_weight": interest_weight
    }
    
    # Appeler l'API FastAPI
    try:
        response = requests.post("http://localhost:8000/recommendations/", json=request_data)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            st.markdown(f"<div class='error'>Erreur : {result['error']}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='success'>Recommandations générées avec succès !</div>", unsafe_allow_html=True)
            
            # Sauvegarder dans l'historique
            st.session_state.history.append({
                "request": request_data,
                "result": result
            })
            if len(st.session_state.history) > 5:
                st.session_state.history.pop(0)
            
            # Afficher les recommandations
            st.markdown("<h3>Coéquipiers recommandés</h3>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, (teammate_id, score) in enumerate(result["teammates"]):
                teammate_row = df[df['ID_Étudiant'] == teammate_id]
                skills = ast.literal_eval(teammate_row['Compétences'].iloc[0]) if not teammate_row.empty else []
                interests = ast.literal_eval(teammate_row.get('Centres_d\'Intérêt', ['[]']).iloc[0]) if not teammate_row.empty else []
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class='card'>
                            <h4>Étudiant {teammate_id}</h4>
                            <p><b>Score :</b> {score:.2f}/5</p>
                            <p><b>Compétences :</b> {', '.join(skills)}</p>
                            <p><b>Centres d'intérêt :</b> {', '.join(interests) if interests else 'Aucun'}</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Créer un graphe de réseau
            nodes = [f"Étudiant {student_id}"] + [f"Étudiant {t[0]}" for t in result["teammates"]]
            edges = [(0, i+1) for i in range(len(result["teammates"]))]  # Connexion étudiant -> coéquipiers
            edge_x = []
            edge_y = []
            node_x = []
            node_y = []
            for i, node in enumerate(nodes):
                x = 0.5 + 0.4 * (i % 3 - 1)
                y = 0.8 - 0.3 * (i // 3)
                node_x.append(x)
                node_y.append(y)
            for edge in edges:
                x0, y0 = node_x[edge[0]], node_y[edge[0]]
                x1, y1 = node_x[edge[1]], node_y[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y, line=dict(width=2, color='#888'), hoverinfo='none', mode='lines')
            node_trace = go.Scatter(
                x=node_x, y=node_y, mode='markers+text', text=nodes, textposition='top center',
                marker=dict(size=20, color=['#3b82f6'] + ['#60a5fa'] * len(result["teammates"])))
            
            fig = go.Figure(data=[edge_trace, node_trace],
                            layout=go.Layout(
                                title="Réseau de collaboration",
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                plot_bgcolor="white", paper_bgcolor="white"))
            st.plotly_chart(fig, use_container_width=True)
            
            # Export CSV
            teammates_data = []
            for teammate_id, score in result["teammates"]:
                teammate_row = df[df['ID_Étudiant'] == teammate_id]
                skills = ', '.join(ast.literal_eval(teammate_row['Compétences'].iloc[0])) if not teammate_row.empty else ''
                interests = ', '.join(ast.literal_eval(teammate_row.get('Centres_d\'Intérêt', ['[]']).iloc[0])) if not teammate_row.empty else 'Aucun'
                teammates_data.append({
                    'ID': teammate_id,
                    'Score': score,
                    'Compétences': skills,
                    'Centres d''intérêt': interests
                })
            export_df = pd.DataFrame(teammates_data)
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="Télécharger en CSV",
                data=csv,
                file_name="recommandations.csv",
                mime="text/csv"
            )
            
            # Export PDF
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, "Recommandations MRSI")
            y = 700
            for _, row in export_df.iterrows():
                c.drawString(100, y, f"Étudiant {row['ID']}: Score {row['Score']:.2f}")
                c.drawString(100, y-20, f"Compétences: {row['Compétences']}")
                c.drawString(100, y-40, f"Centres d'intérêt: {row.get('Centres d''intérêt', '')}")
                y -= 60
            c.showPage()
            c.save()
            pdf = buffer.getvalue()
            st.download_button(
                label="Télécharger en PDF",
                data=pdf,
                file_name="recommandations.pdf",
                mime="application/pdf"
            )
            
    except requests.exceptions.RequestException as e:
        st.markdown(f"<div class='error'>Erreur de connexion à l'API : {str(e)}</div>", unsafe_allow_html=True)

# Afficher l'historique
if st.session_state.history:
    with st.expander("Historique des requêtes"):
        for i, entry in enumerate(st.session_state.history):
            st.markdown(f"<h4>Requête {i+1}</h4>", unsafe_allow_html=True)
            st.json(entry["request"])
            st.markdown("<h5>Résultats</h5>", unsafe_allow_html=True)
            for teammate_id, score in entry["result"]["teammates"]:
                st.markdown(f"- Étudiant {teammate_id}: Score {score:.2f}")

# Placeholder
else:
    st.markdown("<p style='color: #6b7280;'>Remplissez le formulaire à gauche pour explorer le réseau de collaboration.</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)