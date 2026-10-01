"""Shape builders: assemble bigger forms out of individual bricks (each a separate object,
so they can be animated piece by piece)."""
import math
import random

from . import bricks as B


def ring(cx, cy, z0, levels, radius, mats, part=None, start_level=0, coll=None, gap=1.0, stagger=False, arc=(0.0, 1.0)):
    """Cylindrical wall of 1×1 round bricks. `mats(level, k)` → material. Returns bricks bottom-up."""
    part = part or B.part(1, 1, 3, "round")
    out = []
    n = max(6, int(round(2 * math.pi * radius / gap)))
    for level in range(start_level, start_level + levels):
        offset = (level % 2) * 0.5 if stagger else 0.0
        for k in range(n):
            frac = (k + offset) / n
            if not (arc[0] <= frac < arc[1]):
                continue  # partial ring (cutaways)
            a = frac * math.tau
            ob = B.add(part, mats(level, k), (cx + math.cos(a) * radius, cy + math.sin(a) * radius, z0 + level * B.BRICK), coll=coll)
            out.append(ob)
    return out


def hyperboloid(cx, cy, levels, r_base, r_waist, r_top, mat, coll=None):
    """Cooling tower: rings whose radius follows a smooth waist profile."""
    out = []
    for level in range(levels):
        t = level / max(1, levels - 1)
        waist_t = 0.72
        if t < waist_t:
            r = r_base + (r_waist - r_base) * math.sin(t / waist_t * math.pi / 2)
        else:
            r = r_waist + (r_top - r_waist) * ((t - waist_t) / (1 - waist_t)) ** 2
        out += ring(cx, cy, 0, 1, r, lambda *_: mat, start_level=level, coll=coll, gap=1.05)
    return out


def box_walls(x0, y0, w, d, levels, mat, window_mat=None, window_rows=(), z0=0.0, coll=None):
    """Rectangular building shell of 1×1 bricks; windows on given levels (every 2nd stud)."""
    out, windows = [], []
    for level in range(levels):
        for i in range(w):
            for j in range(d):
                if 0 < i < w - 1 and 0 < j < d - 1:
                    continue
                is_window = window_mat is not None and level in window_rows and ((i + j) % 2 == 1) and (
                    i in (0, w - 1) or j in (0, d - 1)) and not (i in (0, w - 1) and j in (0, d - 1))
                ob = B.add(B.part(1, 1, 3, studs=level == levels - 1), window_mat if is_window else mat,
                           (x0 + i, y0 + j, z0 + level * B.BRICK), coll=coll)
                (windows if is_window else out).append(ob)
    return out, windows


def roof(x0, y0, w, d, z, mat, coll=None, tile=True):
    """Flat roof of 2×2 tiles/plates (falls back to 1×1 at odd edges)."""
    out = []
    for i in range(0, w, 2):
        for j in range(0, d, 2):
            pw, pd = min(2, w - i), min(2, d - j)
            ob = B.add(B.part(pw, pd, 1, "tile" if tile else "box"), mat,
                       (x0 + i + (pw - 1) / 2, y0 + j + (pd - 1) / 2, z), coll=coll)
            out.append(ob)
    return out


def voxel_sphere(center, radius, mats, part=None, coll=None, seed=1):
    """Ball of 1×1 bricks (nucleus). mats: list of materials picked at random."""
    rnd = random.Random(seed)
    part = part or B.part(1, 1, 3, "round")
    cx, cy, cz = center
    out = []
    r = int(math.ceil(radius))
    for i in range(-r, r + 1):
        for j in range(-r, r + 1):
            for k in range(-r, r + 1):
                if i * i + j * j + (k * 1.2) ** 2 <= radius * radius:
                    ob = B.add(part, rnd.choice(mats), (cx + i, cy + j, cz + k * B.BRICK), coll=coll)
                    ob["vox"] = (i, j, k)
                    out.append(ob)
    return out


def raster_polygon(points, mat, z=0.0, coll=None, part=None):
    """Fill a polygon (list of (x, y) in stud units) with 1×1 plates — for brick maps."""
    part = part or B.part(1, 1, 1, "box")
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    out = []
    for i in range(int(min(xs)), int(max(xs)) + 1):
        for j in range(int(min(ys)), int(max(ys)) + 1):
            if _inside(i + 0.5, j + 0.5, points):
                out.append(B.add(part, mat, (i + 0.5, j + 0.5, z), coll=coll))
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


def tree(x, y, trunk, leaves, coll=None, size=2):
    out = [B.add(B.part(1, 1, 3, "round"), trunk, (x, y, 0), coll=coll)]
    out.append(B.add(B.part(size, size, 6, "cone"), leaves, (x, y, B.BRICK), coll=coll))
    if size > 1:
        out.append(B.add(B.part(1, 1, 3, "cone"), leaves, (x, y, B.BRICK + 6 * B.PLATE), coll=coll))
    return out


def house(x, y, wall, roof_mat, window, coll=None, w=4, d=3, levels=2):
    """Small house: walls, two lit-able windows, a stepped roof. Returns (bricks, windows)."""
    bricks, windows = box_walls(x, y, w, d, levels, wall, window, window_rows=(1,), coll=coll)
    z = levels * B.BRICK
    for step in range(2):
        bricks += roof(x - 0.5 + step, y - 0.5, w + 1 - 2 * step, d + 1, z + step * B.PLATE * 2, roof_mat, coll=coll, tile=False)
    return bricks, windows
