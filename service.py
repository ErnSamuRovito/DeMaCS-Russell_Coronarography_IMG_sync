import SimpleITK as sitk
from log import Log
from plot import Plot
import numpy as np
from analysis import Analysis
from result import Result
from grayScaleImage import GrayScaleImage
from extractor import Extractor
from pathlib import Path

EXCEL_FILE = "tesi.xlsx"
ROOT_DIR = "Root_dir"


class Service:
    def __init__(self, base_folder=None):
        self.logger = Log("API_History.log")
        self.base_folder = Path(base_folder) if base_folder else Path(__file__).resolve().parent.parent

    def get_result(self, patient: str) -> Result:

        excel_path = self.base_folder / EXCEL_FILE
        nrrd_name = Extractor.get_nrrd_from_excel(patient, excel_path)

        if not nrrd_name:
            self.logger.log("warning", f"No .nrrd file found for '{patient}'")
            return Result()

        nrrd_path = self.base_folder / ROOT_DIR / patient / nrrd_name
        if not nrrd_path.exists():
            self.logger.log("error", f"File not found: {nrrd_path}")
            return Result()

        try:
            img = GrayScaleImage(str(nrrd_path))

            analysis = Analysis(img.get_image())
            analysis.compare_sequence()

            result = Result(
                meta_keys=img.get_meta_data(),
                image_size=tuple(img.get_image().shape),
                Max=int(np.max(img.get_image())),
                Min=int(np.min(img.get_image())),
                distances=analysis.get_distances(),
                pixels_presence=img.get_pixels_prensence().tolist()
            )

            self.logger.log("info", f"Analysis completed for {patient}")
            return result

        except Exception as e:
            self.logger.log("critical", f"Error processing patient {patient}: {e}")
            return Result()
