import numpy as np

from params import *  # pyright: ignore[reportWildcardImportFromLibrary]

SEED = 48
seed_texture, seed_weather, seed_bio, seed_ph, seed_temp, seed_dtr = np.random.SeedSequence(SEED).spawn(6)
rng_texture = np.random.default_rng(seed_texture)
rng_weather = np.random.default_rng(seed_weather)
rng_bio = np.random.default_rng(seed_bio)
rng_ph = np.random.default_rng(seed_ph)
rng_temp = np.random.default_rng(seed_temp)
rng_dtr = np.random.default_rng(seed_dtr)

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
porosity = 1 / (1 + np.exp(-1.5 * mix))     # the bare wall, fixed over time

leak = np.zeros((size, size))
leak[0:3, 68:72] = LEAK_AMOUNT

dampness = np.zeros((size, size))
damp_memory = np.zeros((size, size))
moss = np.zeros((size, size))
soil = np.zeros((size, size))


def neighborSum(a):
    p = np.pad(a, 1, mode="edge")
    return p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]


def step(rain_today, d, mem, m, soil):
    # The surface today = bare wall + whatever soil has built up on it
    porosity_eff = porosity + SOIL_EFFECT * soil * (1 - porosity)
    drying_today = DRYING * (1 - POROSITY_EFFECT * (porosity_eff - 0.5) * 1.4)
    drying_today = np.clip(drying_today, MIN_DRYING, MAX_DRYING)

    # Water
    d = d + rain_today + leak
    d = d + SPREAD * (neighborSum(d) - 4 * d)
    d = d * (1 - drying_today)
    d = np.clip(d, 0, 1)

    mem = mem + MEMORY * (d - mem)

    # Moss
    if MOSS_ENABLE:
        can_grow = mem > MOSS_GROW_ABOVE
        dying = mem < MOSS_DIE_BELOW
        nearby_moss = neighborSum(m) / 4
        spore_lands = rng_bio.random(d.shape) < SPORE_CHANCE
        growth = MOSS_GROWTH * (spore_lands + nearby_moss) * (1 - m) * can_grow
        dieback = MOSS_DIEBACK * m * dying
        m = np.clip(m + growth - dieback, 0, 1)

    # Soil: built by moss and its fringe, washed off where there is no moss
        pressure = np.clip(m + nearby_moss, 0, 1)
        soil = soil + SOIL_BUILD * pressure * (1 - soil) - SOIL_LOSS * soil * (1 - m)
        soil = np.clip(soil, 0, 1)

    return d, mem, m, soil
