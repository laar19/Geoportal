from PIL import Image

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import numpy as np

def black_to_transparency(img):
    x = np.asarray(img.convert("RGBA")).copy()

    x[:, :, 3] = (255 * (x[:, :, :3] > 25).any(axis=2)).astype(np.uint8)

    return Image.fromarray(x)

def intersection(polygon, target):
    return polygon.intersects(target)
