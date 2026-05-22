import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
from log import Log


class Analysis:
    def __init__(self, img_np: np.ndarray):
        self.distances = []
        self.img_np = img_np
        self.peaks_norme = None
        self.frequency_plot = np.array([])
        self.P_norme_plot = np.array([])
        self.logger = Log("history.log")
        self._spectrum_f = np.array([])
        self._spectrum_P = np.array([])
        self._spectrum_ready = False

    def get_P_normed(self):
        return self.P_norme_plot

    def get_frequency_plot(self):
        return self.frequency_plot

    def get_peaks_norme(self):
        return self.peaks_norme

    def get_distances(self):
        return self.distances

    def get_spectrum(self):
        """Return cached FFT spectrum (f, P) or empty arrays."""
        self._ensure_spectrum()
        return self._spectrum_f, self._spectrum_P

    def compare_sequence(self):
        if self.img_np is None or getattr(self.img_np, "size", 0) == 0:
            self.distances = []
            return

        frames = int(self.img_np.shape[0])
        if frames <= 1:
            self.distances = []
            return

        seq = self.img_np.astype(np.float32, copy=False)
        diff = seq[1:] - seq[:-1]
        distances = np.linalg.norm(diff.reshape(diff.shape[0], -1), axis=1)
        self.distances = distances.tolist()
        self._spectrum_ready = False

    def apply_kalman_filter(self, Q=1e-5, R=0.01):
        distances = np.array(self.distances)
        if distances.size == 0:
            return

        n_iter = len(distances)

        xhat = np.zeros(n_iter)
        P = np.zeros(n_iter)
        xhatminus = np.zeros(n_iter)
        Pminus = np.zeros(n_iter)
        K = np.zeros(n_iter)

        xhat[0] = distances[0]
        P[0] = 1.0

        for k in range(1, n_iter):
            xhatminus[k] = xhat[k - 1]
            Pminus[k] = P[k - 1] + Q
            K[k] = Pminus[k] / (Pminus[k] + R)
            xhat[k] = xhatminus[k] + K[k] * (distances[k] - xhatminus[k])
            P[k] = (1 - K[k]) * Pminus[k]

        self.distances = xhat.tolist()
        self._spectrum_ready = False

    def _ensure_spectrum(self) -> bool:
        if self._spectrum_ready:
            return True

        norme = np.asarray(self.distances, dtype=np.float32)
        if norme.size == 0:
            self.peaks_norme = np.array([], dtype=int)
            self.frequency_plot = np.array([])
            self.P_norme_plot = np.array([])
            self._spectrum_f = np.array([])
            self._spectrum_P = np.array([])
            self._spectrum_ready = True
            return False

        T = 1.0
        spaz = int(norme.shape[0])

        fft_norme = fft(norme)
        f = fftfreq(spaz, T)[: spaz // 2]
        P_norme = (2.0 / spaz) * np.abs(fft_norme[: spaz // 2])

        peaks, _ = find_peaks(P_norme, height=0.01, distance=1)
        self.peaks_norme = peaks
        self._spectrum_f = f
        self._spectrum_P = P_norme

        self.frequency_plot = f[2:]
        self.P_norme_plot = P_norme[2:]
        max_val = float(self.P_norme_plot.max()) if self.P_norme_plot.size else 0.0
        if max_val > 0:
            self.P_norme_plot = self.P_norme_plot / max_val

        if self.peaks_norme.size > 0:
            self.logger.log("info", f"Primo peak: {f[self.peaks_norme[0]]}")

        self._spectrum_ready = True
        return self.peaks_norme.size > 0

    def get_frequency(self, i: int = 0) -> int:
        if not self._ensure_spectrum():
            return 0

        if i < 0 or i >= int(self.peaks_norme.size):
            return 0

        freq_value = float(self._spectrum_f[self.peaks_norme[i]])
        if freq_value == 0.0:
            return 0

        return int(1.0 / freq_value)
