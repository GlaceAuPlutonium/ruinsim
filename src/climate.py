# Contains climate pre-calc algorithm. Rain, wet/dry spells, temperature, rain pH, humidity (upcoming), sun exposure (upcoming), wind (upcoming)
import numpy as np

from params import DTR_NOISE, MEAN_RAIN, MIN_DTR, PH_VAR, RAIN_PERSISTENCE, TEMP_PERSISTENCE, WET_DTR_EFFECT

DAYS_PER_YEAR = 365
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

month_centers = (np.arange(12) + 0.5) * DAYS_PER_YEAR / 12

RAIN_PROB_BY_MONTH = np.array([0.15, 0.15, 0.25, 0.35, 0.35, 0.20,
                               0.10, 0.12, 0.30, 0.40, 0.30, 0.18])

PH_MONTH = np.array([5.8, 5.7, 5.6, 5.6, 5.5, 5.4,
                     5.4, 5.5, 5.6, 5.6, 5.7, 5.8])
# ADD A DEDICATED INDUSTRIAL PH PARAMETER

TEMP_MONTH = np.array([5.4, 6.1, 9.1, 11.8, 15.4, 18.9,
                       21.1, 21.4, 17.5, 13.7, 9.0, 6.1])
# temps are Frances's normals from 1991-2020
TEMP_STD_MONTH = np.array([3.2, 3.2, 2.9, 2.5, 2.2, 2.0,
                           1.9, 1.9, 2.1, 2.4, 2.7, 3.0])
RAIN_COOLING_MONTH = np.array([-1.0, -1.0, -0.5, 0.5, 1.0, 1.5,
                               2.5, 2.5, 1.5, 0.0, -0.5, -1.0])

TMIN_MONTH = np.array([1.1, 1.4, 4.2, 7.2, 11.2, 15.0,
                      17.0, 16.6, 12.8, 9.6, 4.9, 2.0])
TMAX_MONTH = np.array([7.1, 9.0, 13.8, 17.4, 21.5, 25.6,
                      28.2, 28.0, 23.1, 17.7, 11.4, 7.7])

DTR_MONTH = TMAX_MONTH - TMIN_MONTH
# dtr value is obtained with Tmax and Tmin values that comes from Lyon-Bron station (69) 1991-2020, see https://www.infoclimat.fr/climatologie/normales-records/1991-2020/lyon-bron/valeurs/07480.html


def rainProb(day):
    return np.interp(day % DAYS_PER_YEAR, month_centers,
                     RAIN_PROB_BY_MONTH, period=DAYS_PER_YEAR)

def genClimate(n_days, rng, rng_ph, rng_temp, rng_dtr):
    """Rain amount for every day (0 on dry days), with wet/dry spells.

    Each day is wet or dry. Chance of a wet day depends on the season AND on
    whether yesterday was wet. Monthly table still means "fraction of rainy
    days": persistence changes how days cluster, not how many are rainy.
    """
    rain = np.zeros(n_days)
    pH = np.full(n_days, np.nan)
    temp = np.zeros(n_days)
    tmin = np.zeros(n_days)
    tmax = np.zeros(n_days)
    z = 0.0
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
        ph_value = np.interp(day % DAYS_PER_YEAR, month_centers, PH_MONTH, period=DAYS_PER_YEAR) + rng_ph.uniform(-PH_VAR, PH_VAR)
        if was_wet:
            rain[day] = amount
            pH[day] = ph_value

        # temperature
        seasonal = np.interp(day % DAYS_PER_YEAR, month_centers, TEMP_MONTH, period=DAYS_PER_YEAR)
        z = TEMP_PERSISTENCE * z + np.sqrt(1 - TEMP_PERSISTENCE ** 2) * rng_temp.standard_normal()
        temp_std = np.interp(day % DAYS_PER_YEAR, month_centers, TEMP_STD_MONTH, period=DAYS_PER_YEAR)
        rain_cooling = np.interp(day % DAYS_PER_YEAR, month_centers, RAIN_COOLING_MONTH, period=DAYS_PER_YEAR)
        temp[day] = seasonal + temp_std * z + rain_cooling * (p - was_wet)

        # diurnal cycle, tmin and tmax
        dtr_month = np.interp(day % DAYS_PER_YEAR, month_centers, DTR_MONTH, period=DAYS_PER_YEAR)
        dtr_noise = rng_dtr.standard_normal()
        dtr = dtr_month * (1 + WET_DTR_EFFECT * (p - was_wet)) * np.exp(DTR_NOISE * dtr_noise - DTR_NOISE**2 / 2)
        dtr = max(dtr, MIN_DTR)
        tmax[day] = temp[day] + dtr / 2
        tmin[day] = temp[day] - dtr / 2
    return rain, pH, temp, tmin, tmax

def spellLengths(is_wet):
    """Lengths of consecutive wet runs and dry runs."""
    change = np.flatnonzero(np.diff(is_wet.astype(int))) + 1
    runs = np.split(is_wet, change)
    wet = [len(r) for r in runs if r[0]]
    dry = [len(r) for r in runs if not r[0]]
    return wet, dry
