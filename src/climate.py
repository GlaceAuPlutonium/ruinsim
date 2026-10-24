# Contains climate pre-calc algorithm. Rain, wet/dry spells, humidity (upcoming), sun exposure (upcoming), wind (upcoming)
import numpy as np

from params import PH_VAR, RAIN_COOLING, TEMP_PERSISTENCE, TEMP_STD

DAYS_PER_YEAR = 365
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

RAIN_PERSISTENCE = 0.3
MEAN_RAIN = 0.12

month_centers = (np.arange(12) + 0.5) * DAYS_PER_YEAR / 12

RAIN_PROB_BY_MONTH = np.array([0.15, 0.15, 0.25, 0.35, 0.35, 0.20,
                               0.10, 0.12, 0.30, 0.40, 0.30, 0.18])

PH_MONTH = np.array([5.8, 5.7, 5.6, 5.6, 5.5, 5.4,
                     5.4, 5.5, 5.6, 5.6, 5.7, 5.8])
# ADD A DEDICATED INDUSTRIAL PH PARAMETER

TEMP_MONTH = np.array([5.7, 8.5, 9.4, 12.1, 16.0, 20.0,
                       21.8, 22.1, 18.8, 14.6, 9.8, 6.8])
# temps obtained by mean value of France's mean temps of 2020 + 2021 + 2022


def rainProb(day):
    return np.interp(day % DAYS_PER_YEAR, month_centers,
                     RAIN_PROB_BY_MONTH, period=DAYS_PER_YEAR)

def genClimate(n_days, rng, rng_ph, rng_temp):
    """Rain amount for every day (0 on dry days), with wet/dry spells.

    Each day is wet or dry. Chance of a wet day depends on the season AND on
    whether yesterday was wet. Monthly table still means "fraction of rainy
    days": persistence changes how days cluster, not how many are rainy.
    """
    rain = np.zeros(n_days)
    pH = np.full(n_days, np.nan)
    temp = np.zeros(n_days)
    anomaly = 0.0
    was_wet = False
    for day in range(n_days):
        p = rainProb(day)                       # seasonal chance of rain
        if was_wet:
            p_wet = p + RAIN_PERSISTENCE * (1 - p)      # rain tends to continue
        else:
            p_wet = p * (1 - RAIN_PERSISTENCE)          # dry tends to continue
        roll = rng.random()                             # always draw both numbers
        amount = rng.exponential(MEAN_RAIN)             # to keep the stream aligned
        was_wet = roll < p_wet
        if was_wet:
            rain[day] = amount
            pH[day] = np.interp(day % DAYS_PER_YEAR, month_centers, PH_MONTH, period=DAYS_PER_YEAR) + rng_ph.uniform(-PH_VAR, PH_VAR)

        # temperature
        seasonal = np.interp(day % DAYS_PER_YEAR, month_centers, TEMP_MONTH, period=DAYS_PER_YEAR)
        anomaly = TEMP_PERSISTENCE * anomaly + TEMP_STD * np.sqrt(1 - TEMP_PERSISTENCE ** 2) * rng_temp.standard_normal()
        temp[day] = seasonal + anomaly + RAIN_COOLING * (p - was_wet)
    return rain, pH, temp

def spellLengths(is_wet):
    """Lengths of consecutive wet runs and dry runs."""
    change = np.flatnonzero(np.diff(is_wet.astype(int))) + 1
    runs = np.split(is_wet, change)
    wet = [len(r) for r in runs if r[0]]
    dry = [len(r) for r in runs if not r[0]]
    return wet, dry
