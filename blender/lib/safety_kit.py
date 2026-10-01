"""Shot kit for "safety": the passive-safety cross-section diorama.

A slice of earth floating in the studio: green ground on top, soil strata on the cut face, a
concrete shaft (~35 m) with the shared BWRX-300 cutaway (lib.vessel) at the bottom, the reactor
building with the isolation-condenser pool on top, the steam / condensate loop between them and a
small hamlet fed by a power line on the right. Shared libs are used unchanged; everything here is
local to the shot.

Coordinates: x → right, y → away from the camera (cut face at y = -1), z → up, ground at z = 0.
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

from . import bricks as B
from . import build as S
from . import look as L
from . import vessel as V

ROW0 = -0.2                 # top of the first soil row (the baseplate plate sits on it, studs at z=0)
ROWS = 33                   # brick rows of the soil slab
FLOOR_ROWS = 2              # bottom rows inside the shaft = concrete floor
BLOCK_X = (-34.0, 40.0)
BLOCK_Y = (-1.0, 12.0)
SHAFT_X = (-12.0, 12.0)     # outer faces of the shaft / building walls
INNER_X = (-11.0, 11.0)
BACK_Y = 8.0                # inner face of the back wall
BUILDING_ROWS = 7           # walls above ground
POOL_TOP = ROW0 + 6 * B.BRICK   # water surface (7.0)
PIPE_X = 9.5                # steam riser (+) / condensate return (-)
COIL_Z = (5.2, 2.8, 0.4)    # the three runs of the serpentine (pipe axis heights)
COIL_X = 7.0                # bends of the serpentine at ±COIL_X


def row_z(r):
    """Bottom z of soil row r (r = 0 directly under the ground)."""
    return ROW0 - B.BRICK * (r + 1)


BOTTOM = row_z(ROWS - 1)                       # underside of the slab (-39.8)
FLOOR_TOP = row_z(ROWS - FLOOR_ROWS) + B.BRICK      # shaft floor (-37.4)
VESSEL_Z0 = FLOOR_TOP + 3 * B.BRICK            # vessel drive housings stand on the floor

STRATA = (  # (rows, two shades) from the top down — colour = soil
    (2, ("#3D2817", "#4A311C")),    # topsoil
    (4, ("#E4CD9E", "#D5BA84")),    # sand
    (6, ("#9A6238", "#87542F")),    # clay
    (2, ("#A39B8D", "#8A8374")),    # gravel
    (8, ("#6B4226", "#5B3820")),    # loam
    (11, ("#56595D", "#46494E")),   # bedrock
)


# --- materials ---------------------------------------------------------------
def own(mat, name):
    """Independent copy of a cached material, so keyframes on it don't leak to other objects."""
    m = mat.copy()
    m.name = name
    return m


def bsdf(mat):
    return mat.node_tree.nodes["Principled BSDF"]


def set_emission(mat, hex_color, strength):
    b = bsdf(mat)
    b.inputs["Emission Color"].default_value = L.srgb(hex_color)
    b.inputs["Emission Strength"].default_value = strength


# --- primitives ----------------------------------------------------------------
def box(name, x0, x1, y0, y1, z0, z1, mat, coll=None):
    """Plain box (hidden filler / water volume)."""
    bm = bmesh.new()
    res = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=res["verts"])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    me.materials.append(mat)
    return ob


def run_x(x0, x1, yc, z, pick, rnd, d=1, sizes=(2, 3, 4, 6), studs=False, coll=None):
    """Fill [x0, x1] at height z with 1×n bricks of random length (running-bond look)."""
    out, x = [], x0
    while x1 - x > 1e-6:
        n = max(1, min(rnd.choice(sizes), int(round(x1 - x))))
        out.append(B.add(B.part(n, d, 3, "box", studs=studs), pick(), (x + n / 2, yc, z), coll=coll))
        x += n
    return out


# --- the slab of earth -----------------------------------------------------------
def soil(rnd, coll=None):
    """Cut face of the soil (one stud deep at y ∈ [-1, 0]) in colour strata, plus hidden filler."""
    out = []
    r = 0
    for rows, cols in STRATA:
        mats = [L.plastic(c, rough=0.55) for c in cols]
        for _ in range(rows):
            z = row_z(r)
            pick = lambda mats=mats: mats[0] if rnd.random() < 0.62 else mats[1]  # noqa: E731
            for x0, x1 in ((BLOCK_X[0], SHAFT_X[0]), (SHAFT_X[1], BLOCK_X[1])):
                out += run_x(x0, x1, -0.5, z, pick, rnd, sizes=(2, 3, 4, 4, 6, 6), coll=coll)
            r += 1
    fill = L.plastic("#2A1D12", rough=0.6)
    for x0, x1, y0 in ((BLOCK_X[0], SHAFT_X[0], 0.0), (SHAFT_X[1], BLOCK_X[1], 0.0), (SHAFT_X[0], SHAFT_X[1], BACK_Y + 1)):
        box("soil_fill", x0, x1, y0, BLOCK_Y[1], BOTTOM, ROW0, fill, coll=coll)
    # end caps: one column of long bricks on each side face so the slab's edges read as built
    for xc in (BLOCK_X[0] + 0.5, BLOCK_X[1] - 0.5):
        for r in range(ROWS):
            mat = L.plastic(_stratum(r)[1], rough=0.55)
            out.append(B.add(B.part(1, 12, 3, "box", studs=False), mat, (xc, 6.0, row_z(r)), coll=coll))
    return out


def _stratum(r):
    acc = 0
    for rows, cols in STRATA:
        acc += rows
        if r < acc:
            return cols
    return STRATA[-1][1]


def ground(coll=None):
    """Green baseplates on both sides of the building + a few trees."""
    grass = own(L.plastic(L.COL["green"]), "grass")      # less glossy: no grazing-angle sheen
    bsdf(grass).inputs["Coat Weight"].default_value = 0.0
    bsdf(grass).inputs["Roughness"].default_value = 0.5
    bsdf(grass).inputs["Specular IOR Level"].default_value = 0.25
    w_left = int(SHAFT_X[0] - BLOCK_X[0])
    w_right = int(BLOCK_X[1] - SHAFT_X[1])
    d = int(BLOCK_Y[1] - BLOCK_Y[0])
    B.baseplate(w_left, d, grass, name="ground_l", loc=(BLOCK_X[0] + 0.5, BLOCK_Y[0] + 0.5, 0.0))
    B.baseplate(w_right, d, grass, name="ground_r", loc=(SHAFT_X[1] + 0.5, BLOCK_Y[0] + 0.5, 0.0))
    trunk = L.plastic(L.COL["brown"])
    leaves = (L.plastic(L.COL["darkgreen"]), L.plastic("#2E7D32"))
    out = []
    for k, (x, y, size) in enumerate(((-30, 9, 2), (-24, 4, 2), (-19, 9, 1), (-16, 3, 1), (17, 9, 2), (23, 10, 1), (38, 8, 2), (36, 2, 1))):
        out += S.tree(x, y, trunk, leaves[k % 2], coll=coll, size=size)
    return out


def shaft(rnd, coll=None):
    """Concrete shaft (light cut faces, dark interior so the vessel reads), floor, ground-level slab
    and the white building above ground. Only the reactor vessel keeps orange cut edges."""
    concrete = L.plastic(L.COL["lightgrey"], rough=0.45)
    inner = L.plastic("#3A4047", rough=0.5)
    white = L.plastic(L.COL["white"])
    trim = L.plastic(L.COL["lightgrey"])
    g = {"walls": [], "floor": [], "slab": [], "building": []}
    for r in range(ROWS):
        z = row_z(r)
        for xc in (SHAFT_X[0] + 0.5, SHAFT_X[1] - 0.5):
            g["walls"].append(B.add(B.part(1, 10, 3, studs=False), concrete, (xc, 4.0, z), coll=coll))
        if r < ROWS - FLOOR_ROWS:
            g["walls"] += run_x(INNER_X[0], INNER_X[1], BACK_Y + 0.5, z, lambda: inner, rnd, sizes=(4, 6, 6), coll=coll)
        else:
            top = r == ROWS - FLOOR_ROWS
            g["floor"] += run_x(INNER_X[0], INNER_X[1], (BLOCK_Y[0] + BACK_Y + 1) / 2, z, lambda: concrete, rnd,
                                d=10, sizes=(4, 6), studs=top, coll=coll)
    # ground-level slab = pool floor, with gaps where the two pipes pass
    z = row_z(0)
    for x0, x1 in ((INNER_X[0], -PIPE_X - 0.5), (-PIPE_X + 0.5, PIPE_X - 0.5), (PIPE_X + 0.5, INNER_X[1])):
        g["slab"] += run_x(x0, x1, (BLOCK_Y[0] + BACK_Y) / 2, z, lambda: concrete, rnd, d=9, sizes=(6,), studs=True, coll=coll)
    # building above ground: white walls, light-grey top course with studs
    for k in range(BUILDING_ROWS):
        z = ROW0 + k * B.BRICK
        top = k == BUILDING_ROWS - 1
        mat = trim if top else white
        for xc in (SHAFT_X[0] + 0.5, SHAFT_X[1] - 0.5):
            g["building"].append(B.add(B.part(1, 10, 3, studs=top), mat, (xc, 4.0, z), coll=coll))
        g["building"] += run_x(INNER_X[0], INNER_X[1], BACK_Y + 0.5, z, lambda mat=mat: mat, rnd, sizes=(4, 6), studs=top, coll=coll)
    return g


def thin_rods(v, mat):
    """Show the control rods as thin blades in the plane of the front fuel row (they slide up between
    the glowing columns, like real cruciform blades between fuel assemblies) and move the back fuel
    row into the gaps behind them, so the blades visibly cover glowing fuel as they go in."""
    for col in v.rod_cols:
        for ob in col:
            ob.location.y = v.cy
            ob.scale = (0.46, 0.9, 1.0)
            ob.material_slots[0].material = mat
    for ob in v.objects["fuel"]:
        if ob.location.y > v.cy + 1.0:   # back row
            if ob.location.x > v.cx + 2.9:
                ob.hide_render = True
                ob.hide_viewport = True
            else:
                ob.location.x += 0.75


def clouds(count, mat, coll=None):
    """Little steam clouds: a 2×2 round plate with two 1×1 round plates, parented to an empty
    (animate the empty; scale 0 hides it)."""
    out = []
    for i in range(count):
        e = bpy.data.objects.new(f"puff_{i}", None)
        (coll or bpy.context.scene.collection).objects.link(e)
        for part, off in ((B.part(2, 2, 1, "round"), (0.0, 0.0, 0.0)), (B.part(1, 1, 1, "round"), (-1.15, 0.3, 0.3)),
                          (B.part(1, 1, 1, "round"), (0.95, -0.25, 0.55))):
            ob = B.add(part, mat, off, coll=coll)
            ob.parent = e
        out.append(e)
    return out


def pool(coll=None):
    """Isolation-condenser pool: a translucent water body (cut at the front) + trans-blue surface tiles."""
    water = own(L.trans(L.COL["trans_blue"]), "pool_water")
    bsdf(water).inputs["Alpha"].default_value = 0.42
    tiles = own(L.trans(L.COL["trans_blue"]), "pool_tiles")
    body = box("pool_body", INNER_X[0] + 0.02, INNER_X[1] - 0.02, -0.92, BACK_Y - 0.02, ROW0, POOL_TOP - 0.03, water, coll=coll)
    surface = S.roof(INNER_X[0] + 0.5, BLOCK_Y[0] + 0.5, int(INNER_X[1] - INNER_X[0]), int(BACK_Y - BLOCK_Y[0]), POOL_TOP - 0.03,
                     tiles, coll=coll)
    return body, surface, water, tiles


# --- pipes ---------------------------------------------------------------------------
def pipe(points, mat, coll=None):
    """1×1 round bricks along axis-aligned segments through `points` (the pipe axis, x/z moves at y=0).
    Vertical runs are stacked upright bricks (heights step by B.BRICK); horizontal runs lie along x."""
    upright = B.part(1, 1, 3, "round")
    lying = B.part(1, 1, 3, "round", studs=False)
    pts = [Vector(p) for p in points]
    out = []
    for a, b in zip(pts, pts[1:]):
        if abs(a.x - b.x) < 1e-6:  # vertical
            lo, hi = min(a.z, b.z), max(a.z, b.z)
            n = int(round((hi - lo) / B.BRICK)) + 1
            for i in range(n):
                out.append(B.add(upright, mat, (a.x, a.y, lo - B.BRICK / 2 + i * B.BRICK), coll=coll))
        else:
            lo, hi = min(a.x, b.x), max(a.x, b.x)
            n = max(1, int(round((hi - lo) / B.BRICK)))
            step = (hi - lo) / n
            for i in range(n):
                ob = B.add(lying, mat, (lo + i * step, a.y, a.z), coll=coll)
                ob.rotation_euler = (0, math.radians(90), 0)
                ob.scale = (1, 1, step / B.BRICK)
                out.append(ob)
    return out


def nozzle_left(v, level, coll=None):
    """Mirror of the vessel's feed nozzle on the left wall (condensate return enters the downcomer)."""
    obs = []
    for k in range(4):
        ob = B.add(B.part(1, 1, 3, "round", studs=False), v.steel, (v.cx - 5.0 + 0.5 - k, v.cy, v.z(level) + B.BRICK / 2), coll=coll)
        ob.rotation_euler = (0, math.radians(-90), 0)
        obs.append(ob)
    return obs


def polyline(points):
    """u ∈ [0, 1] → point along the polyline by arc length. Returns (fn, length)."""
    pts = [Vector(p) for p in points]
    segs = [(a, b, (b - a).length) for a, b in zip(pts, pts[1:])]
    total = sum(s[2] for s in segs)

    def fn(u):
        d = max(0.0, min(1.0, u)) * total
        for a, b, ln in segs:
            if d <= ln:
                return tuple(a + (b - a) * (d / ln if ln else 0.0))
            d -= ln
        return tuple(pts[-1])
    return fn, total


def sag(p0, p1, depth, n=6):
    """Points of a sagging cable between two supports (parabola)."""
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(tuple(p0[k] + (p1[k] - p0[k]) * t for k in range(3))[:2] + (p0[2] + (p1[2] - p0[2]) * t - depth * 4 * t * (1 - t),))
    return out


def cable(points, mat, name="cable", coll=None, radius=0.07):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for p, (x, y, z) in zip(spline.points, points):
        p.co = (x, y, z, 1)
    ob = bpy.data.objects.new(name, curve)
    (coll or bpy.context.scene.collection).objects.link(ob)
    curve.materials.append(mat)
    return ob


# --- motion ----------------------------------------------------------------------------
def flow(objs, path_fn, period, start, end, born=(-1e9, 1e9), grow=0.06, size=1.0):
    """Particles travel a looping path (object k offset by k/n of a lap). A particle is shown only on
    laps that *began* inside `born`, so a flow starts at its source and drains out naturally.
    Scale ramps up/down over the first/last `grow` of the path (no pops, no motion-blur streaks)."""
    n = len(objs)
    for k, ob in enumerate(objs):
        ob.hide_render = True
        ob.keyframe_insert("hide_render", frame=max(0, start - 1))
        shown = None
        for f in range(start, end + 1):
            s = (f - start) / period + k / n
            lap = math.floor(s)
            u = s - lap
            lap_start = start + (lap - k / n) * period
            vis = born[0] <= lap_start <= born[1]
            ob.location = path_fn(u)
            ob.keyframe_insert("location", frame=f)
            sc = size * (min(1.0, u / grow, (1 - u) / grow) if grow > 0 else 1.0)
            ob.scale = (sc, sc, sc)
            ob.keyframe_insert("scale", frame=f)
            if vis != shown:
                ob.hide_render = not vis
                ob.keyframe_insert("hide_render", frame=f)
                shown = vis
        ob.hide_render = True
        ob.keyframe_insert("hide_render", frame=end + 1)


def puffs(objs, start, end, area, z0, rise, period, seed=11, size=1.0):
    """Soft steam clouds drifting up from a water surface: each lap a new random spot,
    growing then fading (scale → 0) as they rise. Works on empties (scale hides children)."""
    rnd = random.Random(seed)
    n = len(objs)
    (x0, x1), (y0, y1) = area
    spots = {}
    for k, ob in enumerate(objs):
        for f in range(max(0, start - 1), end + 1):
            s = (f - start) / period + k / n
            lap = math.floor(s)
            u = s - lap
            vis = f >= start and start + (lap - k / n) * period >= start
            key = (k, lap)
            if key not in spots:
                spots[key] = (rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(-1, 1), rnd.uniform(0, math.tau))
            sx, sy, sw, rot = spots[key]
            ob.location = (sx + 0.9 * sw * u, sy, z0 + rise * (1 - (1 - u) ** 1.5))
            ob.keyframe_insert("location", frame=f)
            ob.rotation_euler = (0, 0, rot + 0.6 * u)
            ob.keyframe_insert("rotation_euler", frame=f)
            sc = size * (0.45 + 0.8 * u) * min(1.0, u / 0.12) * min(1.0, (1 - u) / 0.4) if vis else 0.0
            ob.scale = (sc, sc, sc)
            ob.keyframe_insert("scale", frame=f)


def key_value(owner, path, keys, index=None):
    """Keyframe a property through [(frame, value), ...] (default Bezier between keys)."""
    for f, v in keys:
        if index is None:
            setattr(owner, path, v)
            owner.keyframe_insert(path, frame=f)
        else:
            getattr(owner, path)[index] = v
            owner.keyframe_insert(path, index=index, frame=f)


def key_input(mat, socket, keys):
    """Keyframe a Principled BSDF input (e.g. 'Emission Strength', 'Alpha')."""
    inp = bsdf(mat).inputs[socket]
    for f, v in keys:
        inp.default_value = v
        inp.keyframe_insert("default_value", frame=f)


def rods_slam(v, start, travel_frames=18, settle=8, rebound=0.25, anticipation=3):
    """Control rods driven up into the core: a tiny unlatch dip, a hard accelerating drive, a stop
    with a small rebound. Returns the impact frame."""
    lift = (V.CORE[1] - V.CORE[0]) * B.BRICK
    go = start + anticipation
    impact = go + travel_frames
    for col in v.rod_cols:
        for ob in col:
            x, y, z = ob.location
            for f in range(start, impact + settle + 1):
                if f <= go:
                    dz = -0.12 * math.sin(math.pi / 2 * (f - start) / max(1, anticipation))
                elif f <= impact:
                    t = (f - go) / travel_frames
                    dz = -0.12 * (1 - t) + lift * t * t * (0.35 + 0.65 * t)   # accelerating drive
                else:
                    t = (f - impact) / settle
                    dz = lift - rebound * math.sin(math.pi * t) * (1 - t)
                ob.location = (x, y, z + dz)
                ob.keyframe_insert("location", frame=f)
    return impact


# --- camera ------------------------------------------------------------------------------
def direction(yaw, pitch):
    """View direction for yaw (deg, + looks toward +x) and pitch (deg, - looks down)."""
    y, p = math.radians(yaw), math.radians(pitch)
    return Vector((math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), math.sin(p)))


def pose(target, yaw, pitch, dist):
    """(camera location, target) for a camera `dist` away from `target` looking along (yaw, pitch)."""
    t = Vector(target)
    return tuple(t - direction(yaw, pitch) * dist), tuple(t)


def hermite(keys, stops=()):
    """Smooth curve through [(frame, value-tuple), ...]: Catmull-Rom tangents at interior keys,
    zero velocity at both ends and at frames listed in `stops`. Returns f → tuple."""
    keys = sorted(keys, key=lambda k: k[0])
    fs = [k[0] for k in keys]
    ps = [tuple(float(x) for x in k[1]) for k in keys]
    n, dim = len(keys), len(ps[0])
    tang = []
    for i in range(n):
        if i in (0, n - 1) or fs[i] in stops:
            tang.append((0.0,) * dim)
        else:
            span = fs[i + 1] - fs[i - 1]
            tang.append(tuple((ps[i + 1][d] - ps[i - 1][d]) / span for d in range(dim)))

    def at(f):
        if f <= fs[0]:
            return ps[0]
        if f >= fs[-1]:
            return ps[-1]
        i = max(j for j in range(n - 1) if fs[j] <= f)
        dt = fs[i + 1] - fs[i]
        t = (f - fs[i]) / dt
        h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
        h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
        return tuple(h00 * ps[i][d] + h10 * dt * tang[i][d] + h01 * ps[i + 1][d] + h11 * dt * tang[i + 1][d]
                     for d in range(dim))
    return at


def bake_fn(owner, path, first, last, fn):
    for f in range(first, last + 1):
        setattr(owner, path, fn(f))
        owner.keyframe_insert(path, frame=f)
