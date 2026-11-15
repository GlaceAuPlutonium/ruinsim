import numpy as np

from climate import DAYS_PER_YEAR, evap_et0, genClimate
from materials import gridDims, loadMaterial
from model import posTemp_frac, step
from render import LiveView, plotHistory
from scene import loadScene
from seed import (
    rng_dtr,
    rng_hum,
    rng_ph,
    rng_sun,
    rng_temp,
    rng_texture,
    rng_weather,
    rng_ws,
)

YEARS = 20

scene = loadScene()
face = scene.faces[0]

n_rows, n_cols, cell_h, cell_w = gridDims(face.length, face.width, scene.res)
mat = loadMaterial(face.material, rng_texture, n_rows, n_cols, cell_h, cell_w)

n_days = DAYS_PER_YEAR * YEARS
rain, pH, temp, tmin, tmax, humidity, ghi, ws, wd = genClimate(n_days, rng_weather, rng_ph, rng_temp, rng_dtr, rng_hum, rng_sun, rng_ws, scene.site.latitude)

evap = evap_et0(np.arange(n_days), temp, tmin, tmax, humidity, ghi, ws * 4.87 / np.log(67.8 * 10 - 5.42), mat.albedo_fresh, scene.site.latitude, scene.site.altitude) * posTemp_frac(tmin, tmax)


shape = mat.porosity.shape
water, water_memory, moss, soil = (np.zeros(shape) for _ in range(4))


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

view = LiveView(water, moss, soil, mat.porosity)

moss_mean = np.zeros(n_days)
soil_mean = np.zeros(n_days)
for t in range(n_days):
    water, wet_frac, water_memory, moss, soil = step(mat, rain[t], evap[t], temp[t], humidity[t], ghi[t], water, water_memory, moss, soil)
    moss_mean[t] = moss.mean()
    soil_mean[t] = soil.mean()

    if t % 360 == 0:
        view.update(t, wet_frac, moss, soil)

history["moss"] = moss_mean
history["soil"] = soil_mean

np.savez("history.npz", **history) # type: ignore
plotHistory(history, n_days)
