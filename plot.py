import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from processer import Processer


class Plot:
    def __init__(self):
        self.processer = Processer()

    def plot_line(self, values: np.ndarray, patient_id: str, title: str = 'plot_line'):
        plt.figure(figsize=(8, 5))
        plt.plot(values, linestyle="-", color="royalblue", linewidth=2)
        plt.title(title)
        plt.xlabel("Step")
        plt.ylabel("Distance")
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig(f"{self.processer.get_processed_folder(patient_id)}/{title}.jpg", dpi=300)

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

        plt.show()
        plt.close()
