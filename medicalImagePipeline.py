import sys

from pathlib import Path
from plot import Plot
from processer import Processer
from log import Log
from grayScaleImage import GrayScaleImage
from analysis import Analysis
from extractor import Extractor
from paths import validate_patient_id, resolve_patient_nrrd
from typing import Optional

EXCEL_FILE = "Tesi.xlsx"
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


class MedicalImagePipeline:
    def __init__(self, base_folder: Path):
        self.base_folder = base_folder
        self.logger = Log("history.log")
        self.processer = Processer()
        self.plotter = Plot()
        self.excel_path = base_folder / EXCEL_FILE
        self.patient = None
        self.nrrd_path = None

    def run(self) -> None:
        try:
            self._validate_excel_file()

            self.patient, self.nrrd_path = self._resolve_inputs()

            img = self._load_image(self.nrrd_path, self.patient)
            analysis = _perform_analysis(img)

            if self._should_apply_kalman():
                analysis.apply_kalman_filter()

            self._plot_histogram(img, self.patient)

            self.plotter.plot_fft(
                analysis.get_frequency_plot(),
                analysis.get_P_normed(),
                self.patient,
                "FFT",
            )

            validated_index = self._validate_peaks(analysis, self.patient)
            if validated_index is None:
                self.logger.log("warning", "No valid plot was confirmed. Exiting.")
                sys.exit(0)

            frequency = self._validate_frequency(analysis.get_frequency(validated_index))
            subdivision = self._calculate_subdivision(len(img.get_image()), frequency)
            heartrate_splitted = img.split_slice(subdivision)

            self._plot_sinusoid(analysis, self.patient, validated_index)
            self._save_results(img, self.patient, frequency, heartrate_splitted)

        except KeyboardInterrupt:
            self.logger.log("info", "Process interrupted by user.")
            sys.exit(0)
        except Exception as e:
            self.logger.log("critical", f"Unexpected error in pipeline: {e}")
            sys.exit(1)

    def _is_batch_mode(self) -> bool:
        args = [a.lower() for a in sys.argv[1:]]
        return "--batch" in args or "--no-show" in args

    def _resolve_inputs(self) -> tuple[str, Path]:
        """
        Supported invocations:
        - python main.py <patient_id>
        - python main.py <file.nrrd> <patient_id>
        """
        if len(sys.argv) >= 3 and str(sys.argv[1]).lower().endswith(".nrrd"):
            patient = validate_patient_id(str(sys.argv[2]))
            return patient, self._get_nrrd_path_from_terminal(sys.argv[1])

        patient = self._get_patient_name()
        return patient, self._get_nrrd_path(patient)

    def _should_apply_kalman(self) -> bool:
        args = [a.lower() for a in sys.argv[1:]]
        return "--kilman-filtering" in args or "--kalman-filtering" in args

    def _get_nrrd_path_from_terminal(self, nrrd_arg: str) -> Path:
        self.logger.log("info", "Inserted a .nrrd file")
        return Path(nrrd_arg)

    def _get_patient_name(self) -> str:
        if len(sys.argv) >= 2 and sys.argv[1].strip() and not sys.argv[1].startswith("-"):
            return validate_patient_id(sys.argv[1])

        while True:
            patient = input("Enter patient name (e.g., Paz_001_01): ").strip()
            if patient:
                return validate_patient_id(patient)
            print("Patient name cannot be empty. Please try again.")

    def _validate_excel_file(self) -> None:
        if not self.excel_path.exists():
            self.logger.log("error", f"Excel file not found: {self.excel_path}")
            sys.exit(1)

    def _get_nrrd_path(self, patient: str) -> Path:
        patient = validate_patient_id(patient)
        nrrd_name = Extractor.get_nrrd_from_excel(patient, self.excel_path)

        if not nrrd_name:
            self.logger.log("warning", f"No .nrrd file found for '{patient}' in Excel.")
            sys.exit(1)

        try:
            nrrd_path = resolve_patient_nrrd(self.base_folder, patient, nrrd_name)
        except ValueError as e:
            self.logger.log("error", str(e))
            sys.exit(1)

        if not nrrd_path.exists():
            self.logger.log("error", f"File not found: {nrrd_path}")
            sys.exit(1)

        return nrrd_path

    def _load_image(self, nrrd_path: Path, patient: str) -> GrayScaleImage:
        try:
            img = GrayScaleImage(str(nrrd_path))
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
            "Sequence Comparison Pixels Presence",
        )

    def _validate_peaks(self, analysis: Analysis, patient: str) -> Optional[int]:
        peaks = analysis.get_peaks_norme()
        self.logger.log("info", f"Number of peaks detected: {len(peaks)}")

        max_iterations = min(len(peaks), MAX_PLOT_RETRIES)
        interactive = not self._is_batch_mode()

        for i in range(max_iterations):
            peak_frequency = analysis.get_frequency(i)
            if peak_frequency <= 0:
                self.logger.log("debug", f"Skipping peak {i + 1}: invalid frequency")
                continue

            output_path = str(
                self.processer.get_folder_to_save_file(
                    patient,
                    f"sequence_distances_{i + 1}",
                    "jpg",
                )
            )
            self.plotter.plot_line(
                analysis.get_distances(),
                output_path,
                peak_frequency,
                f"Sequence Comparison Distances {i + 1}",
                interactive=interactive,
            )

            answer = _get_validation_input(i + 1, max_iterations)

            if answer == USER_CONFIRM_YES:
                self.logger.log("info", f"Plot validated: {output_path}")
                return i

        return None

    def _plot_sinusoid(self, analysis: Analysis, patient: str, peak_index: int) -> None:
        try:
            self.plotter.plot_sinusoid(analysis, patient, peak_index)
        except Exception as e:
            self.logger.log("error", f"Failed to plot sinusoid: {e}")

    def _save_results(
            self,
            img: GrayScaleImage,
            patient: str,
            frequency: int,
            heartrate_splitted: list,
    ) -> None:
        self.logger.log("info", f"Repetition FFT = {frequency}")
        self.logger.log("info", f"Sequence length: {len(img.get_image())}")

        try:
            img.save_subarrays_as_nrrd(patient, heartrate_splitted)
            self.logger.log("info", f"Subarrays saved for patient {patient}.")
        except Exception as e:
            self.logger.log("error", f"Failed to save subarrays: {e}")
