import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Site:
    latitude: float
    altitude: float

@dataclass(frozen=True)
class Face:
    id: str
    length: float
    width: float
    material: str
    az_deg: float
    alt_deg: float
    sun_map: str | None
    rain_map: str | None

@dataclass(frozen=True)
class Scene:
    site: Site
    res: float
    faces: list[Face]

def loadScene(path="scene.json"):
    d = json.load(open(path))  # noqa: SIM115
    assert d["version"] == 1, "Unsupported scene version."
    faces = []
    for b in d["buildings"]:
        for o in b["objects"]:
            for f in o["faces"]:
                maps = f.get("maps", {})
                faces.append(Face(
                    id=f"{b['id']}/{o['id']}/{f['id']}",
                    length=f["length"], width=f["width"],
                    material=f["material"],
                    az_deg=f["az_deg"], alt_deg=f["alt_deg"],
                    sun_map=maps.get("sun"),
                    rain_map=maps.get("rain"),
                ))
    return Scene(Site(d["site"]["latitude"], d["site"]["altitude"]), d["resolution_m"], faces)
