from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI()

# Chargement du dataset
try:
    df = pd.read_csv("dataset_etudiants.csv")
    print("✅ Dataset chargé avec succès !")
except Exception as e:
    print(f"❌ Erreur lors du chargement du dataset : {e}")
    df = pd.DataFrame()  # Crée un DataFrame vide en cas d'échec

print("🔍 Aperçu du dataset :")
print(df.head())

# Route pour récupérer tous les étudiants
@app.get("/students")
def get_students():
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset non disponible")
    return df.to_dict(orient="records")

# Route pour récupérer un étudiant par son ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataset non disponible")
    if student_id < 0 or student_id >= len(df):
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    return df.iloc[student_id].to_dict()

# Route pour la prédiction (Exemple de structure)
@app.post("/predict")
def predict():
    return {"message": "La fonctionnalité de prédiction sera implémentée ici."}

# Lancement du serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
