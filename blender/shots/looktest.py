"""Look test: one small diorama to calibrate plastic, light and depth of field."""
import math

from lib import bricks as B
from lib import look as L


def build(shot):
    L.world()
    green = L.plastic(L.COL["green"])
    white = L.plastic(L.COL["white"])
    grey = L.plastic(L.COL["lightgrey"])
    dark = L.plastic(L.COL["darkgrey"])
    water = L.trans(L.COL["trans_blue"])
    fuel = L.trans(L.COL["trans_green"])
    window = L.glow(L.COL["electric"], 4.0, name="window", base=L.COL["yellow"])
    neutron = L.glow(L.COL["neutron"], 12.0, name="neutron")

    B.baseplate(32, 24, green, loc=(-16, -12, 0))
    # river of trans-blue tiles
    for i in range(-16, 16):
        for j in range(5, 9):
            B.add(B.part(1, 1, 1, "tile"), water, B.at(i, j + 0.5, 0))
    # reactor tower: stacked 2x2 round bricks in a ring
    for level in range(9):
        for k in range(8):
            a = k / 8 * math.tau
            B.add(B.part(2, 2, 3, "round"), white if level % 4 else grey, (math.cos(a) * 2.2, math.sin(a) * 2.2, level * B.BRICK))
    # turbine hall: 2x4 bricks
    for level in range(4):
        for i in range(0, 8, 4):
            for j in range(0, 4, 2):
                B.add(B.part(4, 2, 3), grey if level < 3 else white, (5 + i + (level % 2), -1 + j, level * B.BRICK))
    for i in range(3):
        B.add(B.part(1, 1, 3), window, (5.5 + i * 2.5, -2.05, 1.5 * B.BRICK))
    # fuel column, control rod, neutron
    for level in range(6):
        B.add(B.part(1, 1, 3, "round"), fuel, (-7, -4, level * B.BRICK))
        B.add(B.part(1, 2, 3), dark, (-5.5, -4, level * B.BRICK))
    B.add(B.part(1, 1, 1, "round"), neutron, (-8.5, -6, 2.0))
    # trees
    for x, y in ((-12, -7), (-10, -9), (12, -6)):
        B.add(B.part(1, 1, 3, "round"), L.plastic(L.COL["brown"]), (x, y, 0))
        B.add(B.part(2, 2, 6, "cone"), L.plastic(L.COL["darkgreen"]), (x, y, B.BRICK))

    L.studio(center=(0, 0, 3))
    L.camera((-26, -38, 26), (0, -1, 4), lens=60, fstop=2.8)
