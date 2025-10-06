import SimpleITK as sitk
import numpy as np


class Analysis:
    def __init__(self, img_np):
        self.distances = []
        self.img_np = img_np 

    def get_distances(self):
        return self.distances

    def compare_sequence(self):
        initial_image = self.img_np[:,:,0]

        for i in range(self.img_np.shape[2]):
            self.distances.append(
                self.calculate_spatial_distance(initial_image, self.img_np[:,:,i])
            )

    def calculate_spatial_distance(self, image1, image2):
        return np.linalg.norm(image1 - image2)
