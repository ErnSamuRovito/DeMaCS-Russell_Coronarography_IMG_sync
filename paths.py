from pathlib import Path

ROOT_DIR = "Root_dir"


def validate_patient_id(patient: str) -> str:
    patient = patient.strip()
    if not patient:
        raise ValueError("Patient id is empty.")
    if "/" in patient or "\\" in patient or ".." in patient:
        raise ValueError(f"Invalid patient id: {patient!r}")
    return patient


def resolve_patient_nrrd(base_folder: Path, patient: str, nrrd_name: str) -> Path:
    """Resolve NRRD path and ensure it stays under base_folder/Root_dir."""
    patient = validate_patient_id(patient)
    root = (base_folder / ROOT_DIR).resolve()
    nrrd_path = (root / patient / nrrd_name).resolve()
    if not str(nrrd_path).startswith(str(root)):
        raise ValueError("Path traversal detected")
    return nrrd_path
