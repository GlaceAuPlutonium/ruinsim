import numpy as np

from climate import DAYS_PER_YEAR, genClimate, spellLengths
from model import damp_memory, dampness, moss, porosity, rng_ph, rng_weather, rng_temp, rng_dtr, rng_hum, soil, step
from render import LiveView, plotHistory

YEARS = 20

n_days = DAYS_PER_YEAR * YEARS
rain, pH, temp, tmin, tmax, humidity = genClimate(n_days, rng_weather, rng_ph, rng_temp, rng_dtr, rng_hum)

wet, dry = spellLengths(rain > 0)
print(f"Rainy days per year: {(rain > 0).sum() / YEARS:.1f}")
print(f"Wet spells: mean {np.mean(wet):.1f} days, longest {max(wet)}")
print(f"Dry spells: mean {np.mean(dry):.1f} days, longest {max(dry)}")

print(f"Frost nights/year (tmin<0): {(tmin < 0).sum() / YEARS:.1f}")
print(f"Freeze-thaw days/year (tmin<0<tmax): {((tmin < 0) & (tmax > 0)).sum() / YEARS:.1f}")
print(f"Mean tmin {tmin.mean():.1f}, tmax {tmax.mean():.1f}, tmean {temp.mean():.1f}")

history = {
    "rain": np.zeros(n_days),
    #"mean_dampness": np.zeros(n_days),
    "temp": np.zeros(n_days),
    "tmin": np.zeros(n_days),
    "tmax": np.zeros(n_days),
    "humidity": np.zeros(n_days),
    "pH": np.zeros(n_days)
    #"mean_memory": np.zeros(n_days),
    #"moss_coverage": np.zeros(n_days),
    #"mean_soil": np.zeros(n_days),
}

#view = LiveView(dampness, moss, soil, porosity)

for t in range(n_days):
    dampness, damp_memory, moss, soil = step(rain[t], dampness, damp_memory, moss, soil)

    history["rain"][t] = rain[t]
    #history["mean_dampness"][t] = dampness.mean()
    history["temp"][t] = temp[t]
    history["tmin"][t] = tmin[t]
    history["tmax"][t] = tmax[t]
    history["humidity"][t] = humidity[t]
    history["pH"][t] = pH[t]
    #history["mean_memory"][t] = damp_memory.mean()
    #history["moss_coverage"][t] = moss.mean()
    #history["mean_soil"][t] = soil.mean()

    #if t % 360 == 0:
     #   view.update(t, dampness, moss, soil)

np.savez("history.npz", **history) # type: ignore

plotHistory(history, n_days)
