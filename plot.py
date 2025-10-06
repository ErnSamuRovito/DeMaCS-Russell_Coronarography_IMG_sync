import matplotlib.pyplot as plt
import sys
from pathlib import Path
import pandas as pd
import numpy as np

class Plot:
    def __init__(self):
        pass

    @staticmethod
    def plot_line(values: np.array, title='plot line'):
        plt.figure(figsize=(8, 5))
        plt.plot(values, linestyle="-", color="blue")
        plt.title(title)
        plt.xlabel("Step")
        plt.ylabel("Distance")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.show()

    @staticmethod
    def plot_histogram(values, title='plot histogram'):
        plt.figure(figsize=(8, 5))
        plt.hist(values, linestyle="-", color="blue")
        plt.title(title)
        plt.xlabel("Step")
        plt.ylabel("Distance")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.show()