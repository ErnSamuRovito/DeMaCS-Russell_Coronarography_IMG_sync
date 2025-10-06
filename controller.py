from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from service import Service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = Service()

@app.get("/{patient_id}")
def read_item(patient_id: str):
    return service.get_result(patient = patient_id)