from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.core.service import Service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = Service()


@app.get("/patients/{patient_id}")
def read_item(patient_id: str):
    result = service.get_result(patient=patient_id)
    if result.error:
        status = 422 if "Invalid" in result.error or "empty" in result.error.lower() else 404
        raise HTTPException(status_code=status, detail=result.error)
    return result
