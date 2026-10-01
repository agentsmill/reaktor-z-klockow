"""Extras for the diorama shots ("why", "outro"): coal plant, rain cloud, cable pulses,
day/night lighting."""
import math
import random

from . import anim as A
from . import bricks as B
from . import build as S
from . import look as L

CABLE = [(25, -9, 3.0), (24, -2, 8.6), (22, 8.5, 8.6), (20, 19, 8.6), (6, 18, 3.6)]
COAL_SITE = (-27.0, -12.0)


def polyline(points):
    """u in 0..1 → point along the polyline (by length)."""
    segs = []
    total = 0.0
    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        segs.append((a, b, length))
        total += length

    def at(u):
        d = u * total
        for a, b, length in segs:
            if d <= length:
                t = d / length
                return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
            d -= length
        return points[-1]

    return at


def cable_pulses(start, end, count=10, period=70):
    mat = L.glow(L.COL["electric"], 9.0, name="pulse", base=L.COL["yellow"])
    obs = [B.add(B.part(1, 1, 1, "round", studs=False), mat, CABLE[0]) for _ in range(count)]
    for ob in obs:
        ob.scale = (0.7, 0.7, 0.7)
    A.stream(obs, start, end, polyline(CABLE), period)
    return obs


def coal_plant(x, y, seed=11):
    """Old coal plant: dark boiler house + striped chimney. Returns (bricks, chimney_top)."""
    dark = L.plastic(L.COL["darkgrey"])
    grey = L.plastic(L.COL["grey"])
    red = L.plastic(L.COL["red"])
    walls, _ = S.box_walls(int(x) - 3, int(y) - 2, 7, 5, 4, dark)
    roof = S.roof(int(x) - 3.5, int(y) - 2.5, 8, 6, 4 * B.BRICK, grey)
    chimney = S.ring(x + 5, y + 2, 0, 14, 1.3, lambda level, k: red if level in (11, 12) else grey)
    return walls + roof + chimney, (x + 5, y + 2, 14 * B.BRICK)


def smoke(top, start, end, count=5, period=110):
    mat = L.trans("#9AA0A8", rough=0.5)
    obs = [B.add(B.part(2, 2, 3, "round", studs=False), mat, top) for _ in range(count)]
    tx, ty, tz = top
    A.stream(obs, start, end, lambda u: (tx + 3 * u, ty + 1.5 * u, tz + 12 * u), period)
    for k, ob in enumerate(obs):  # puffs grow as they rise
        for f in range(start, end + 1):
            u = ((f - start) / period + k / count) % 1.0
            s = 0.5 + 2.2 * u
            ob.scale = (s, s, s * 0.7)
            ob.keyframe_insert("scale", frame=f)
    return obs


def blow_away(obs, start, end, seed=4):
    """Bricks lift off and fly away, top first (taking a building apart)."""
    rnd = random.Random(seed)
    ordered = sorted(obs, key=lambda o: -o.location.z)
    for k, ob in enumerate(ordered):
        t0 = start + int(k / max(1, len(ordered)) * (end - start - 12))
        x, y, z = ob.location
        dx, dy = rnd.uniform(-6, 6), rnd.uniform(-6, 6)
        A.bake(ob, t0, t0 + 14, lambda t, x=x, y=y, z=z, dx=dx, dy=dy: (x + dx * t, y + dy * t, z + 40 * t * t))
        A.hide_from(ob, t0 + 15)


def rain_cloud(center, start, end, seed=8):
    """A brick cloud drifting over with trans-blue raindrops."""
    rnd = random.Random(seed)
    white = L.plastic("#D9DEE5", rough=0.5)
    cx, cy, cz = center
    cloud = []
    for _ in range(26):
        ox, oy, oz = rnd.uniform(-6, 6), rnd.uniform(-2.5, 2.5), rnd.uniform(-1, 1.5)
        cloud.append(B.add(B.part(2, 2, 3, "round"), white, (cx + ox, cy + oy, cz + oz)))
    for ob in cloud:
        x, y, z = ob.location
        A.show_from(ob, start)
        A.hide_from(ob, end + 1)
        A.bake(ob, start, end, lambda t, x=x, y=y, z=z: (x - 24 + 48 * t, y, z))
    drops = [B.add(B.part(1, 1, 1, "round", studs=False), L.trans(L.COL["trans_blue"]), (cx, cy, cz)) for _ in range(30)]
    offsets = [(rnd.uniform(-6, 6), rnd.uniform(-2, 2)) for _ in drops]
    for ob, (ox, oy) in zip(drops, offsets):
        A.show_from(ob, start + 10)
        A.hide_from(ob, end - 9)
        phase = rnd.random()
        prev = None
        for f in range(start + 10, end - 9):
            t = (f - start) / (end - start)
            fall = ((f - start) / 18 + phase) % 1.0
            ob.location = (cx - 24 + 48 * t + ox, cy + oy, cz - fall * cz)
            ob.keyframe_insert("location", frame=f)
            if prev is not None and fall < prev:  # drop restarts at the cloud: hide the jump
                A.hide_span(ob, f - 1, f, end - 10)
            prev = fall
    return cloud + drops


def light_cycle(lights, world, keys):
    """keys: list of (frame, mood) where mood ∈ {"day", "dusk", "night"}; keys light energy/colour and world strength."""
    moods = {
        "day": {"key": (52000, "#FFE2B8"), "rim": (60000, "#9CC4FF"), "fill": (9000, "#DDE6FF"), "world": 0.55},
        "dusk": {"key": (26000, "#FF9A5A"), "rim": (50000, "#7FA8FF"), "fill": (5000, "#C9B8FF"), "world": 0.35},
        "night": {"key": (11000, "#7C96FF"), "rim": (42000, "#6F8BFF"), "fill": (3000, "#5A6CB0"), "world": 0.32},
    }
    key, rim, fill = lights
    for frame, mood in keys:
        m = moods[mood]
        for ob, name in ((key, "key"), (rim, "rim"), (fill, "fill")):
            energy, color = m[name]
            ob.data.energy = energy * ob.get("energy_scale", 1.0)
            ob.data.color = L.srgb(color)[:3]
            ob.data.keyframe_insert("energy", frame=frame)
            ob.data.keyframe_insert("color", frame=frame)
        bg = world.node_tree.nodes["Background"]
        bg.inputs["Strength"].default_value = m["world"]
        bg.inputs["Strength"].keyframe_insert("default_value", frame=frame)
