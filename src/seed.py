import numpy as np

SEED = 1685
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
