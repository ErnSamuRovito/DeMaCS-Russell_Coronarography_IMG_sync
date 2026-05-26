from log import Log
import numpy as np
from api.models.result import Result
from analysis import Analysis
from grayScaleImage import GrayScaleImage
from extractor import Extractor
from pathlib import Path
from paths import validate_patient_id, resolve_patient_nrrd

EXCEL_FILE = "../../Dataset.xlsx"

class Service:
    def __init__(self, base_folder=None):
        self.logger = Log("API_History.log")
        self.base_folder = Path(base_folder) if base_folder else Path(__file__).resolve().parent

    def get_result(self, patient: str) -> Result:
        try:
            patient = validate_patient_id(patient)
        except ValueError as e:
            self.logger.log("warning", str(e))
            return Result(error=str(e))

        excel_path = self.base_folder / EXCEL_FILE
        nrrd_name = Extractor.get_nrrd_from_excel(patient, excel_path)

        if not nrrd_name:
            msg = f"No .nrrd file found for patient '{patient}'"
            self.logger.log("warning", f"{msg} in {excel_path}")
            return Result(error=msg)

        try:
            nrrd_path = resolve_patient_nrrd(self.base_folder, patient, nrrd_name)
        except ValueError as e:
            self.logger.log("warning", str(e))
            return Result(error=str(e))

        if not nrrd_path.exists():
            msg = f"File not found: {nrrd_path}"
            self.logger.log("error", msg)
            return Result(error=msg)

        try:
            img = GrayScaleImage(str(nrrd_path))
            image_data = img.get_image()

            if image_data.size == 0:
                raise ValueError("Empty image data.")

            analysis = Analysis(image_data)
            analysis.compare_sequence()

            result = Result(
                meta_keys=list(img.get_meta_data().keys()),
                image_size=tuple(int(x) for x in image_data.shape),
                Max=float(np.max(image_data)),
                Min=float(np.min(image_data)),
                distances=analysis.get_distances(),
                pixels_presence=img.get_pixels_presence().tolist(),
            )

            self.logger.log("info", f"Analysis completed successfully for patient {patient}")
            return result

        except Exception as e:
            msg = f"Error processing patient '{patient}': {e}"
            self.logger.log("critical", msg)
            return Result(error=msg)
