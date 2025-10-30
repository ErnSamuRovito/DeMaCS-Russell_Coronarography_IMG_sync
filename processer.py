from pathlib import Path
from log import Log

ROOT_DIR_PROCESSED = "Root_dir_processed"

class Processer:
    def __init__(self):
        self.logger = Log("history.log")
        self.base_folder = Path(__file__).resolve().parent
        self.processed_path = self.base_folder / ROOT_DIR_PROCESSED

    def get_processed_folder(self, patient_id: str) -> Path:
        patient_dir = self.processed_path / patient_id
        patient_dir.mkdir(parents=True, exist_ok=True)
        return patient_dir

    def get_folder_to_save_file(self, patient_id: str, title: str, extension: str = "jpg") -> Path:
        output_folder = self.get_processed_folder(patient_id)
        output_path = output_folder / f"{title}.{extension}"
        self.logger.log("info", f"Saving output file at: {output_path}")
        return output_path
