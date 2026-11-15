import matplotlib.pyplot as plt
import numpy as np

from climate import DAYS_PER_YEAR, MONTH_NAMES


class LiveView:
    def __init__(self, water, moss, soil, shape):
        self.fig, axs = plt.subplots(2, 2, figsize=(10, 9))
        self.img_damp = axs[0, 0].imshow(water, cmap="Blues", vmin=0, vmax=1)
        self.img_moss = axs[0, 1].imshow(moss, cmap="Greens", vmin=0, vmax=1)
        self.img_soil = axs[1, 0].imshow(soil, cmap="Oranges", vmin=0, vmax=1)
        axs[1, 1].imshow(shape, cmap="Greys", vmin=0, vmax=1)
        axs[0, 0].set_title("Water")
        axs[0, 1].set_title("Moss")
        axs[1, 0].set_title("Soil")
        axs[1, 1].set_title("Porosity of the bare wall (dark = holds water)")

    def update(self, t, water, moss, soil):
        self.img_damp.set_data(water)
        self.img_moss.set_data(moss)
        self.img_soil.set_data(soil)
        month = MONTH_NAMES[int((t % DAYS_PER_YEAR) / DAYS_PER_YEAR * 12)]
        self.fig.suptitle(f"Year {t // DAYS_PER_YEAR + 1}, {month}")
        plt.pause(0.0001)


# Plot the history
def plotHistory(history, n_days):
    years = np.arange(n_days) / DAYS_PER_YEAR
    _fig2, axes = plt.subplots(4, 1, figsize=(11, 11), sharex=True)
    axes[0].plot(years, history["rain"], lw=0.6)
    axes[0].set_ylabel("rain / day")
    axes[1].plot(years, history["temp"], lw=0.8, color="purple")
    axes[1].plot(years, history["tmin"], lw=0.5, color="green")
    axes[1].plot(years, history["tmax"], lw=0.5, color="red")
    axes[1].set_ylabel("temperature")
    axes[2].plot(years, history["moss"], lw=0.8, color="tab:orange")
    axes[2].set_ylabel("Average moss coverage")
    axes[3].plot(years, history["soil"], lw=0.8, color="brown")
    axes[3].set_ylabel("Average soil coverage")
    #axes[3].plot(years, history["sat"], lw=0.8, color="lime")
    #axes[3].set_ylabel("mean satuartion")
    #axes[4].plot(years, history["water"], lw=0.8, color="blue")
    #axes[4].set_ylabel("water")
    #axes[5].plot(years, history["mem"], lw=0.8, color="blue")
    #axes[5].set_ylabel("water memory")
    axes[3].set_xlabel("years")
    plt.tight_layout()
    plt.show()
