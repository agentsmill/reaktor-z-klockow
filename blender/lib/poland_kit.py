"""Helpers for the "poland" shot: the Poland outline from src/data/poland.ts rasterised onto
1×1 plates (north = +y), the same lon/lat projection as the 2D map (projectLonLat), site
beacons, the Vistula as a trans-blue ribbon, a mini SMR tower and coin stacks."""
import math
import os
import re

import bpy

from . import anim as A
from . import bricks as B
from . import look as L

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POLAND_TS = os.path.join(ROOT, "src", "data", "poland.ts")

# Vistula from the source (Barania Góra) to the mouth (Przekop Wisły), lon/lat waypoints
VISTULA = [(18.97, 49.61), (18.86, 49.66), (18.80, 49.80), (18.86, 49.94), (19.23, 50.03), (19.60, 50.01),
           (19.94, 50.05), (20.30, 50.10), (21.07, 50.31), (21.50, 50.55), (21.75, 50.68), (21.86, 50.89),
           (21.97, 51.42), (21.85, 51.56), (21.21, 51.98), (21.03, 52.24), (20.70, 52.44), (20.20, 52.48),
           (19.70, 52.55), (19.07, 52.66), (18.60, 53.01), (18.42, 53.35), (18.75, 53.48), (18.93, 53.73),
           (18.79, 54.09), (18.94, 54.35)]


class PolandMap:
    """Outline + projection in stud units (map centred on the origin, `width` studs wide)."""

    def __init__(self, width=50.0):
        src = open(POLAND_TS).read()
        path = re.search(r'POLAND_PATH\s*=\s*"([^"]+)"', src).group(1)
        size = re.search(r"POLAND_SIZE\s*=\s*\{\s*width:\s*([\d.]+),\s*height:\s*([\d.]+)", src)
        self.w_px, self.h_px = float(size.group(1)), float(size.group(2))
        proj = re.search(r"\(lon - ([\d.]+)\) \* ([\d.]+) \* ([\d.]+),\s*\(([\d.]+) - lat\) \* ([\d.]+)", src)
        if proj:
            self.lon0, self.kx, self.k, self.lat0 = (float(proj.group(i)) for i in (1, 2, 3, 4))
        else:  # values of projectLonLat at the time of writing
            self.lon0, self.kx, self.k, self.lat0 = 14.128341283412851, 0.6156614753256583, 110.01577469788755, 54.83750415269779
        self.s = width / self.w_px
        pts = [(float(x), float(y)) for x, y in re.findall(r"(-?[\d.]+),(-?[\d.]+)", path)]
        self.poly = [self.px(x, y) for x, y in pts]
        xs, ys = [p[0] for p in self.poly], [p[1] for p in self.poly]
        self.cells = {(i, j) for i in range(math.floor(min(xs)) - 1, math.ceil(max(xs)) + 1)
                      for j in range(math.floor(min(ys)) - 1, math.ceil(max(ys)) + 1)
                      if _inside(i + 0.5, j + 0.5, self.poly)}
        self.border = {c for c in self.cells
                       if any((c[0] + dx, c[1] + dy) not in self.cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        self.interior = self.cells - self.border

    def px(self, x, y):
        """SVG pixel (y down) → studs (y up, centred)."""
        return ((x - self.w_px / 2) * self.s, -(y - self.h_px / 2) * self.s)

    def lonlat(self, lon, lat):
        """projectLonLat from poland.ts, then the same pixel → stud mapping as the outline."""
        return self.px((lon - self.lon0) * self.kx * self.k, (self.lat0 - lat) * self.k)

    @staticmethod
    def cell_of(x, y):
        return (math.floor(x), math.floor(y))

    def top(self, cell):
        """Height of the map surface on a cell (ring cells are two plates tall)."""
        return 2 * B.PLATE if cell in self.border else (B.PLATE if cell in self.cells else 0.0)

    def river_cells(self, waypoints, step=0.2):
        out = []
        pts = [self.lonlat(*p) for p in waypoints]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
            for k in range(n + 1):
                c = self.cell_of(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n)
                if c in self.interior and (not out or out[-1] != c) and c not in out:
                    out.append(c)
        return out


def _inside(x, y, poly):
    inside = False
    n = len(poly)
    for a in range(n):
        x1, y1 = poly[a]
        x2, y2 = poly[(a + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            inside = not inside
    return inside


def gold():
    mat = L.plastic("#F4C430", rough=0.22, name="coin_gold")
    mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.35
    return mat


def beacon(x, y, z, red, glow, start, coll=None):
    """Red stacked 2×2 round bricks with a glowing cap; they drop in one after another.
    (x, y) = stud corner the 2×2 bricks are centred on. Returns (parts, top point)."""
    parts = [B.add(B.part(2, 2, 3, "round"), red, (x, y, z), coll=coll),
             B.add(B.part(2, 2, 3, "round"), red, (x, y, z + B.BRICK), coll=coll),
             B.add(B.part(2, 2, 1, "round"), glow, (x, y, z + 2 * B.BRICK), coll=coll)]
    for k, ob in enumerate(parts):
        A.drop_in(ob, start + 3 * k, dur=9, height=6)
    return parts, (x, y, z + 2 * B.BRICK + B.PLATE + B.STUD_H)


def glow_light(loc, color, start, name="beacon_light", coll=None):
    """Small coloured point light (a glow pool on the white map); returns the light data."""
    data = bpy.data.lights.new(name, "POINT")
    data.color = L.srgb(color)[:3]
    data.shadow_soft_size = 0.6
    data.energy = 0.0
    ob = bpy.data.objects.new(name, data)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    A.show_from(ob, start)
    return data


def pulse(mat, start, end, lo, hi, period=40, phase=0.0, ramp=8, step=2, light=None, light_gain=0.0):
    """Emission: 0 → hi over `ramp` frames, then breathe between lo and hi. Optionally drives
    a light's energy in sync (energy = emission × light_gain)."""
    def key(f, v):
        L.key_emission(mat, f, v)
        if light is not None:
            light.energy = v * light_gain
            light.keyframe_insert("energy", frame=f)
    key(max(0, start - 1), 0.0)
    for f in range(start, end + 1, step):
        if f < start + ramp:
            v = hi * (f - start + 1) / ramp
        else:
            v = lo + (hi - lo) * (0.5 + 0.5 * math.cos(math.tau * ((f - start - ramp) / period + phase)))
        key(f, v)
