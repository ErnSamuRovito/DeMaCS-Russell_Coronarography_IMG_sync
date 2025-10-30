from pathlib import Path
from medicalImagePipeline import MedicalImagePipeline

def main() -> None:
    base_folder = Path(__file__).resolve().parent
    pipeline = MedicalImagePipeline(base_folder)
    pipeline.run()

if __name__ == "__main__":
    main()
