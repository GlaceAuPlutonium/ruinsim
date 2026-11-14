import numpy as np

from params import *  # pyright: ignore[reportWildcardImportFromLibrary]


SEED = 48
seed_texture, seed_weather, seed_bio, seed_ph, seed_temp, seed_dtr, seed_hum, seed_sun, seed_ws = np.random.SeedSequence(SEED).spawn(9)
rng_texture = np.random.default_rng(seed_texture)
rng_weather = np.random.default_rng(seed_weather)
rng_bio = np.random.default_rng(seed_bio)
rng_ph = np.random.default_rng(seed_ph)
rng_temp = np.random.default_rng(seed_temp)
rng_dtr = np.random.default_rng(seed_dtr)
rng_hum = np.random.default_rng(seed_hum)
rng_sun = np.random.default_rng(seed_sun)
rng_ws = np.random.default_rng(seed_ws)

size = SIZE

_a = np.log(2) / np.log((MOSS_T_MAX - MOSS_T_MIN) / (MOSS_T_OPT - MOSS_T_MIN)) # for cardinalTemp



def step(mat, rain, evap, temp, hum, ghi, w, mem, m, soil):
    # the surface today = bare slab + whatever soil has built up on it
    porosity_eff = mat.porosity + SOIL_EFFECT * soil * (1 - mat.porosity)
    phi = mat.phi_min + (mat.phi_max - mat.phi_min) * porosity_eff
    cap = mat.pore_depth * phi # + DEPR_MM * hollows

    w = w + rain #+ dew #+ leak
    w = w + SPREAD * (neighborSum(w) - 4 * w)
    runoff = np.maximum(w - cap, 0)               # for soil washing
    w = np.minimum(w, cap)                        # after rain, before drying
    evap_cell = max(evap * mat.surf_evap, 1e-6)
    wet_frac = np.minimum(w / evap_cell, 1.0)    # fraction of the day it is wet
    w = np.maximum(w - evap_cell, 0)

    f_T = cardinalTemp(temp)     # 0-1
    f_hum = VAPOR_EFF * np.clip((hum - HUM_ACT_RH) / (HUM_SAT_RH - HUM_ACT_RH), 0, 1)
    f_light = np.clip(ghi / GHI_SAT, 0, 1)     # maybe use (ghi/GHI_SAT + K), K in [1;1.5] instead
    active = np.maximum(wet_frac, f_hum) * f_T * f_light

    mem = mem + MEMORY * (wet_frac - mem)

    # Moss
    if MOSS_ENABLE and mat.moss:
        can_grow = mem > MOSS_GROW_ABOVE
        dying = mem < MOSS_DIE_BELOW

        nearby_moss = neighborSum(m) / 4
        spore_lands = rng_bio.random(w.shape) < SPORE_CHANCE

        growth = MOSS_GROWTH * (spore_lands + nearby_moss) * (1 - m) * can_grow * active
        dieback = MOSS_DIEBACK * m * dying
        m = np.clip(m + growth - dieback, 0, 1)

        pressure = np.clip(m + nearby_moss, 0, 1)
        wash = mat.wash_coef * runoff ** mat.wash_exp * (1 - pressure)
        soil = soil + mat.soil_build * pressure * (1 - soil) - wash
        soil = np.clip(soil, 0, 1)

    return w, wet_frac, mem, m, soil


# ----- side functions -----

def neighborSum(a):
    p = np.pad(a, 1, mode="edge")
    return p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]

def posTemp_frac(tmin, tmax): # fraction of the day surface is above 0°C
    k = np.clip((tmin + tmax) / (tmax - tmin), -1, 1)
    return 0.5 + np.arcsin(k) / np.pi

def cardinalTemp(temp):
    # Wang & Engel (1998) beta function: f(Tmin)=f(Tmax)=0, f(Topt)=1, peak exactly at Topt
    x = np.clip(temp - MOSS_T_MIN, 0, MOSS_T_MAX - MOSS_T_MIN)
    f = (2 * x**_a * (MOSS_T_OPT - MOSS_T_MIN)**_a - x**(2*_a)) / (MOSS_T_OPT - MOSS_T_MIN)**(2*_a)
    return np.clip(f, 0, 1)
