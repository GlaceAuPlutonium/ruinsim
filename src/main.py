import numpy as np

from climate import DAYS_PER_YEAR, genClimate, spellLengths
from model import damp_memory, dampness, moss, porosity, rng_ph, rng_weather, rng_temp, rng_dtr, rng_hum, rng_sun, rng_ws, soil, step
from render import LiveView, plotHistory

YEARS = 8

n_days = DAYS_PER_YEAR * YEARS
rain, pH, temp, tmin, tmax, humidity, ghi, ws, wd = genClimate(n_days, rng_weather, rng_ph, rng_temp, rng_dtr, rng_hum, rng_sun, rng_ws)

wet, dry = spellLengths(rain > 0)
print(f"Rainy days per year: {(rain > 0).sum() / YEARS:.1f}")
print(f"Wet spells: mean {np.mean(wet):.1f} days, longest {max(wet)}")
print(f"Dry spells: mean {np.mean(dry):.1f} days, longest {max(dry)}")

print(f"Frost nights/year (tmin<0): {(tmin < 0).sum() / YEARS:.1f}")
print(f"Freeze-thaw days/year (tmin<0<tmax): {((tmin < 0) & (tmax > 0)).sum() / YEARS:.1f}")
print(f"Mean tmin {tmin.mean():.1f}, tmax {tmax.mean():.1f}, tmean {temp.mean():.1f}")

print(np.corrcoef(np.log(ws[:-1]), np.log(ws[1:])))

history = {
    "rain": rain,
    "temp": temp,
    "tmin": tmin,
    "tmax": tmax,
    "ws": ws,
    "wd": wd
}

#view = LiveView(dampness, moss, soil, porosity)

#for t in range(n_days):
    #dampness, damp_memory, moss, soil = step(rain[t], dampness, damp_memory, moss, soil)

    #if t % 360 == 0:
     #   view.update(t, dampness, moss, soil)

np.savez("history.npz", **history) # type: ignore

plotHistory(history, n_days)
