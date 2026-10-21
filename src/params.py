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
