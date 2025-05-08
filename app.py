# from fastapi import FastAPI
# from pydantic import BaseModel
# from codeKNN import recommander 
# from codeSVD import recommander_svd

# app = FastAPI()

# class RecommandationRequest(BaseModel):
#     id_etudiant: int
#     top_n: int = 5  # Nombre de recommandations à renvoyer

# @app.post("/recommander/")
# def recommander_api(request: RecommandationRequest):
#     result = recommander(request.id_etudiant)
#     if result is None:
#         return {"error": "Étudiant non trouvé"}
#     return result

# @app.post("/recommander_svd/")
# def recommander_svd_api(request: RecommandationRequest):
#     result = recommander_svd(request.id_etudiant, top_n=request.top_n)
#     if result is None:
#         return {"error": "Étudiant non trouvé"}
#     return result


# app.py
# from fastapi import FastAPI
# from pydantic import BaseModel
# from codeKNN import recommander
# from codeSVD import recommend as recommander_svd

# app = FastAPI()

# class RecommandationRequest(BaseModel):
#     id_etudiant: int
#     top_n: int = 5
#     mode: str = "hybride"  # "knn", "svd", "hybride"

# @app.post("/recommander/")
# def recommander_api(request: RecommandationRequest):
#     if request.mode == "knn":
#         result = recommander(request.id_etudiant)
#         if result is None:
#             return {"error": "Étudiant non trouvé"}
#         return result
#     elif request.mode == "svd":
#         result = recommander_svd(request.id_etudiant, top_n=request.top_n, use_surprise=True)
#         return result
#     else:  # mode hybride par défaut
#         result = recommander_svd(request.id_etudiant, top_n=request.top_n, use_hybrid_surprise_content=True)
#         return result

# app.py dernier
# from dash import Dash, html, dcc, Input, Output
# from flask import Flask
# from codeSVD import recommend as recommend_svd, init_model
# from codeKNN import recommander as recommend_knn

# # Initialize Flask server (for Gunicorn)
# server = Flask(__name__)

# # Initialize Dash app
# app = Dash(__name__, server=server)

# # Initialize the SVD model once and store globally
# try:
#     global_svd_model = init_model()  # Assuming init_model returns the model or None
#     print("SVD model initialized globally.")
# except Exception as e:
#     print(f"Error initializing SVD model: {e}")

# # Define the layout of the Dash app
# app.layout = html.Div([
#     html.H1("Recommendation System Visualization"),
#     html.Label("Enter Student ID:"),
#     dcc.Input(id="student-id", type="number", value=1, min=1),
#     html.Label("Select Recommendation Mode:"),
#     dcc.Dropdown(
#         id="mode",
#         options=[
#             {"label": "KNN", "value": "knn"},
#             {"label": "SVD", "value": "svd"},
#             {"label": "Hybrid", "value": "hybride"}
#         ],
#         value="svd"
#     ),
#     html.Label("Number of Recommendations:"),
#     dcc.Input(id="top-n", type="number", value=5, min=1),
#     html.Button("Get Recommendations", id="submit-button", n_clicks=0),
#     html.Div(id="recommendation-output")
# ])

# # Callback to update recommendations based on user input
# @app.callback(
#     Output("recommendation-output", "children"),
#     [
#         Input("submit-button", "n_clicks"),
#         Input("student-id", "value"),
#         Input("mode", "value"),
#         Input("top-n", "value")
#     ]
# )
# def update_recommendations(n_clicks, student_id, mode, top_n):
#     if n_clicks == 0:
#         return "Enter a student ID and click the button to get recommendations."

#     try:
#         if student_id is None or top_n is None:
#             return "Please provide a valid student ID and number of recommendations."

#         if mode == "knn":
#             result = recommend_knn(student_id)
#         elif mode == "svd":
#             result = recommend_svd(student_id, top_n=top_n, use_surprise=True)
#         elif mode == "hybride":
#             result = recommend_svd(student_id, top_n=top_n, use_hybrid=True)
#         else:
#             return "Invalid mode selected."

#         if result is None or len(result) == 0:
#             return "No recommendations found for this student."

#         # Format the recommendations as a list
#         recommendation_list = [
#             html.Li(f"Student ID: {item['ID_Étudiant']}, Name: {item['Nom']}")
#             for item in result
#         ]
#         return html.Ul(recommendation_list)
#     except Exception as e:
#         return f"Error: {str(e)}"

# if __name__ == "__main__":
#     app.run(debug=True)

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
from flask import Flask
from codeSVD import recommend as recommend_svd, init_model
from codeKNN import recommander as recommend_knn

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask server (for Gunicorn)
server = Flask(__name__)

# Initialize Dash app
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.FLATLY], title="Système de Recommandation Étudiants")
app.config.suppress_callback_exceptions = True

# Initialize SVD model and load data
try:
    init_model()
    print("SVD model initialized globally.")
except Exception as e:
    print(f"Error initializing SVD model: {e}")

# Chargement et prétraitement des données
df = pd.read_csv("Dataset/dataset_etudiants.csv")
df['Communautés'] = df['Communautés'].apply(ast.literal_eval)
df["Coéquipiers"] = df["Coéquipiers"].apply(ast.literal_eval)

def extraire_communauté_principale(communautés):
    return communautés[0] if communautés else "Aucune"
df['Communauté_Principale'] = df['Communautés'].apply(extraire_communauté_principale)

# Vectorisation des caractéristiques (KNN)
def concat_features(row):
    return ' '.join(row['Communautés']) + ' ' + \
           ' '.join(ast.literal_eval(str(row['Compétences']))) + ' ' + \
           ' '.join(ast.literal_eval(str(row["Centres_d'Intérêt"])))
df['features'] = df.apply(concat_features, axis=1)
vectorizer = CountVectorizer()
X_features = vectorizer.fit_transform(df['features'])

# PCA pour KNN
similarity_matrix = cosine_similarity(X_features)
pca_knn = PCA(n_components=2)
projection_knn = pca_knn.fit_transform(similarity_matrix)
df['X_KNN'] = projection_knn[:, 0]
df['Y_KNN'] = projection_knn[:, 1]

# SVD pour collaboration
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

# Layout
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
                    html.Label("Mode de Recommandation:", className="mt-2"),
                    dcc.Dropdown(
                        id="mode",
                        options=[
                            {"label": "KNN", "value": "knn"},
                            {"label": "SVD", "value": "svd"},
                            {"label": "Hybride", "value": "hybride"}
                        ],
                        value="svd",
                        className="mb-3"
                    ),
                    html.Label("Nombre de Recommandations:", className="mt-2"),
                    dcc.Input(
                        id="top-n",
                        type="number",
                        value=5,
                        min=1,
                        className="mb-3",
                        style={'width': '100%'}
                    ),
                    html.Button("📥 Obtenir Recommandations", id="btn-recommend", className="btn btn-primary mb-3"),
                    html.Button("📥 Télécharger Recommandations", id="btn-download", className="btn btn-secondary mb-3"),
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

# Callbacks
@app.callback(
    [Output('reco-ids', 'data'),
     Output('output-reco', 'children'),
     Output('output-sim', 'children'),
     Output('download-reco', 'data')],
    [Input('btn-recommend', 'n_clicks'),
     Input('btn-download', 'n_clicks'),
     Input('input-id', 'value'),
     Input('mode', 'value'),
     Input('top-n', 'value')],
    prevent_initial_call=True
)
def update_recommendation(recommend_clicks, download_clicks, student_id, mode, top_n):
    from dash import ctx
    if not student_id or student_id not in id_to_index:
        return [], html.Div("❌ Veuillez sélectionner un étudiant.", className="text-danger"), None, None

    # Générer les recommandations
    try:
        if mode == "knn":
            reco = recommend_knn(student_id)
        elif mode == "svd":
            reco = recommend_svd(student_id, top_n=top_n, use_surprise=True)
        elif mode == "hybride":
            reco = recommend_svd(student_id, top_n=top_n, use_hybrid=True)
        else:
            return [], html.Div("❌ Mode invalide.", className="text-danger"), None, None

        if not reco:
            return [], html.Div(f"❌ Aucune recommandation pour l'étudiant ID {student_id}.", className="text-danger"), None, None

        # Extraire les ID des recommandations
        reco_ids = [item['ID_Étudiant'] for item in reco]

        # Tableau des recommandations
        reco_df = df[df['ID_Étudiant'].isin(reco_ids)][['ID_Étudiant', 'Nom', 'Communauté_Principale', 'Compétences', 'Centres_d\'Intérêt']]
        reco_table = dash_table.DataTable(
            data=reco_df.to_dict('records'),
            columns=[
                {'name': 'ID', 'id': 'ID_Étudiant'},
                {'name': 'Nom', 'id': 'Nom'},
                {'name': 'Communauté', 'id': 'Communauté_Principale'},
                {'name': 'Compétences', 'id': 'Compétences'},
                {'name': 'Centres d\'Intérêt', 'id': 'Centres_d\'Intérêt'}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'backgroundColor': '#e9ecef', 'fontWeight': 'bold', 'color': 'black'}
        )

        reco_display = html.Div([
            html.H5(f"🔗 Recommandations ({mode.upper()}) :"),
            reco_table
        ])

        # Similarité SVD
        sim_table = html.Div([
            html.H5("📊 Similarité SVD :"),
            html.Ul([html.Li(f"Étudiant ID {student_id} et ID {x} : Similarité = {similarity_svd[id_to_index[student_id], id_to_index[x]]:.2f}") for x in reco_ids])
        ])

        # Téléchargement
        download_data = None
        if ctx.triggered_id == 'btn-download':
            download_data = pd.DataFrame(reco, columns=["ID_Étudiant", "Nom"])
            download_data = download_data.merge(df[['ID_Étudiant', 'Communauté_Principale', 'Compétences', 'Centres_d\'Intérêt']], on="ID_Étudiant")
            download_data = dcc.send_data_frame(download_data.to_csv, "recommandations.csv")

        return reco_ids, reco_display, sim_table, download_data
    except Exception as e:
        return [], html.Div(f"❌ Erreur : {str(e)}", className="text-danger"), None, None

# Visualisation SVD
@app.callback(
    Output('graph-svd', 'figure'),
    [Input('input-id', 'value')]
)
def update_svd_plot(student_id):
    if not student_id or student_id not in id_to_index:
        return go.Figure()

    student_index = id_to_index[student_id]
    fig = px.scatter(df, x='X_SVD', y='Y_SVD', color='Communauté_Principale', hover_name='ID_Étudiant', 
                     title="Visualisation des Étudiants (SVD)")
    fig.add_scatter(x=[df['X_SVD'][student_index]], y=[df['Y_SVD'][student_index]], mode='markers',
                    marker=dict(size=12, color='red', symbol='star'), name="Étudiant sélectionné")
    fig.update_layout(title="Visualisation des Étudiants (SVD)", xaxis_title="Composante Principale 1", yaxis_title="Composante Principale 2")
    return fig

# Visualisation KNN
@app.callback(
    Output('graph-knn', 'figure'),
    [Input('input-id', 'value')]
)
def update_knn_plot(student_id):
    if not student_id or student_id not in id_to_index:
        return go.Figure()

    student_index = id_to_index[student_id]
    fig = px.scatter(df, x='X_KNN', y='Y_KNN', color='Communauté_Principale', hover_name='ID_Étudiant', 
                     title="Visualisation des Étudiants (KNN - Contenu)")
    fig.add_scatter(x=[df['X_KNN'][student_index]], y=[df['Y_KNN'][student_index]], mode='markers',
                    marker=dict(size=12, color='red', symbol='star'), name="Étudiant sélectionné")
    fig.update_layout(title="Visualisation des Étudiants (KNN - Contenu)", xaxis_title="Composante Principale 1", yaxis_title="Composante Principale 2")
    return fig

if __name__ == "__main__":
    app.run(debug=True)

# from fastapi import FastAPI
# from pydantic import BaseModel
# from codeSVD import recommend as recommander_par_mode_svd, init_model
# from codeKNN import recommander as recommander_knn
# from contextlib import asynccontextmanager

# # Initialisation automatique du modèle SVD au démarrage de l'app
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     init_model()
#     yield
#     # Code optionnel à l'arrêt de l'app

# app = FastAPI(lifespan=lifespan)

# # Structure de la requête d'API
# class RecommandationRequest(BaseModel):
#     id_etudiant: int
#     top_n: int = 5
#     mode: str = "hybride"  # "knn", "svd", "hybride"

# @app.post("/recommander/")
# def recommander_api(request: RecommandationRequest):
#     if request.mode == "knn":
#         result = recommander_knn(request.id_etudiant)
#         if result is None or len(result) == 0:
#             return {"error": "Étudiant non trouvé ou aucune recommandation"}
#         return {"mode": "knn", "recommendations": result}

#     elif request.mode == "svd":
#         result = recommander_par_mode_svd(request.id_etudiant, top_n=request.top_n, use_surprise=True)
    
#     elif request.mode == "hybride":
#         result = recommander_par_mode_svd(request.id_etudiant, top_n=request.top_n, use_hybrid=True)

#     else:
#         return {"error": "Mode invalide. Choisissez 'knn', 'svd' ou 'hybride'"}

#     if result is None or len(result) == 0:
#         return {"error": "Étudiant non trouvé ou aucune recommandation"}

#     return {"mode": request.mode, "recommendations": result}
