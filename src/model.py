from climate import extraRad
import numpy as np

from params import *  # pyright: ignore[reportWildcardImportFromLibrary]

# STATES:  water  [mm, 0..cap]   real water stock
#          mem    [0..1]          EMA of wet_frac (~50-day), what moss reads
#          moss   [0..1]          cover fraction
#          soil   [0..1]          substrate built, raises capacity

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

size = 100

# Wall texture
def smoothNoise(sigma):
    """Random noise blurred at a given scale (in cells), then normalized."""
    white = rng_texture.standard_normal((size, size))
    k = np.fft.fftfreq(size)
    k2 = k[:, None] ** 2 + k[None, :] ** 2
    blurred = np.fft.ifft2(np.fft.fft2(white) * np.exp(-2 * (np.pi * sigma) ** 2 * k2))
    out = np.real(blurred)
    return (out - out.mean()) / out.std()


mix = 0.6 * smoothNoise(6) + 0.4 * smoothNoise(2)
mix = (mix - mix.mean()) / mix.std()
porosity = 1 / (1 + np.exp(-1.5 * mix))     # the bare slab, fixed over time

water = np.zeros((size, size))
water_memory = np.zeros((size, size))
moss = np.zeros((size, size))
soil = np.zeros((size, size))


def step(rain, evap, w, mem, m, soil):
    # The surface today = bare slab + whatever soil has built up on it
    porosity_eff = porosity + SOIL_EFFECT * soil * (1 - porosity)
    phi = PHI_MIN + (PHI_MAX - PHI_MIN) * porosity_eff
    cap = PORE_DEPTH_MM * phi # + DEPR_MM * hollows      # ~2-3 mm on average

    # Water
    w = w + rain #+ leak
    w = w + SPREAD * (neighborSum(w) - 4 * w)
    runoff = np.maximum(w - cap, 0)                        # for soil washing
    w = np.minimum(w, cap)                                # after rain, before drying
    evap_cell = max(evap * SURF_EVAP, 1e-6)
    wet_frac = np.minimum(w / evap_cell, 1.0)             # fraction of the day it is wet
    w = np.maximum(w - evap_cell, 0)

    mem = mem + MEMORY * (wet_frac - mem)

    # Moss
    if MOSS_ENABLE:
        can_grow = mem > MOSS_GROW_ABOVE
        dying = mem < MOSS_DIE_BELOW
        nearby_moss = neighborSum(m) / 4
        spore_lands = rng_bio.random(w.shape) < SPORE_CHANCE
        growth = MOSS_GROWTH * (spore_lands + nearby_moss) * (1 - m) * can_grow
        dieback = MOSS_DIEBACK * m * dying
        m = np.clip(m + growth - dieback, 0, 1)

    # Soil: built by moss and its fringe, washed off where there is no moss
        pressure = np.clip(m + nearby_moss, 0, 1)
        soil = soil + SOIL_BUILD * pressure * (1 - soil) - SOIL_LOSS * soil * (1 - m)
        soil = np.clip(soil, 0, 1)

    return w, wet_frac, mem, m, soil


# ----- side functions -----

def neighborSum(a):
    p = np.pad(a, 1, mode="edge")
    return p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]

def esat(T): # saturation vapour pressure, kPa (Magnus / FAO-56 eq.11)
    return 0.6108 * np.exp(17.27 * T / (T + 237.3))

def evap_et0(day, temp, tmin, tmax, hum, ghi, wsu2): # mm.day, FAO-56 Penman-Monteith
    es = (esat(tmin) + esat(tmax)) / 2
    ea = hum * es
    vpd = np.maximum(es-ea, 0)
    delta = 4098 * es / (temp+237.3)**2         # slope of es(T), kPa/°C
    gamma = 0.0658                              # kPa/°C at Lyon-Bron ~200 m
    Rso = (0.75 + 2e-5*ALTITUDE) * extraRad(day)
    Rn = (1 - ALBEDO)*ghi - 4.903e-9*((tmax+273.16)**4 + (tmin+273.16)**4)/2 * (0.34 - 0.14*np.sqrt(ea)) * (1.35*np.minimum(ghi/Rso,1) - 0.35)
    return np.maximum((0.408*delta*Rn + gamma*(900/(temp+273))*wsu2*vpd) / (delta + gamma*(1+0.34*wsu2)), 0 )

def posTemp_frac(tmin, tmax): # Fraction of the day surface is above 0°C
    k = np.clip((tmin + tmax) / (tmax - tmin), -1, 1)
    return 0.5 + np.arcsin(k) / np.pi
