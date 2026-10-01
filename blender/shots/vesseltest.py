"""Vessel test: the cutaway with rods going in, bubbles rising, water sinking."""
from lib import camera as Cam
from lib import look as L
from lib import vessel as V


def build(shot):
    L.world()
    v = V.Vessel(0, 0)
    v.glow(1, 1.0)
    v.bubbles(1, 120)
    v.downflow(1, 120)
    v.rods(30, 60)
    L.studio(center=(0, 0, 12), scale=1.2)
    cam, target = L.camera((0, -46, 16), v.points["chimney"], lens=45, fstop=5.6)
    Cam.path(cam, [(1, (0, -46, 16)), (120, (-14, -42, 18))])
