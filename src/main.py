import numpy as np

from climate import DAYS_PER_YEAR, genClimate, evap_et0
from model import posTemp_frac, water_memory, water, moss, porosity, rng_ph, rng_weather, rng_temp, rng_dtr, rng_hum, rng_sun, rng_ws, soil, step
from render import LiveView, plotHistory

YEARS = 20

n_days = DAYS_PER_YEAR * YEARS
rain, pH, temp, tmin, tmax, humidity, ghi, ws, wd = genClimate(n_days, rng_weather, rng_ph, rng_temp, rng_dtr, rng_hum, rng_sun, rng_ws)

evap = evap_et0(np.arange(n_days), temp, tmin, tmax, humidity, ghi, ws * 4.87 / np.log(67.8 * 10 - 5.42)) * posTemp_frac(tmin, tmax)

history = {
    "rain": rain,
    "temp": temp,
    "tmin": tmin,
    "tmax": tmax,
    "hum": humidity,
    "ghi": ghi,
    "ws": ws,
    "evap": evap
}

view = LiveView(water, moss, soil, porosity)

moss_mean = np.zeros(n_days)
soil_mean = np.zeros(n_days)
for t in range(n_days):
    water, wet_frac, water_memory, moss, soil = step(rain[t], evap[t], temp[t], humidity[t], ghi[t], water, water_memory, moss, soil)
    moss_mean[t] = moss.mean()
    soil_mean[t] = soil.mean()

    if t % 120 == 0:
        view.update(t, wet_frac, moss, soil)

history["moss"] = moss_mean
history["soil"] = soil_mean

np.savez("history.npz", **history) # type: ignore
plotHistory(history, n_days)
