"""Circulation: inside the reactor the water circulates with no pumps (natural circulation).

Close-up of the shared vessel cutaway, centred-left (right third kept calm for the 2D pump icon and
the radiator inset). Steam bubbles are born small between the fuel columns and grow as the hot
two-phase mixture rises up the tall chimney (warm orange light there); at the separators the steam
goes on up to the dome and out of the steam nozzle, while the cooler water turns outwards and sinks
down the down-comer on both sides, turns under the core and enters it again.
"""
from lib import anchors
from lib import bricks as B
from lib import build as S
from lib import circulation_kit as C
from lib import look as L
from lib import power_kit as K
from lib import vessel as V

Z0 = 3.6  # same placement as in the power shot (drive housings on the floor)


def build(shot):
    L.world()
    dark = L.plastic(L.COL["darkgrey"])
    steam = K.steam_material()
    cool = C.cool_water_material()
    end = shot.end
    # "noPumps" and "radiator" are 2D overlays (pump icon top-right, radiator inset in the right third):
    # nothing happens there in 3D, the right third of the frame stays empty throughout.
    inside, hot = shot.cue("inside"), shot.cue("hot")
    rise, chimney, sink = shot.cue("rise"), shot.cue("chimney"), shot.cue("sink")

    B.baseplate(34, 24, L.plastic("#737D8A"), name="plant_floor", loc=(-17, -10, 0))
    v = V.Vessel(0, 0, z0=Z0)
    for col in v.rod_cols:  # the two lowest rod bricks sit inside the drive housings
        for ob in col[:2]:
            ob.hide_render = True
    S.ring(0, 0, Z0, 3, 3.4, lambda *_: dark, start_level=-3, arc=(0.0, 0.5))  # support skirt
    z = v.z

    # the reactor is running: core glows throughout
    L.key_emission(v.fuel, 1, 3.6)
    K.key_light(v.core_light, 1, 4000.0)

    # --- rising: hot two-phase mixture up the chimney ------------------------------------------
    pre = -160  # flows pre-rolled so they are already running on frame 1
    C.core_bubbles(v, pre, end, per_column=6, period=120, seed=11)
    # "Gorąca…" → "unosi się" → "kominem": more and faster bubbles, chimney warms up
    C.core_bubbles(v, hot - 10, end, xs=(-2.25, -0.75, 0.75, 2.25), per_column=9, period=72, seed=12, y_chim=0.55)
    C.chimney_bubbles(v, rise - 16, end, columns=(-1.5, -0.45, 0.6, 1.55), per_column=7, period=52, seed=13,
                      ys=(0.7, 1.4), wobble=0.2)
    C.chimney_bubbles(v, chimney - 14, end, columns=(-1.0, 0.05, 1.05), per_column=7, period=44, seed=14,
                      ys=(-0.1, 0.3), wobble=0.18)
    heat = C.chimney_lights(v)
    C.chimney_heat(heat, [(1, 300.0), (hot - 6, 300.0), (rise, 1800.0), (chimney + 10, 2600.0)])
    # warm light spilling out of the open chimney onto the floor in front of the vessel
    spill = K.point_light("chimney_spill", (0, -3.5, z(11)), L.COL["heat"], 0.0, 3.0)
    for f, e in ((1, 150.0), (hot - 6, 150.0), (rise, 900.0), (chimney + 10, 1300.0)):
        K.key_light(spill, f, e)

    # steam leaves the separators upwards, through the dryer and out of the steam nozzle
    dome = K.concat(C.dome_steam_path(v), K.Path([(V.R - 0.5, 0, z(V.LEVELS - 2) + 0.6),
                                                   (V.R + 3.4, 0, z(V.LEVELS - 2) + 0.6)]))
    K.flow(K.plates(8, steam, name="steam"), pre, end, dome, 64, scale_fn=lambda u: K.ends_scale(u, 0.06, 0.06))

    # --- sinking: cooler water down both sides, under the core, back up into it -----------------
    C.downflow(v, pre, end, per_side=7, period=170, mat=cool, seed=2, h=2)
    C.downflow(v, sink - 40, end, per_side=12, period=130, mat=cool, seed=3, y=0.9, h=2)
    C.downflow(v, sink - 22, end, per_side=10, period=120, mat=cool, seed=4, y=-0.15, h=2)
    cool_lights = [K.point_light("downcomer_glow", (side * (V.CHIMNEY_R + 1.0), -0.8, z(9)), "#5C9BFF", 0.0, 1.5)
                   for side in (-1, 1)]
    for lt in cool_lights:
        K.key_light(lt, 1, 0.0)
        K.key_light(lt, sink - 10, 0.0)
        K.key_light(lt, sink + 20, 900.0)

    # --- camera: settle into the cutaway, tilt up the chimney with the rising mixture, ease back
    # down to show both down-comers. Vessel centred-left; right third stays empty for overlays.
    L.studio(center=(0, 0, 16), scale=1.1)
    fill = L.area_light("cutaway_fill", (2, -30, 18), (0, 2, 16), 12, 2200, "#E8EEFF")
    K.quiet_vessel_lights(v, fill)
    keys = [  # frame, camera, target, lens mm, real f-number (miniature depth of field via L.fstop)
        (1, (-24, -82, 26), (5.5, 0, 17.5), 45, 9),            # the whole vessel, from the left …
        (inside + 6, (-13, -64, 17), (5.0, 0, 14.2), 45, 9),   # … arcs in and settles into the cutaway
        (hot - 4, (-8, -59, 15), (4.8, 0, 14.2), 45, 9),       # slow push while the pump icon shows
        (rise + 6, (-5, -55, 13.5), (4.5, 0, 17.0), 45, 9),    # tilt up with the rising mixture (low angle)
        (chimney + 24, (-3, -52, 14.5), (4.3, 0, 19.8), 45, 9),  # top of the tall chimney + separators
        (sink + 6, (-7, -64, 14.3), (4.8, 0, 13.4), 45, 9),    # ease back down: both down-comers + bottom turn
        (end, (-12, -67, 14.8), (5.0, 0, 13.4), 45, 10),
    ]
    cam, target = K.camera_tour(keys)

    anchors.anchor("chimney", v.points["chimney"])
    anchors.anchor("downcomer_l", v.points["downcomer_l"])
    anchors.anchor("downcomer_r", v.points["downcomer_r"])
    anchors.anchor("core", v.points["core"])
