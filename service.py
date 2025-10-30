from log import Log
import numpy as np
from analysis import Analysis
from result import Result
from grayScaleImage import GrayScaleImage
from extractor import Extractor
from pathlib import Path

EXCEL_FILE = "Tesi.xlsx"
ROOT_DIR = Path("Root_dir")

class Service:
    def __init__(self, base_folder=None):
        self.logger = Log("API_History.log")
        self.base_folder = Path(base_folder) if base_folder else Path(__file__).resolve().parent

    def get_result(self, patient: str) -> Result:
        excel_path = self.base_folder / EXCEL_FILE
        nrrd_name = Extractor.get_nrrd_from_excel(patient, excel_path)

        if not nrrd_name:
            self.logger.log("warning", f"No .nrrd file found for patient '{patient}' in {excel_path}")
            return Result()

        nrrd_path = self.base_folder / ROOT_DIR / patient / nrrd_name
        if not nrrd_path.exists():
            self.logger.log("error", f"File not found: {nrrd_path}")
            return Result()

        try:
            img = GrayScaleImage(str(nrrd_path))
            image_data = img.get_image()

            if image_data.size == 0:
                raise ValueError("Empty image data.")

            analysis = Analysis(image_data)
            analysis.compare_sequence()

            result = Result(
                meta_keys=list(img.get_meta_data().keys()),
                image_size=(int(image_data.shape[0]), int(image_data.shape[1]), int(image_data.shape[2])),
                Max=int(np.max(image_data)),
                Min=int(np.min(image_data)),
                distances=analysis.get_distances(),
                pixels_presence=img.get_pixels_presence().tolist()
            )

            self.logger.log("info", f"Analysis completed successfully for patient {patient}")
            return result

        except Exception as e:
            self.logger.log("critical", f"Error processing patient '{patient}': {e}")
            return Result()
