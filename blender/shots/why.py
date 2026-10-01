"""Why it matters: the diorama runs through a day/night cycle and a rain shower (power 24/7,
whatever the weather); then the old coal plant is taken apart brick by brick and an SMR is
built in its place."""
from lib import anchors
from lib import anim as A
from lib import bricks as B
from lib import build as S
from lib import camera as Cam
from lib import diorama as Dio
from lib import look as L
from lib import why_kit as K


def build(shot):
    world = L.world()
    g = Dio.build()
    lights = L.studio(center=(0, 0, 4), scale=1.7)
    a, w, r = shot.cue("allDay"), shot.cue("weather"), shot.cue("replace")

    # power keeps flowing to the town the whole time
    K.cable_pulses(1, shot.end)
    for mat in g["house_window_mats"]:
        for f, s in ((1, 3.0), (a + 20, 3.0), (a + 45, 9.0), (a + 80, 3.0)):
            L.key_emission(mat, f, s)

    # 24 h: day → dusk → night → dusk → day
    K.light_cycle(lights, world, [(1, "day"), (a, "day"), (a + 25, "dusk"), (a + 45, "night"), (a + 70, "dusk"), (a + 92, "day")])

    # whatever the weather: a brick cloud with rain drifts over the town
    K.rain_cloud((0, 16, 15), w - 6, w + 70)

    # old coal plant → taken apart → SMR tower rises in its place
    coal, top = K.coal_plant(*K.COAL_SITE)
    K.smoke(top, 1, r + 6)
    K.blow_away(coal, r - 4, r + 34)
    cx, cy = K.COAL_SITE
    white = L.plastic(L.COL["white"])
    grey = L.plastic(L.COL["lightgrey"])
    tower = S.ring(cx + 1, cy + 1, 0, 6, 2.6, lambda level, k: grey if level == 4 else white)
    cap = B.add(B.part(2, 2, 3, "round"), grey, (cx + 1, cy + 1, 6 * B.BRICK))
    for k, ob in enumerate(sorted(tower, key=lambda o: o.location.z)):
        A.drop_in(ob, r + 24 + int(k / len(tower) * 40), dur=9, height=10)
    A.drop_in(cap, r + 68, dur=12, height=12)
    anchors.anchor("coal_site", (cx + 1, cy + 1, 9 * B.BRICK))
    anchors.anchor("town", (0, 17, 6))

    # camera: slow orbit that ends favouring the coal → SMR site (the CO₂ chart overlay is compact, top-right)
    cam, target = L.camera((-18, -80, 46), (-4, 0, 2), lens=40, fstop=L.fstop(5.6))
    co2 = shot.cue("co2")
    Cam.path(cam, [(1, (-18, -80, 46)), (co2, (-30, -74, 40)), (r - 10, (-40, -66, 34)), (shot.end, (-44, -58, 28))])
    Cam.path(target, [(1, (-4, 0, 2)), (co2, (-8, 0, 2)), (r - 10, (-14, -6, 3)), (shot.end, (-16, -8, 4))])
