import matplotlib.pyplot as plt
import numpy as np

from climate import DAYS_PER_YEAR, MONTH_NAMES
from params import MOSS_DIE_BELOW, MOSS_GROW_ABOVE


class LiveView:
    def __init__(self, dampness, moss, soil, porosity):
        self.fig, axs = plt.subplots(2, 2, figsize=(10, 9))
        self.img_damp = axs[0, 0].imshow(dampness, cmap="Blues", vmin=0, vmax=1)
        self.img_moss = axs[0, 1].imshow(moss, cmap="Greens", vmin=0, vmax=1)
        self.img_soil = axs[1, 0].imshow(soil, cmap="Oranges", vmin=0, vmax=1)
        axs[1, 1].imshow(porosity, cmap="Greys", vmin=0, vmax=1)
        axs[0, 0].set_title("Dampness")
        axs[0, 1].set_title("Moss")
        axs[1, 0].set_title("Soil")
        axs[1, 1].set_title("Porosity of the bare wall (dark = holds water)")

    def update(self, t, dampness, moss, soil):
        self.img_damp.set_data(dampness)
        self.img_moss.set_data(moss)
        self.img_soil.set_data(soil)
        month = MONTH_NAMES[int((t % DAYS_PER_YEAR) / DAYS_PER_YEAR * 12)]
        self.fig.suptitle(f"Year {t // DAYS_PER_YEAR + 1}, {month}")
        plt.pause(0.0001)


# Plot the history
def plotHistory(history, n_days):
    years = np.arange(n_days) / DAYS_PER_YEAR
    _fig2, axes = plt.subplots(3, 1, figsize=(11, 11), sharex=True)
    axes[0].plot(years, history["rain"], lw=0.6)
    axes[0].set_ylabel("rain / day")
    axes[1].plot(years, history["mean_dampness"], lw=0.7)
    axes[1].set_ylabel("mean dampness")
    axes[2].plot(years, history["temp"], lw=0.8, color="purple")
    axes[2].plot(years, history["tmin"], lw=0.5, color="green")
    axes[2].plot(years, history["tmax"], lw=0.5, color="red")
    axes[2].set_ylabel("temperature")
    axes[2].set_xlabel("years")
    #axes[2].plot(years, history["mean_memory"])
    #axes[2].axhline(MOSS_GROW_ABOVE, color="g", ls="--", lw=0.8, label="moss grows above")
    #axes[2].axhline(MOSS_DIE_BELOW, color="r", ls="--", lw=0.8, label="moss dies below")
    #axes[2].set_ylabel("mean damp memory")
    #axes[2].legend(loc="upper right", fontsize=8)
    #axes[3].plot(years, history["moss_coverage"], color="green")
    #axes[3].set_ylabel("moss coverage")
    #axes[4].plot(years, history["mean_soil"], color="saddlebrown")
    #axes[4].set_ylabel("mean soil")
    #axes[4].set_xlabel("years")
    plt.tight_layout()
    plt.show()
