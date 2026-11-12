# Rain
RAIN_PERSISTENCE = 0.3
RAIN_SHAPE = 0.7

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

# GHI
WET_KT_EFFECT = 0.25
KT_NOISE = 0.11
SUN_PERSISTENCE = 0.30
assert KT_NOISE >= 0, "KT_NOISE can't be negative."
assert 0 <= SUN_PERSISTENCE < 1, "SUN_PERSISTENCE must be a percentage."

# Wind
WET_WS_EFFECT = 0.35
WS_NOISE = 0.45
WS_PERSISTENCE = 0.6



# Water parameters (all rates are per day)
SPREAD = 0.2             # must stay <= 0.25, see the assert below

assert SPREAD <= 0.25, "SPREAD must be <= 0.25 or the water spreading becomes unstable"

# Moss parameters
MEMORY = 0.02
MOSS_GROW_ABOVE = 0.22
MOSS_DIE_BELOW = 0.10
SPORE_CHANCE = 0.00002
MOSS_GROWTH = 0.03
MOSS_DIEBACK = 0.01
MOSS_T_MIN = 0
MOSS_T_OPT = 18
MOSS_T_MAX = 32

MOSS_ENABLE = True

# Soil parameters
SOIL_BUILD = 0.0008      # per day: moss and its fringe build substrate
SOIL_EFFECT = 0.6        # max fraction of the porosity gap that soil can fill
WASH_COEF = 0.001
WASH_EXP = 1.5


ALTITUDE = 204
ALBEDO = 0.35
SURF_EVAP = 1.2

PORE_DEPTH_MM = 10.0       # active depth of concrete that wets/dries within days, in mm
PHI_MIN, PHI_MAX = 0.10, 0.15   # real porosity range of your porosity map
