"""Power: the whole BWR loop as one brick diorama, toured by the camera along the energy path.

Heat boils the water right inside the reactor (bubbles in the chimney, core glow) → steam (white
plates) leaves through the steam nozzle and rides the grey pipe to the turbine → the rotor spins up →
the generator on the same shaft lights up → yellow pulses run along the power line → the houses'
windows light up one by one → the turbine exhaust drops into the condenser (white plates in, blue
plates out) → the feed pump sends the water back up into the reactor.
"""
from mathutils import Vector

from lib import anchors
from lib import anim as A
from lib import bricks as B
from lib import build as S
from lib import circulation_kit as C
from lib import look as L
from lib import power_kit as K
from lib import vessel as V

Z0 = 3.6  # vessel raised so the control-rod drive housings stand on the floor
NOZ_Z = Z0 + (V.LEVELS - 2) * B.BRICK + B.BRICK / 2  # steam nozzle axis (28.2)
FEED_Z = Z0 + (V.WATER_LEVEL - 3) * B.BRICK + B.BRICK / 2  # feed nozzle axis (21.0)
NOZ_END = V.R + 3.7  # nozzles end at x = 8.7
TX0, TX1, TCZ, TR = 15.0, 26.0, 18.0, 5.6  # turbine: x span, shaft height, casing radius
INLET_X = TX0 + 0.27 * (TX1 - TX0)  # steam drops in above the high-pressure wheel
CASING_TOP = TCZ + TR + B.BRICK
DECK = 9 * B.BRICK + B.PLATE  # top of the turbine deck (condenser roof) = 11.2
GEN_X = 28.5
RISER_X = 9.2
PIPE_Z = 1.6  # feed-water pipe along the floor
PUMP_X = 11.3
HOUSES = ((43.0, 18.0), (50.0, 20.0), (57.0, 18.0))  # lower-left corners (x, y); 5×4 studs, 3 storeys
HOUSE_W, HOUSE_D, HOUSE_LV = 5, 4, 3
RIDGE_Z = HOUSE_LV * B.BRICK + 3 * 2 * B.PLATE  # top of the stepped roof (6.0)


def build(shot):
    L.world()
    steel = L.plastic("#5D6675", rough=0.35)
    dark = L.plastic(L.COL["darkgrey"])
    grey = L.plastic(L.COL["grey"])
    white = L.plastic(L.COL["white"])
    steam = K.steam_material()
    cool = C.cool_water_material()
    spark = L.glow(L.COL["electric"], 3.0, name="electric_pulse", base=L.COL["yellow"])
    end = shot.end

    # --- ground: plant floor + green town plot ---------------------------------
    B.baseplate(50, 26, L.plastic("#737D8A"), name="plant_floor", loc=(-10, -9, 0))
    B.baseplate(28, 36, L.plastic(L.COL["green"]), name="town_floor", loc=(40, -9, 0))

    # --- reactor --------------------------------------------------------------
    v = V.Vessel(0, 0, z0=Z0)
    for col in v.rod_cols:  # the two lowest rod bricks sit inside the drive housings
        for ob in col[:2]:
            ob.hide_render = True
    S.ring(0, 0, Z0, 3, 3.4, lambda *_: dark, start_level=-3, arc=(0.0, 0.5))  # support skirt

    # --- machines -------------------------------------------------------------
    turb = K.Turbine(TX0, TX1, 0.0, TCZ, casing_r=TR, shaft_to=GEN_X + 0.6)
    gen = K.Generator(GEN_X, 0.0, DECK, w=8, d=6, levels=8)
    cond = K.Condenser(13, 28, -3, 4, 9, opening=(19.5, 25.5), extend_to=37)
    _, impeller = K.pump(PUMP_X, 0.0, PIPE_Z)

    # --- pipes ----------------------------------------------------------------
    steam_pts = [(NOZ_END, 0, NOZ_Z), (INLET_X, 0, NOZ_Z), (INLET_X, 0, CASING_TOP)]
    K.pipe(steam_pts, steel, joint_mat=dark)
    feed_pts = [(14.6, 0, PIPE_Z), (RISER_X, 0, PIPE_Z), (RISER_X, 0, FEED_Z)]
    K.pipe(feed_pts, steel, joint_mat=dark)
    B.add(B.part(1, 1, 3, studs=False), dark, (RISER_X, 0, FEED_Z - B.BRICK / 2))  # elbow into the feed nozzle

    # --- grid + town ----------------------------------------------------------
    _, pyl_top = K.pylon(39.5, 5.0, 18, grey, dark)
    _, pole_top = K.pylon(41.5, 19.0, 6, L.plastic(L.COL["brown"]), dark)
    wall_mats = [white, L.plastic(L.COL["tan"]), white]
    roof_mats = [L.plastic(L.COL["red"]), dark, L.plastic(L.COL["red"])]
    house_windows = []  # per house: [(window object, material)], left → right
    posts = []
    for h, (hx, hy) in enumerate(HOUSES):
        mats = {}

        def win_mat(k, h=h, mats=mats):
            mats[k] = L.glow(L.COL["electric"], 0.0, name=f"win_{h}_{k}", base="#2E3A4C")
            return mats[k]

        _, wins = K.house(hx, hy, HOUSE_W, HOUSE_D, HOUSE_LV, wall_mats[h], roof_mats[h], win_mat, trim=dark,
                          window_rows=(1, 2))
        house_windows.append([(w, w.material_slots[0].material) for w in wins])
        post = (hx + HOUSE_W / 2, hy + HOUSE_D / 2)
        B.add(B.part(1, 1, 3, "round"), dark, (post[0], post[1], RIDGE_Z))
        posts.append((post[0], post[1], RIDGE_Z + B.BRICK + 0.3))
    for x, y in ((65, 24), (64, 13), (48, 25), (55, 25), (66, 18), (46, 9), (58, 6), (62, 1), (51, 2), (44, -4), (56, -6)):
        S.tree(x, y, L.plastic(L.COL["brown"]), L.plastic(L.COL["darkgreen"] if x % 2 else "#2E7D32"), size=2)
    line_pts = [gen.points["terminal"], pyl_top, pole_top] + posts
    _, dense = K.cable(line_pts, dark, radius=0.07, sag=0.5)

    # ======================= animation (Blender frames) =======================
    boil, name, steam_cue = shot.cue("boil"), shot.cue("name"), shot.cue("steam")
    turbine_cue, generator_cue = shot.cue("turbine"), shot.cue("generator")
    electricity, kettle = shot.cue("electricity"), shot.cue("kettle")
    condense, ret = shot.cue("condense"), shot.cue("return")

    # boil: core glows, bubbles start in the chimney, stronger on "wrzącą"
    for f, fuel, light in ((1, 0.5, 0.0), (boil, 0.5, 0.0), (boil + 40, 3.6, 4000.0)):  # core heats up on "zagotowuje"
        L.key_emission(v.fuel, f, fuel)
        K.key_light(v.core_light, f, light)
    C.core_bubbles(v, boil - 4, end, per_column=6, period=84, seed=21)  # born between the fuel columns
    C.chimney_bubbles(v, boil - 6, end, columns=(-1.6, -0.5, 0.6, 1.7), per_column=6, period=62, seed=3)
    C.chimney_bubbles(v, name - 24, end, columns=(-1.8, -0.9, 0.0, 0.9, 1.8), per_column=5, period=52, seed=4,
                      wobble=0.18)
    C.downflow(v, boil + 30, end, per_side=6, period=170, mat=cool)

    # steam: dome → nozzle → riding the steam pipe → down into the turbine (front reaches it on "turbinę")
    steam_path = K.concat(
        C.dome_steam_path(v),
        K.rider([(V.R - 0.5, 0, NOZ_Z), (NOZ_END, 0, NOZ_Z), (INLET_X, 0, NOZ_Z), (INLET_X, 0, CASING_TOP)]),
        K.Path([(INLET_X, -0.36, CASING_TOP), (INLET_X, -0.7, TCZ + 3.4)], rots=[K.STAND_UP]),
    )
    # timing from the cues: the front leaves the nozzle just before "Para" and reaches the wheel on "turbinę"
    d_noz = C.dome_steam_path(v).length + 0.42
    steam_period, steam_start = _front_timing(steam_path.length, d_noz, steam_path.length, steam_cue - 4, turbine_cue, 30, 80)
    K.flow(K.plates(20, steam, name="steam"), steam_start, end, steam_path, steam_period,
           scale_fn=lambda u: K.ends_scale(u, 0.05, 0.07), last=end)

    # turbine spins up as the steam arrives; the shaft turns the generator
    turb.spin(turbine_cue - 3, end, peak_deg=10.0, ramp_frames=64)  # starts as the first steam hits the wheel
    gen.power(generator_cue + 2, dur=14, strength=2.5, light=140.0)

    # electricity: yellow pulses along the line; windows light one by one as the front passes
    line = K.Path(dense)
    e_period, e_start = 30, electricity - 4
    K.flow(K.plates(24, spark, name="pulse"), e_start, end, line, e_period,
           scale_fn=lambda u: K.ends_scale(u, 0.03, 0.04), last=end)
    for h, wins in enumerate(house_windows):
        d = _distance_along(dense, posts[h])
        arrive = e_start + 1 + d / line.length * (e_period - 3)
        hx, hy = HOUSES[h]
        spill = K.point_light(f"house_glow_{h}", (hx + HOUSE_W / 2, hy - 1.6, 2.6), "#FFC46B", 0.0, 1.2)
        K.key_light(spill, 1, 0.0)
        K.key_light(spill, int(round(arrive)) + 1, 0.0)
        K.key_light(spill, int(round(arrive)) + 10, 320.0)
        order = sorted(wins, key=lambda wm: (wm[0].location.z, wm[0].location.x))
        for k, (_, mat) in enumerate(order):
            f = int(round(arrive)) + 1 + k
            L.key_emission(mat, 1, 0.0)
            L.key_emission(mat, f, 0.0)
            L.key_emission(mat, f + 5, 3.5)

    # condense: exhaust steam drops into the condenser; water comes out the bottom
    ex_period, ex_start = 22, condense - 8
    exhaust = K.Path([(turb.lp_x, -1.4, TCZ - 4.9), (22.6, -1.4, DECK - 0.2), (22.6, -1.4, 6.6)])
    K.flow(K.plates(6, steam, name="exhaust"), ex_start, end, exhaust, ex_period,
           scale_fn=lambda u: K.ends_scale(u, 0.15, 0.3), last=end)
    # return: the condensate rides the feed pipe through the pump, up the riser and into the vessel
    in_condenser = K.Path([(22.6, -1.4, 6.6), (22.6, -1.4, 0.5), (15.4, -1.2, 0.5), (14.6, 0, PIPE_Z + 0.42)])
    water_path = K.concat(
        in_condenser,
        K.rider([(14.6, 0, PIPE_Z), (RISER_X, 0, PIPE_Z), (RISER_X, 0, FEED_Z)]),
        K.rider([(RISER_X, 0, FEED_Z), (V.R - 0.4, 0, FEED_Z)]),
        K.Path([(V.R - 0.4, 0, FEED_Z + 0.42), (V.CHIMNEY_R + 1.0, 0.25, FEED_Z - 0.4)]),
    )
    w_start = ex_start + ex_period - 4  # as the first exhaust plates reach the tubes
    d_pump = in_condenser.length + (14.6 - PUMP_X)  # arc length to the pump centre
    w_period, _ = _front_timing(water_path.length, 0.0, d_pump, w_start, ret + 2, 40, 100)  # front at the pump on "wraca"
    K.flow(K.plates(32, cool, name="condensate"), w_start, end, water_path, w_period,
           scale_fn=lambda u: K.ends_scale(u, 0.04, 0.03), last=end)
    A.spin(impeller, w_start + 4, end, lambda f: 16.0 * K.smoothstep((f - w_start - 4) / 20.0), axis=1)
    # the returning water joins the down-comer
    C.downflow(v, w_start + w_period - 6, end, per_side=5, period=120, mat=cool, sides=(1,), seed=7)

    # ======================= camera: guided tour along the energy path ========
    # reactor (boil) → along the steam pipe to the turbine → generator → town → wide loop for the
    # kettle analogy, the condenser and the water's way back. Smooth C1 glide, no stop-and-go.
    L.studio(center=(26, 4, 12), scale=1.8)
    fill = L.area_light("cutaway_fill", (2, -30, 22), (0, 2, 17), 14, 2600, "#E8EEFF")  # opens up the vessel interior
    K.quiet_vessel_lights(v, fill)
    keys = _monotonic([  # frame, camera, target, lens mm, real f-number (miniature DOF via L.fstop)
        (1, (-10, -60, 22), (7, 0, 16), 45, 8),                         # boil: into the cutaway, core + chimney
        (name - 45, (-14, -76, 32), (8, 0, 17.5), 46, 8),
        (name + 10, (-18, -92, 42), (9, 0, 18.5), 47, 9),               # "reaktor z wrzącą wodą": whole vessel
        (turbine_cue + 27, (-16, -86, 50), (15, 1, 17.5), 50, 9),       # steam rides the pipe into the turbine
        (generator_cue + 4, (6, -80, 50), (32, 7, 12), 50, 9),          # generator lights up
        (electricity + 22, (30, -54, 40), (51, 15, 7), 50, 8),          # pulses reach the town, windows ripple
        (kettle - 6, (29, -56, 41), (50.5, 14.5, 7.2), 50, 8),
        (kettle + 65, (-14, -106, 64), (33, 5, 11), 50, 8),             # kettle analogy: whole loop, bottom-right calm
        (ret + 16, (-21, -104, 62), (24, 4, 11), 50, 9),                # condenser → water back to the reactor
        (end, (-24, -100, 58), (19, 3, 12), 50, 10),
    ], end)
    cam, target = K.camera_tour(keys)

    anchors.anchor("reactor", (-V.R - 0.6, 0, Z0 + 14 * B.BRICK))  # left wall, mid-height (label to its left)
    anchors.anchor("steam_pipe", ((NOZ_END + INLET_X) / 2, 0, NOZ_Z + 0.6))
    anchors.anchor("turbine", turb.points["top"])
    anchors.anchor("generator", gen.points["top"])
    anchors.anchor("houses", (HOUSES[1][0] + HOUSE_W / 2, HOUSES[1][1] + HOUSE_D / 2, RIDGE_Z + 2.0))
    anchors.anchor("condenser", cond.points["center"])
    anchors.anchor("return_pipe", (RISER_X, -0.5, (PIPE_Z + FEED_Z) / 2))


def _front_timing(length, d_from, d_to, f_from, f_to, lo, hi):
    """Period and start frame for K.flow so the first object passes arc length d_from at frame f_from and
    d_to at frame f_to (a trip covers the whole path in period - 3 visible frames)."""
    period = int(round((f_to - f_from) * length / max(1e-6, d_to - d_from))) + 3
    period = max(lo, min(hi, period))
    start = int(round(f_from - 1 - d_from / length * (period - 3)))
    return period, start


def _monotonic(keys, end, gap=8):
    """Keep camera keys strictly increasing (cue-relative keys could collide if the timeline changes)."""
    out = []
    for k in keys:
        f = k[0] if not out else max(k[0], out[-1][0] + gap)
        out.append((min(f, end - gap * (len(keys) - len(out) - 1)),) + tuple(k[1:]))
    return out


def _distance_along(dense, p):
    """Arc length along the dense polyline to the vertex closest to p."""
    best, acc, at = 1e9, 0.0, 0.0
    for i, q in enumerate(dense):
        if i:
            acc += (Vector(q) - Vector(dense[i - 1])).length
        dist = (Vector(q) - Vector(p)).length
        if dist < best:
            best, at = dist, acc
    return at
