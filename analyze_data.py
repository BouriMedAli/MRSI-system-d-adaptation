import pandas as pd
import json
import ast
from collections import Counter

# Charger les données complètes
df = pd.read_csv('Dataset/dataset_etudiants.csv')

print(f"📊 Analyse complète de {len(df)} étudiants\n")

# Statistiques de base
stats = {
    "total_etudiants": len(df),
    "travaux_collaboratifs": {
        "moyenne": float(df['Travaux_Collaboratifs'].mean()),
        "min": int(df['Travaux_Collaboratifs'].min()),
        "max": int(df['Travaux_Collaboratifs'].max()),
        "total": int(df['Travaux_Collaboratifs'].sum())
    },
    "interactions": {
        "moyenne": float(df['Nombre_Interactions'].mean()),
        "min": int(df['Nombre_Interactions'].min()),
        "max": int(df['Nombre_Interactions'].max()),
        "total": int(df['Nombre_Interactions'].sum())
    }
}

# Analyser les communautés
all_communities = []
for communities_str in df['Communautés']:
    try:
        communities = ast.literal_eval(communities_str)
        all_communities.extend(communities)
    except:
        pass

community_counts = Counter(all_communities)
stats['communautes'] = dict(community_counts.most_common())

# Analyser les compétences
all_skills = []
for skills_str in df['Compétences']:
    try:
        skills = ast.literal_eval(skills_str)
        all_skills.extend(skills)
    except:
        pass

skill_counts = Counter(all_skills)
stats['competences'] = dict(skill_counts.most_common())

# Analyser les centres d'intérêt
all_interests = []
for interests_str in df['Centres_d\'Intérêt']:
    try:
        interests = ast.literal_eval(interests_str)
        all_interests.extend(interests)
    except:
        pass

interest_counts = Counter(all_interests)
stats['centres_interet'] = dict(interest_counts.most_common())

# Analyser le réseau de collaboration
total_coequipiers = 0
for coequipiers_str in df['Coéquipiers']:
    try:
        coequipiers = ast.literal_eval(coequipiers_str)
        total_coequipiers += len(coequipiers)
    except:
        pass

stats['reseau'] = {
    "total_connexions": total_coequipiers,
    "moyenne_coequipiers": round(total_coequipiers / len(df), 2)
}

# Distribution des travaux collaboratifs
travaux_distribution = df['Travaux_Collaboratifs'].value_counts().sort_index().to_dict()
stats['travaux_distribution'] = {int(k): int(v) for k, v in travaux_distribution.items()}

# Top étudiants par interactions
top_students = df.nlargest(10, 'Nombre_Interactions')[['Nom', 'Nombre_Interactions']].to_dict('records')
stats['top_etudiants'] = top_students

# Sauvegarder les résultats
with open('analysis_results.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print("✅ Analyse terminée!")
print(f"\n📈 Statistiques clés:")
print(f"   - Total étudiants: {stats['total_etudiants']}")
print(f"   - Moyenne travaux collaboratifs: {stats['travaux_collaboratifs']['moyenne']:.1f}")
print(f"   - Moyenne interactions: {stats['interactions']['moyenne']:.1f}")
print(f"   - Communautés principales: {list(stats['communautes'].keys())[:3]}")
print(f"   - Compétences principales: {list(stats['competences'].keys())[:3]}")
print(f"\n💾 Résultats sauvegardés dans analysis_results.json")
