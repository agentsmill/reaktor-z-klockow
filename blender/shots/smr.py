"""SMR — "SMR to mały reaktor modułowy: kilka razy mniejszy od dużego bloku jądrowego
i budowany z gotowych modułów z fabryki — trochę jak z klocków."

1. Opening (Remotion puts S·M·R over the top half): a compact SMR plant on its own small
   baseplate, low in frame, slow tilt-shift orbit; the reactor cap hops on "reaktor", the
   three hall modules hop in turn on "modułowy".
2. "kilka" → "dużego": a big conventional plant slides in on its own baseplate and builds
   itself ring by ring — two hyperboloid cooling towers with cotton-wool steam, a
   containment dome, a turbine hall, a vent stack — while the camera cranes up and back
   to frame both (same trees on both plates = scale reference).
3. "modułów" → "fabryki" → "klocków": a saw-tooth factory assembles on the other side, a
   toy low-loader drives three white prefab modules out of it to the SMR, and the modules
   hop onto the hall bays; the last (middle) one clicks on exactly on "klocków", then the
   hall windows light up.
Anchors: big_plant, smr_plant, factory.
"""
import math
import random

import bpy

from lib import anchors
from lib import anim as A
from lib import bricks as B
from lib import build as S
from lib import look as L
from lib import smr_kit as K

# --- layout (studs) -----------------------------------------------------------
TOWER, TOWER_R, TOWER_LEVELS = (-8.0, 1.0), 3.8, 8
HALL_X0, HALL_Y0, HALL_LEVELS = -3, -3, 3          # three 4×6 bays along +x
BAYS = [(HALL_X0 + 1.5 + 4 * k, HALL_Y0 + 2.5) for k in range(3)]
HALL_TOP = HALL_LEVELS * B.BRICK + B.PLATE         # modules land here
ROAD_Y = -7.5
COOLING = [(-64.0, 6.0), (-45.0, 9.0)]
CT_LEVELS = 34
DOME, DOME_R, DOME_LEVELS = (-27.0, -7.0), 6.5, 8
FACTORY_X0, FACTORY_Y0, FACTORY_W, FACTORY_D, FACTORY_LEVELS = 17, -11, 20, 14, 4
TRUCK_HOME, TRUCK_STOP = 27.0, 2.0   # low-loader origin inside the factory / parked at the hall


def materials():
    return {
        "ground": L.plastic(L.COL["green"]),
        "white": L.plastic(L.COL["white"]),
        "lightgrey": L.plastic(L.COL["lightgrey"]),
        "grey": L.plastic(L.COL["grey"]),
        "dark": L.plastic(L.COL["darkgrey"]),
        "road": L.plastic("#2F3437", rough=0.5),
        "brown": L.plastic(L.COL["brown"]),
        "leaves": L.plastic(L.COL["darkgreen"]),
        "leaves2": L.plastic("#2E7D32"),
        "glass": L.trans("#BFD7F2"),
        "cab": L.plastic(L.COL["blue"]),
        "smr_glass": L.glow("#FFDDA6", 0.0, name="smr_windows", base="#BFD7F2"),  # lights on at the end
    }


def trees(spots, m, rnd, lowpoly=False):
    out = []
    for x, y in spots:
        parts = S.tree(x, y, m["brown"], m["leaves"] if rnd.random() > 0.4 else m["leaves2"], size=rnd.choice([1, 2, 2]))
        out.append(K.merge(parts, "tree", origin=(x, y, 0), lowpoly=lowpoly))
    return out


# --- builders -------------------------------------------------------------------
def build_smr(m, rnd):
    B.baseplate(30, 22, m["ground"], name="smr_plate", loc=(-15, -11, 0))
    tx, ty = TOWER
    S.ring(tx, ty, 0, TOWER_LEVELS, TOWER_R, lambda level, k: m["lightgrey"] if level in (5, 6) else m["white"])
    roof_z = TOWER_LEVELS * B.BRICK
    for i in range(-4, 5):
        for j in range(-4, 5):
            if i * i + j * j <= (TOWER_R - 0.6) ** 2:
                B.add(B.part(1, 1, 1, "round"), m["white"], (tx + i, ty + j, roof_z))
    cap = B.add(B.part(2, 2, 3, "round"), m["lightgrey"], (tx, ty, roof_z + B.PLATE))

    bays = []
    for k in range(3):
        x0 = HALL_X0 + 4 * k
        walls, wins = S.box_walls(x0, HALL_Y0, 4, 6, HALL_LEVELS, m["lightgrey"], m["smr_glass"], window_rows=(1,))
        roof = S.roof(x0, HALL_Y0, 4, 6, HALL_LEVELS * B.BRICK, m["lightgrey"], tile=False)
        base = lambda ob: m["grey"] if ob.location.z < 0.1 and ob.material_slots[0].material == m["lightgrey"] else ob.material_slots[0].material  # noqa: E731
        bays.append(K.merge(walls + wins + roof, f"bay_{k}", origin=(*BAYS[k], 0), mat_fn=base))

    road = [B.add(B.part(2, 2, 1, "tile"), m["road"], (x + 0.5, y + 0.5, 0)) for x in range(-12, 14, 2) for y in (-10, -8, -6)]
    K.merge(road, "road_smr")

    spots = [(-13, 8), (-11, 9), (-14, 4), (-3, 8), (1, 9), (12, 3), (13, 9), (-14, -3)]
    trees(spots, m, rnd)

    # power line: two pylons behind the hall carry the output off the plate
    for px, py in ((5.0, 6.0), (10.0, 9.5)):
        pylon = [B.add(B.part(1, 1, 3, "round"), m["grey"], (px, py, k * B.BRICK)) for k in range(6)]
        pylon.append(B.add(B.part(5, 1, 1), m["dark"], (px, py, 6 * B.BRICK)))
        K.merge(pylon, "pylon", origin=(px, py, 0))
    curve = bpy.data.curves.new("smr_cable", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.05
    spline = curve.splines.new("POLY")
    pts = [(6.5, 2.0, 4.2), (5.0, 6.0, 7.6), (10.0, 9.5, 7.6), (14.0, 12.5, 5.5)]
    spline.points.add(len(pts) - 1)
    for pt, (x, y, z) in zip(spline.points, pts):
        pt.co = (x, y, z, 1)
    cable = bpy.data.objects.new("smr_cable", curve)
    bpy.context.scene.collection.objects.link(cable)
    cable.data.materials.append(m["dark"])
    return {"bays": bays, "cap": cap}


def build_modules(m):
    mods = []
    for k in range(3):
        walls, wins = S.box_walls(-1.5, -2.5, 4, 6, 2, m["white"], m["smr_glass"], window_rows=(1,))
        roof = S.roof(-1.5, -2.5, 4, 6, 2 * B.BRICK, m["white"], tile=False)
        mods.append(K.merge(walls + wins + roof, f"module_{k}"))
    return mods


def build_big(m, rnd):
    g = {"plate": list(B.baseplate(58, 44, m["ground"], name="big_plate", loc=(-76, -22, 0)))}
    g["towers"] = []
    for cx, cy in COOLING:
        objs = S.hyperboloid(cx, cy, CT_LEVELS, 8.5, 6.0, 6.6, m["white"])
        rings = []
        for k, level in enumerate(K.by_level(objs)):
            band = m["lightgrey"] if k in (CT_LEVELS - 5, CT_LEVELS - 4) else m["white"]
            rings.append(K.merge(level, "ct_ring", origin=(cx, cy, k * B.BRICK), lowpoly=True, mat_fn=lambda ob, b=band: b))
        g["towers"].append(rings)

    # containment: cylinder + stepped dome + cap
    dx, dy = DOME
    objs = S.ring(dx, dy, 0, DOME_LEVELS, DOME_R, lambda level, k: m["lightgrey"] if level == 0 else m["white"])
    for k in range(5):
        r = math.sqrt(DOME_R ** 2 - (k * B.BRICK + 0.6) ** 2)
        objs += S.ring(dx, dy, 0, 1, r, lambda *_: m["white"], start_level=DOME_LEVELS + k)
    g["dome"] = [K.merge(level, "dome_ring", origin=(dx, dy, k * B.BRICK), lowpoly=True)
                 for k, level in enumerate(K.by_level(objs))]
    top_z = (DOME_LEVELS + 5) * B.BRICK
    cap = [B.add(B.part(1, 1, 1, "round"), m["white"], (dx + i, dy + j, top_z))
           for i in range(-3, 4) for j in range(-3, 4) if i * i + j * j <= 7.5]
    cap.append(B.add(B.part(2, 2, 3, "round"), m["lightgrey"], (dx, dy, top_z + B.PLATE)))
    g["dome"].append(K.merge(cap, "dome_cap", origin=(dx, dy, top_z), lowpoly=True))

    # turbine hall + auxiliary block
    walls, wins = S.box_walls(-62, -16, 24, 10, 6, m["lightgrey"], m["glass"], window_rows=(3, 4))
    g["hall"] = [K.merge(level, "big_hall", origin=(-50.5, -11.5, k * B.BRICK)) for k, level in enumerate(K.by_level(walls + wins))]
    g["hall"].append(K.merge(S.roof(-62.5, -16.5, 25, 11, 6 * B.BRICK, m["dark"]), "big_hall_roof", origin=(-50.5, -11.5, 6 * B.BRICK)))
    walls, _ = S.box_walls(-38, -15, 5, 9, 5, m["white"])
    g["aux"] = [K.merge(level, "aux", origin=(-36, -11, k * B.BRICK)) for k, level in enumerate(K.by_level(walls))]
    g["aux"].append(K.merge(S.roof(-38, -15, 5, 9, 5 * B.BRICK, m["lightgrey"], tile=False), "aux_roof", origin=(-36, -11, 5 * B.BRICK)))

    # vent stack (2×2 round), banded top
    sx, sy = -73.0, -3.0  # left of the towers, clear of the label gap above the dome
    g["stack"] = [K.merge([B.add(B.part(2, 2, 3, "round"), m["lightgrey"] if k in (21, 23) else m["white"], (sx, sy, k * B.BRICK))],
                          "stack", origin=(sx, sy, k * B.BRICK), lowpoly=True) for k in range(25)]

    spots = [(-74, -20), (-71, -20), (-74, 18), (-58, 19), (-34, 19), (-21, -20), (-29, 18), (-74, -9), (-68, -19), (-20, 0)]
    g["trees"] = trees(spots, m, rnd, lowpoly=True)
    return g


def build_factory(m, rnd):
    g = {"plate": list(B.baseplate(24, 22, m["ground"], name="factory_plate", loc=(15, -11, 0)))}
    road = [B.add(B.part(2, 2, 1, "tile"), m["road"], (x + 0.5, y + 0.5, 0)) for x in range(14, 18, 2) for y in (-10, -8, -6)]
    g["plate"].append(K.merge(road, "road_factory"))

    levels = []
    x0, y0, w, d = FACTORY_X0, FACTORY_Y0, FACTORY_W, FACTORY_D
    for level in range(FACTORY_LEVELS):
        bricks = []
        for i in range(w):
            for j in range(d):
                if 0 < i < w - 1 and 0 < j < d - 1:
                    continue
                if i == 0 and 1 <= j <= 7:
                    continue  # gate facing the SMR site (road passes through)
                front = j == 0 and 0 < i < w - 1
                window = front and level in (1, 2) and i % 3 != 0
                mat = m["glass"] if window else (m["dark"] if level == 0 else m["lightgrey"])
                bricks.append(B.add(B.part(1, 1, 3, studs=level == FACTORY_LEVELS - 1), mat, (x0 + i, y0 + j, level * B.BRICK)))
        levels.append(K.merge(bricks, "factory_wall", origin=(x0 + w / 2 - 0.5, y0 + d / 2 - 0.5, level * B.BRICK)))
    g["walls"] = levels

    # inner dark floor so the open gate reads as a deep interior
    g["walls"][0:0] = [K.merge([B.add(B.part(2, 2, 1, "tile"), m["dark"], (x + 0.5, y + 0.5, 0))
                                for x in range(x0 + 1, x0 + w - 2, 2) for y in range(y0 + 1, y0 + d - 2, 2)],
                               "factory_floor", origin=(x0 + w / 2, y0 + d / 2, 0))]

    teeth = []
    z = FACTORY_LEVELS * B.BRICK
    for k in range(5):
        ob = K.slope(4, d, 0.4, 2.4, m["dark"], L.trans("#9CC4F0"), name=f"tooth_{k}")
        ob.location = (x0 - 0.5 + 2 + 4 * k, y0 - 0.5 + d / 2, z)
        teeth.append(ob)
    g["teeth"] = teeth

    g["chimney"] = [B.add(B.part(2, 2, 3, "round"), m["white"] if k in (7, 8) else m["grey"], (37.5, 5.5, k * B.BRICK))
                    for k in range(9)]
    g["trees"] = trees([(16, 8), (19, 9), (23, 8), (28, 9), (33, 8), (37, -9), (16, 4)], m, rnd)
    return g


# --- shot -----------------------------------------------------------------------------
def build(shot):
    L.world()
    rnd = random.Random(5)
    m = materials()
    smr = build_smr(m, rnd)
    mods = build_modules(m)
    big = build_big(m, rnd)
    fac = build_factory(m, rnd)

    c_mod, c_cmp, c_big = shot.cue("modular"), shot.cue("compare"), shot.cue("big")
    c_mods, c_fac, c_bricks = shot.cue("modules"), shot.cue("factory"), shot.cue("bricks")

    # 1) "reaktor": the reactor tower's cap gives a little hop; "modułowy": the three hall
    #    bays hop in turn (they are modules)
    cap, c_rea = smr["cap"], shot.cue("reactor")
    cz = cap.location.z
    K.bake_fn(cap, c_rea - 2, c_rea + 6, lambda f: (cap.location.x, cap.location.y,
                                                     cz + 1.4 * math.sin(math.pi * min(1.0, (f - c_rea + 2) / 8))))
    K.squash(cap, c_rea + 6, amount=0.12)
    for k, bay in enumerate(smr["bays"]):
        f0 = c_mod - 2 + 4 * k
        bx, by = bay.location.x, bay.location.y
        K.bake_fn(bay, f0, f0 + 8, lambda f, f0=f0, bx=bx, by=by: (bx, by, 1.6 * math.sin(math.pi * min(1.0, (f - f0) / 8))))
        K.squash(bay, f0 + 8, amount=0.07)

    # 2) the big plant slides in on its own baseplate and builds itself
    slide0 = c_cmp - 4
    for ob in big["plate"]:
        x, y, z = ob.location
        A.show_from(ob, slide0)
        A.fly(ob, slide0, 16, (x - 70, y, z), (x, y, z), ease=A.ease_out_cubic)
    t0 = slide0 + 12
    for k, ob in enumerate(big["hall"]):
        A.drop_in(ob, t0 + 3 * k, dur=9, height=8)
    for k, ob in enumerate(big["aux"]):
        A.drop_in(ob, t0 + 4 + 3 * k, dur=9, height=8)
    for k, ob in enumerate(big["dome"]):
        A.drop_in(ob, t0 + 2 + 2 * k, dur=8, height=8)
    for n, rings in enumerate(big["towers"]):
        for k, ob in enumerate(rings):
            A.drop_in(ob, t0 + 4 + 4 * n + int(k * 0.8), dur=7, height=6)
    for k, ob in enumerate(big["stack"]):
        A.drop_in(ob, t0 + 8 + int(k * 0.9), dur=7, height=6)
    for ob in big["trees"]:
        A.drop_in(ob, t0 + rnd.randint(0, 24), dur=9, height=6)
    for n, (cx, cy) in enumerate(COOLING):
        done = t0 + 4 + 4 * n + int((CT_LEVELS - 1) * 0.8) + 7
        K.plume((cx, cy, CT_LEVELS * B.BRICK + 0.8), done - 4, shot.end, n=14, period=100, rise=18.0,
                drift=(-10.0, 5.0), size=(2.2, 6.0), seed=3 + n)

    # 3) the factory drops in on the far side and assembles itself
    f_plate = c_mods - 44
    for ob in fac["plate"]:
        A.drop_in(ob, f_plate, dur=14, height=14)
    for ob in fac["trees"]:
        A.drop_in(ob, f_plate + 8 + rnd.randint(0, 10), dur=9, height=7)
    for k, ob in enumerate(fac["walls"]):
        A.drop_in(ob, f_plate + 14 + 3 * k, dur=9, height=8)
    for k, ob in enumerate(fac["chimney"]):
        A.drop_in(ob, f_plate + 18 + 2 * k, dur=8, height=7)
    for k, ob in enumerate(fac["teeth"]):
        A.drop_in(ob, f_plate + 26 + 4 * k, dur=10, height=8)

    # one low-loader leaves the factory with three white prefab modules, parks at the hall,
    # and the modules hop onto the hall bays: front, rear, then the middle on "klocków"
    depart = c_mods - 8
    arrive = depart + 33
    root, wheels = K.truck("lowloader", m["cab"])
    for ob in [root] + list(root.children):
        A.show_from(ob, depart)
    root.location = (TRUCK_HOME, ROAD_Y, 0)
    x_at = K.drive(root, wheels, depart, arrive, TRUCK_HOME, TRUCK_STOP, ROAD_Y)
    lands = {0: c_bricks - 25, 2: c_bricks - 13, 1: c_bricks}
    for k, mod in enumerate(mods):
        A.show_from(mod, depart)
        hop0 = lands[k] - (12 if k == 1 else 10)
        K.bake_fn(mod, depart, hop0, lambda f, k=k: (x_at(f) + K.LOAD_X[k], ROAD_Y, 1.4))
        K.hop(mod, hop0, lands[k], (TRUCK_STOP + K.LOAD_X[k], ROAD_Y, 1.4), (BAYS[k][0], BAYS[k][1], HALL_TOP),
              arc=5.0 if k == 1 else 3.6)

    # the finished plant switches its lights on right after the last click
    L.key_emission(m["smr_glass"], c_bricks + 2, 0.0)
    L.key_emission(m["smr_glass"], c_bricks + 14, 2.5)

    # light: low golden sun from the front-right (long shadows fall back-left, away from the SMR)
    K.lighting(center=(-20, 0, 6), scale=2.4, sun_az=55, sun_el=22, sun_strength=6.0, sun_color="#FFC98A", key_dim=0.5)
    cam, tgt = L.camera((0, -90, 10), (-2, 0, 3.5), lens=70, fstop=L.fstop(4.0))
    end = shot.end
    K.camera_rig(
        cam, tgt, end,
        target_keys=[(1, (-1.0, 0.0, 4.2)), (c_cmp, (-1.5, 0.0, 4.4)), (c_big + 18, (-18.0, 3.0, 14.0)),
                     (c_mods - 36, (-17.0, 3.0, 13.5)), (c_fac - 4, (12.0, -4.0, 3.5)), (c_bricks, (3.5, -3.0, 4.8)),
                     (end, (3.5, -3.0, 5.2))],
        orbit_keys=[(1, (150.0, 22.0, 4.0)), (c_cmp, (146.0, 8.0, 5.0)), (c_big + 18, (190.0, -6.0, 13.0)),
                    (c_mods - 36, (184.0, -4.0, 13.0)), (c_fac - 4, (88.0, -6.0, 15.0)), (c_bricks, (62.0, -2.0, 18.0)),
                    (end, (56.0, -5.0, 17.0))],
        lens_keys=[(1, 70.0), (c_cmp, 70.0), (c_big + 18, 50.0), (c_fac - 4, 50.0), (c_bricks, 55.0), (end, 55.0)],
        fstop_keys=[(f, L.fstop(n)) for f, n in ((1, 4.0), (c_cmp, 4.0), (c_big + 18, 5.6), (c_mods - 36, 5.6),
                                                  (c_fac - 4, 9.0), (c_bricks, 11.0), (end, 11.0))],
        shift_keys=[(1, (0.0, 0.085)), (c_cmp, (0.0, 0.085)), (c_big + 18, (0.0, 0.02)), (end, (0.0, 0.02))],
    )

    # label anchors for Remotion
    anchors.anchor("big_plant", (-27.0, -7.0, 27.0))
    anchors.anchor("smr_plant", (-3.0, 0.0, 15.0))
    anchors.anchor("factory", (27.0, -4.0, 12.5))
