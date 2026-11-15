import json
from dataclasses import dataclass

import numpy as np


@dataclass(eq=False)
class Material:
    name: str
    porosity: np.ndarray      # 0-1 texture map
    phi_min: float
    phi_max: float
    pore_depth: float
    surf_evap: float
    albedo_fresh: float
    albedo_aged: float
    ph_fresh: float
    ph_aged: float
    moss: bool
    soil_build: float
    wash_coef: float
    wash_exp: float

def freshAged(v):
    """Accepts either a number or {"fresh": ..., "aged": ...}."""
    return (v["fresh"], v["aged"]) if isinstance(v, dict) else (v, v)



def gridDims(length, width, res):
    n_cols = int(np.floor(length / res + 0.5))
    n_rows = int(np.floor(width / res + 0.5))
    return n_rows, n_cols, width / n_rows, length / n_cols

def smoothNoise(sigma, rng, n_rows, n_cols, cell_h, cell_w):
    white = rng.standard_normal((n_rows, n_cols))
    ky = np.fft.fftfreq(n_rows)
    kx = np.fft.fftfreq(n_cols)
    k2 = ky[:, None]**2 / cell_h**2 + kx[None, :]**2 / cell_w**2
    out = np.real(np.fft.ifft2(np.fft.fft2(white) * np.exp(-2 * (np.pi * sigma)**2 * k2)))
    return (out - out.mean()) / out.std()

def loadMaterial(name, rng, n_rows, n_cols, cell_h, cell_w, path="materials.json"):
    d = json.load(open(path))[name]  # noqa: SIM115
    p = d["porosity"]

    mix = p["mix"][0] * smoothNoise(p["sigma_large"], rng, n_rows, n_cols, cell_h, cell_w) \
        + p["mix"][1] * smoothNoise(p["sigma_small"], rng, n_rows, n_cols, cell_h, cell_w)
    mix = (mix - mix.mean()) / mix.std()
    porosity = 1 / (1 + np.exp(-1.5 * mix))

    alb_f, alb_a = freshAged(d["albedo"])
    ph_f, ph_a = freshAged(d["ph"])

    return Material(
        name=name, porosity=porosity,
        phi_min=p["min"], phi_max=p["max"],
        pore_depth=d["pore_depth"],
        surf_evap=d["surf_evap"],
        albedo_fresh=alb_f, albedo_aged=alb_a,
        ph_fresh=ph_f, ph_aged=ph_a,
        moss=d["moss"],
        soil_build=d["soil"]["build"],
        wash_coef=d["soil"]["wash_coef"],
        wash_exp=d["soil"]["wash_exp"],
    )
