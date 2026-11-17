import zlib

from export import exportMaps
import matplotlib.pyplot as plt
import numpy as np

from climate import DAYS_PER_YEAR, evap_et0, genClimate
from materials import gridDims, loadMaterial
from model import posTemp_frac, step
from render import LiveView, plotHistory
from scene import loadScene
from seed import (
    SEED,
    rng_dtr,
    rng_hum,
    rng_ph,
    rng_sun,
    rng_temp,
    rng_weather,
    rng_ws,
)


def faceRngs(face):
    ss = np.random.SeedSequence([SEED, zlib.crc32(face.id.encode())])
    s_tex, s_bio = ss.spawn(2)
    return np.random.default_rng(s_tex), np.random.default_rng(s_bio)

def simulateFace(face, res, n_days, clim, live=False):
    rng_tex, rng_bio = faceRngs(face)
    n_rows, n_cols, cell_h, cell_w = gridDims(face.length, face.width, scene.res)
    mat = loadMaterial(face.material, rng_tex, n_rows, n_cols, cell_h, cell_w)

    evap = evap_et0(np.arange(n_days), clim["temp"], clim["tmin"], clim["tmax"], clim["hum"], clim["ghi"], clim["ws"] * 4.87 / np.log(67.8 * 10 - 5.42), mat.albedo_fresh, scene.site.latitude, scene.site.altitude) * posTemp_frac(clim["tmin"], clim["tmax"])

    shape = mat.porosity.shape
    water, water_memory, moss, soil = (np.zeros(shape) for _ in range(4))
    moss_mean = np.zeros(n_days)
    soil_mean = np.zeros(n_days)
    view = LiveView(water, moss, soil, mat.porosity) if live else None

    for t in range(n_days):
        water, wet_frac, water_memory, moss, soil = step(mat, clim["rain"][t], evap[t], clim["temp"][t], clim["hum"][t], clim["ghi"][t], water, water_memory, moss, soil, rng_bio)
        moss_mean[t]=moss.mean()
        soil_mean[t]=soil.mean()
        if view and t % 360 == 0:
            view.update(t, wet_frac, moss, soil)

    hist = {**clim, "evap": evap, "moss": moss_mean, "soil": soil_mean}
    maps = {"moss": moss, "soil": soil, "mem": water_memory, "porosity": mat.porosity}
    return hist, maps


YEARS = 20

scene = loadScene()
n_days = DAYS_PER_YEAR * YEARS

rain, pH, temp, tmin, tmax, hum, ghi, ws, wd = genClimate(n_days, rng_weather, rng_ph, rng_temp, rng_dtr, rng_hum, rng_sun, rng_ws, scene.site.latitude)

clim = {"rain": rain, "temp": temp, "tmin": tmin, "tmax": tmax, "hum": hum, "ghi": ghi, "ws": ws}

results = {}
for face in scene.faces:
    hist, maps = simulateFace(face, scene.res, n_days, clim, live=(len(scene.faces)==1))
    results[face.id] = hist
    np.savez(f"hist_{face.id.replace('/', '_')}.npz", **results[face.id])
    exportMaps(face, maps)

for face_id, h in results.items():
    plotHistory(h, n_days, title=face_id)
plt.show()
