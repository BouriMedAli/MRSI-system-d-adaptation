from fastapi import FastAPI
from pydantic import BaseModel
from codeKNN import recommander 

app = FastAPI()

class RecommandationRequest(BaseModel):
    id_etudiant: int

@app.post("/recommander/")
def recommander_api(request: RecommandationRequest):
    result = recommander(request.id_etudiant)
    if result is None:
        return {"error": "Étudiant non trouvé"}
    return result
