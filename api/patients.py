from fastapi import APIRouter, HTTPException
from core.service import Service
from models.result import Result

router = APIRouter(prefix="/patients", tags=["Patients"])

service = Service(base_folder="/app")

@router.get("/{patient_id}", response_model=Result)
def get_patient(patient_id: str):
    result = service.get_result(patient_id)

    if result.error:
        status = 422 if "invalid" in result.error.lower() else 404
        raise HTTPException(status_code=status, detail=result.error)

    return result