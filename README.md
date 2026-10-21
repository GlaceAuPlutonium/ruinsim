# Time damage simulation and rendering engine

WIP

## What is this ?

A project I've had in mind for a long time : simulating time on human infrastructures. \
I've always loved the The Last Of Us or Horizon Zero Dawn world aesthetic, buildings decaying, nature taking control once again, so basically post-apo (or post-post-post apo for HZD). And that got me wondered : What if this building stood untounched for dozens or hundreds of years ? What would it look like ? \
\
That's the idea : Taking a normal building, passing it through an engine that simulates rain, weather, erosion, nature growing, materials deteriorating, structures failing and falling, etc.. and outputting a 3d environment you can explore and walk through.

## How the program works

The simulation runs on a 100×100 grid (for now, building faces later) representing a patch of concrete wall (more materials later), one step per day, for `YEARS` amount of years.

1. `climate.py` pre-computes the whole rain (and later climate) history before the simulation starts. Each day is wet or dry. The chance of a wet day follows a monthly table (interpolated smoothly between month centers), and a persistence term makes wet days and dry days cluster into spells. On wet days, the rain amount is drawn from an exponential distribution.
2. `model.py` builds the wall and runs the simulation with `step`. At the start it creates the fixed porosity map and the empty state grids: dampness, damp memory, moss and soil.
3. `main.py` ties everything together. It calculates the weather, loops `step` over every day, records mean values into `history`, refreshes the live view, saves `history.npz` and plots the full history.
4. `render.py` draws the live 2×2 window and the final five-panel plot.
5. `params.py` holds the tunable constants for water, moss and soil. (more later)

Each day in `step` goes through this chain:

- **Surface**, the effective porosity is the bare wall plus whatever soil has built up. This sets a per-cell drying rate. \
- **Water**, rain and leak (may be removed) are added, water spreads to the 4 neighbors, dries, and values are clipped to 0–1. \
- **Damp memory**, a slow running average of dampness. \
- **Moss**, grows where damp memory is above a threshold and dies (death will be changed to "inactivty" for short term drying) where it is below a lower one. Growth comes from random spores or from neighboring moss. \
- **Soil**, built by moss and its fringe, washed away where there is no moss. Soil then changes porosity, which feeds back into drying. \

## Parameters currently in play

| Parameter | Value (current, may change) | Role |
|---|---|---|
| `SPREAD` | 0.2 | Diffusion to neighbors (must be ≤ 0.25) |
| `DRYING` | 0.15 | Average daily drying rate |
| `POROSITY_EFFECT` | 1.0 | How much porosity changes drying |
| `MIN_DRYING` / `MAX_DRYING` | 0.01 / 0.9 | Safety bounds on drying |
| `LEAK_AMOUNT` | 0.0 | Gutter leak (off) |
| `MEMORY` | 0.02 | Speed of the damp-memory average |
| `MOSS_GROW_ABOVE` / `MOSS_DIE_BELOW` | 0.22 / 0.18 | Growth and death thresholds |
| `SPORE_CHANCE` | 0.00002 | Daily chance a spore lands on a cell |
| `MOSS_GROWTH` / `MOSS_DIEBACK` | 0.006 / 0.01 | Growth and die-off rates |
| `SOIL_BUILD` / `SOIL_LOSS` | 0.0008 / 0.0003 | Build-up and wash-off rates |
| `SOIL_EFFECT` | 0.6 | Max share of the porosity gap soil can fill |
| `RAIN_PROB_BY_MONTH` | 0.10–0.40 | Seasonal chance of a rainy day |
| `RAIN_PERSISTENCE` | 0.3 | Clustering of wet and dry spells |
| `MEAN_RAIN` | 0.12 | Mean rain amount on a wet day |
| `SEED`, `size` | 48, 100 | Reproducibility and grid size |

Some parameters may later be removed.
## Roadmap

**Soon : finish climate engine and base components**
- Add temperature, humidity, sun exposure/UV, wind and rain pH and their associated effects
- All of them as monthly tables (except pH), and later per region
- Test each one alone with moss disabled, then connect them to moss.
- Switch moss death to dormant state for short term drying
- Add different materials with associated parameters

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
