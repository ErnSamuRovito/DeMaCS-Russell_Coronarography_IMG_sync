import SimpleITK as sitk
import numpy as np
from processer import Processer
from scipy.ndimage import gaussian_filter
from log import Log

class GrayScaleImage:
    def __init__(self, file_path: str):
        self.logger = Log("history.log")

        try:
            self._sitk_image = sitk.ReadImage(file_path)
        except RuntimeError as e:
            raise IOError(f"Cannot read NRRD file: {file_path}") from e

        self.numpy_array = self.get_numpy_array()

        self.size = self._sitk_image.GetSize()
        self.pixel_id = self._sitk_image.GetPixelID()
        self.components = self._sitk_image.GetNumberOfComponentsPerPixel()

        self.meta_data = {
            key: self._sitk_image.GetMetaData(key)
            for key in self._sitk_image.GetMetaDataKeys()
        }

    def get_numpy_array(self):
        numpy_array = sitk.GetArrayFromImage(self._sitk_image)
        return np.clip(numpy_array, 0, 255).astype(np.uint8)

    def get_pixels_presence(self):
        unique, counts = np.unique(self.numpy_array, return_counts=True)
        return counts

    def get_gaussian_filter(self, image: np.ndarray, sigma: float) -> np.ndarray:
        return gaussian_filter(image, sigma)

    def get_meta_data(self):
        return self.meta_data

    def get_image_size(self):
        return self.size

    def get_min(self):
        return self.numpy_array.min()

    def get_max(self):
        return self.numpy_array.max()

    def get_image(self):
        return self.numpy_array

    def split_slice(self, split: int):
        if split <= 0:
            raise ValueError("Split must be > 0.")
        return np.array_split(self.numpy_array, split)

    def save_subarrays_as_nrrd(self, id_patient: str, subarrays: list):
        processer = Processer()
        output_folder = processer.get_processed_folder(id_patient)

        for i, subarray in enumerate(subarrays):
            sub_image = sitk.GetImageFromArray(subarray)

            sub_image.SetSpacing(self._sitk_image.GetSpacing())
            sub_image.SetOrigin(self._sitk_image.GetOrigin())
            sub_image.SetDirection(self._sitk_image.GetDirection())

            output_path = output_folder / f"heartbeat_{id_patient}_{i + 1}.nrrd"
            sitk.WriteImage(sub_image, str(output_path))
            print(f"[INFO] Saved subarray {i + 1}/{len(subarrays)} → {output_path}")

    def print_info(self):
        self.logger.log("info", f"Type : {self.numpy_array.dtype}")
        self.logger.log("info", f"Pixels dtype: {self.pixel_id}")
        self.logger.log("info", f"Image size: {self.size}")
        self.logger.log("info", f"Max: {self.numpy_array.max()}, Min: {self.numpy_array.min()}")
        self.logger.log("info", f"Numpy shape: {self.numpy_array.shape}")
        self.logger.log("info", f"Meta keys: {list(self.meta_data.keys())[:5]}")
