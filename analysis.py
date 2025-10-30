import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
from log import Log

def _calculate_spatial_distance(image1, image2):
    return np.linalg.norm(image1 - image2)

class Analysis:
    def __init__(self, img_np: np.ndarray):
        self.distances = []
        self.img_np = img_np
        self.peaks_norme = None
        self.frequency_plot = np.array([])
        self.P_norme_plot = np.array([])
        self.logger = Log("history.log")

    def get_P_normed(self):
        return self.P_norme_plot

    def get_frequency_plot(self):
        return self.frequency_plot

    def get_peaks_norme(self):
        return self.peaks_norme

    def get_distances(self):
        return self.distances

    def compare_sequence(self):
        initial_image = self.img_np[0, :, :]

        for i in range(1, self.img_np.shape[0]):
            distance = _calculate_spatial_distance(initial_image, self.img_np[i, :, :])
            self.distances.append(distance)

    def get_frequency(self, i: int = 0):
        norme = np.array(self.get_distances())
        if norme.size == 0:
            return 0

        T = 1.0
        spaz = norme.shape[0]

        # FFT
        fft_norme = fft(norme)
        f = fftfreq(spaz, T)[:spaz // 2]
        P_norme = 2.0 / spaz * np.abs(fft_norme[0:spaz // 2])

        # Trova picchi significativi
        self.peaks_norme, _ = find_peaks(P_norme, height=0.01, distance=1)

        if self.peaks_norme.size == 0:
            return 0

        freq_value = f[self.peaks_norme[i]]

        self.logger.log("info", f"Primo peak: {f[self.peaks_norme[0]]}")

        if freq_value == 0:
            return 0

        ripetizione = int(1.0 / freq_value)

        # magnitude = np.abs(fft_norme[:spaz // 2])

        # Normalizzazione a 1
        #if magnitude.max() > 0:
        #    magnitude /= magnitude.max()

        # Calcolo periodi (1/f), evitando divisione per zero
        with np.errstate(divide='ignore'):
            periods = np.where(f > 0, 1.0 / f, np.inf)

        self.frequency_plot = f[2:]
        self.P_norme_plot = P_norme[2:]
        periods_plot = 1.0 / self.frequency_plot
        rev_periods_plot = np.flip(periods_plot)

        self.P_norme_plot = self.P_norme_plot/self.P_norme_plot.max()

        # Plot
        # plt.figure(figsize=(8, 5))
        # plt.plot(frequency_plot, P_norme_plot, marker='o', linestyle='-')
        # plt.xlabel("Periodo [campioni]")
        # plt.ylabel("Magnitudo normalizzata")
        # plt.title("FFT (asse x = Periodo)")
        # plt.grid(True)
        # plt.show()

        return ripetizione
