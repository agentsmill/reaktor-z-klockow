"""Intro: one brick lands on an empty baseplate, then the whole riverside SMR diorama
assembles itself; town windows light up on "setki tysięcy domów"; the reactor cap
clicks on at "Zbudujmy go z klocków!"."""
import math
import random

from lib import anim as A
from lib import camera as Cam
from lib import diorama as Dio
from lib import look as L


def build(shot):
    L.world()
    g = Dio.build()
    rnd = random.Random(3)
    tx, ty = Dio.TOWER

    # 1) the first brick (bottom of the tower) lands alone
    tower = sorted(g["tower"], key=lambda o: (round(o.location.z, 2), math.atan2(o.location.y - ty, o.location.x - tx)))
    first, rest = tower[0], tower[1:]
    A.drop_in(first, 8, dur=14, height=16)

    # 2) river sweeps in left → right, trees pop up on both banks
    for ob in g["river"]:
        A.drop_in(ob, 26 + int((ob.location.x + 36) / 72 * 40) + rnd.randint(0, 4), dur=9, height=5)
    for ob in g["trees"]:
        A.drop_in(ob, 40 + rnd.randint(0, 60), dur=10, height=8)

    # 3) tower rises ring by ring; hall, yard, pylons and town fill in around it
    levels = sorted({round(o.location.z, 2) for o in rest})
    span = shot.cue("homes") - 40
    for ob in rest:
        li = levels.index(round(ob.location.z, 2))
        ang = (math.atan2(ob.location.y - ty, ob.location.x - tx) + math.pi) / math.tau
        A.drop_in(ob, 40 + int(li / len(levels) * span) + int(ang * 8), dur=9, height=10)
    for group, start, end in (("hall", 55, 150), ("hall_windows", 120, 150), ("yard", 110, 165),
                              ("pylons", 120, 170), ("houses", 50, shot.cue("homes") - 6)):
        obs = sorted(g[group], key=lambda o: (round(o.location.z, 2), o.location.x))
        for k, ob in enumerate(obs):
            A.drop_in(ob, start + int(k / max(1, len(obs)) * (end - start)), dur=9, height=9)
    for ob in g["town_windows"]:
        A.drop_in(ob, shot.cue("homes") - 20, dur=8, height=6)
    A.show_from(g["cable"], 168)

    # 4) the town lights up house by house on "setki tysięcy domów"
    for k, mat in enumerate(g["house_window_mats"]):
        f = shot.cue("homes") + k * 3
        L.key_emission(mat, f, 0.0)
        L.key_emission(mat, f + 8, 7.0)

    # 5) the reactor cap clicks on at "Zbudujmy…"
    A.drop_in(g["tower_cap"], shot.cue("build") - 10, dur=12, height=14)

    # light: golden-hour sun (long shadows) + softened studio key
    key, rim, fill = L.studio(center=(0, 0, 4), scale=1.7)
    key.data.energy *= 0.45
    L.sun(elevation=20, azimuth=-130, strength=4.5)

    # camera, one take: macro at stud height on the first brick → crane up through the falling
    # bricks into the full diorama → push towards the tower for "Zbudujmy go z klocków!"
    fx, fy, _ = first.location
    macro_cam = (fx - 7.5, fy - 9.0, 1.6)
    macro_tgt = (fx, fy, 0.7)
    cam, target = L.camera(macro_cam, macro_tgt, lens=85, fstop=1.8)
    q = shot.cue("question")
    Cam.path(cam, [(1, macro_cam), (22, (fx - 6.8, fy - 8.2, 1.9)), (120, (-34, -70, 40)), (q, (-38, -58, 30)), (shot.end, (-28, -40, 20))])
    Cam.path(target, [(1, macro_tgt), (22, (fx, fy, 0.8)), (120, (-2, -2, 2)), (q, (-4, -4, 4)), (shot.end, (tx, ty, 6))])
    Cam.lens(cam, [(1, 85), (22, 85), (120, 38), (q, 42), (shot.end, 50)])
    Cam.fstop(cam, [(1, 1.8), (22, 1.8), (120, L.fstop(5.6)), (shot.end, L.fstop(5.6))])  # macro → tilt-shift miniature
