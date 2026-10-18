import numpy as np
import matplotlib.pyplot as plt

# --- Random generators: one independent stream per job ----------------------
# Changing the texture code no longer changes the weather, and vice versa.
SEED = 48
seed_texture, seed_weather, seed_bio = np.random.SeedSequence(SEED).spawn(3)
rng_texture = np.random.default_rng(seed_texture)
rng_weather = np.random.default_rng(seed_weather)
rng_bio = np.random.default_rng(seed_bio)

size = 100
DAYS_PER_YEAR = 365
YEARS = 500

# --- Seasons ----------------------------------------------------------------
RAIN_PROB_BY_MONTH = np.array([0.15, 0.15, 0.25, 0.35, 0.35, 0.20,
                               0.10, 0.12, 0.30, 0.40, 0.30, 0.18])
month_centers = (np.arange(12) + 0.5) * DAYS_PER_YEAR / 12
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def rain_probability(day):
    return np.interp(day % DAYS_PER_YEAR, month_centers,
                     RAIN_PROB_BY_MONTH, period=DAYS_PER_YEAR)


# --- Water parameters (all rates are per day) --------------------------------
MEAN_RAIN = 0.12
SPREAD = 0.2             # must stay <= 0.25, see the assert below
DRYING = 0.15            # average drying rate per day
POROSITY_EFFECT = 1.0    # 0 = uniform wall; sensible range 0 to 1.4
LEAK_AMOUNT = 0.0        # set to 0.03 to bring the gutter leak back
MIN_DRYING = 0.01        # safety floor: a cell can never stop drying
MAX_DRYING = 0.9         # safety ceiling: a cell can never lose more than this

# A cell gives SPREAD of its dampness to each of its 4 neighbors per step.
# Above 0.25 it would give away more than it has and the numbers explode.
assert SPREAD <= 0.25, "SPREAD must be <= 0.25 or the water spreading becomes unstable"

# --- Moss parameters --------------------------------------------------------
MEMORY = 0.02
MOSS_GROW_ABOVE = 0.22
MOSS_DIE_BELOW = 0.18
SPORE_CHANCE = 0.00002
MOSS_GROWTH = 0.006
MOSS_DIEBACK = 0.01


# --- Wall texture -------------------------------------------------------------
def smooth_noise(sigma):
    """Random noise blurred at a given scale (in cells), then normalized."""
    white = rng_texture.standard_normal((size, size))
    k = np.fft.fftfreq(size)
    k2 = k[:, None] ** 2 + k[None, :] ** 2
    blurred = np.fft.ifft2(np.fft.fft2(white) * np.exp(-2 * (np.pi * sigma) ** 2 * k2))
    out = np.real(blurred)
    return (out - out.mean()) / out.std()


mix = 0.6 * smooth_noise(6) + 0.4 * smooth_noise(2)
mix = (mix - mix.mean()) / mix.std()
porosity = 1 / (1 + np.exp(-1.5 * mix))

drying = DRYING * (1 - POROSITY_EFFECT * (porosity - 0.5) * 1.4)
drying = np.clip(drying, MIN_DRYING, MAX_DRYING)

leak = np.zeros((size, size))
leak[0:3, 68:72] = LEAK_AMOUNT

dampness = np.zeros((size, size))
damp_memory = np.zeros((size, size))
moss = np.zeros((size, size))


def neighbor_sum(a):
    p = np.pad(a, 1, mode="edge")
    return p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]


def step(day, d, mem, m):
    # Weather: always draw both numbers, so the weather stream stays aligned
    # even when the rain probabilities or amounts change.
    roll = rng_weather.random()
    amount = rng_weather.exponential(MEAN_RAIN)
    rain_today = amount if roll < rain_probability(day) else 0.0

    d = d + rain_today + leak
    d = d + SPREAD * (neighbor_sum(d) - 4 * d)
    d = d * (1 - drying)
    d = np.clip(d, 0, 1)

    mem = mem + MEMORY * (d - mem)

    can_grow = mem > MOSS_GROW_ABOVE
    dying = mem < MOSS_DIE_BELOW
    nearby_moss = neighbor_sum(m) / 4
    spore_lands = rng_bio.random(d.shape) < SPORE_CHANCE
    growth = MOSS_GROWTH * (spore_lands + nearby_moss) * (1 - m) * can_grow
    dieback = MOSS_DIEBACK * m * dying
    m = np.clip(m + growth - dieback, 0, 1)

    return d, mem, m, rain_today


# --- History: one number per day, for plotting and comparing runs ------------
n_days = DAYS_PER_YEAR * YEARS
history = {
    "rain": np.zeros(n_days),
    "mean_dampness": np.zeros(n_days),
    "mean_memory": np.zeros(n_days),
    "moss_coverage": np.zeros(n_days),   # average moss density over the wall
}

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
img1 = ax1.imshow(dampness, cmap="Blues", vmin=0, vmax=1)
img2 = ax2.imshow(moss, cmap="Greens", vmin=0, vmax=1)
ax3.imshow(porosity, cmap="Greys", vmin=0, vmax=1)
ax1.set_title("Dampness")
ax2.set_title("Moss")
ax3.set_title("Porosity (dark = holds water)")

for t in range(n_days):
    dampness, damp_memory, moss, rain_today = step(t, dampness, damp_memory, moss)

    history["rain"][t] = rain_today
    history["mean_dampness"][t] = dampness.mean()
    history["mean_memory"][t] = damp_memory.mean()
    history["moss_coverage"][t] = moss.mean()

    if t % 240 == 0:
        img1.set_data(dampness)
        img2.set_data(moss)
        month = MONTH_NAMES[int((t % DAYS_PER_YEAR) / DAYS_PER_YEAR * 12)]
        fig.suptitle(f"Year {t // DAYS_PER_YEAR + 1}, {month}")
        plt.pause(0.0001)

np.savez("history.npz", **history)   # keep it, to compare with later runs

# --- Plot the history -------------------------------------------------------
years = np.arange(n_days) / DAYS_PER_YEAR
fig2, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
axes[0].plot(years, history["rain"], lw=0.5)
axes[0].set_ylabel("rain / day")
axes[1].plot(years, history["mean_dampness"], lw=0.7)
axes[1].set_ylabel("mean dampness")
axes[2].plot(years, history["mean_memory"])
axes[2].axhline(MOSS_GROW_ABOVE, color="g", ls="--", lw=0.8, label="moss grows above")
axes[2].axhline(MOSS_DIE_BELOW, color="r", ls="--", lw=0.8, label="moss dies below")
axes[2].set_ylabel("mean damp memory")
axes[2].legend(loc="upper right", fontsize=8)
axes[3].plot(years, history["moss_coverage"], color="green")
axes[3].set_ylabel("moss coverage")
axes[3].set_xlabel("years")
plt.tight_layout()
plt.show()
