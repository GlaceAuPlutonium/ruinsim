# Rain
RAIN_PERSISTENCE = 0.3
MEAN_RAIN = 0.12

# Water parameters (all rates are per day)
SPREAD = 0.2             # must stay <= 0.25, see the assert below
DRYING = 0.15            # average drying rate per day
POROSITY_EFFECT = 1.0    # 0 = uniform wall; sensible range 0 to 1.4
LEAK_AMOUNT = 0.0        # set to 0.03 to bring the gutter leak back
MIN_DRYING = 0.01        # safety floor: a cell can never stop drying
MAX_DRYING = 0.9         # safety ceiling: a cell can never lose more than this

assert SPREAD <= 0.25, "SPREAD must be <= 0.25 or the water spreading becomes unstable"

# Moss parameters
MEMORY = 0.02
MOSS_GROW_ABOVE = 0.22
MOSS_DIE_BELOW = 0.18
SPORE_CHANCE = 0.00002
MOSS_GROWTH = 0.006
MOSS_DIEBACK = 0.01

MOSS_ENABLE = False

# Soil parameters
SOIL_BUILD = 0.0008      # per day: moss and its fringe build substrate
SOIL_LOSS = 0.0003       # per day: rain washes soil off where no moss protects it
SOIL_EFFECT = 0.6        # max fraction of the porosity gap that soil can fill

# Rain pH
PH_VAR = 0.15

# Temperature
TEMP_PERSISTENCE = 0.75   # day-to-day correlation of the anomaly (0 = independent)

WET_DTR_EFFECT = 0.35   # wet days have a range ~35% smaller than dry days
DTR_NOISE = 0.25        # day-to-day variation of the range (fraction)
MIN_DTR = 1.0           # safety floor (°C)

assert 0<=TEMP_PERSISTENCE < 1, "TEMP_PERSISTENCE must be between 0 and 1 else the temperature calculation will fail"
assert 0 <= WET_DTR_EFFECT < 1
assert DTR_NOISE >= 0

# Humidity
RAIN_HUM_EFFECT = 0.5     # fraction of the headroom gained on a wet day
HUM_NOISE = 0.25          # std of the anomaly, as a fraction of the headroom
HUM_PERSISTENCE = 0.6
MIN_HUM = 0.15            # safety floor
HUM_TEMP_COUPLING = 0.2
