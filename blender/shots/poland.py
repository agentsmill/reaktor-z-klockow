"""POLAND — "W Polsce takie reaktory chce budować firma Michała Sołowowa — część z nich
wspólnie z Orlenem. Wybrano technologię BWRX-300 o mocy trzystu megawatów. Projekt wsparli
też polscy przedsiębiorcy: zainwestują w firmę Sołowowa około pół miliarda złotych."

Brick map of Poland on a dark studded "table island" (outline from src/data/poland.ts,
50 studs wide, north = +y). Remotion puts three info cards on the RIGHT ~45 % of the
frame, so the map always sits in the left half (lens shift).
- 1 → "Polsce": low macro over the empty island; on "Polsce" the grey outline ring is laid
  around the country, the white interior fills in a sweeping wave while the camera cranes
  up to the three-quarter view from the south; the Vistula flows in from source to mouth.
- then Warsaw (dark tile) and six red beacons with glowing caps pop up one by one.
- "technologię": a mini white SMR tower stacks itself next to Włocławek; "trzystu": its cap
  lights up electric yellow.
- "przedsiębiorcy": gold coin stacks rise at the bottom-left; "pół": they grow taller.
Anchors: wloclawek, ostroleka, stalowa_wola, dabrowa, stawy, krakow, warszawa (+ smr_mini, coins).
"""
import math
import random

from lib import anchors
from lib import anim as A
from lib import bricks as B
from lib import look as L
from lib import poland_kit as P
from lib import smr_kit as K

SITES = [("wloclawek", 19.068, 52.648), ("ostroleka", 21.575, 53.086), ("stalowa_wola", 22.05, 50.58),
         ("dabrowa", 19.19, 50.33), ("stawy", 19.29, 50.03), ("krakow", 20.10, 50.07)]
WARSAW = (21.01, 52.23)
MINI_SMR = (-3.0, 5.0)                     # 2×2 footprint just west of Włocławek
COIN_STACKS = [(-12.0, -20.0), (-9.0, -22.0), (-14.0, -23.0), (-7.0, -19.0)]   # SW corner, outside the map


def build(shot):
    L.world()
    rnd = random.Random(8)
    pm = P.PolandMap(width=50.0)
    white = L.plastic(L.COL["white"])
    rim = L.plastic("#8F9BA8")
    island = L.plastic("#1F2831", rough=0.4)
    water = L.trans(L.COL["trans_blue"])
    red = L.plastic(L.COL["red"])
    dark = L.plastic(L.COL["black"])
    gold = P.gold()

    c_map, c_tech, c_power = shot.cue("map"), shot.cue("tech"), shot.cue("power")
    c_inv, c_amt = shot.cue("investors"), shot.cue("amount")
    end = shot.end

    B.baseplate(58, 56, island, name="island", loc=(-28.5, -27.5, 0))

    # 1) the outline ring is laid clockwise from the south-west, then the interior fills in
    cx = sum(c[0] + 0.5 for c in pm.cells) / len(pm.cells)
    cy = sum(c[1] + 0.5 for c in pm.cells) / len(pm.cells)
    a0 = math.radians(-135)
    border = sorted(pm.border, key=lambda c: (a0 - math.atan2(c[1] + 0.5 - cy, c[0] + 0.5 - cx)) % math.tau)
    ring_part = B.part(1, 1, 2, "box")
    for k, c in enumerate(border):
        ob = B.add(ring_part, rim, (c[0] + 0.5, c[1] + 0.5, 0))
        A.drop_in(ob, c_map + int(k / len(border) * 26), dur=8, height=4)
    plate = B.part(1, 1, 1, "box")
    for c in pm.interior:
        x, y = c[0] + 0.5, c[1] + 0.5
        d = ((x + 25) + (y + 24) * 0.8) / (50 + 48 * 0.8)
        ob = B.add(plate, white, (x, y, 0))
        A.drop_in(ob, c_map + 10 + int(d * 36) + rnd.randint(0, 3), dur=9, height=5)

    # sites: 2×2 pieces are centred on the nearest stud corner
    def corner(lon, lat):
        x, y = pm.lonlat(lon, lat)
        return (round(x), round(y))

    def footprint(cx_, cy_):
        return [(cx_ - 1, cy_ - 1), (cx_, cy_ - 1), (cx_ - 1, cy_), (cx_, cy_)]

    site_xy = {name: corner(lon, lat) for name, lon, lat in SITES}
    w_xy = corner(*WARSAW)
    taken = {c for xy in list(site_xy.values()) + [w_xy, MINI_SMR] for c in footprint(int(xy[0]), int(xy[1]))}

    # 2) the Vistula flows in from the mountains to the Baltic
    river = [c for c in pm.river_cells(P.VISTULA) if c not in taken]
    tile = B.part(1, 1, 1, "tile")
    for k, c in enumerate(river):
        ob = B.add(tile, water, (c[0] + 0.5, c[1] + 0.5, B.PLATE))
        A.drop_in(ob, c_map + 40 + int(k / 3), dur=7, height=3)

    # 3) Warsaw (dark 2×2 tile), then the six beacons pop up one by one
    wz = max(pm.top(c) for c in footprint(*w_xy))
    wt = B.add(B.part(2, 2, 1, "tile"), dark, (w_xy[0], w_xy[1], wz))
    A.drop_in(wt, c_map + 50, dur=8, height=4)
    anchors.anchor("warszawa", (w_xy[0], w_xy[1], wz + B.PLATE))
    for k, (name, _, _) in enumerate(SITES):
        x, y = site_xy[name]
        z0 = max(pm.top(c) for c in footprint(x, y))
        glow = L.glow("#FF2A1A", 0.0, name=f"beacon_{name}", base="#D42010")
        _, top = P.beacon(x, y, z0, red, glow, c_map + 54 + 4 * k)
        lamp = P.glow_light((x, y, top[2] + 0.8), "#FF3A28", c_map + 60 + 4 * k, name=f"beacon_light_{name}")
        P.pulse(glow, c_map + 60 + 4 * k, end, 2.2, 4.8, period=46, phase=k / 6, light=lamp, light_gain=18.0)
        anchors.anchor(name, top)

    # 4) "technologię": mini SMR tower stacks up next to Włocławek; "trzystu": it lights up
    mx, my = MINI_SMR
    z = B.PLATE
    spark = L.glow(L.COL["electric"], 0.0, name="mini_smr_power", base=L.COL["yellow"])
    stack = [(3, L.plastic(L.COL["white"])), (3, L.plastic(L.COL["white"])), (1, L.plastic(L.COL["lightgrey"])),
             (3, L.plastic(L.COL["white"])), (1, spark)]  # (height in plates, material)
    for k, (h, mat) in enumerate(stack):
        ob = B.add(B.part(2, 2, h, "round"), mat, (mx, my, z))
        A.drop_in(ob, c_tech + 2 + 4 * k, dur=10, height=7)
        z += h * B.PLATE
    spark_lamp = P.glow_light((mx, my, z + 1.0), "#FFD447", c_power, name="mini_smr_light")
    P.pulse(spark, c_power, end, 4.0, 8.0, period=36, ramp=10, light=spark_lamp, light_gain=14.0)
    anchors.anchor("smr_mini", (mx, my, z + 0.4))

    # 5) "przedsiębiorcy": gold coin stacks rise at the bottom-left; "pół": they grow
    coin = B.part(2, 2, 1, "round")
    first, final = [3, 4, 2, 3], [7, 9, 5, 8]
    order = [(lvl, s) for lvl in range(max(first)) for s in range(len(COIN_STACKS)) if lvl < first[s]]
    for k, (lvl, s) in enumerate(order):
        x, y = COIN_STACKS[s]
        A.drop_in(B.add(coin, gold, (x, y, lvl * B.PLATE)), c_inv + 2 + 3 * k, dur=8, height=5)
    order = [(lvl, s) for lvl in range(max(final)) for s in range(len(COIN_STACKS)) if first[s] <= lvl < final[s]]
    for k, (lvl, s) in enumerate(order):
        x, y = COIN_STACKS[s]
        A.drop_in(B.add(coin, gold, (x, y, lvl * B.PLATE)), c_amt + 2 * k, dur=8, height=5)
    anchors.anchor("coins", (-10.5, -21.0, 9 * B.PLATE + 1.0))

    # light: low golden sun from the west-south-west → long beacon shadows across the map
    K.lighting(center=(0, 0, 0), scale=1.3, sun_az=-65, sun_el=32, sun_strength=6.5, sun_color="#FFCB90", key_dim=0.5)

    # camera: low macro over the empty island → crane up into the three-quarter view from
    # the south (map in the left half via lens shift) → slow orbit + push to the end
    cam, tgt = L.camera((-30, -40, 6), (-16, -9, 0.6), lens=50, fstop=L.fstop(5.6))
    reveal = c_map + 76
    K.camera_rig(
        cam, tgt, end,
        target_keys=[(1, (-16.0, -9.0, 0.6)), (c_map, (-15.0, -8.0, 0.6)), (reveal, (0.5, -2.0, 0.0)), (end, (0.5, -1.0, 0.0))],
        orbit_keys=[(1, (34.0, -40.0, 9.0)), (c_map, (32.0, -36.0, 10.0)), (reveal, (152.0, -7.0, 43.0)),
                    ((reveal + end) // 2, (146.0, -2.0, 41.5)), (end, (140.0, 3.0, 40.0))],
        fstop_keys=[(f, L.fstop(n)) for f, n in ((1, 5.6), (c_map, 5.6), (reveal, 6.3), (end, 6.3))],
        shift_keys=[(1, (0.0, 0.0)), (c_map, (0.0, 0.0)), (reveal, (0.235, -0.035)), (end, (0.235, -0.035))],
    )
