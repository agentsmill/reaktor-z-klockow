"""Natural circulation inside the shared lib.vessel cutaway (used by the power and circulation shots).

Physics shown (BWR, natural circulation, no recirculation pumps):
  core heats the water → steam bubbles form → the light two-phase mixture rises up the tall chimney →
  separators: steam goes on up through the dryer into the dome (→ steam nozzle), the separated water
  turns outwards → cooler, denser water sinks down the down-comer between chimney and vessel wall →
  turns under the core in the lower plenum → back up into the core.

All flows use power_kit.flow (emitted progressively, hidden on wrap → no motion-blur streaks).
"""
import math
import random

from . import look as L
from . import vessel as V
from .power_kit import Path, ends_scale, flow, key_light, plates, point_light


def cool_water_material():
    """Down-comer water: trans-blue with a soft inner glow so it reads against the water volume."""
    mat = L.glow(L.COL["trans_blue"], 1.4, name="cool_water", base="#3D7DDB")
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.12
    bsdf.inputs["Coat Weight"].default_value = 0.5
    return mat


def chimney_bubbles(v, start, end, columns=(-1.6, -0.5, 0.6, 1.7), per_column=6, period=60, ys=(-0.1, 0.3),
                    size=1, seed=1, mat=None, z_from=None, z_to=None, wobble=0.25, stagger=True, grow=True, last=None):
    """White plates (steam bubbles in water) rising from the top of the core to the separators."""
    rnd = random.Random(seed)
    z_lo = v.z(V.CORE[1]) - 0.3 if z_from is None else z_from
    z_hi = v.z(V.WATER_LEVEL - 1) - 0.2 if z_to is None else z_to
    out = []
    for c in columns:
        yy = rnd.uniform(*ys)
        obs = plates(per_column, mat or v.bubble_mat, size=size, name="bubble")
        ph, amp = rnd.uniform(0, math.tau), wobble * rnd.uniform(0.6, 1.2)
        per = max(12, period + rnd.randint(-period // 8, period // 8))
        path = Path([(v.cx + c, v.cy + yy, z_lo), (v.cx + c, v.cy + yy, z_hi)])
        flow(obs, start + (rnd.randint(0, per // 5) if stagger else 0), end, path, per,
             scale_fn=(lambda u: ends_scale(u, 0.12, 0.1) * (0.65 + 0.45 * u)) if grow else (lambda u: ends_scale(u, 0.12, 0.1)),
             jitter=lambda k, trip, u, ph=ph, amp=amp: (amp * math.sin(u * 8.0 + ph + k * 1.7 + trip), 0.0, 0.0),
             last=last)
        out += obs
    return out


def core_bubbles(v, start, end, xs=(-2.25, -0.75, 0.75, 2.25), per_column=7, period=110, seed=11, mat=None,
                 y_core=0.8, y_chim=0.15, wobble=0.22, last=None):
    """Bubbles born small in the gaps between the fuel columns, growing as they rise out of the core
    and up the chimney (void fraction grows with height) — boiling happens in the core itself."""
    rnd = random.Random(seed)
    z = v.z
    out = []
    core_top = z(V.CORE[1])
    for x in xs:
        xc = max(-1.9, min(1.9, x * 0.85))
        path = Path([(v.cx + x, v.cy + y_core, z(V.CORE[0]) + 0.6), (v.cx + x, v.cy + y_core, core_top),
                     (v.cx + xc, v.cy + y_chim, core_top + 1.9), (v.cx + xc, v.cy + y_chim, z(V.WATER_LEVEL - 1) - 0.2)])
        frac = (core_top - z(V.CORE[0]) - 0.6) / path.length
        per = max(16, period + rnd.randint(-period // 10, period // 10))
        obs = plates(per_column, mat or v.bubble_mat, name="bubble")
        ph, amp = rnd.uniform(0, math.tau), wobble * rnd.uniform(0.7, 1.2)
        flow(obs, start + rnd.randint(0, per // 5), end, path, per,
             scale_fn=lambda u, frac=frac: ends_scale(u, 0.04, 0.07) * (0.42 + 0.7 * max(0.0, min(1.0, (u - frac * 0.8) / (1 - frac * 0.8))) ** 0.8),
             jitter=lambda k, trip, u, ph=ph, amp=amp, frac=frac: (amp * max(0.0, (u - frac) / (1 - frac)) * math.sin(u * 9.0 + ph + k * 1.3 + trip), 0.0, 0.0),
             last=last)
        out += obs
    return out


def downcomer_path(v, side, y=0.25, y_low=-0.3, top_level=16.6, into_core=True):
    """Separator edge → out to the down-comer → down along the wall → under the core → up into it."""
    cx, cy, z = v.cx, v.cy, v.z
    xd = side * (V.CHIMNEY_R + 1.0)
    pts = [(cx + side * 2.7, cy + y, z(top_level + 0.3)),
           (cx + xd, cy + y, z(top_level - 0.4)),
           (cx + xd, cy + y, z(2.5)),
           (cx + side * 2.9, cy + y_low, z(1.35)),
           (cx + side * 1.4, cy + y_low, z(1.3))]
    if into_core:
        pts.append((cx + side * 1.2, cy + y_low, z(V.CORE[0]) - 0.3))
    return Path(pts)


def downflow(v, start, end, per_side=7, period=150, mat=None, sides=(-1, 1), seed=2, y=0.25, last=None, h=1):
    """Cooler water sinking down both sides and turning under the core (emitted progressively).
    h: plate height in plates (2 = chunkier 'drops', easier to read in close-ups)."""
    rnd = random.Random(seed)
    out = []
    for side in sides:
        obs = plates(per_side, mat or v.water_mat, name="downflow", h=h)
        flow(obs, start + rnd.randint(0, period // per_side), end, downcomer_path(v, side, y=y), period,
             scale_fn=lambda u: ends_scale(u, 0.05, 0.08), last=last)
        out += obs
    return out


def dome_steam_path(v, x=0.0, y=-0.15):
    """Steam leaving the separators, through the dryer, into the steam nozzle (vessel-internal part)."""
    z = v.z
    noz = V.LEVELS - 2
    zn = z(noz) + 0.6
    return Path([(v.cx + x, v.cy + y, z(V.WATER_LEVEL + 1) + 0.2),
                 (v.cx + x, v.cy + y, z(V.WATER_LEVEL + 3) - 0.2),
                 (v.cx + V.R - 1.4, v.cy + y, zn - 0.2),
                 (v.cx + V.R - 0.5, v.cy, zn)])


def chimney_lights(v, coll=None):
    """Two warm point lights inside the chimney (keyed with chimney_heat)."""
    lights = []
    for lv in (V.CORE[1] + 2.0, V.WATER_LEVEL - 2.5):
        lights.append(point_light("chimney_heat", (v.cx, v.cy + 0.9, v.z(lv)), L.COL["heat"], 0.0, 1.6, coll))
    return lights


def chimney_heat(lights, keys):
    """keys: [(frame, energy_per_light)]."""
    for f, e in keys:
        for lt in lights:
            key_light(lt, f, e)
