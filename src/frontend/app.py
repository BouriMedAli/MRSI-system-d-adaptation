
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

# Configuration de la page
st.set_page_config(page_title="MRSI Recommandeur IA", layout="wide", page_icon="🤖")

# CSS personnalisé
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 5px; }
    .stTextInput>div>input { border-radius: 5px; }
    .header { color: #2c3e50; font-size: 2.5em; text-align: center; }
    .subheader { color: #34495e; font-size: 1.5em; }
    .chat-message { padding: 10px; border-radius: 5px; margin: 5px 0; }
    .user-message { background-color: #d1e7dd; }
    .bot-message { background-color: #e9ecef; }
    </style>
""", unsafe_allow_html=True)

# Initialisation de l'état de la session
if "recommendation_history" not in st.session_state:
    st.session_state.recommendation_history = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Navigation dans la barre latérale
st.sidebar.image("src/frontend/assets/logo.png", use_column_width=True)
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choisir une page", ["Accueil", "Profil Étudiant", "Recommandations", "Chat IA", "Historique"])

# Contenu principal
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    if page == "Accueil":
        st.markdown("<h1 class='header'>Système de Recommandation MRSI avec IA</h1>", unsafe_allow_html=True)
        st.write("Découvrez des cours personnalisés et trouvez des coéquipiers grâce à l'IA ! Naviguez pour explorer les profils, obtenir des recommandations ou discuter avec notre assistant IA.")

    elif page == "Profil Étudiant":
        st.markdown("<h2 class='subheader'>Profil Étudiant</h2>", unsafe_allow_html=True)
        student_id = st.number_input("Entrez l'ID de l'étudiant", min_value=1, value=5, step=1, help="Entrez un ID valide")
        if st.button("Récupérer le profil"):
            with st.spinner("Récupération du profil..."):
                try:
                    response = requests.get(f"http://backend:8000/students/{student_id}")
                    if response.status_code == 200:
                        profile = response.json()
                        st.success("Profil récupéré !")
                        st.write(f"**Nom** : {profile['Nom']}")
                        st.write(f"**Compétences** : {', '.join(profile['Compétences'])}")
                        st.write(f"**Centres d'Intérêt** : {', '.join(profile['Centres_d_Intérêt'])}")
                        # Nuage de mots pour les compétences
                        wordcloud = WordCloud(width=400, height=200, background_color="white").generate(" ".join(profile['Compétences']))
                        plt.figure(figsize=(8, 4))
                        plt.imshow(wordcloud, interpolation="bilinear")
                        plt.axis("off")
                        buf = io.BytesIO()
                        plt.savefig(buf, format="png")
                        buf.seek(0)
                        img_str = base64.b64encode(buf.read()).decode()
                        st.image(f"data:image/png;base64,{img_str}", caption="Nuage de Compétences")
                    else:
                        st.error(f"Erreur : {response.status_code} - {response.text}")
                except requests.RequestException as e:
                    st.error(f"Échec de la connexion au backend : {e}")

    elif page == "Recommandations":
        st.markdown("<h2 class='subheader'>Recommandations de Cours avec IA</h2>", unsafe_allow_html=True)
        with st.form("recommendation_form"):
            student_id = st.number_input("ID Étudiant", min_value=1, value=5, step=1, help="Entrez un ID valide")
            skills = st.text_input("Compétences (séparées par des virgules)", value="python", help="Ex. : python, java, sql")
            interests = st.text_input("Intérêts (séparés par des virgules)", value="jeux vidéo", help="Ex. : jeux vidéo, musique")
            learning_styles = st.text_input("Styles d'apprentissage (séparés par des virgules)", value="Visuel", help="Ex. : Visuel, Auditif")
            submitted = st.form_submit_button("Obtenir des recommandations")

            if submitted:
                if not all([student_id, skills, interests, learning_styles]):
                    st.error("Veuillez remplir tous les champs")
                else:
                    with st.spinner("Génération des recommandations IA..."):
                        try:
                            response = requests.get(
                                f"http://backend:8000/recommend/courses/{student_id}",
                                params={"skills": skills, "interests": interests, "learning_styles": learning_styles}
                            )
                            if response.status_code == 200:
                                data = response.json()
                                st.session_state.recommendation_history.append({
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "student_id": data["student_id"],
                                    "courses": data["courses"],
                                    "teammates": data["teammates"],
                                    "message": data["motivational_message"]
                                })
                                st.success("Recommandations récupérées !")
                                st.subheader("ID Étudiant")
                                st.write(data["student_id"])
                                with st.expander("Cours recommandés", expanded=True):
                                    for course in data["courses"]:
                                        st.write(f"- {course['title']} : {course['description']}")
                                with st.expander("Coéquipiers"):
                                    for teammate in data["teammates"]:
                                        st.write(f"- {teammate['Nom']} (ID: {teammate['ID_Étudiant']})")
                                st.subheader("Message motivant")
                                st.write(data["motivational_message"])
                                # Graphique pour la pertinence des cours
                                if data["courses"]:
                                    course_titles = [c["title"] for c in data["courses"]]
                                    course_scores = [random.uniform(0.7, 1.0) for _ in course_titles]  # Scores placeholders
                                    plt.figure(figsize=(8, 4))
                                    plt.bar(course_titles, course_scores, color="#007bff")
                                    plt.xlabel("Cours")
                                    plt.ylabel("Score de pertinence")
                                    plt.xticks(rotation=45, ha="right")
                                    plt.tight_layout()
                                    buf = io.BytesIO()
                                    plt.savefig(buf, format="png")
                                    buf.seek(0)
                                    img_str = base64.b64encode(buf.read()).decode()
                                    st.image(f"data:image/png;base64,{img_str}", caption="Pertinence des cours")
                                if st.button("Exporter les recommandations"):
                                    df = pd.DataFrame({
                                        "Cours": [c["title"] for c in data["courses"]],
                                        "Coéquipiers": [t["Nom"] for t in data["teammates"]]
                                    })
                                    st.download_button(
                                        label="Télécharger en CSV",
                                        data=df.to_csv(index=False),
                                        file_name=f"recommandations_{student_id}.csv",
                                        mime="text/csv"
                                    )
                            else:
                                st.error(f"Erreur : {response.status_code} - {response.text}")
                        except requests.RequestException as e:
                            st.error(f"Échec de la connexion au backend : {e}")

    elif page == "Chat IA":
        st.markdown("<h2 class='subheader'>Assistant IA</h2>", unsafe_allow_html=True)
        user_input = st.text_area("Posez une question sur les cours ou les coéquipiers :", height=100)
        if st.button("Envoyer"):
            if user_input:
                with st.spinner("Génération de la réponse..."):
                    try:
                        response = requests.post(
                            "http://backend:8000/ai-chat",
                            json={"query": user_input}
                        )
                        if response.status_code == 200:
                            reply = response.json()["response"]
                            st.session_state.chat_history.append(("user", user_input))
                            st.session_state.chat_history.append(("bot", reply))
                        else:
                            st.error(f"Erreur : {response.status_code} - {response.text}")
                    except requests.RequestException as e:
                        st.error(f"Échec de la connexion au backend : {e}")
        # Afficher l'historique du chat
        for sender, message in st.session_state.chat_history:
            css_class = "user-message" if sender == "user" else "bot-message"
            st.markdown(f"<div class='chat-message {css_class}'>{message}</div>", unsafe_allow_html=True)

    elif page == "Historique":
        st.markdown("<h2 class='subheader'>Historique des recommandations</h2>", unsafe_allow_html=True)
        if st.session_state.recommendation_history:
            for entry in st.session_state.recommendation_history:
                with st.expander(f"Recommandation du {entry['timestamp']} pour l'étudiant {entry['student_id']}"):
                    st.write(f"**Cours** : {', '.join([c['title'] for c in entry['courses']])}")
                    st.write(f"**Coéquipiers** : {', '.join([t['Nom'] for t in entry['teammates']])}")
                    st.write(f"**Message** : {entry['message']}")
        else:
            st.info("Aucune recommandation pour le moment. Allez à la page Recommandations pour commencer !")