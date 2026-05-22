# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.patients import router as patients_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients_router)