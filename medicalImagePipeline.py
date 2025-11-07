import sys

from pathlib import Path
from plot import Plot
from processer import Processer
from log import Log
from grayScaleImage import GrayScaleImage
from analysis import Analysis
from extractor import Extractor
from typing import Optional

EXCEL_FILE = "Tesi.xlsx"
ROOT_DIR = "Root_dir"
MIN_VALID_FREQUENCY = 1
MAX_PLOT_RETRIES = 10

USER_CONFIRM_YES = "y"
USER_CONFIRM_NO = "n"
VALID_RESPONSES = {USER_CONFIRM_YES, USER_CONFIRM_NO}


def _perform_analysis(img: GrayScaleImage) -> Analysis:
    analysis = Analysis(img.get_image())
    analysis.compare_sequence()
    return analysis


def _get_validation_input(current: int, total: int) -> str:
    while True:
        response = input(
            f"[{current}/{total}] Is this valid? (y/n): "
        ).strip().lower()

        if response in VALID_RESPONSES:
            return response

        print(f"Invalid input. Please enter '{USER_CONFIRM_YES}' or '{USER_CONFIRM_NO}'.")


def _get_patient_name() -> str:
    if len(sys.argv) != 0:
        return sys.argv[1]
    else:
        while True:
            patient = input("Enter patient name (e.g., Paz_001_01): ").strip()
            if patient:
                return patient
            print("Patient name cannot be empty. Please try again.")


class MedicalImagePipeline:
    def __init__(self, base_folder: Path):
        self.base_folder = base_folder
        self.logger = Log("history.log")
        self.processer = Processer()
        self.plotter = Plot()
        self.excel_path = base_folder / EXCEL_FILE

    def run(self) -> None:
        try:
            self._validate_excel_file()
            patient = _get_patient_name()
            nrrd_path = self._get_nrrd_path(patient)

            img = self._load_image(nrrd_path, patient)
            analysis = _perform_analysis(img)

            frequency = self._validate_frequency(analysis.get_frequency())
            subdivision = self._calculate_subdivision(len(img.get_image()), frequency)

            heartrate_splitted = img.split_slice(subdivision)

            self._plot_histogram(img, patient)
            # validated_index = self._validate_peaks(analysis, patient, frequency)

            self.plotter.plot_fft(
                analysis.get_frequency_plot(),
                analysis.get_P_normed(),
                patient,
                "FFT"
            )

            # if validated_index is not None:
            self._plot_sinusoid(analysis, patient)
            self._save_results(img, patient, frequency, heartrate_splitted)
            #else:
            #    self.logger.log("warning", "No valid plot was confirmed. Exiting.")

        except KeyboardInterrupt:
            self.logger.log("info", "Process interrupted by user.")
            sys.exit(0)
        except Exception as e:
            self.logger.log("critical", f"Unexpected error in pipeline: {e}")
            sys.exit(1)

    def _validate_excel_file(self) -> None:
        if not self.excel_path.exists():
            self.logger.log("error", f"Excel file not found: {self.excel_path}")
            sys.exit(1)

    def _get_nrrd_path(self, patient: str) -> Path:
        nrrd_name = Extractor.get_nrrd_from_excel(patient, self.excel_path)

        if not nrrd_name:
            self.logger.log("warning", f"No .nrrd file found for '{patient}' in Excel.")
            sys.exit(1)

        nrrd_path = self.base_folder / ROOT_DIR / patient / nrrd_name

        if not nrrd_path.exists():
            self.logger.log("error", f"File not found: {nrrd_path}")
            sys.exit(1)

        return nrrd_path

    def _load_image(self, nrrd_path: Path, patient: str) -> GrayScaleImage:
        try:
            img = GrayScaleImage(str(nrrd_path))
            img.get_gaussian_filter(img.get_image(), 2)
            self.logger.log("info", f"Loaded image for {patient}: {nrrd_path}")
            return img
        except Exception as e:
            self.logger.log("critical", f"Failed to load image: {e}")
            sys.exit(1)

    def _validate_frequency(self, frequency: float) -> int:
        if frequency < MIN_VALID_FREQUENCY:
            self.logger.log("error", f"Invalid frequency: {frequency}")
            sys.exit(1)
        return int(frequency)

    def _calculate_subdivision(self, image_length: int, frequency: int) -> int:
        if frequency == 0:
            self.logger.log("error", "Cannot divide by zero frequency")
            sys.exit(1)

        subdivision = image_length // frequency
        self.logger.log("debug", f"Subdivision: {subdivision}")
        return subdivision

    def _plot_histogram(self, img: GrayScaleImage, patient: str) -> None:
        self.plotter.plot_histogram(
            img.get_pixels_presence(),
            patient,
            "Sequence Comparison Pixels Presence"
        )

    def _validate_peaks(
            self,
            analysis: Analysis,
            patient: str,
            frequency: int
    ) -> Optional[int]:
        peaks = analysis.get_peaks_norme()
        self.logger.log("info", f"Number of peaks detected: {len(peaks)}")

        max_iterations = min(len(peaks), MAX_PLOT_RETRIES)

        for i in range(max_iterations):
            self.plotter.plot_line(
                analysis.get_distances(),
                patient,
                analysis.get_frequency(i),
                f"Sequence Comparison Distances {i + 1}"
            )

            answer = _get_validation_input(i + 1, frequency + 1)

            if answer == USER_CONFIRM_YES:
                output_path = self.processer.get_folder_to_save_file(
                    patient,
                    f"validated_plot_{i + 1}"
                )
                self.logger.log("info", f"Plot validated: {output_path}")
                return i

        return None

    def _plot_sinusoid(self, analysis: Analysis, patient: str) -> None:
        try:
            self.plotter.plot_sinusoid(analysis, patient)
        except Exception as e:
            self.logger.log("error", f"Failed to plot sinusoid: {e}")

    def _save_results(
            self,
            img: GrayScaleImage,
            patient: str,
            frequency: int,
            heartrate_splitted: list
    ) -> None:
        self.logger.log("info", f"Repetition FFT = {frequency}")
        self.logger.log("info", f"Sequence length: {len(img.get_image())}")

        try:
            img.save_subarrays_as_nrrd(patient, heartrate_splitted)
            self.logger.log("info", f"Subarrays saved for patient {patient}.")
        except Exception as e:
            self.logger.log("error", f"Failed to save subarrays: {e}")