import logging
from pathlib import Path
import slicer
from slicer.ScriptedLoadableModule import *

from extractor import Extractor
from analysis import Analysis
from grayScaleImage import GrayScaleImage


#
# Russell
#

class Russell(ScriptedLoadableModule):
    """Defines the module metadata."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.title = "Russell"
        self.parent.categories = ["Cardiology"]
        self.parent.contributors = ["Ernesto Samuele Rovito (Università della Calabria)"]
        self.parent.helpText = "Custom 3D Slicer module for image extraction and analysis."
        self.parent.acknowledgementText = "Developed for research and testing."

        pip_install = slicer.util.pip_install

        pip_install("SimpleITK")
        pip_install("numpy")
        pip_install("scipy")
        pip_install("pandas")
        pip_install("openpyxl")

#
# RussellWidget
#

class RussellWidget(ScriptedLoadableModuleWidget):

    def __init__(self):
        self.ui = None

    def setup(self):
        super().setup()

        uiWidget = slicer.util.loadUI(self.resourcePath('Russell.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        self.ui.outputSelector.setMRMLScene(slicer.mrmlScene)

        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

    # -------------------------

    def onApplyButton(self):
        try:
            outputVolume = self.ui.outputSelector.currentNode()
            if not outputVolume:
                slicer.util.errorDisplay("Select output volume")
                return

            id_patient = self.ui.id_patient_textbox.text().strip()
            output_folder = self.ui.output_folder_textbox.text().strip()
            excel_folder = self.ui.Excel_folder_textbox.text().strip()  # FIX

            if not id_patient or not output_folder or not excel_folder:
                slicer.util.errorDisplay("Fill all fields")
                return

            logic = RussellLogic()
            result = logic.run(id_patient, output_folder, excel_folder)

            slicer.util.infoDisplay(f"Done. Frequency: {result['frequency']}")

        except Exception as e:
            slicer.util.errorDisplay(str(e))
            logging.exception(e)


#
# RussellLogic
#

class RussellLogic(ScriptedLoadableModuleLogic):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("RussellLogic")

    # -------------------------

    def run(self, id_patient: str, output_folder: str, excel_folder: str):

        base_folder = Path(__file__).resolve().parent
        excel_path = Path(excel_folder)
        output_path = Path(output_folder)

        output_path.mkdir(parents=True, exist_ok=True)

        # 1. get NRRD from Excel
        nrrd_name = Extractor.get_nrrd_from_excel(id_patient, excel_path)

        if not nrrd_name:
            raise ValueError(f"No NRRD for patient {id_patient}")

        nrrd_path = base_folder / nrrd_name

        if not nrrd_path.exists():
            raise FileNotFoundError(str(nrrd_path))

        # 2. load image
        img = GrayScaleImage(str(nrrd_path))
        image = img.get_image()

        if image.size == 0:
            raise ValueError("Empty image")

        # 3. analysis
        analysis = Analysis(image)
        analysis.compare_sequence()

        # 4. compute features
        frequency = getattr(analysis, "get_frequency", lambda: 1)()
        subdivision = max(1, len(image) // frequency)

        slices = img.split_slice(subdivision)

        # 5. save results (opzionale)
        result = {
            "patient": id_patient,
            "frequency": frequency,
            "subdivision": subdivision,
            "num_slices": len(slices),
        }

        self.logger.info(f"Completed for {id_patient}")

        return result
