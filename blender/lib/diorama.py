"""The hero diorama reused by several shots: an SMR plant on the south bank of a winding
river, a small town on the north bank, pylons in between. Returns groups of brick objects
so shots can animate them (assemble, light up, take apart)."""
import math
import random

import bpy

from . import bricks as B
from . import build as S
from . import look as L

W, D = 72, 44  # baseplate size in studs, centred on the origin
TOWER = (-8.0, -7.0)
TOWER_R = 4.2
TOWER_LEVELS = 9


def river_center(x):
    return 8.5 + 2.2 * math.sin(x / 11.0)


def build(coll=None, seed=7):
    rnd = random.Random(seed)
    m = {
        "ground": L.plastic(L.COL["green"]),
        "white": L.plastic(L.COL["white"]),
        "lightgrey": L.plastic(L.COL["lightgrey"]),
        "grey": L.plastic(L.COL["grey"]),
        "dark": L.plastic(L.COL["darkgrey"]),
        "red": L.plastic(L.COL["red"]),
        "tan": L.plastic(L.COL["tan"]),
        "brown": L.plastic(L.COL["brown"]),
        "leaves": L.plastic(L.COL["darkgreen"]),
        "leaves2": L.plastic("#2E7D32"),
        "water": L.trans(L.COL["trans_blue"]),
        "glass": L.trans("#BFD7F2"),
    }
    g = {k: [] for k in ("river", "trees", "tower", "hall", "hall_windows", "yard", "pylons", "houses", "town_windows")}
    g["house_window_mats"] = []

    B.baseplate(W, D, m["ground"], loc=(-W / 2, -D / 2, 0))

    # river: 1×1 tiles following a gentle meander
    tile = B.part(1, 1, 1, "tile")
    for i in range(-W // 2, W // 2):
        c = river_center(i + 0.5)
        for j in range(-D // 2, D // 2):
            if abs(j + 0.5 - c) < 2.6:
                g["river"].append(B.add(tile, m["water"], (i + 0.5, j + 0.5, 0.0), coll=coll))

    # reactor building: round tower with a grey band, flat round roof, cap
    tx, ty = TOWER
    g["tower"] = S.ring(tx, ty, 0, TOWER_LEVELS, TOWER_R,
                        lambda level, k: m["lightgrey"] if level in (6, 7) else m["white"], coll=coll)
    roof_z = TOWER_LEVELS * B.BRICK
    for i in range(-4, 5):
        for j in range(-4, 5):
            if i * i + j * j <= (TOWER_R - 0.6) ** 2:
                g["tower"].append(B.add(B.part(1, 1, 1, "round"), m["white"], (tx + i, ty + j, roof_z), coll=coll))
    g["tower_cap"] = B.add(B.part(2, 2, 3, "round"), m["lightgrey"], (tx, ty, roof_z + B.PLATE), coll=coll)

    # turbine hall with a band of windows, dark roof
    hx, hy, hw, hd, hl = -1, -12, 15, 7, 5
    walls, wins = S.box_walls(hx, hy, hw, hd, hl, m["lightgrey"], m["glass"], window_rows=(3,), coll=coll)
    g["hall"] = walls + S.roof(hx - 0.5, hy - 0.5, hw + 1, hd + 1, hl * B.BRICK, m["dark"], coll=coll)
    g["hall_windows"] = wins
    # link block tower → hall
    link, _ = S.box_walls(-4, -9, 4, 3, 3, m["white"], coll=coll)
    g["hall"] += link

    # switchyard: grey posts + crossbars
    for i in range(18, 28, 3):
        for j in range(-14, -5, 3):
            for level in range(2):
                g["yard"].append(B.add(B.part(1, 1, 3, "round"), m["grey"], (i, j, level * B.BRICK), coll=coll))
            g["yard"].append(B.add(B.part(1, 3, 1), m["dark"], (i, j + 1, 2 * B.BRICK), coll=coll))

    # pylons carrying the line over the river
    for px, py in ((24, -2), (22, 8.5), (20, 19)):
        for level in range(7):
            g["pylons"].append(B.add(B.part(1, 1, 3, "round"), m["grey"], (px, py, level * B.BRICK), coll=coll))
        g["pylons"].append(B.add(B.part(5, 1, 1), m["dark"], (px, py, 7 * B.BRICK), coll=coll))

    # town on the north bank
    for idx, x in enumerate(range(-30, 32, 8)):
        y = 15 + (idx % 2) * 3
        window = L.glow(L.COL["electric"], 0.0, name=f"window_{idx}", base=L.COL["yellow"])
        g["house_window_mats"].append(window)
        bricks, wins = S.house(x, y, m["white"] if idx % 2 else m["tan"], m["red"] if idx % 3 else m["dark"], window, coll=coll)
        g["houses"] += bricks
        g["town_windows"] += wins

    # trees on both banks
    for _ in range(26):
        x = rnd.uniform(-34, 34)
        y = rnd.choice([rnd.uniform(-20, -15), rnd.uniform(12.5, 20)])
        if abs(y - river_center(x)) < 3.5 or (x > -14 and x < 30 and y < -2):
            continue
        g["trees"] += S.tree(round(x), round(y), m["brown"], m["leaves"] if rnd.random() > 0.4 else m["leaves2"], coll=coll,
                             size=rnd.choice([1, 2, 2]))

    # power line (a thin cable, not a brick)
    curve = bpy.data.curves.new("cable", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.06
    spline = curve.splines.new("POLY")
    pts = [(25, -9, 3.0), (24, -2, 8.6), (22, 8.5, 8.6), (20, 19, 8.6), (6, 18, 3.6)]
    spline.points.add(len(pts) - 1)
    for p, (x, y, z) in zip(spline.points, pts):
        p.co = (x, y, z, 1)
    cable = bpy.data.objects.new("cable", curve)
    (coll or bpy.context.scene.collection).objects.link(cable)
    cable.data.materials.append(m["dark"])
    g["cable"] = cable
    g["mats"] = m
    return g
