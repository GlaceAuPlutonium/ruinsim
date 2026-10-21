import numpy as np

from climate import DAYS_PER_YEAR, genClimate, spellLengths
from model import damp_memory, dampness, moss, porosity, rng_ph, rng_weather, soil, step
from render import LiveView, plotHistory

YEARS = 20

n_days = DAYS_PER_YEAR * YEARS
rain, pH = genClimate(n_days, rng_weather, rng_ph)

wet, dry = spellLengths(rain > 0)
print(f"Rainy days per year: {(rain > 0).sum() / YEARS:.1f}")
print(f"Wet spells: mean {np.mean(wet):.1f} days, longest {max(wet)}")
print(f"Dry spells: mean {np.mean(dry):.1f} days, longest {max(dry)}")

history = {
    "rain": np.zeros(n_days),
    "mean_dampness": np.zeros(n_days),
    "ph": pH.copy(),
    #"mean_memory": np.zeros(n_days),
    #"moss_coverage": np.zeros(n_days),
    #"mean_soil": np.zeros(n_days),
}

view = LiveView(dampness, moss, soil, porosity)

for t in range(n_days):
    dampness, damp_memory, moss, soil = step(rain[t], dampness, damp_memory, moss, soil)

    history["rain"][t] = rain[t]
    history["mean_dampness"][t] = dampness.mean()
    history["ph"][t] = pH[t]
    #history["mean_memory"][t] = damp_memory.mean()
    #history["moss_coverage"][t] = moss.mean()
    #history["mean_soil"][t] = soil.mean()

    if t % 360 == 0:
        view.update(t, dampness, moss, soil)

np.savez("history.npz", **history) # type: ignore

plotHistory(history, n_days)
