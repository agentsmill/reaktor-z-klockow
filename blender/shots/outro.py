"""Outro: the finished diorama at night — town lit, power flowing — while the camera pulls
back and up for the title."""
from lib import camera as Cam
from lib import diorama as Dio
from lib import look as L
from lib import why_kit as K


def build(shot):
    world = L.world()
    g = Dio.build()
    lights = L.studio(center=(0, 0, 4), scale=1.7)
    K.light_cycle(lights, world, [(1, "night")])
    for mat in g["house_window_mats"]:
        L.key_emission(mat, 1, 9.0)
    hall_glow = L.glow("#BFD7F2", 3.0, name="hall_glow", base="#BFD7F2")
    for ob in g["hall_windows"]:
        ob.material_slots[0].material = hall_glow
    K.cable_pulses(1, shot.end)

    tx, ty = Dio.TOWER
    cam, target = L.camera((-22, -42, 14), (tx, ty, 6), lens=45, fstop=L.fstop(8.0))
    t = shot.cue("title")
    Cam.path(cam, [(1, (-22, -42, 14)), (t, (-10, -82, 52)), (shot.end, (-4, -92, 62))])
    Cam.path(target, [(1, (tx, ty, 6)), (t, (0, 2, 0)), (shot.end, (0, 4, 0))])
    Cam.lens(cam, [(1, 45), (t, 36), (shot.end, 34)])
