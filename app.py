from fastapi import FastAPI
from pydantic import BaseModel
from codeKNN import recommander 
from codeSVD import recommander_svd

app = FastAPI()

class RecommandationRequest(BaseModel):
    id_etudiant: int

@app.post("/recommander/")
def recommander_api(request: RecommandationRequest):
    result = recommander(request.id_etudiant)
    if result is None:
        return {"error": "Étudiant non trouvé"}
    return result

@app.post("/recommander_svd/")
def recommander_svd_api(request: RecommandationRequest):
    result = recommander_svd(request.id_etudiant)
    if result is None:
        return {"error": "Étudiant non trouvé"}
    return result
