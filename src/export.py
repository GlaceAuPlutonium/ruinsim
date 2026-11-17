import os

import numpy as np
from PIL import Image


def toUint8(a):
    # all four arrays in [0;1], guards against float drift
    return np.round(np.clip(a, 0, 1) * 255).astype(np.uint8)


def exportMaps(face, arrays, out_dir="maps"):
    folder = os.path.join(out_dir, face.id.replace("/", "_"))
    os.makedirs(folder, exist_ok=True)
    for name, a in arrays.items():
        Image.fromarray(toUint8(a)).save(os.path.join(folder, f"{name}.png"))
