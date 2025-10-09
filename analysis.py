import SimpleITK as sitk
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

class Analysis:
    def __init__(self, img_np):
        self.distances = []
        self.img_np = img_np 

    def get_distances(self):
        return self.distances

    def compare_sequence(self):
        initial_image = self.img_np[0,:,:]

        for i in range(1, self.img_np.shape[0]):
            self.distances.append(
                self.calculate_spatial_distance(initial_image, self.img_np[i,:,:])
            )

    def calculate_spatial_distance(self, image1, image2):
        return np.linalg.norm(image1 - image2)

    def get_frequency(self):
        norme = np.array(self.get_distances())
        
        T = 1
        spaz = norme.shape[0]
        time = np.linspace(0.0, spaz*T, spaz, endpoint=False)
        fft_norme = fft(norme)
        f = fftfreq(spaz, T)[:spaz//2]
        # Calcolo il modulo dei coefficienti complessi della trasformata
        P_norme = 2.0/spaz * np.abs(fft_norme[0:spaz//2])
        peaks_norme, _ = find_peaks(P_norme, height=0.01, distance=1)
        ripetizione =  int(1.0/f[peaks_norme[0]])
        return ripetizione