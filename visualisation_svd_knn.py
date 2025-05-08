import pandas as pd
import numpy as np
import ast
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD
from sklearn.decomposition import PCA
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import logging
import os

# === Configuration des logs ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Chargement et Prétraitement des Données ===
df = pd.read_csv("Dataset/dataset_etudiants.csv")
df['Communautés'] = df['Communautés'].apply(ast.literal_eval)
df["Coéquipiers"] = df["Coéquipiers"].apply(ast.literal_eval)

def extraire_communauté_principale(communautés):
    return communautés[0] if communautés else "Aucune"
df['Communauté_Principale'] = df['Communautés'].apply(extraire_communauté_principale)

# === Vectorisation des Caractéristiques ===
def concat_features(row):
    return ' '.join(row['Communautés']) + ' ' + \
           ' '.join(ast.literal_eval(str(row['Compétences']))) + ' ' + \
           ' '.join(ast.literal_eval(str(row["Centres_d'Intérêt"])))

df['features'] = df.apply(concat_features, axis=1)
vectorizer = CountVectorizer()
X_features = vectorizer.fit_transform(df['features'])

# === PCA pour KNN ===
similarity_matrix = cosine_similarity(X_features)
pca_knn = PCA(n_components=2)
projection_knn = pca_knn.fit_transform(similarity_matrix)
df['X_KNN'] = projection_knn[:, 0]
df['Y_KNN'] = projection_knn[:, 1]

# === SVD pour Collaboration ===
student_ids = df["ID_Étudiant"].tolist()
interactions = []
for _, row in df.iterrows():
    for teammate in row["Coéquipiers"]:
        interactions.append((row["ID_Étudiant"], teammate, 1.0))

reader = Reader(rating_scale=(0, 1))
data = Dataset.load_from_df(pd.DataFrame(interactions, columns=["userID", "itemID", "rating"]), reader)
trainset = data.build_full_trainset()

svd_model = SVD(n_factors=20)
svd_model.fit(trainset)

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

# === Fonctions de Recommandation ===
def svd_predict(student_id, all_student_ids, top_n=5):
    predictions = []
    for other_id in all_student_ids:
        if other_id != student_id:
            prediction = svd_model.predict(student_id, other_id)
            predictions.append((other_id, prediction.est))
    predictions.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in predictions[:top_n]]

def hybrid_predict(student_id, all_student_ids, top_n=5, alpha=0.5):
    svd_recommendations = svd_predict(student_id, all_student_ids, top_n)
    idx = id_to_index[student_id]
    content_scores = similarity_svd[idx]
    
    hybrid_predictions = []
    for i, other_id in enumerate(all_student_ids):
        if other_id != student_id:
            content_score = content_scores[i]
            svd_score = svd_model.predict(student_id, other_id).est
            hybrid_score = alpha * svd_score + (1 - alpha) * content_score
            hybrid_predictions.append((other_id, hybrid_score))
    
    hybrid_predictions.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in hybrid_predictions[:top_n]]

# === Application Dash ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], title="Système de Recommandation Étudiants")
app.config.suppress_callback_exceptions = True

# === Layout ===
app.layout = dbc.Container([
    # En-tête
    dbc.Row([
        dbc.Col(html.H1("🎓 Système de Recommandation pour Étudiants", className="text-center mb-4"), width=12)
    ]),

    # Contenu principal
    dbc.Row([
        # Colonne gauche : Inputs et Recommandations
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🔍 Sélectionner un Étudiant", className="card-title"),
                    dcc.Dropdown(
                        id='input-id',
                        options=[{'label': f"Étudiant ID {id}", 'value': id} for id in student_ids],
                        placeholder="Choisissez un étudiant...",
                        className="mb-3"
                    ),
                    html.Button("📥 Télécharger Recommandations", id="btn-download", className="btn btn-primary mb-3"),
                    dcc.Download(id="download-reco"),
                    dcc.Loading(
                        id="loading-reco",
                        type="circle",
                        children=html.Div(id='output-reco')
                    ),
                    dcc.Loading(
                        id="loading-sim",
                        type="circle",
                        children=html.Div(id='output-sim')
                    ),
                    dcc.Store(id='reco-ids')
                ])
            ], className="mb-4")
        ], width=4),

        # Colonne droite : Visualisations
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊 Visualisation SVD (Collaborations)", className="card-title"),
                    dcc.Graph(id='graph-svd')
                ])
            ], className="mb-4"),
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊 Visualisation KNN (Contenu)", className="card-title"),
                    dcc.Graph(id='graph-knn')
                ])
            ])
        ], width=8)
    ])
], fluid=True)

# === Callbacks ===
@app.callback(
    [Output('reco-ids', 'data'),
     Output('output-reco', 'children'),
     Output('output-sim', 'children'),
     Output('download-reco', 'data')],
    [Input('input-id', 'value'),
     Input('btn-download', 'n_clicks')],
    prevent_initial_call=True
)
def update_recommendation(student_id, n_clicks):
    if not student_id or student_id not in id_to_index:
        return [], html.Div("❌ Veuillez sélectionner un étudiant.", className="text-danger"), None, None

    # Recommandations
    svd_reco = svd_predict(student_id, student_ids, top_n=5)
    hybrid_reco = hybrid_predict(student_id, student_ids, top_n=5)

    # Tableau des recommandations
    reco_df = df[df['ID_Étudiant'].isin(hybrid_reco)][['ID_Étudiant', 'Communauté_Principale', 'Compétences', 'Centres_d\'Intérêt']]
    reco_table = dash_table.DataTable(
        data=reco_df.to_dict('records'),
        columns=[
            {'name': 'ID', 'id': 'ID_Étudiant'},
            {'name': 'Communauté', 'id': 'Communauté_Principale'},
            {'name': 'Compétences', 'id': 'Compétences'},
            {'name': 'Centres d\'Intérêt', 'id': 'Centres_d\'Intérêt'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'backgroundColor': '#e9ecef', 'fontWeight': 'bold', 'color': 'black'}
    )

    reco_display = html.Div([
        html.H5("🔗 Recommandations SVD :"),
        html.Ul([html.Li(f"Étudiant ID {x}") for x in svd_reco]),
        html.H5("🔗 Recommandations Hybrides :"),
        reco_table
    ])

    # Similarité SVD
    sim_table = html.Div([
        html.H5("📊 Similarité SVD :"),
        html.Ul([html.Li(f"Étudiant ID {student_id} et ID {x} : Similarité = {similarity_svd[id_to_index[student_id], id_to_index[x]]:.2f}") for x in svd_reco])
    ])

    # Données à télécharger
    download_data = pd.DataFrame(hybrid_reco, columns=["ID_Étudiant"])
    download_data = download_data.merge(df[['ID_Étudiant', 'Communauté_Principale', 'Compétences', 'Centres_d\'Intérêt']], on="ID_Étudiant")
    return hybrid_reco, reco_display, sim_table, dcc.send_data_frame(download_data.to_csv, "recommandations.csv")

# === Visualisation SVD ===
@app.callback(
    Output('graph-svd', 'figure'),
    [Input('input-id', 'value')]
)
def update_svd_plot(student_id):
    if not student_id or student_id not in id_to_index:
        return go.Figure()

    # Plot SVD
    student_index = id_to_index[student_id]
    fig = px.scatter(df, x='X_SVD', y='Y_SVD', color='Communauté_Principale', hover_name='ID_Étudiant', 
                     title="Visualisation des Étudiants (SVD)")
    fig.add_scatter(x=[df['X_SVD'][student_index]], y=[df['Y_SVD'][student_index]], mode='markers',
                    marker=dict(size=12, color='red', symbol='star'), name="Étudiant sélectionné")
    fig.update_layout(title="Visualisation des Étudiants (SVD)", xaxis_title="Composante Principale 1", yaxis_title="Composante Principale 2")
    return fig

# === Visualisation KNN ===
@app.callback(
    Output('graph-knn', 'figure'),
    [Input('input-id', 'value')]
)
def update_knn_plot(student_id):
    if not student_id or student_id not in id_to_index:
        return go.Figure()

    # Plot KNN
    student_index = id_to_index[student_id]
    fig = px.scatter(df, x='X_KNN', y='Y_KNN', color='Communauté_Principale', hover_name='ID_Étudiant', 
                     title="Visualisation des Étudiants (KNN - Contenu)")
    fig.add_scatter(x=[df['X_KNN'][student_index]], y=[df['Y_KNN'][student_index]], mode='markers',
                    marker=dict(size=12, color='red', symbol='star'), name="Étudiant sélectionné")
    fig.update_layout(title="Visualisation des Étudiants (KNN - Contenu)", xaxis_title="Composante Principale 1", yaxis_title="Composante Principale 2")
    return fig

# === Lancement du serveur ===
if __name__ == '__main__':
    app.run(debug=True)
