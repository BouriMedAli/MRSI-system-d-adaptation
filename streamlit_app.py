import streamlit as st
import pandas as pd
import requests
import ast
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(page_title="Réseau de Collaboration MRSI", layout="wide", page_icon="🌐")

# Styles CSS pour un design moderne
st.markdown("""
    <style>
    .main { background-color: #f8fafc; padding: 20px; }
    .dark-mode { background-color: #1f2937; color: white; }
    .dark-mode h1, .dark-mode h3 { color: #60a5fa; }
    .stButton>button {
        background-color: #3b82f6; color: white; border-radius: 8px; padding: 10px 20px;
        font-weight: bold; border: none; transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2563eb; transform: scale(1.05);
    }
    .stExpander {
        background-color: #f1f5f9; border-radius: 8px; padding: 10px;
    }
    .stExpander summary {
        background-color: #3b82f6; color: white; border-radius: 8px; padding: 10px;
        font-weight: bold; cursor: pointer; transition: all 0.3s;
    }
    .stExpander summary:hover {
        background-color: #2563eb;
    }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>select {
        border-radius: 8px; border: 1px solid #d1d5db; padding: 10px;
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

# Relations thématiques entre compétences et centres d'intérêt
THEMATIC_RELATIONS = {
    "Python": ["Data Science", "Machine Learning", "IA", "Développement"],
    "IA": ["Machine Learning", "Data Science", "Robotique", "Technologie", "Artificial Intelligence Ethics", "Natural Language Processing"],
    "Blockchain": ["Cryptographie", "Smart Contracts", "Technologie"],
    "Marketing": ["Publicité", "SEO", "Communication"],
    "Design": ["UX/UI", "Graphisme", "Prototypage", "Digital Art"],
    "Data Science": ["Python", "Machine Learning", "Big Data", "Statistiques", "IA"],
    "SQL": ["Data Science", "Big Data"],
    "Communication": ["Marketing", "Publicité"],
    "SEO": ["Marketing", "Publicité"],
    "Publicité": ["Marketing", "SEO"],
    "UX/UI": ["Design", "Prototypage"],
    "Graphisme": ["Design", "Digital Art"],
    "Prototypage": ["UX/UI", "Design"],
    "Cryptographie": ["Blockchain", "Sécurité"],
    "Sécurité": ["Cybersecurity", "Ethical Hacking"],
    "Smart Contracts": ["Blockchain"],
    "Statistiques": ["Data Science", "Machine Learning"],
    "Big Data": ["Data Science", "Cloud Computing"],
    "Machine Learning": ["IA", "Data Science", "Statistiques"],
    "Cloud Computing": ["Big Data", "DevOps"],
    "DevOps": ["Cloud Computing", "Développement"],
    "Cybersecurity": ["Sécurité", "Ethical Hacking"],
    "Augmented Reality": ["Virtual Reality", "Technologie"],
    "Natural Language Processing": ["IA", "Machine Learning"],
    "Game Development": ["Jeux vidéo", "3D Modeling"],
    "Quantum Computing": ["Technologie"],
    "3D Modeling": ["Game Development", "Digital Art"],
    "Ethical Hacking": ["Cybersecurity", "Sécurité"],
    "Robotique": ["IA", "Technologie"],
    "Hackathon": ["Développement", "Innovation"],
    "Musique": ["Art"],
    "Jeux vidéo": ["Game Development", "E-sport"],
    "Écologie": ["Développement Durable", "Nature", "Sustainable Tech"],
    "Technologie": ["IA", "Blockchain", "Robotique", "Innovation"],
    "Entrepreneuriat": ["Innovation"],
    "Innovation": ["Entrepreneuriat", "Technologie"],
    "Art": ["Musique", "Digital Art"],
    "Créativité": ["Innovation", "Art"],
    "Développement": ["Python", "DevOps", "Hackathon"],
    "E-sport": ["Jeux vidéo"],
    "Développement Durable": ["Écologie", "Sustainable Tech"],
    "Sciences": ["Nature", "Astronomy"],
    "Nature": ["Écologie", "Sciences"],
    "Photography": ["Art", "Digital Art"],
    "Artificial Intelligence Ethics": ["IA"],
    "Space Exploration": ["Astronomy", "Sciences"],
    "Virtual Reality": ["Augmented Reality", "Technologie"],
    "Sustainable Tech": ["Écologie", "Développement Durable"],
    "Digital Art": ["Art", "Design", "Photography"],
    "Cyberpunk Culture": ["Technologie"],
    "Astronomy": ["Space Exploration", "Sciences"],
    "Board Games": ["Jeux vidéo"],
    "Urban Farming": ["Écologie", "Développement Durable"]
}

# Liste statique de ressources pour les cours recommandés avec des liens réels et variés
RECOMMENDED_COURSES = {
    "Python": [
        ("Python for Beginners - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=rfscVS0vtbw"),
        ("Python Official Tutorial (PDF)", "https://docs.python.org/3/tutorial/python-3.12-tutorial.pdf"),
        ("Python Basics - Real Python (Article)", "https://realpython.com/python-basics/")
    ],
    "IA": [
        ("Intro to AI - Crash Course AI #1 (YouTube)", "https://www.youtube.com/watch?v=F1vAEer3c1A"),
        ("AI for Everyone by Andrew Ng - Coursera (Audit Free)", "https://www.coursera.org/learn/ai-for-everyone"),
        ("AI Ethics Guide (PDF)", "https://aiethics.princeton.edu/wp-content/uploads/sites/587/2020/10/AI-Ethics-Primer.pdf")
    ],
    "Blockchain": [
        ("Blockchain Basics Explained - Simply Explained (YouTube)", "https://www.youtube.com/watch?v=SSo_EIwHSd4"),
        ("Blockchain Technology Explained - IBM (Article)", "https://www.ibm.com/topics/blockchain"),
        ("Bitcoin Whitepaper by Satoshi Nakamoto (PDF)", "https://bitcoin.org/bitcoin.pdf")
    ],
    "Marketing": [
        ("Digital Marketing Tutorial - Simplilearn (YouTube)", "https://www.youtube.com/watch?v=nU-IIXBWlS4"),
        ("Digital Marketing Guide (PDF)", "https://www.hubspot.com/hubfs/assets/hubspot.com/pdf/All-in-One-Inbound-Marketing-Strategy-Playbook.pdf"),
        ("Google Digital Marketing Certificate (Free Lessons)", "https://grow.google/certificates/digital-marketing-ecommerce/")
    ],
    "Design": [
        ("UI/UX Design Tutorial - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=5zI_9-j0FrA"),
        ("Design Principles - Canva (Article)", "https://www.canva.com/learn/design-elements-principles/"),
        ("Graphic Design Basics (PDF)", "https://www.gcfglobal.org/assets/documents/Graphic-Design-Basics.pdf")
    ],
    "Data Science": [
        ("Data Science Tutorial - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=r-uOLxNrNk8"),
        ("Introduction to Data Science - Coursera (Audit Free)", "https://www.coursera.org/learn/introduction-to-data-science"),
        ("Python Data Science Handbook (PDF)", "https://jakevdp.github.io/PythonDataScienceHandbook/pdfs/PythonDataScienceHandbook.pdf")
    ],
    "SQL": [
        ("SQL Tutorial for Beginners - Programming with Mosh (YouTube)", "https://www.youtube.com/watch?v=p3qvj9hO_Bo"),
        ("SQL Cheat Sheet (PDF)", "https://www.sqltutorial.org/wp-content/uploads/2016/04/SQL-Cheat-Sheet.pdf"),
        ("Learn SQL - W3Schools (Interactive)", "https://www.w3schools.com/sql/")
    ],
    "Communication": [
        ("Effective Communication Skills - MindTools (YouTube)", "https://www.youtube.com/watch?v=2aN4rfDrqT8"),
        ("Communication Skills - Coursera (Audit Free)", "https://www.coursera.org/learn/communication-skills"),
        ("Communication Skills Guide (PDF)", "https://www.skillsyouneed.com/pdfs/SkillsYouNeed-Interpersonal-Skills.pdf")
    ],
    "SEO": [
        ("SEO Tutorial for Beginners - Ahrefs (YouTube)", "https://www.youtube.com/watch?v=DvwS7cV9GmQ"),
        ("SEO Basics - Moz (Article)", "https://moz.com/beginners-guide-to-seo"),
        ("Beginner’s Guide to SEO (PDF)", "https://moz.com/files/SEO-Basics-Guide-2023.pdf")
    ],
    "Publicité": [
        ("Online Advertising Explained - HubSpot (YouTube)", "https://www.youtube.com/watch?v=HMXhT9I3i7M"),
        ("Google Ads Tutorial - Google (Free)", "https://support.google.com/google-ads/answer/6146252"),
        ("Digital Advertising Glossary (PDF)", "https://www.iab.com/wp-content/uploads/2015/05/IAB_Digital_Advertising_Glossary.pdf")
    ],
    "UX/UI": [
        ("UX Design for Beginners - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=5zI_9-j0FrA"),
        ("Google UX Design Certificate (Free Lessons)", "https://grow.google/certificates/ux-design/"),
        ("UX Principles (PDF)", "https://www.nngroup.com/files/reports/UX101.pdf")
    ],
    "Graphisme": [
        ("Graphic Design Basics - Canva (YouTube)", "https://www.youtube.com/watch?v=ZfjdYGr1L78"),
        ("Introduction to Graphic Design - Coursera (Audit Free)", "https://www.coursera.org/learn/fundamentals-of-graphic-design"),
        ("Graphic Design Basics (PDF)", "https://www.gcfglobal.org/assets/documents/Graphic-Design-Basics.pdf")
    ],
    "Prototypage": [
        ("Prototyping with Figma - Figma (YouTube)", "https://www.youtube.com/watch?v=3qdpUoE_ArI"),
        ("Figma for Beginners - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=Cx2dkpBxst8"),
        ("Figma Prototyping Guide (Article)", "https://www.figma.com/resources/learn-design/prototyping/")
    ],
    "Cryptographie": [
        ("Cryptography Explained - Khan Academy (YouTube)", "https://www.youtube.com/watch?v=6-JjLa8KulM"),
        ("Cryptography I by Dan Boneh - Coursera (Audit Free)", "https://www.coursera.org/learn/crypto"),
        ("Introduction to Cryptography (PDF)", "https://www.cs.umd.edu/~waa/414-F11/IntroToCrypto.pdf")
    ],
    "Sécurité": [
        ("Cybersecurity Basics - IBM Skills (YouTube)", "https://www.youtube.com/watch?v=5q5e_8x4tRQ"),
        ("Introduction to Cybersecurity - Cisco Networking Academy (Free)", "https://www.netacad.com/courses/cybersecurity/introduction-cybersecurity"),
        ("Cybersecurity Essentials (PDF)", "https://www.netacad.com/sites/default/files/2023-04/cybersecurity-essentials-course.pdf")
    ],
    "Smart Contracts": [
        ("Smart Contracts with Solidity - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=umXlkGkv4nU"),
        ("Solidity Tutorial - Dapp University (YouTube)", "https://www.youtube.com/watch?v=v_hU0jPtLto"),
        ("Solidity Documentation (PDF)", "https://docs.soliditylang.org/_/downloads/en/latest/pdf/")
    ],
    "Statistiques": [
        ("Statistics for Beginners - StatQuest (YouTube)", "https://www.youtube.com/watch?v=qBigTkBLU6g"),
        ("Intro to Statistics - Udacity (Free)", "https://www.udacity.com/course/intro-to-statistics--st101"),
        ("Statistics Cheat Sheet (PDF)", "https://web.mit.edu/~csvoss/Public/usabo/stats_handout.pdf")
    ],
    "Big Data": [
        ("Big Data Explained - IBM (YouTube)", "https://www.youtube.com/watch?v=bAyrObl7TYE"),
        ("Big Data Fundamentals - edX (Free)", "https://www.edx.org/learn/big-data/big-data-fundamentals"),
        ("Big Data Guide (PDF)", "https://www.oracle.com/a/ocom/docs/big-data-guide-2023.pdf")
    ],
    "Machine Learning": [
        ("Machine Learning for Beginners - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=NWONeJKn6kc"),
        ("Machine Learning Basics - Coursera (Audit Free)", "https://www.coursera.org/learn/machine-learning"),
        ("Intro to Machine Learning (PDF Guide) - Google", "https://developers.google.com/machine-learning/crash-course/static/downloads/mlcc.pdf")
    ],
    "Cloud Computing": [
        ("Cloud Computing Basics - AWS (YouTube)", "https://www.youtube.com/watch?v=ljL_2zjbfhI"),
        ("Introduction to Cloud Computing - Coursera (Audit Free)", "https://www.coursera.org/learn/cloud-computing"),
        ("Cloud Computing Concepts (PDF)", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-145.pdf")
    ],
    "DevOps": [
        ("What is DevOps? - AWS (YouTube)", "https://www.youtube.com/watch?v=SDG1t2dYF_4"),
        ("DevOps Roadmap (Article)", "https://roadmap.sh/devops"),
        ("DevOps Basics (PDF)", "https://www.redhat.com/en/resources/devops-basics-cheat-sheet")
    ],
    "Cybersecurity": [
        ("Cybersecurity for Beginners - Cybrary (YouTube)", "https://www.youtube.com/watch?v=5q5e_8x4tRQ"),
        ("Introduction to Cybersecurity - Coursera (Audit Free)", "https://www.coursera.org/learn/introduction-cybersecurity-cyber-attacks"),
        ("Cybersecurity Awareness (PDF)", "https://www.cisa.gov/sites/default/files/publications/Cybersecurity-Awareness-Month-Toolkit-2023.pdf")
    ],
    "Augmented Reality": [
        ("What is Augmented Reality? - Unity (YouTube)", "https://www.youtube.com/watch?v=3U8w1zP7m0g"),
        ("AR Development Tutorial - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=8i2tQ1e9p0A"),
        ("Augmented Reality Basics (Article)", "https://www.realitytechnologies.com/augmented-reality")
    ],
    "Natural Language Processing": [
        ("NLP Tutorial for Beginners - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=8S3qHHUKqYk"),
        ("Introduction to NLP - Coursera (Audit Free)", "https://www.coursera.org/learn/natural-language-processing"),
        ("NLP Basics (PDF)", "https://web.stanford.edu/~jurafsky/slp3/ed3book.pdf")
    ],
    "Game Development": [
        ("Game Development with Unity - Brackeys (YouTube)", "https://www.youtube.com/watch?v=IlKaB1etrik"),
        ("Unity Basics - Unity Learn (Article)", "https://learn.unity.com/tutorials"),
        ("Unity Manual (PDF)", "https://docs.unity3d.com/uploads/Manual/UnityManual.pdf")
    ],
    "Quantum Computing": [
        ("Quantum Computing Explained - IBM (YouTube)", "https://www.youtube.com/watch?v=OWJCfOvochA"),
        ("Introduction to Quantum Computing - Coursera (Audit Free)", "https://www.coursera.org/learn/quantum-computing-algorithms"),
        ("Quantum Computing Basics (PDF)", "https://www.qiskit.org/textbook/preface.pdf")
    ],
    "3D Modeling": [
        ("Blender Tutorial for Beginners - Blender Guru (YouTube)", "https://www.youtube.com/watch?v=TPrnSACiTJ4"),
        ("3D Modeling Basics - Autodesk (Article)", "https://www.autodesk.com/solutions/3d-modeling"),
        ("Blender Quick Start Guide (PDF)", "https://download.blender.org/documentation/pdf/BlenderQuickStart.pdf")
    ],
    "Ethical Hacking": [
        ("Ethical Hacking for Beginners - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=3Kq1MIfTWCE"),
        ("Introduction to Ethical Hacking - Cybrary (Free)", "https://www.cybrary.it/course/ethical-hacking-basics/"),
        ("Ethical Hacking Basics (PDF)", "https://www.eccouncil.org/wp-content/uploads/2021/09/CEH-Handbook.pdf")
    ],
    "Robotique": [
        ("Introduction to Robotics - MIT OpenCourseWare (YouTube)", "https://www.youtube.com/watch?v=8JqKq8tH9QU"),
        ("Robotics for Beginners - edX (Free)", "https://www.edx.org/learn/robotics/robotics-for-beginners"),
        ("Robotics Primer (PDF)", "https://www.cs.cmu.edu/~rasc/Download/AMRobots/RoboticsPrimer.pdf")
    ],
    "Hackathon": [
        ("How to Prepare for a Hackathon - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=2o0Xv5U0_kQ"),
        ("Hackathon Tips - Devpost (Blog)", "https://devpost.com/hackathons-guide"),
        ("Hackathon Survival Guide (PDF)", "https://mlh.io/hackathon-survival-guide.pdf")
    ],
    "Musique": [
        ("Music Theory for Beginners - Andrew Huang (YouTube)", "https://www.youtube.com/watch?v=rgaTLrZGlk0"),
        ("Piano for Beginners - Pianote (YouTube)", "https://www.youtube.com/watch?v=5Y01jIor_fo"),
        ("Music Theory Basics (PDF)", "https://www.music-theory-for-musicians.com/support-files/music_theory_in_one_lesson.pdf")
    ],
    "Jeux vidéo": [
        ("Game Development with Unreal Engine - Unreal Engine (YouTube)", "https://www.youtube.com/watch?v=5qW0uWv-RrY"),
        ("Game Development Basics - Unity (Article)", "https://learn.unity.com/tutorials"),
        ("Game Design Document Template (PDF)", "https://www.gamedesigning.org/wp-content/uploads/2015/10/Game-Design-Document-Template.pdf")
    ],
    "Écologie": [
        ("Sustainability Explained - National Geographic (YouTube)", "https://www.youtube.com/watch?v=lsFcbm-cbwM"),
        ("Introduction to Sustainability - Coursera (Audit Free)", "https://www.coursera.org/learn/sustainability"),
        ("Ecology Basics (PDF)", "https://www.eolss.net/Sample-Chapters/C16/E1-53.pdf")
    ],
    "Technologie": [
        ("Tech Trends 2025 - Futurist (YouTube)", "https://www.youtube.com/watch?v=2e5KBLphx7w"),
        ("Technology Overview - MIT Technology Review (Article)", "https://www.technologyreview.com/topics/"),
        ("Emerging Tech Guide (PDF)", "https://www.pwc.com/gx/en/issues/technology/emerging-technology-report.pdf")
    ],
    "Entrepreneuriat": [
        ("Entrepreneurship 101 - Y Combinator (YouTube)", "https://www.youtube.com/watch?v=0qW8z8lS_0g"),
        ("How to Start a Startup - Stanford (YouTube)", "https://www.youtube.com/watch?v=CBYhVcO4WgI"),
        ("Startup Guide (PDF)", "https://www.startupgrind.com/startup-guide.pdf")
    ],
    "Innovation": [
        ("How to Be More Innovative - TEDx (YouTube)", "https://www.youtube.com/watch?v=5t3gYcZQZ6s"),
        ("Innovation and Creativity - Coursera (Audit Free)", "https://www.coursera.org/learn/innovation-creativity-entrepreneurship"),
        ("Innovation Toolkit (PDF)", "https://www.ideo.com/post/ideo-innovation-toolkit")
    ],
    "Art": [
        ("Contemporary Art Explained - The Art Assignment (YouTube)", "https://www.youtube.com/watch?v=8o8kG0U7xE8"),
        ("Drawing Basics - Proko (YouTube)", "https://www.youtube.com/watch?v=30xl2Ev44wI"),
        ("Art History Timeline (PDF)", "https://www.metmuseum.org/-/media/files/learn/for-educators/publications-for-educators/art-history-timeline.pdf")
    ],
    "Créativité": [
        ("How to Boost Creativity - TED-Ed (YouTube)", "https://www.youtube.com/watch?v=9zSHz7Thvbc"),
        ("Creativity Exercises - MindTools (Article)", "https://www.mindtools.com/pages/article/creativity-exercises.htm"),
        ("Creativity Guide (PDF)", "https://www.creativityatwork.com/creativity-guide.pdf")
    ],
    "Développement": [
        ("Web Development for Beginners - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=3t7DzqS1x5A"),
        ("HTML & CSS Tutorial - Traversy Media (YouTube)", "https://www.youtube.com/watch?v=0afZj1G0BIE"),
        ("Web Development Basics (PDF)", "https://www.w3.org/standards/webdesign/WebDesignBasics.pdf")
    ],
    "E-sport": [
        ("What is Esports? - ESPN (YouTube)", "https://www.youtube.com/watch?v=7H5L1I9y2uY"),
        ("How to Become an Esports Pro - Red Bull (Article)", "https://www.redbull.com/int-en/how-to-become-an-esports-pro"),
        ("Esports Guide (PDF)", "https://www.esportsearnings.com/documents/Esports-Guide.pdf")
    ],
    "Développement Durable": [
        ("Sustainable Development Goals - UN (YouTube)", "https://www.youtube.com/watch?v=0XTBYMfZyrM"),
        ("Sustainability for Beginners - Coursera (Audit Free)", "https://www.coursera.org/learn/sustainability"),
        ("Sustainable Development Report (PDF)", "https://dashboards.sdgindex.org/static/profiles/pdf/SDR-2023.pdf")
    ],
    "Sciences": [
        ("Introduction to Science - Khan Academy (YouTube)", "https://www.youtube.com/watch?v=9t9e0zI0e8M"),
        ("Science Basics - edX (Free)", "https://www.edx.org/learn/science/introduction-to-science"),
        ("Science for All (PDF)", "https://www.nap.edu/resource/4962/Science_for_All_Children.pdf")
    ],
    "Nature": [
        ("Exploring Nature - BBC Earth (YouTube)", "https://www.youtube.com/watch?v=5i5e_8x4tRQ"),
        ("Ecology Basics - Coursera (Audit Free)", "https://www.coursera.org/learn/ecology"),
        ("Nature Conservation Guide (PDF)", "https://www.iucn.org/sites/dev/files/content/documents/2020_iucn_global_strategy.pdf")
    ],
    "Photography": [
        ("Photography for Beginners - Adorama (YouTube)", "https://www.youtube.com/watch?v=5vXh4G0gDTo"),
        ("Photography Basics - Canon (YouTube)", "https://www.youtube.com/watch?v=7vXh4G0gDTo"),
        ("Photography Fundamentals (PDF)", "https://www.photographytips.com/pdf/photography-fundamentals.pdf")
    ],
    "Artificial Intelligence Ethics": [
        ("AI Ethics Explained - Future of Life Institute (YouTube)", "https://www.youtube.com/watch?v=OzTHxH20J8A"),
        ("Ethics of AI - Coursera (Audit Free)", "https://www.coursera.org/learn/ethics-of-ai"),
        ("AI Ethics Primer (PDF)", "https://aiethics.princeton.edu/wp-content/uploads/sites/587/2020/10/AI-Ethics-Primer.pdf")
    ],
    "Space Exploration": [
        ("Space Exploration History - NASA (YouTube)", "https://www.youtube.com/watch?v=Z8g8lPEvXvY"),
        ("Introduction to Space Exploration - edX (Free)", "https://www.edx.org/learn/space-exploration/introduction-to-space-exploration"),
        ("Space Exploration Guide (PDF)", "https://www.nasa.gov/pdf/582711main_Space_Exploration.pdf")
    ],
    "Virtual Reality": [
        ("What is Virtual Reality? - Oculus (YouTube)", "https://www.youtube.com/watch?v=DXRwF5x4N3U"),
        ("VR Development Tutorial - freeCodeCamp (YouTube)", "https://www.youtube.com/watch?v=8i2tQ1e9p0A"),
        ("VR Basics (Article)", "https://www.vrs.org.uk/virtual-reality/basics.html")
    ],
    "Sustainable Tech": [
        ("Sustainable Technology - GreenBiz (YouTube)", "https://www.youtube.com/watch?v=9uK2y9eL8dY"),
        ("Sustainable Tech Basics - Coursera (Audit Free)", "https://www.coursera.org/learn/sustainable-technology"),
        ("Sustainable Tech Report (PDF)", "https://www.unep.org/resources/report/sustainable-digitalization")
    ],
    "Digital Art": [
        ("Digital Art for Beginners - Wacom (YouTube)", "https://www.youtube.com/watch?v=2k2p0J8z8dY"),
        ("Intro to Digital Art - Skillshare (YouTube)", "https://www.youtube.com/watch?v=2k2p0J8z8dY"),
        ("Digital Art Guide (Article)", "https://www.clipstudio.net/how-to-draw/archives/156922")
    ],
    "Cyberpunk Culture": [
        ("What is Cyberpunk? - The Verge (YouTube)", "https://www.youtube.com/watch?v=5uK2y9eL8dY"),
        ("Cyberpunk Culture Guide - Medium (Article)", "https://medium.com/the-cyberpunk/what-is-cyberpunk-9ebedb")
    ],
    "Astronomy": [
        ("Astronomy for Beginners - Crash Course (YouTube)", "https://www.youtube.com/watch?v=0rHUDWjR5gg"),
        ("Introduction to Astronomy - Coursera (Audit Free)", "https://www.coursera.org/learn/astronomy"),
        ("Astronomy Basics (PDF)", "https://www.astronomy.ohio-state.edu/ryden.1/ast161/Astronomy_161.pdf")
    ],
    "Board Games": [
        ("How to Play Board Games - Watch It Played (YouTube)", "https://www.youtube.com/watch?v=5uK2y9eL8dY"),
        ("Board Game Basics - BoardGameGeek (Article)", "https://boardgamegeek.com/boardgamebasics"),
        ("Board Game Design Guide (PDF)", "https://www.boardgamedesign.com/resources/Board_Game_Design_Guide.pdf")
    ],
    "Urban Farming": [
        ("Urban Farming for Beginners - Epic Gardening (YouTube)", "https://www.youtube.com/watch?v=5uK2y9eL8dY"),
        ("Introduction to Urban Agriculture - Coursera (Audit Free)", "https://www.coursera.org/learn/urban-agriculture"),
        ("Urban Farming Guide (PDF)", "https://www.fao.org/3/i5030e/i5030e.pdf")
    ]
}

# Titre principal
st.markdown("<h1>Système de recommandation MRSI</h1>", unsafe_allow_html=True)

# Créer des onglets pour les deux interfaces
tab1, tab2 = st.tabs(["Recommandations avec Filtres", "Recommandations Simples"])

# Interface 1 : Recommandations avec Filtres
with tab1:
    with st.sidebar:
        st.markdown("<h2 style='color: #1e3a8a;'>Réseau de Collaboration (Onglet 1)</h2>", unsafe_allow_html=True)
        
        student_id_tab1 = st.number_input("ID Étudiant (1-50)", min_value=1, max_value=50, value=1, key="student_id_tab1")
        n_recommendations_tab1 = st.number_input("Nombre de recommandations", min_value=1, max_value=10, value=5, key="n_recommendations_tab1")
        
        skill_filter = st.multiselect("Compétences", skills, default=["Python"], key="skill_filter_tab1")
        interest_filter = st.multiselect("Centres d'intérêt", interests, default=["Robotique"], key="interest_filter_tab1")
        
        skill_weight = st.slider("Poids des compétences", 0.0, 1.0, 0.5, 0.1, key="skill_weight_tab1")
        interest_weight = st.slider("Poids des centres d'intérêt", 0.0, 1.0, 0.5, 0.1, key="interest_weight_tab1")
        
        submit_button_tab1 = st.button("Obtenir les recommandations", key="submit_tab1")
        reset_button_tab1 = st.button("Réinitialiser", key="reset_tab1")
        theme_button = st.button("Changer de thème", on_click=toggle_theme, key="theme_button_tab1")

    theme_class = "dark-mode" if st.session_state.theme == 'dark' else ""
    st.markdown(f"<div class='{theme_class}'>", unsafe_allow_html=True)

    if reset_button_tab1:
        st.session_state.clear()
        st.experimental_rerun()

    if submit_button_tab1:
        request_data = {
            "student_id": student_id_tab1,
            "n_recommendations": n_recommendations_tab1,
            "skill_filter": skill_filter if skill_filter else None,
            "interest_filter": interest_filter if interest_filter else None,
            "skill_weight": skill_weight,
            "interest_weight": interest_weight
        }
        
        try:
            response = requests.post("http://localhost:8000/recommendations/", json=request_data)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                st.markdown(f"<div class='error'>Erreur : {result['error']}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='success'>Recommandations générées avec succès !</div>", unsafe_allow_html=True)
                
                st.session_state.history.append({
                    "request": request_data,
                    "result": result
                })
                if len(st.session_state.history) > 5:
                    st.session_state.history.pop(0)
                
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
                
                nodes = [f"Étudiant {student_id_tab1}"] + [f"Étudiant {t[0]}" for t in result["teammates"]]
                edges = [(0, i+1) for i in range(len(result["teammates"]))]
                st.write("Nœuds générés :", nodes)
                st.write("Arêtes générées :", edges)
                
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
                
                teammates_data = []
                for teammate_id, score in result["teammates"]:
                    teammate_row = df[df['ID_Étudiant'] == teammate_id]
                    skills = ', '.join(ast.literal_eval(teammate_row['Compétences'].iloc[0])) if not teammate_row.empty else ''
                    interests = ', '.join(ast.literal_eval(teammate_row.get('Centres_d\'Intérêt', ['[]']).iloc[0])) if not teammate_row.empty else 'Aucun'
                    teammates_data.append({
                        'ID': teammate_id,
                        'Score': score,
                        'Compétences': skills,
                        'Centres_d\'intérêt': interests
                    })
                export_df = pd.DataFrame(teammates_data)
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Télécharger en CSV",
                    data=csv,
                    file_name="recommandations.csv",
                    mime="text/csv",
                    key="download_csv_tab1"
                )
                
                # Export PDF
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)
                c.drawString(100, 750, "Recommandations MRSI")
                y = 700
                interest_key = 'Centres_d\'intérêt'
                for _, row in export_df.iterrows():
                    c.drawString(100, y, f"Étudiant {row['ID']}: Score {row['Score']:.2f}")
                    c.drawString(100, y-20, f"Compétences: {row['Compétences']}")
                    c.drawString(100, y-40, f"Centres d'intérêt: {row.get(interest_key, '')}")
                    y -= 60
                c.showPage()
                c.save()
                pdf = buffer.getvalue()
                st.download_button(
                    label="Télécharger en PDF",
                    data=pdf,
                    file_name="recommandations.pdf",
                    mime="application/pdf",
                    key="download_pdf_tab1"
                )
                
        except requests.exceptions.RequestException as e:
            st.markdown(f"<div class='error'>Erreur de connexion à l'API : {str(e)}</div>", unsafe_allow_html=True)

# Interface 2 : Recommandations Simples
with tab2:
    with st.sidebar:
        st.markdown("<h2 style='color: #1e3a8a;'>Recommandations Simples (Onglet 2)</h2>", unsafe_allow_html=True)
        
        student_id_tab2 = st.number_input("ID Étudiant (1-50)", min_value=1, max_value=50, value=1, key="student_id_tab2")
        n_recommendations_tab2 = st.number_input("Nombre de recommandations", min_value=1, max_value=10, value=5, key="n_recommendations_tab2")
        
        submit_button_tab2 = st.button("Obtenir les recommandations", key="submit_tab2")
        reset_button_tab2 = st.button("Réinitialiser", key="reset_tab2")

    theme_class = "dark-mode" if st.session_state.theme == 'dark' else ""
    st.markdown(f"<div class='{theme_class}'>", unsafe_allow_html=True)

    if reset_button_tab2:
        st.session_state.clear()
        st.experimental_rerun()

    if submit_button_tab2:
        request_data = {
            "student_id": student_id_tab2,
            "n_recommendations": n_recommendations_tab2
        }
        
        try:
            response = requests.post("http://localhost:8000/fictitious_recommendations/", json=request_data)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                st.markdown(f"<div class='error'>Erreur : {result['error']}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='success'>Recommandations générées avec succès !</div>", unsafe_allow_html=True)
                
                # Afficher les compétences et centres d'intérêt actuels
                student_row = df[df['ID_Étudiant'] == student_id_tab2]
                current_skills = ast.literal_eval(student_row['Compétences'].iloc[0]) if not student_row.empty else []
                current_interests = ast.literal_eval(student_row.get('Centres_d\'Intérêt', ['[]']).iloc[0]) if not student_row.empty else []
                st.markdown("<h3>Profil de l'étudiant</h3>", unsafe_allow_html=True)
                st.markdown(f"**Compétences actuelles** : {', '.join(current_skills) if current_skills else 'Aucune'}")
                st.markdown(f"**Centres d'intérêt actuels** : {', '.join(current_interests) if current_interests else 'Aucun'}")
                
                # Calcul des scores pour les compétences et centres d'intérêt recommandés
                def calculate_score(item, item_type, current_skills, current_interests, is_programmatic):
                    score = 3.0  # Score de base
                    # Bonus pour correspondance directe
                    if item_type == "skill" and item in current_skills:
                        score += 1.0
                    if item_type == "interest" and item in current_interests:
                        score += 1.0
                    # Bonus pour relations thématiques
                    related_items = THEMATIC_RELATIONS.get(item, [])
                    for related in related_items:
                        if related in current_skills or related in current_interests:
                            score += 0.5
                    # Bonus programmatique
                    if is_programmatic:
                        score += 0.3
                    # Plafonner le score à 5.0
                    return min(score, 5.0)

                # Préparer les compétences et centres d'intérêt avec leurs scores
                skills_from_db = [(skill, calculate_score(skill, "skill", current_skills, current_interests, False)) for skill in result['recommended_skills_from_db']]
                skills_programmatic = [(skill, calculate_score(skill, "skill", current_skills, current_interests, True)) for skill in result['recommended_skills_programmatic']]
                interests_from_db = [(interest, calculate_score(interest, "interest", current_skills, current_interests, False)) for interest in result['recommended_interests_from_db']]
                interests_programmatic = [(interest, calculate_score(interest, "interest", current_skills, current_interests, True)) for interest in result['recommended_interests_programmatic']]

                # Trier par score décroissant pour chaque catégorie
                skills_from_db = sorted(skills_from_db, key=lambda x: x[1], reverse=True)
                skills_programmatic = sorted(skills_programmatic, key=lambda x: x[1], reverse=True)
                interests_from_db = sorted(interests_from_db, key=lambda x: x[1], reverse=True)
                interests_programmatic = sorted(interests_programmatic, key=lambda x: x[1], reverse=True)

                # Afficher les compétences et centres d'intérêt recommandés (programmatiques)
                st.markdown("<h3>Compétences et centres d'intérêt recommandés (Programmatiques - Non présents dans la base)</h3>", unsafe_allow_html=True)
                st.markdown("**Compétences recommandées** :")
                for skill, score in skills_programmatic:
                    st.markdown(f"- {skill} (Score : {score:.1f})")
                st.markdown("**Centres d'intérêt recommandés** :")
                for interest, score in interests_programmatic:
                    st.markdown(f"- {interest} (Score : {score:.1f})")
                
                # Afficher les compétences et centres d'intérêt recommandés (basés sur la base)
                st.markdown("<h3>Compétences et centres d'intérêt recommandés (Basés sur la base)</h3>", unsafe_allow_html=True)
                st.markdown("**Compétences recommandées** :")
                for skill, score in skills_from_db:
                    st.markdown(f"- {skill} (Score : {score:.1f})")
                st.markdown("**Centres d'intérêt recommandés** :")
                for interest, score in interests_from_db:
                    st.markdown(f"- {interest} (Score : {score:.1f})")
                
                # Combiner toutes les recommandations en une seule liste avec leur catégorie
                all_recommendations = []
                for skill, score in skills_from_db:
                    all_recommendations.append({
                        "Type": "Compétence (Base)",
                        "Nom": skill,
                        "Score": score
                    })
                for skill, score in skills_programmatic:
                    all_recommendations.append({
                        "Type": "Compétence (Programmatique)",
                        "Nom": skill,
                        "Score": score
                    })
                for interest, score in interests_from_db:
                    all_recommendations.append({
                        "Type": "Centre d'intérêt (Base)",
                        "Nom": interest,
                        "Score": score
                    })
                for interest, score in interests_programmatic:
                    all_recommendations.append({
                        "Type": "Centre d'intérêt (Programmatique)",
                        "Nom": interest,
                        "Score": score
                    })

                # Trier toutes les recommandations par score décroissant
                all_recommendations = sorted(all_recommendations, key=lambda x: x["Score"], reverse=True)

                # Collecter les cours recommandés pour l'export dans l'ordre trié
                courses_data = []

                # Afficher les cours recommandés dans l'ordre global
                st.markdown("<h3>Cours recommandés </h3>", unsafe_allow_html=True)
                previous_score = float('inf')  # Pour vérifier que les scores sont bien décroissants
                for item in all_recommendations:
                    item_type = item["Type"]
                    name = item["Nom"]
                    score = item["Score"]

                    # Vérifier l'ordre des scores
                    if score > previous_score:
                        st.markdown(f"<div class='error'>Erreur : l'ordre des scores n'est pas respecté ({name} avec score {score:.1f} après un score {previous_score:.1f})</div>", unsafe_allow_html=True)
                    previous_score = score

                    try:
                        if name not in RECOMMENDED_COURSES:
                            st.markdown(f"<div class='error'>{item_type} {name} non trouvé dans RECOMMENDED_COURSES</div>", unsafe_allow_html=True)
                            continue
                        courses = RECOMMENDED_COURSES[name]
                        if not courses or not isinstance(courses, list) or not all(isinstance(course, tuple) and len(course) == 2 for course in courses):
                            st.markdown(f"<div class='error'>Données invalides pour {item_type} {name}</div>", unsafe_allow_html=True)
                            continue
                        st.markdown(f"- **{item_type} : {name} (Score : {score:.1f})** :")
                        # Afficher le premier cours
                        course_name, course_url = courses[0]
                        st.markdown(f"  - [{course_name}]({course_url})")
                        courses_data.append({
                            "Type": item_type,
                            "Nom": name,
                            "Score": score,
                            "Cours": course_name,
                            "URL": course_url
                        })
                        # Ajouter tous les cours pour l'export
                        for course_name, course_url in courses[1:]:
                            courses_data.append({
                                "Type": item_type,
                                "Nom": name,
                                "Score": score,
                                "Cours": course_name,
                                "URL": course_url
                            })
                        # Expander pour les cours supplémentaires
                        if len(courses) > 1:
                            with st.expander(f"Voir plus pour {name}"):
                                try:
                                    for course_name, course_url in courses[1:]:
                                        st.markdown(f"  - [{course_name}]({course_url})")
                                except Exception as e:
                                    st.markdown(f"<div class='error'>Erreur lors de l'affichage des cours supplémentaires pour {name} : {str(e)}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"<div class='error'>Erreur lors de l'affichage des cours pour {name} : {str(e)}</div>", unsafe_allow_html=True)
                
                # Export CSV
                profile_data = [
                    {'Type': 'Profil étudiant', 'ID': student_id_tab2, 'Score': '', 'Compétences': ', '.join(current_skills) if current_skills else 'Aucune', 'Centres_d\'intérêt': ', '.join(current_interests) if current_interests else 'Aucun'},
                    {'Type': 'Recommandation (Base)', 'ID': '', 'Score': '', 'Compétences': ', '.join([f"{skill} (Score: {score:.1f})" for skill, score in skills_from_db]) if skills_from_db else 'Aucune', 'Centres_d\'intérêt': ', '.join([f"{interest} (Score: {score:.1f})" for interest, score in interests_from_db]) if interests_from_db else 'Aucune'},
                    {'Type': 'Recommandation (Programmatique)', 'ID': '', 'Score': '', 'Compétences': ', '.join([f"{skill} (Score: {score:.1f})" for skill, score in skills_programmatic]) if skills_programmatic else 'Aucune', 'Centres_d\'intérêt': ', '.join([f"{interest} (Score: {score:.1f})" for interest, score in interests_programmatic]) if interests_programmatic else 'Aucune'}
                ]
                
                all_data = profile_data + courses_data
                
                export_df = pd.DataFrame(all_data)
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Télécharger en CSV",
                    data=csv,
                    file_name="recommandations_fictives.csv",
                    mime="text/csv",
                    key="download_csv_tab2"
                )
                
                # Export PDF
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)
                c.drawString(100, 750, "Recommandations MRSI")
                y = 700
                
                c.drawString(100, y, f"Profil de l'Étudiant {student_id_tab2}")
                y -= 20
                c.drawString(100, y, f"Compétences actuelles: {', '.join(current_skills) if current_skills else 'Aucune'}")
                y -= 20
                c.drawString(100, y, f"Centres d'intérêt actuels: {', '.join(current_interests) if current_interests else 'Aucun'}")
                y -= 40
                
                c.drawString(100, y, "Compétences et centres d'intérêt recommandés (Programmatiques)")
                y -= 20
                c.drawString(100, y, f"Compétences: {', '.join([f'{skill} (Score: {score:.1f})' for skill, score in skills_programmatic]) if skills_programmatic else 'Aucune'}")
                y -= 20
                c.drawString(100, y, f"Centres d'intérêt: {', '.join([f'{interest} (Score: {score:.1f})' for interest, score in interests_programmatic]) if interests_programmatic else 'Aucun'}")
                y -= 40
                
                c.drawString(100, y, "Compétences et centres d'intérêt recommandés (Basés sur la base)")
                y -= 20
                c.drawString(100, y, f"Compétences: {', '.join([f'{skill} (Score: {score:.1f})' for skill, score in skills_from_db]) if skills_from_db else 'Aucune'}")
                y -= 20
                c.drawString(100, y, f"Centres d'intérêt: {', '.join([f'{interest} (Score: {score:.1f})' for interest, score in interests_from_db]) if interests_from_db else 'Aucune'}")
                y -= 40
                
                c.drawString(100, y, "Cours recommandés (triés par score)")
                y -= 20
                for course in courses_data:
                    c.drawString(100, y, f"{course['Type']} : {course['Nom']} (Score: {course['Score']:.1f}): {course['Cours']} ({course['URL']})")
                    y -= 20
                    if y < 50:
                        c.showPage()
                        y = 750
                
                c.showPage()
                c.save()
                pdf = buffer.getvalue()
                st.download_button(
                    label="Télécharger en PDF",
                    data=pdf,
                    file_name="recommandations_fictives.pdf",
                    mime="application/pdf",
                    key="download_pdf_tab2"
                )
                
        except requests.exceptions.RequestException as e:
            st.markdown(f"<div class='error'>Erreur de connexion à l'API : {str(e)}</div>", unsafe_allow_html=True)

# Afficher l'historique (pour l'onglet 1 uniquement)
if st.session_state.history:
    with st.expander("Historique des requêtes (Onglet 1)"):
        for i, entry in enumerate(st.session_state.history):
            st.markdown(f"<h4>Requête {i+1}</h4>", unsafe_allow_html=True)
            st.json(entry["request"])
            st.markdown("<h5>Résultats</h5>", unsafe_allow_html=True)
            for teammate_id, score in entry["result"]["teammates"]:
                st.markdown(f"- Étudiant {teammate_id}: Score {score:.2f}")

st.markdown("</div>", unsafe_allow_html=True)