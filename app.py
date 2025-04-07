from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import pandas as pd
from modules import recommender

app = FastAPI(
    title="Recommendation System API",
    description="API for managing personalized recommendations and comparing models (KNN, SVD, etc.)",
    version="1.1.0",
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags=["Recommendations"])
async def home(request: Request):
    recommendations = recommender.get_global_recommendations()
    return templates.TemplateResponse("index.html", {"request": request, "recommendations": recommendations})


'''

@app.get("/user/{user_id}", tags=["User Profile"])
async def user_profile(request: Request, user_id: int):
    try:
        # Récupérer toutes les recommandations
        cosine_recs = recommender.get_user_recommendations(user_id)
        knn_recs = recommender.get_knn_recommendations(user_id)
        svd_recs = recommender.get_svd_recommendations(user_id)
        comparison = recommender.compare_models()
        

        if not cosine_recs:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "message": f"User {user_id} not found"
            })

        return templates.TemplateResponse("user_comparison.html", {
            "request": request,
            "cosine_recs": cosine_recs,
            "knn_recs": knn_recs,
            "svd_recs": svd_recs,
            "comparison": comparison,
            "user_id": user_id
        })
    
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Error loading profile: {str(e)}"
        })
    


'''
@app.get("/user/{user_id}", tags=["User Profile"])
async def user_profile(request: Request, user_id: int):
    try:
        # Vérification de l'existence de l'utilisateur
        df = recommender.load_data()
        if user_id not in df["ID_Étudiant"].values:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "message": f"Étudiant {user_id} non trouvé"
            })

        return templates.TemplateResponse("user_comparison.html", {
            "request": request,
            "cosine_recs": recommender.get_user_recommendations(user_id),
            "knn_recs": recommender.get_knn_recommendations(user_id),
            "svd_recs": recommender.get_svd_recommendations(user_id),
            "comparison": recommender.compare_models(),
            "user_id": user_id
        })
    
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Erreur de chargement: {str(e)}"
        })
    

@app.get("/compare", tags=["Model Comparison"])
async def compare_models(request: Request):
    try:
        results = recommender.compare_models()
        return templates.TemplateResponse("compare.html", {"request": request, "results": results})
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Comparison error: {str(e)}"
        })

@app.get("/add_user", tags=["User Management"])
async def add_user_get(request: Request):
    return templates.TemplateResponse("add_user.html", {"request": request})

@app.post("/add_user", tags=["User Management"])
async def add_user_post(
    request: Request,
    user_name: str = Form(...),
    communities: str = Form(...),
    skills: str = Form(...),
    interests: str = Form(...),
    interactions: int = Form(...),
    teamwork: int = Form(...)
):
    try:
        # Create new user data
        new_user = {
            "Nom": user_name,
            "Travaux_Collaboratifs": teamwork,
            "Coéquipiers": [],
            "Communautés": [c.strip() for c in communities.split(",") if c.strip()],
            "Nombre_Interactions": interactions,
            "Compétences": [s.strip() for s in skills.split(",") if s.strip()],
            "Centres_d'Intérêt": [i.strip() for i in interests.split(",") if i.strip()]
        }

        # Add to dataset
        recommender.add_user_to_dataset(new_user)
        
        # Redirect to new user's profile
        
        return RedirectResponse(url=f"/user/{new_user['ID_Étudiant']}", status_code=303)
    
    
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Error adding user: {str(e)}"
        })




@app.get("/search", tags=["Search"])
async def search_student(request: Request, query: str = ""):
    try:
        # Charger les données fraîches à chaque recherche
        df = recommender.load_data()
        
        # Nettoyer la requête
        clean_query = query.strip().lower()
        
        if not clean_query:
            return RedirectResponse(url="/")

        # Recherche par ID si numérique
        if clean_query.isdigit():
            user_id = int(clean_query)
            results = df[df["ID_Étudiant"] == user_id]
        
        # Recherche par nom sinon
        else:
            df["Nom"] = df["Nom"].str.strip().str.lower()  # Normaliser les noms
            results = df[df["Nom"].str.contains(clean_query, case=False, na=False)]

        if not results.empty:
            return RedirectResponse(url=f"/user/{results.iloc[0]['ID_Étudiant']}")
        
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Aucun étudiant trouvé pour '{query}'"
        })

    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Erreur technique lors de la recherche : {str(e)}"
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.6", port=80)