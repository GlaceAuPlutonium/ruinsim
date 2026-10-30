# Contains climate pre-calc algorithm. Rain, wet/dry spells, temperature, rain pH, humidity, GHI, wind
import numpy as np

from params import DTR_NOISE, HUM_NOISE, HUM_PERSISTENCE, HUM_TEMP_COUPLING, KT_NOISE, MIN_DTR, MIN_HUM, PH_VAR, RAIN_HUM_EFFECT, RAIN_PERSISTENCE, RAIN_SHAPE, TEMP_PERSISTENCE, WET_DTR_EFFECT, WET_KT_EFFECT, SUN_PERSISTENCE, WET_WS_EFFECT, WS_NOISE, WS_PERSISTENCE

LATITUDE = 45.72
G_SC = 0.082


DAYS_PER_YEAR = 365
MONTH_DAYS = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_centers = (np.arange(12) + 0.5) * DAYS_PER_YEAR / 12


TOTAL_RAIN_MONTH = np.array([49.8, 41.6, 49.4, 68.9, 80.9, 74.1,
                            67.4, 65.5, 82.5, 99.8, 87.2, 53.7])

WET_DAYS_MONTH = np.array([8.1, 7.9, 8.4, 9.0, 10.3, 8.5,
                           7.5, 7.2, 7.3, 9.9, 9.4, 9.2])

RAIN_PROB_MONTH = WET_DAYS_MONTH / MONTH_DAYS
MEAN_RAIN_MONTH = TOTAL_RAIN_MONTH / WET_DAYS_MONTH
# Rain data from Lyon-Bron's 1991-2020 normals report


PH_MONTH = np.array([5.8, 5.7, 5.6, 5.6, 5.5, 5.4,
                     5.4, 5.5, 5.6, 5.6, 5.7, 5.8])
# ADD A DEDICATED INDUSTRIAL PH PARAMETER


TEMP_MONTH = np.array([4.1, 5.2, 9.0, 12.3, 16.3, 20.3,
                       22.6, 22.3, 17.9, 13.7, 8.1, 4.8])
# Temperature data from Lyon-Bron's 1991-2020 normals report
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


HUMIDITY_MONTH = np.array([0.900, 0.856, 0.811, 0.770, 0.758, 0.717,
                           0.661, 0.647, 0.718, 0.815, 0.882, 0.905])
# relative humidity from NASA/POWER Source Native Resolution Climatology in LST, MERRA-2 instrument, 1991-2020, Lyon-Bron station


SFC_MONTH = np.array([1.3585, 2.212, 3.4989, 4.6378, 5.4419, 6.2574,
                      6.3703, 5.4806, 4.0868, 2.5422, 1.5, 1.0953])
TOA_MONTH = np.array([3.3247, 4.8588, 7.025, 9.2329, 10.8561, 11.5476,
                      11.154, 9.7706, 7.7486, 5.5258, 3.709, 2.8803])
# SFC_SW_DWN and TOA_SW_DWN from NASA/POWER Source Native Resolution Climatology in LST, MERRA-2 instrument, 1991-2020, Lyon-Bron station
KT_MONTH = SFC_MONTH / TOA_MONTH


WS_MONTH = np.array([3.72, 3.89, 3.93, 3.92, 3.7, 3.42,
                     3.21, 3.08, 3.3, 3.58, 3.69, 3.71])
WD_MONTH = np.array([280.23, 299.65, 306.26, 302.52, 306.25, 322.25,
                     328.3, 321.85, 308.65, 243.6, 262.53, 262.37])
# Wind data at 10m altitude from NASA/POWER Source Native Resolution Climatology in LST, MERRA-2 instrument, 1991-2020, Lyon-Bron station


def genClimate(n_days, rng, rng_ph, rng_temp, rng_dtr, rng_hum, rng_sun, rng_ws):
    rain = np.zeros(n_days)
    pH = np.full(n_days, np.nan)
    temp = np.zeros(n_days)
    tmin = np.zeros(n_days)
    tmax = np.zeros(n_days)
    humidity = np.zeros(n_days)
    ghi = np.zeros(n_days)
    ws = np.zeros(n_days)
    wd = np.zeros(n_days)

    # ADD A unit_z(rng, persistence, z) FUNCTION
    zt = 0.0
    zh = 0.0
    zs = 0.0
    zw = 0.0
    was_wet = False

    for day in range(n_days):
        p = rainProb(day)
        if was_wet:
            p_wet = p + RAIN_PERSISTENCE * (1 - p)      # rain tends to continue
        else:
            p_wet = p * (1 - RAIN_PERSISTENCE)          # dry tends to continue
        roll = rng.random()
        mean_rain = np.interp(day % DAYS_PER_YEAR, month_centers, MEAN_RAIN_MONTH, period=DAYS_PER_YEAR)
        amount = rng.gamma(RAIN_SHAPE, mean_rain / RAIN_SHAPE)
        was_wet = roll < p_wet
        ph_value = np.interp(day % DAYS_PER_YEAR, month_centers, PH_MONTH, period=DAYS_PER_YEAR) + rng_ph.uniform(-PH_VAR, PH_VAR)
        if was_wet:
            rain[day] = amount
            pH[day] = ph_value

        # temperature
        seasonal = np.interp(day % DAYS_PER_YEAR, month_centers, TEMP_MONTH, period=DAYS_PER_YEAR)
        zt = TEMP_PERSISTENCE * zt + np.sqrt(1 - TEMP_PERSISTENCE ** 2) * rng_temp.standard_normal()
        temp_std = np.interp(day % DAYS_PER_YEAR, month_centers, TEMP_STD_MONTH, period=DAYS_PER_YEAR)
        rain_cooling = np.interp(day % DAYS_PER_YEAR, month_centers, RAIN_COOLING_MONTH, period=DAYS_PER_YEAR)
        temp[day] = seasonal + temp_std * zt + rain_cooling * (p - was_wet)

        # diurnal cycle, tmin and tmax
        dtr_month = np.interp(day % DAYS_PER_YEAR, month_centers, DTR_MONTH, period=DAYS_PER_YEAR)
        dtr_noise = rng_dtr.standard_normal()
        dtr = dtr_month * (1 + WET_DTR_EFFECT * (p - was_wet)) * np.exp(DTR_NOISE * dtr_noise - DTR_NOISE**2 / 2)
        dtr = max(dtr, MIN_DTR)
        tmax[day] = temp[day] + dtr / 2
        tmin[day] = temp[day] - dtr / 2

        # humidity
        base_hum = np.interp(day % DAYS_PER_YEAR, month_centers, HUMIDITY_MONTH, period=DAYS_PER_YEAR)
        headroom = 1 - base_hum
        zh = HUM_PERSISTENCE * zh + np.sqrt(1 - HUM_PERSISTENCE**2) * rng_hum.standard_normal()
        humidity[day] = np.clip(base_hum + headroom * (RAIN_HUM_EFFECT * (was_wet - p) - HUM_TEMP_COUPLING * zt + HUM_NOISE * zh), MIN_HUM, 1.0)

        # ghi and cloudiness (kt)
        kt_base = np.interp(day % DAYS_PER_YEAR, month_centers, KT_MONTH, period=DAYS_PER_YEAR)
        kt_max = 0.362 + 0.597 * kt_base
        zs = SUN_PERSISTENCE * zs + np.sqrt(1 - SUN_PERSISTENCE**2) * rng_sun.standard_normal()
        kt = np.clip(kt_base - WET_KT_EFFECT * (was_wet - p) + KT_NOISE * zs, 0.05, kt_max) # Clasical Bendt model takes 0.05 as a minimum,and gives kt_max = 0.362 + 0.597 * mean_monthly_kt. From Polo & al. on radiation modeling
        ghi[day] = kt * extraRad(day) # maybe make sun_persistence/kt_noise change seasonaly ?

        # wind
        ws_base = np.interp(day % DAYS_PER_YEAR, month_centers, WS_MONTH, period=DAYS_PER_YEAR)
        zw = WS_PERSISTENCE * zw + np.sqrt(1 - WS_PERSISTENCE**2) * rng_ws.standard_normal()
        ws[day] = ws_base * (1 + WET_WS_EFFECT * (was_wet - p)) * np.exp(WS_NOISE * zw - WS_NOISE**2 / 2)

        wd[day] = np.interp(day % DAYS_PER_YEAR, month_centers, WD_MONTH, period=DAYS_PER_YEAR)

    return rain, pH, temp, tmin, tmax, humidity, ghi, ws, wd

def rainProb(day):
    return np.interp(day % DAYS_PER_YEAR, month_centers, RAIN_PROB_MONTH, period=DAYS_PER_YEAR)

def spellLengths(is_wet):
    change = np.flatnonzero(np.diff(is_wet.astype(int))) + 1
    runs = np.split(is_wet, change)
    wet = [len(r) for r in runs if r[0]]
    dry = [len(r) for r in runs if not r[0]]
    return wet, dry

def sunsetHourAngle(day):
    n = day % DAYS_PER_YEAR + 1
    phi = np.radians(LATITUDE)
    delta = 0.409 * np.sin(2 * np.pi * n / DAYS_PER_YEAR - 1.39)   # declination
    return np.arccos(np.clip(-np.tan(phi) * np.tan(delta), -1, 1))

def extraRad(day):
    n = day % DAYS_PER_YEAR + 1
    phi = np.radians(LATITUDE)
    delta = 0.409 * np.sin(2 * np.pi * n / DAYS_PER_YEAR - 1.39) # declination
    dr = 1 + 0.033 * np.cos(2 * np.pi * n / DAYS_PER_YEAR) # earth-sun distance
    ws = sunsetHourAngle(day)
    return (24 * 60 / np.pi) * G_SC * dr * (ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws))
