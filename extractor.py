import sys
from pathlib import Path
import pandas as pd

EXCEL_USECOLS = ["Sequenza", "Segmentation"]

_excel_cache: dict[tuple[str, float], pd.DataFrame] = {}


def _read_excel_minimal(excel_path: Path) -> pd.DataFrame:
    resolved = excel_path.resolve()
    mtime = resolved.stat().st_mtime
    key = (str(resolved), mtime)
    if key in _excel_cache:
        return _excel_cache[key]

    df = pd.read_excel(resolved, usecols=EXCEL_USECOLS)
    for col in EXCEL_USECOLS:
        if col in df.columns:
            df[col] = df[col].astype("string")

    _excel_cache[key] = df
    stale = [k for k in _excel_cache if k[0] == str(resolved) and k != key]
    for k in stale:
        del _excel_cache[k]
    return df


class Extractor:
    @staticmethod
    def get_nrrd_from_excel(patient: str, excel_path: Path) -> str | None:
        try:
            df = _read_excel_minimal(excel_path)
        except FileNotFoundError:
            print(f"Excel file not found: {excel_path}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error reading Excel file: {e}", file=sys.stderr)
            return None

        if "Sequenza" not in df.columns or "Segmentation" not in df.columns:
            return None

        patient_key = patient.strip().casefold()
        patient_rows = df[
            df["Sequenza"].str.strip().str.casefold() == patient_key
        ]
        if patient_rows.empty:
            return None

        for f in patient_rows["Segmentation"].dropna():
            s = str(f)
            if s.lower().endswith(".nrrd"):
                return s
        return None
