import sys
from pathlib import Path
from plot import Plot
from log import Log
from grayScaleImage import GrayScaleImage
from analysis import Analysis
from extractor import Extractor

EXCEL_FILE = "tesi.xlsx"
ROOT_DIR = "Root_dir"

def main():
    logger = Log("history.log")

    base_folder = Path(__file__).resolve().parent.parent
    excel_path = base_folder / EXCEL_FILE

    if not excel_path.exists():
        logger.log("error", f"Excel file not found: {excel_path}")
        sys.exit(1)

    patient = input("Enter patient name (e.g., Paz_001_01): ").strip()
    if not patient:
        logger.log("error", "Patient name cannot be empty")
        sys.exit(1)

    nrrd_name = Extractor.get_nrrd_from_excel(patient, excel_path)
    if not nrrd_name:
        logger.log("warning", f"No .nrrd file found for '{patient}' in Excel file")
        sys.exit(1)

    nrrd_path = base_folder / ROOT_DIR / patient / nrrd_name
    if not nrrd_path.exists():
        logger.log("error", f"File not found: {nrrd_path}")
        sys.exit(1)

    try:        
        img = GrayScaleImage(str(nrrd_path))

        analysis = Analysis(img.get_image())
        analysis.compare_sequence()

        plotter = Plot()
        plotter.plot_line(analysis.get_distances(), patient, "Sequence Comparison Distances")
        plotter.plot_histogram(img.get_pixels_prensence(), patient, "Sequence Comparison Pixels Presence")

        logger.log("info", f"repetition fft = {analysis.get_frequency()}") 
        logger.log("info", f"split = {img.split_slice(analysis.get_frequency())}")

        logger.log("info", f"Len sequence: {len(img.get_image())}")
        logger.log("info", f"Loaded image for patient {patient}: {nrrd_path}")
        img.print_info()

    except Exception as e:
        logger.log("critical", f"Error processing image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
