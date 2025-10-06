import SimpleITK as sitk
from log import Log
from plot import Plot
import numpy as np

class GrayScaleImage:
    def __init__(self, file_path: str):
        self.logger = Log("log.txt")

        # Carico immagine con SimpleITK
        self._sitk_image = sitk.ReadImage(file_path)
        self.numpy_array = sitk.GetArrayFromImage(self._sitk_image)

        self.size = self._sitk_image.GetSize()
        self.pixel_id = self._sitk_image.GetPixelID()
        self.components = self._sitk_image.GetNumberOfComponentsPerPixel()

        # Metadata
        self.meta_data = {}
        for key in self._sitk_image.GetMetaDataKeys():
            self.meta_data[key] = self._sitk_image.GetMetaData(key)   

    def get_pixels_prensence(self):
        unique, counts = np.unique(self.numpy_array, return_counts=True)

        return counts

    def get_meta_data(self):
        return self.meta_data.keys()
    
    def get_image_size(self):
        return self.get_image_size
    
    def get_min(self):
        return self.numpy_array.min()

    def get_max(self):
        return self.numpy_array.max()

    def get_image(self):
        return self.numpy_array

    def print_info(self):
        self.logger.log("info", f"Pixels dtype: {self.pixel_id}")
        self.logger.log("info", f"Image size: {self.size}")
        self.logger.log("info", f"Max: {self.numpy_array.max()}")
        self.logger.log("info", f"Min: {self.numpy_array.min()}")
        self.logger.log("info", f"Meta keys: {list(self.meta_data.keys())[:5]}")