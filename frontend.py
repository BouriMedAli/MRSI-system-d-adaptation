import streamlit as st
import requests
import pandas as pd

# -------------------- Config --------------------
st.set_page_config(page_title="Système de Recommandation Étudiant", layout="wide")

API_URL = "http://localhost:8000/recommend/"
REGISTER_URL = "http://localhost:8000/register/"
CATEGORIES_URL = "http://localhost:8000/categories/"

# -------------------- Récupération des catégories --------------------
@st.cache_data(show_spinner=False)
def fetch_categories():
    try:
        res = requests.get(CATEGORIES_URL)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return {
        "communities": ["Club Robotique", "Groupe IA", "Club Entrepreneurs", "Association Écologie", "Club Data Science"],
        "skills": ["Blockchain", "IA", "Data Science", "Python", "Design", "Électronique", "Marketing"],
        "interests": ["Jeux vidéo", "Musique", "Robotique", "Entrepreneuriat", "Écologie", "Hackathon"]
    }

st.session_state.categories = fetch_categories()

# -------------------- Interface --------------------
tab1, tab2, tab3 = st.tabs(["🎯 Recommandation", "📝 Enregistrement", "ℹ️ À propos"])

# -------------------- Tab 1: Recommandation --------------------
with tab1:
    st.header("Obtenir des Recommandations")

    with st.form("recommend_form"):
        col1, col2 = st.columns(2)

        with col1:
            tc = st.slider("Travaux Collaboratifs", 0, 10, 7)
            ni = st.slider("Nombre d'Interactions", 0, 100, 50)
            is_existing = st.checkbox("Étudiant existant")
            student_id = st.number_input("ID Étudiant", min_value=1, value=1) if is_existing else None

        with col2:
            c = st.multiselect("Communautés", st.session_state.categories["communities"], default=[])
            s = st.multiselect("Compétences", st.session_state.categories["skills"], default=[])
            i = st.multiselect("Centres d’intérêt", st.session_state.categories["interests"], default=[])

        submitted = st.form_submit_button("📥 Obtenir recommandations")

    if submitted:
        data = {
            "numeric": [float(tc), float(ni)],
            "communautés": c,
            "compétences": s,
            "centres_d_intérêt": i
        }
        if student_id:
            data["student_id"] = int(student_id)

        try:
            with st.spinner("Recherche en cours..."):
                res = requests.post(API_URL, json=data)
                if res.status_code == 200:
                    results = res.json()
                    recs = results.get("recommended_students", [])
                    t = results.get("metadata", {}).get("processing_time_ms", "N/A")
                    st.success(f"Recommandations reçues en {t} ms")

                    if recs:
                        df = pd.DataFrame(recs)
                        st.subheader("Étudiants recommandés")

                        for _, r in df.iterrows():
                            col1, col2 = st.columns([1, 3])
                            col1.markdown(f"**{r['Nom']}** (ID: {r['ID_Étudiant']})")
                            col2.progress(min(r['similarity_score'], 1.0))
                            col2.markdown(f"Similarité: `{r['similarity_score']:.2f}`")
                            with st.expander(f"Détails pour {r['Nom']}"):
                                st.write("**Communautés:**", ", ".join(r.get("communautés", [])))
                                st.write("**Compétences:**", ", ".join(r.get("compétences", [])))
                                st.write("**Centres d’intérêt:**", ", ".join(r.get("centres_d_intérêt", [])))
                    else:
                        st.warning("Aucune recommandation trouvée.")
                else:
                    st.error(f"Erreur {res.status_code} : {res.text}")
        except Exception as e:
            st.error(f"Erreur lors de la connexion à l’API : {e}")

# -------------------- Tab 2: Enregistrement --------------------
with tab2:
    st.header("Enregistrer un Nouvel Étudiant")

    with st.form("register_form"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom de l'étudiant")
            tc = st.slider("Travaux Collaboratifs", 0, 10, 5, key="reg_tc")
            ni = st.slider("Nombre d'Interactions", 0, 100, 50, key="reg_ni")

        with col2:
            c = st.multiselect("Communautés", st.session_state.categories["communities"], key="reg_comm")
            s = st.multiselect("Compétences", st.session_state.categories["skills"], key="reg_comp")
            i = st.multiselect("Centres d’intérêt", st.session_state.categories["interests"], key="reg_int")

        register = st.form_submit_button("✅ Enregistrer")

    if register:
        if not nom:
            st.warning("Le nom de l'étudiant est requis.")
        else:
            student = {
                "nom": nom,
                "travaux_collaboratifs": tc,
                "nombre_interactions": ni,
                "communautés": c,
                "compétences": s,
                "centres_d_intérêt": i
            }
            try:
                with st.spinner("Enregistrement en cours..."):
                    res = requests.post(REGISTER_URL, json=student)
                    if res.status_code == 200:
                        new_id = res.json().get("student_id")
                        st.success(f"Étudiant enregistré ! ID attribué : {new_id}")
                        st.balloons()
                    else:
                        st.error(f"Erreur {res.status_code} : {res.text}")
            except Exception as e:
                st.error(f"Connexion échouée : {e}")

# -------------------- Tab 3: À propos --------------------
with tab3:
    st.header("À propos du système")

    st.markdown("""
    ### 🔍 Comment ça marche ?
    Ce système repose sur une approche de recommandation hybride :

    - **Filtrage Collaboratif** : Basé sur les similarités entre profils
    - **Filtrage Basé Contenu** : Utilise les attributs du profil utilisateur
    - **Gestion du Cold Start** : Pour les nouveaux étudiants

    ### 🔧 Technologies utilisées :
    - FastAPI (backend)
    - Streamlit (frontend)
    - Scikit-learn / Scikit-Surprise (recommandation)
    - Docker

    ### 📊 Données utilisées :
    - Score de collaboration
    - Nombre d’interactions
    - Communautés, compétences, centres d’intérêt
    """)
    st.info("Pour toute assistance, veuillez contacter l’administrateur du système.")
