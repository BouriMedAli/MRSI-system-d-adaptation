import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Système de Recommandation Éducatif", layout="wide", page_icon="🎓")

# Style CSS
st.markdown("""
    <style>
    .main { background-color: #f0f4f8; }
    .stButton>button { background-color: #4CAF50; color: white; }
    .stTabs { background-color: #ffffff; padding: 10px; border-radius: 5px; }
    .course-box { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; background-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# Charger les données
df = pd.read_csv('data/dataset_etudiants.csv')

# Titre
st.title("🎓 Système de Recommandation Éducatif")

# Sidebar
student_id = st.sidebar.selectbox("Sélectionner un étudiant", df['ID_Étudiant'].values)

# Onglets
tab1, tab2, tab3 = st.tabs(["Profil", "Recommandations", "Formulaires"])

with tab1:
    st.header "Profil de l’étudiant")
    student = df[df['ID_Étudiant'] == student_id]
    st.write(f"**Nom** : {student['Nom'].iloc[0]}")
    st.write(f"**Compétences** : {student['Compétences'].iloc[0]}")
    st.write(f"**Centres d’intérêt** : {student['Centres_d\'Intérêt'].iloc[0]}")
    st.write(f"**Communautés** : {student['Communautés'].iloc[0]}")

with tab2:
    st.header("Recommandations")
    
    # Coéquipiers
    response = requests.get(f"http://api:8000/recommend/teammates/{student_id}")
    if response.status_code == 200:
        teammates = response.json()['recommended_teammates']
        st.subheader("Coéquipiers recommandés")
        st.dataframe(pd.DataFrame(teammates))
    
    # Cours
    response = requests.get(f"http://api:8000/recommend/courses/{student_id}")
    if response.status_code == 200:
        courses = response.json()['recommended_courses']
        st.subheader("Cours recommandés")
        for course in courses:
            with st.container():
                st.markdown(f"<div class='course-box'>", unsafe_allow_html=True)
                st.markdown(f"**{course['course']}**")
                st.markdown(f"{course['description']}", unsafe_allow_html=True)
                st.write("**Ressources** :")
                for resource in course['resources']:
                    st.markdown(f"- [{resource['title']}]({resource['url']})")
                st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.header("Formulaires")
    
    # Formulaire VARK
    st.subheader("Style d’apprentissage (VARK)")
    with st.form("vark_form"):
        visual = st.slider("Visuel (diagrammes, vidéos)", 0, 10, 5)
        auditory = st.slider("Auditif (podcasts, discussions)", 0, 10, 5)
        reading_writing = st.slider("Lecture/Écriture (textes, notes)", 0, 10, 5)
        kinesthetic = st.slider("Kinesthésique (pratique, ateliers)", 0, 10, 5)
        submitted = st.form_submit_button("Soumettre")
        if submitted:
            response = requests.post("http://api:8000/submit/vark", 
                                    json={"student_id": student_id, "visual": visual, 
                                          "auditory": auditory, "reading_writing": reading_writing, 
                                          "kinesthetic": kinesthetic})
            if response.status_code == 200:
                st.success(f"Style : {response.json()['learning_style']}")

    # Formulaire d’objectifs
    st.subheader("Objectif d’apprentissage")
    with st.form("goal_form"):
        goal = st.text_input("Votre objectif (ex. : Apprendre Python, Hackathon)")
        submitted = st.form_submit_button("Soumettre")
        if submitted:
            response = requests.post("http://api:8000/submit/goal", 
                                    json={"student_id": student_id, "goal": goal})
            if response.status_code == 200:
                st.success(f"Objectif enregistré : {goal}")

# Visualisation
st.header("Visualisation des profils")
embeddings = np.random.rand(len(df), 2)  # À remplacer
fig = px.scatter(x=embeddings[:, 0], y=embeddings[:, 1], text=df['Nom'], title="Carte des profils")
st.plotly_chart(fig)