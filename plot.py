import matplotlib.pyplot as plt
import numpy as np
from analysis import Analysis
from processer import Processer


class Plot:
    def __init__(self):
        self.processer = Processer()

    def plot_line(
            self,
            values,
            output_path: str,
            frequency: int,
            title: str = 'plot_line',
            interactive: bool = True,
    ) -> None:
        self._validate_plot_inputs(values, frequency)

        plt.figure(figsize=(10, 6))
        plt.plot(values, linestyle="-", color="royalblue", linewidth=2, marker='o',
                 markersize=3, alpha=0.7)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel("Step", fontsize=12)
        plt.ylabel("Distance", fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.4)

        max_y = np.max(values)
        for i in range(1, len(values) // frequency + 1):
            x_pos = i * frequency
            plt.axvline(x=x_pos, color='red', linestyle='--', alpha=0.6, linewidth=1.5)
            plt.text(x_pos, max_y * 0.95, f'F{i}', ha='center',
                     fontsize=9, color='red', fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if interactive:
            plt.show()
        plt.close()

    def plot_histogram(self, values: np.ndarray, patient_id: str, title: str = 'plot_histogram'):
        bins = np.arange(len(values))

        plt.figure(figsize=(8, 5))
        plt.bar(bins, values, color="royalblue", alpha=0.8)
        plt.title(title)
        plt.xlabel("Pixel")
        plt.ylabel("Counter")
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig(f"{self.processer.get_processed_folder(patient_id)}/{title}.jpg", dpi=300)
        plt.close()

    def plot_sinusoid(
            self,
            analysis: Analysis,
            patient_id: str,
            peak_index: int = 0,
    ) -> None:
        norme = np.array(analysis.get_distances())

        if norme.size == 0:
            raise ValueError("Analysis contains no distance data")

        spaz = norme.shape[0]
        T = 1.0
        time = np.linspace(0.0, spaz * T, spaz, endpoint=False)

        f, P_norme = analysis.get_spectrum()
        peaks = analysis.get_peaks_norme()

        if peaks is None or len(peaks) == 0:
            print("No peaks found in FFT spectrum")
            return

        if peak_index < 0 or peak_index >= len(peaks):
            raise ValueError(f"Invalid peak index: {peak_index}")

        dominant_freq = float(f[peaks[peak_index]])
        amplitude = float(P_norme[peaks[peak_index]])
        sinusoid = amplitude * np.sin(2 * np.pi * dominant_freq * time)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        ax1.plot(time, norme, color='royalblue', linewidth=1.5, alpha=0.7, label='Original')
        ax1.set_title("Original Distance Signal", fontsize=12, fontweight='bold')
        ax1.set_xlabel("Time (frames)")
        ax1.set_ylabel("Distance")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        ax2.plot(time, sinusoid, color='orange', linewidth=2, label=f'{dominant_freq:.3f} Hz')
        ax2.set_title(f"Dominant Sinusoid Component ({dominant_freq:.3f} Hz)",
                      fontsize=12, fontweight='bold')
        ax2.set_xlabel("Time (frames)")
        ax2.set_ylabel("Amplitude")
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()

        output_path = self.processer.get_folder_to_save_file(patient_id, "Sinusoid")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

    def plot_fft(self, f, P_norme, patient_id: str, title: str):
        if f is None or P_norme is None:
            return None

        P_norme_plot = np.asarray(P_norme)
        if P_norme_plot.size == 0:
            return None

        max_val = float(P_norme_plot.max())
        if max_val > 0:
            P_norme_plot = P_norme_plot / max_val

        plt.figure(figsize=(8, 5))
        plt.plot(f, P_norme_plot, marker='o', linestyle='-')
        plt.xlabel("Periodo [campioni]")
        plt.ylabel("Magnitudo normalizzata")
        plt.title("FFT (asse x = Periodo)")
        plt.grid(True)

        output_path = self.processer.get_folder_to_save_file(patient_id, title, "jpg")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

        return output_path

    @staticmethod
    def _validate_plot_inputs(values, frequency: int) -> None:
        if values is None or len(values) == 0:
            raise ValueError("Values array is empty or invalid")
        if frequency <= 0:
            raise ValueError(f"Frequency must be positive, got {frequency}")
