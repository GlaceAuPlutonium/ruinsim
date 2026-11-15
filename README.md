# Time damage simulation and rendering engine

Simulating the damages of time on actual human structures, with real world data and realistic decay 🌿 🏢 \

### **WIP**

## What is this ?

A project I've had in mind for a long time : simulating time on human infrastructures. \
I've always loved the The Last Of Us or Horizon Zero Dawn world aesthetic, buildings decaying, nature taking control once again, so basically post-apo (or post-post-post apo for HZD). And that got me wondering : What if this building stood untounched for dozens or hundreds of years ? What would it look like ? \
\
That's the idea : Taking a normal building, passing it through an engine that simulates rain, weather, erosion, nature growing, materials deteriorating, structures failing and falling, etc.. and outputting a 3d environment you can explore and walk through.

## How the program works

The simulation runs on a 100×100 grid (for now) representing a concrete slab, one step per day, for `YEARS` amount of years.

1. `climate.py` pre-computes the full climate hisotry before the simulation : wet/dry Markovdays with spell clustering, gamma-distributed rain amounts, temperature,humidity, radiation, wind, all based off Lyon-Bron 1991–2020 normals, plus FAO-56 Penman-Monteith evaporation.
2. `model.py` builds the slab (a porosity map) and runs the daily chain:rain fills each cell's pore storage (capacity = pore depth × porosity, mm) → excess runs off → water spreads, evaporates (scaled by the frozen fraction of that day) → a slow wetness memory tracks how long cells stayed wet → moss grows on that memory → moss builds soil, soil raises capacity.
3. `main.py` ties everything together : climate, model over N years, history, plots.
4. `render.py` draws the live 2×2 live view window and the final history plot.

`params.py` holds the constants.

## Roadmap

**Soon : finish climate engine and base components**
- Test each one alone with moss disabled, then connect them to moss.
- Switch moss death to dormant state for short term drying
- Add different materials with associated parameters
- Refine pH model, higher noise, take into account logarithmic scale, draw noise once per wet spell, store acid load (10-pH + rain_mm) to use later
- Change humidity a bit, ie. add hmax and hmin at tmax and tmin ?

**Later : move to 3D**
- Keep the simulation headless in Python (possibly Rust later) and feed the data to a separate renderer (Blender for very early tests, then UE5)
- Get UE5 to send back heightmap before simulations by raycasting to deduce sun/shading maps, etc... Also AO and curvature maps, stuff like that
- Try to reach this kind of setup : UE5 bakes scene → sends data to sim engine → engine does its magic → sends back data to UE5 as maps (and 3d states later) → UE5 reconstructs the decayed scene based off simulated maps
- Once moss is good to go in 3d, add vines and other plants, then erosion, then materials wearout, stress and rupture (without FEM else computer kaboom)(opsec level hacker type of challenge)
- Optional additions later like snow, cracking by roots, etc...
- Final goal is a chain of events such as roof leak → wood rot → partial collapse → skylight reaches new places → moss and young trees below → pretty :D

**In a different timeline probably because it's so far away : real-world data and scaling**
- First with a few real buildings and their surrounding terrain, classify materials and building parts
- Replace monthyl table with real location-specific climate data
- Actual real world building but that seems a bit far-stretched

## Running it

### With uv (recommended)

If you use `uv`:
```plain
uv sync
uv run src/main.py
```

### Manually

You can run it manually, you need the following dependencies :
- `numpy`
- `matplotlib`
- `dataclass`
- `json`

Using Python 3.15
