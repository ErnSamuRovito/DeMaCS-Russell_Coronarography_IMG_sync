import matplotlib.pyplot as plt
import sys
from pathlib import Path
import pandas as pd

class Extractor:
    @staticmethod
    def get_nrrd_from_excel(patient: str, excel_path: Path) -> str | None:
        try:
            df = pd.read_excel(excel_path)
        except FileNotFoundError:
            print(f"Excel file not found: {excel_path}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error reading Excel file: {e}", file=sys.stderr)
            return None

        patient_rows = df[df["Sequenza"].str.contains(patient, case=False, na=False)]
        if patient_rows.empty:
            return None

        for f in patient_rows["Segmentation"].dropna():
            if isinstance(f, str) and f.lower().endswith(".nrrd"):
                return f
        return None