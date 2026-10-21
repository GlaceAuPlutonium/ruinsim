import numpy as np

from climate import DAYS_PER_YEAR, genClimate, spellLengths
from model import damp_memory, dampness, moss, porosity, rng_weather, soil, step
from render import LiveView, plotHistory

YEARS = 80

n_days = DAYS_PER_YEAR * YEARS
weather = genClimate(n_days, rng_weather)

wet, dry = spellLengths(weather > 0)
print(f"Rainy days per year: {(weather > 0).sum() / YEARS:.1f}")
print(f"Wet spells: mean {np.mean(wet):.1f} days, longest {max(wet)}")
print(f"Dry spells: mean {np.mean(dry):.1f} days, longest {max(dry)}")

history = {
    "rain": np.zeros(n_days),
    "mean_dampness": np.zeros(n_days),
    "mean_memory": np.zeros(n_days),
    "moss_coverage": np.zeros(n_days),
    "mean_soil": np.zeros(n_days),
}

view = LiveView(dampness, moss, soil, porosity)

for t in range(n_days):
    dampness, damp_memory, moss, soil = step(weather[t], dampness, damp_memory, moss, soil)

    history["rain"][t] = weather[t]
    history["mean_dampness"][t] = dampness.mean()
    history["mean_memory"][t] = damp_memory.mean()
    history["moss_coverage"][t] = moss.mean()
    history["mean_soil"][t] = soil.mean()

    if t % 360 == 0:
        view.update(t, dampness, moss, soil)

np.savez("history.npz", **history) # type: ignore

plotHistory(history, n_days)
