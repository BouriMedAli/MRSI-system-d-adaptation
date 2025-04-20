import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

# === Données ===
df = pd.read_csv("Dataset/dataset_etudiants.csv")
df['Communautés'] = df['Communautés'].apply(ast.literal_eval)
df["Coéquipiers"] = df["Coéquipiers"].apply(ast.literal_eval)

def extraire_communauté_principale(communautés):
    return communautés[0] if communautés else "Aucune"
df['Communauté_Principale'] = df['Communautés'].apply(extraire_communauté_principale)

# === Vectorisation ===
def concat_features(row):
    return ' '.join(row['Communautés']) + ' ' + \
           ' '.join(ast.literal_eval(str(row['Compétences']))) + ' ' + \
           ' '.join(ast.literal_eval(str(row["Centres_d'Intérêt"])))
df['features'] = df.apply(concat_features, axis=1)

vectorizer = CountVectorizer()
X_features = vectorizer.fit_transform(df['features'])

# === PCA KNN ===
similarity_matrix = cosine_similarity(X_features)
pca_knn = PCA(n_components=2)
projection_knn = pca_knn.fit_transform(similarity_matrix)
df['X_KNN'] = projection_knn[:, 0]
df['Y_KNN'] = projection_knn[:, 1]

# === SVD Collaboration ===
student_ids = df["ID_Étudiant"].tolist()
collab_matrix = pd.DataFrame(0, index=student_ids, columns=student_ids)
for _, row in df.iterrows():
    for teammate in row["Coéquipiers"]:
        if teammate in student_ids:
            collab_matrix.at[row["ID_Étudiant"], teammate] = 1
            collab_matrix.at[teammate, row["ID_Étudiant"]] = 1

n_components = min(10, len(collab_matrix.columns) - 1)
svd = TruncatedSVD(n_components=n_components)
svd_matrix = svd.fit_transform(collab_matrix)
similarity_svd = cosine_similarity(svd_matrix)

index_to_id = dict(enumerate(collab_matrix.index))
id_to_index = {v: k for k, v in index_to_id.items()}

pca_svd = PCA(n_components=2)
projection_svd = pca_svd.fit_transform(collab_matrix)
df['X_SVD'] = projection_svd[:, 0]
df['Y_SVD'] = projection_svd[:, 1]

# === App Dash ===
app = dash.Dash(__name__)
app.title = "Recommandation Étudiants"

app.layout = html.Div([
    html.H1("🎓 Visualisation des étudiants & recommandations"),
    
    html.Div([
        html.Label("Entrez l'ID de l'étudiant :"),
        dcc.Input(id='input-id', type='number', min=1, step=1),
        html.Div(id='output-reco', style={'marginTop': '15px'}),
        html.Div(id='output-sim', style={'marginTop': '15px'})
    ], style={'padding': '10px'}),

    dcc.Store(id='reco-ids'),  # Stocker les IDs recommandés

    html.Div([
        html.H2("📌 Projection SVD (basée sur les collaborations)"),
        dcc.Graph(id='graph-svd')
    ])
])

@app.callback(
    Output('reco-ids', 'data'),
    Output('output-reco', 'children'),
    Output('output-sim', 'children'),
    Input('input-id', 'value')
)
def update_recommendation(student_id):
    if student_id is None or student_id not in id_to_index:
        return [], html.Div("❌ Veuillez sélectionner un étudiant."), None

    idx = id_to_index[student_id]
    sim_scores = similarity_svd[idx]

    similar_indices = sim_scores.argsort()[::-1]
    similar_ids = [
        index_to_id[i] for i in similar_indices
        if index_to_id[i] != student_id
    ][:5]

    recommandations = df[df["ID_Étudiant"].isin(similar_ids)][["ID_Étudiant", "Nom"]]
    reco_display = html.Div([
        html.Strong("🔗 Recommandation SVD :"),
        html.Ul([
            html.Li(f"{row['Nom']} (ID {row['ID_Étudiant']})")
            for _, row in recommandations.iterrows()
        ])
    ])

    # Affichage des scores de similarité
    sim_table = html.Div([
        html.Strong("📊 Similarité SVD avec les autres étudiants :"),
        html.Ul([
            html.Li(f"Étudiant_{index_to_id[i]} (score: {score:.3f})")
            for i, score in zip(similar_indices[:10], sim_scores[similar_indices[:10]])
            if index_to_id[i] != student_id
        ])
    ])

    return similar_ids, reco_display, sim_table


@app.callback(
    Output('graph-svd', 'figure'),
    Input('reco-ids', 'data'),
    State('input-id', 'value')
)
def update_graph(reco_ids, selected_id):
    fig = px.scatter(df, x='X_SVD', y='Y_SVD',
                     text=df['ID_Étudiant'],
                     color='Communauté_Principale',
                     labels={'color': 'Communauté'})

    fig.update_traces(marker=dict(size=10), textposition='top center')

    # Surligner les recommandations
    if reco_ids:
        reco_df = df[df['ID_Étudiant'].isin(reco_ids)]
        fig.add_trace(go.Scatter(
            x=reco_df['X_SVD'],
            y=reco_df['Y_SVD'],
            mode='markers+text',
            marker=dict(symbol='star', size=15, color='red'),
            text=reco_df['ID_Étudiant'],
            name='Recommandés'
        ))

    # Surligner l’étudiant sélectionné
    if selected_id:
        selected_df = df[df['ID_Étudiant'] == selected_id]
        fig.add_trace(go.Scatter(
            x=selected_df['X_SVD'],
            y=selected_df['Y_SVD'],
            mode='markers+text',
            marker=dict(symbol='circle', size=15, color='black'),
            text=selected_df['ID_Étudiant'],
            name='Étudiant sélectionné'
        ))

    return fig

if __name__ == '__main__':
    app.run(debug=True)
