"""Safety — "A co, jeśli zabraknie prądu?" Passive safety of the BWRX-300 as a brick cross-section.

A slice of earth floating in the studio: the reactor building with its isolation-condenser pool on
top, the reactor vessel ~35 m down a concrete shaft, a hamlet on a power line to the right.

Beats (Blender frame = cue + 1):
  start      normal operation: bubbles, glowing core, pulses on the line, lit windows
  blackout   lights flicker and cut, windows die, pulses stop; a red rotating beacon sweeps the dark
  rodsIn     rods slam up into the core (unlatch dip, hard drive, rebound, camera bump)
  off        the green core glow collapses; boiling dies down
  decay      a faint, slow orange pulse stays in the core (decay heat)
  ic/pools   the condenser coil, then the pool light up; the studio light comes back, calm
  rise       white steam plates leave the vessel and climb into the coil
  back       blue condensate falls back down the return line into the vessel (gravity);
             the pool surface steams gently
  noPower    calm medium framing of the loop, subject left (right third free for the badges)
  days       the camera rises above the building; seven quick days (warm sun sweeps / blue moonlight)
  underground  from high above, the camera dives down the cut face through the soil strata and
             settles on the reactor at the bottom of the shaft
"""
import math
import random

import bpy
from mathutils import Vector

from lib import anchors
from lib import anim as A
from lib import bricks as B
from lib import build as S
from lib import camera as Cam
from lib import look as L
from lib import safety_kit as K
from lib import vessel as V


def build(shot):
    c = shot.cue
    END = shot.end
    rnd = random.Random(21)
    world = L.world()

    # ------------------------------------------------------------------ the diorama
    K.soil(rnd)
    K.ground()
    K.shaft(rnd)
    _, _, water_mat, tile_mat = K.pool()

    v = V.Vessel(0.0, 0.0, z0=K.VESSEL_Z0)
    K.nozzle_left(v, V.WATER_LEVEL - 3)

    # isolation-condenser loop: steam riser (right) → serpentine coil in the pool → return (left)
    pipe_mat = L.plastic(L.COL["lightgrey"], rough=0.3)
    coil_mat = K.own(L.plastic(L.COL["lightgrey"], rough=0.3), "coil")
    K.set_emission(coil_mat, "#EAF4FF", 0.0)
    X, CX = K.PIPE_X, K.COIL_X
    z1, z2, z3 = K.COIL_Z
    zs = v.points["steam_out"][2]                     # steam nozzle axis (-9.2)
    zf = v.z(V.WATER_LEVEL - 3) + B.BRICK / 2         # feedwater level axis (-16.4)
    K.pipe([(8.7, 0, zs), (X, 0, zs), (X, 0, z1)], pipe_mat)
    K.pipe([(X, 0, z1), (-CX, 0, z1), (-CX, 0, z2), (CX, 0, z2), (CX, 0, z3), (-X, 0, z3)], coil_mat)
    K.pipe([(-X, 0, z3), (-X, 0, zf), (-8.7, 0, zf)], pipe_mat)

    # hamlet on the right: pylon, two houses, the line from the plant
    grey = L.plastic(L.COL["grey"])
    dark = L.plastic(L.COL["darkgrey"])
    for level in range(7):
        B.add(B.part(1, 1, 3, "round"), grey, (20, 4.5, level * B.BRICK))
    B.add(B.part(1, 5, 1), dark, (20, 4.5, 7 * B.BRICK))
    B.add(B.part(1, 1, 1, "round"), dark, (20, 4.5, 7 * B.BRICK + B.PLATE))
    B.add(B.part(1, 1, 3, "round"), dark, (11.5, 4.5, K.ROW0 + K.BUILDING_ROWS * B.BRICK))  # line insulator on the roof
    win_mats = []
    for k, (hx, hy, wall, roof) in enumerate(((25, 1, L.COL["white"], L.COL["red"]), (32, 3, L.COL["tan"], L.COL["darkgrey"]))):
        wmat = L.glow(L.COL["electric"], 7.0, name=f"house_window_{k}", base=L.COL["yellow"])
        win_mats.append(wmat)
        S.house(hx, hy, L.plastic(wall), L.plastic(roof), wmat)
    line_pts = (K.sag((11.5, 4.5, 9.3), (20, 4.5, 9.0), 1.0) + K.sag((20, 4.5, 9.0), (24.5, 2.0, 2.2), 0.8)[1:]
                + [(28.5, 2.0, 2.2)] + K.sag((28.5, 2.0, 2.2), (31.5, 4.0, 2.2), 0.3)[1:] + [(33.0, 4.0, 2.2)])
    K.cable(line_pts, dark, name="power_line")

    # ------------------------------------------------------------------ light & world
    key, rim, fill = L.studio(center=(4, 0, -8), scale=1.6)
    rim.data.energy *= 0.45   # the rim grazes the ground plates; keep it a sheen, not a wash
    base = {o: o.data.energy for o in (key, rim, fill)}
    bg = world.node_tree.nodes["Background"]
    bf = c("blackout")
    impact = c("rodsIn") + 3 + 18   # rods hit their stop (see K.rods_slam: 3-frame unlatch + 18-frame drive)
    # lights flicker and cut → a moment of darkness → dim emergency light → calm returns with the coil
    # (one gentle off-on flicker, then down: well under 3 flashes per second)
    level = [(1, 1.0), (bf - 1, 1.0), (bf + 1, 0.35), (bf + 3, 0.8), (bf + 5, 0.22), (bf + 7, 0.09),
             (bf + 26, 0.09), (c("rodsIn") - 6, 0.5), (c("ic") - 8, 0.5), (c("pools") + 30, 1.0)]
    for ob in (key, fill, rim):
        K.key_value(ob.data, "energy", [(f, base[ob] * (m if ob is not rim else 0.35 + 0.65 * m)) for f, m in level])
    for f, m in level:
        bg.inputs["Strength"].default_value = 0.55 * (0.3 + 0.7 * m)
        bg.inputs["Strength"].keyframe_insert("default_value", frame=f)

    # ------------------------------------------------------------------ normal operation → blackout
    # lit windows flicker and die
    for wmat in win_mats:
        for f, s in ((1, 7.0), (bf - 1, 7.0), (bf + 1, 1.2), (bf + 3, 5.0), (bf + 5, 0.6), (bf + 7, 0.0)):
            L.key_emission(wmat, f, s)
    # electricity pulses run along the line until the grid goes
    pulse_mat = L.glow(L.COL["electric"], 9.0, name="pulse")
    line_fn, line_len = K.polyline(line_pts)
    pulses = [B.add(B.part(1, 1, 1, "round"), pulse_mat, (0, 0, 0)) for _ in range(6)]
    K.flow(pulses, lambda u: tuple(Vector(line_fn(u)) - Vector((0, 0, 0.2))), 54, 1, bf - 1, grow=0.04, size=1.0)

    # red rotating beacon on the building (brick blinks when the lamp faces us)
    beacon_mat = L.glow("#FF2B1C", 0.0, name="beacon", base="#B5160A")
    bx, by, bz = K.SHAFT_X[0] + 0.5, 0.5, K.ROW0 + K.BUILDING_ROWS * B.BRICK
    B.add(B.part(1, 1, 1, "round"), dark, (bx, by, bz))
    lamp = B.add(B.part(1, 1, 3, "round"), beacon_mat, (bx, by, bz + B.PLATE))
    lamp.visible_shadow = False
    spot_data = bpy.data.lights.new("beacon_spot", "SPOT")
    spot_data.color = L.srgb("#FF2A1A")[:3]
    spot_data.spot_size = math.radians(46)
    spot_data.spot_blend = 0.45
    spot_data.shadow_soft_size = 0.2
    spot = bpy.data.objects.new("beacon_spot", spot_data)
    bpy.context.scene.collection.objects.link(spot)
    spot.location = (bx, by, bz + B.PLATE + 0.7)
    glow_data = bpy.data.lights.new("beacon_glow", "POINT")
    glow_data.color = L.srgb("#FF2A1A")[:3]
    glow_data.shadow_soft_size = 0.4
    glow = bpy.data.objects.new("beacon_glow", glow_data)
    bpy.context.scene.collection.objects.link(glow)
    glow.location = (bx, by - 1.2, bz + B.PLATE + 0.9)
    on = bf + 2
    rev = 32.0  # frames per revolution
    # alarm at full strength through the scram, then easing off: calm once the condenser takes over
    alarm = K.hermite([(0, (1.0,)), (impact + 30, (1.0,)), (c("ic") - 10, (0.3,)), (c("pools") + 20, (0.08,))])
    for f in range(0, END + 1):
        ang = math.tau * (f - on) / rev
        spot.rotation_euler = (math.radians(78), 0, ang)
        spot.keyframe_insert("rotation_euler", frame=f)
        lit = f >= on
        fade = alarm(f)[0]
        facing = max(0.0, math.cos(ang - math.pi)) ** 6   # lamp pointing at the camera (-y)
        spot_data.energy = 140000 * fade if lit else 0.0
        spot_data.keyframe_insert("energy", frame=f)
        glow_data.energy = (1500 + 16000 * facing) * fade if lit else 0.0
        glow_data.keyframe_insert("energy", frame=f)
        L.key_emission(beacon_mat, f, (1.5 + 14 * facing) * (0.35 + 0.65 * fade) if lit else 0.0)

    # ------------------------------------------------------------------ the reactor
    # boiling: normal two-phase flow, dies down after the scram; gentle decay-heat boiling later
    z_lo, z_hi = v.z(V.CORE[1]), v.z(V.WATER_LEVEL - 1)

    def bubble_column(x, period, count, born):
        obs = [B.add(B.part(1, 1, 1, "round"), v.bubble_mat, (x, 0.3, z_lo)) for _ in range(count)]
        wob = rnd.uniform(0, 6)
        K.flow(obs, lambda u: (x + 0.25 * math.sin(u * 9 + wob), 0.3, z_lo + (z_hi - z_lo) * u), period, 1, END, born=born, grow=0.08)

    for x in (-1.6, -0.5, 0.6, 1.7):
        bubble_column(x, 58 + rnd.randint(-6, 6), 7, (-1e9, impact + 4))
    bubble_column(0.1, 96, 3, (c("off"), 1e9))                 # a little heat is left
    for x in (-1.1, 1.2):
        bubble_column(x, 74, 4, (c("rise") - 45, 1e9))         # decay heat boils water for the condenser
    v.downflow(1, END)

    K.thin_rods(v, L.plastic("#474F55", rough=0.22))
    hit = K.rods_slam(v, c("rodsIn"), travel_frames=18, anticipation=3)
    assert hit == impact, (hit, impact)
    # core glow: full power → flux collapses as the rods go in → "gaśnie" → faint orange decay heat
    v.glow(1, 1.0)
    v.glow(impact - 1, 1.0)
    v.glow(impact + 5, 0.62)
    v.glow(c("off") - 4, 0.42)
    v.glow(c("off") + 28, 0.05)
    # decay heat: the (now dim) fuel glow turns to a slow, faint orange pulse — heat, not fission
    t0 = c("off") + 32
    emit_col = K.bsdf(v.fuel).inputs["Emission Color"]
    for f, col in ((1, L.COL["uranium"]), (t0 - 6, L.COL["uranium"]), (t0 + 8, "#FF8A3D")):
        emit_col.default_value = L.srgb(col)
        emit_col.keyframe_insert("default_value", frame=f)
    for f in range(t0, END + 1, 3):
        pulse = 0.5 - 0.5 * math.cos(math.tau * (f - t0) / 54.0)
        ramp = min(1.0, (f - t0) / 24.0)
        L.key_emission(v.fuel, f, 0.7 + ramp * (0.15 + 0.65 * pulse))
        v.core_light.data.energy = 500 + ramp * (700 + 1500 * pulse)
        v.core_light.data.keyframe_insert("energy", frame=f)

    # ------------------------------------------------------------------ the passive loop
    # condenser coil and pool light up on "skraplacze" / "basenach"
    K.key_input(coil_mat, "Emission Strength", [(1, 0.0), (c("ic") - 3, 0.0), (c("ic") + 10, 2.4), (c("ic") + 45, 0.8)])
    for mat, peak, rest in ((water_mat, 1.1, 0.4), (tile_mat, 1.4, 0.45)):
        K.key_input(mat, "Emission Strength", [(1, 0.15), (c("pools") - 3, 0.15), (c("pools") + 12, peak), (c("pools") + 55, rest)])

    Y = -0.62  # particles ride just in front of the pipes
    steam_mat = L.glow("#FFFFFF", 1.4, name="steam_plate", base=L.COL["white"])
    drop_mat = L.glow("#4FA3FF", 1.6, name="water_drop", base="#2F7BFF")
    steam_fn, steam_len = K.polyline([(3.0, Y, zs), (X, Y, zs), (X, Y, z1), (-CX, Y, z1)])
    water_fn, water_len = K.polyline([(-CX, Y, z1), (-CX, Y, z2), (CX, Y, z2), (CX, Y, z3), (-X, Y, z3),
                                      (-X, Y, zf), (-4.0, Y, zf), (-4.0, Y, zf - 5.0)])
    speed = 0.75
    steam_start = c("rise") - 14
    water_start = steam_start + int(steam_len / speed)
    steam = [B.add(B.part(1, 1, 1, "round"), steam_mat, (0, 0, 0)) for _ in range(15)]
    drops = [B.add(B.part(1, 1, 1, "round"), drop_mat, (0, 0, 0)) for _ in range(25)]
    K.flow(steam, steam_fn, steam_len / speed, steam_start, END, born=(steam_start, 1e9), grow=0.05)
    K.flow(drops, water_fn, water_len / speed, water_start, END, born=(water_start, 1e9), grow=0.04)

    # the pool gently steams once the loop runs (that's where the heat finally goes)
    puff_mat = K.own(L.trans(L.COL["trans_clear"]), "puff")
    K.set_emission(puff_mat, "#FFFFFF", 0.6)
    K.puffs(K.clouds(9, puff_mat), c("rise") + 30, END, ((-8.5, 8.5), (0.5, 6.0)), K.POOL_TOP + 0.6, 7.0, 90, size=1.25)

    # ------------------------------------------------------------------ seven days
    sun_data = bpy.data.lights.new("sun", "SUN")
    sun_data.color = L.srgb("#FFE3B0")[:3]
    sun_data.angle = math.radians(4)
    sun = bpy.data.objects.new("sun", sun_data)
    bpy.context.scene.collection.objects.link(sun)
    moon_data = bpy.data.lights.new("moon", "SUN")
    moon_data.color = L.srgb("#86A8FF")[:3]
    moon_data.angle = math.radians(8)
    moon = bpy.data.objects.new("moon", moon_data)
    bpy.context.scene.collection.objects.link(moon)
    moon.rotation_euler = (math.radians(-35), math.radians(-30), 0)
    d0, d1 = c("days") - 6, c("days") + 78   # seven days, 12 frames each (smooth, < 3 Hz)
    for f in range(0, END + 1):
        if f < d0 or f > d1:
            day, night, theta = 0.0, 0.0, math.radians(70)
        else:
            ph = 7 * (f - d0) / (d1 - d0)
            frac = ph - math.floor(ph)
            wave = math.sin(math.tau * frac)
            day = max(0.0, wave) ** 0.8                                  # first half of each cycle = daylight
            night = max(0.0, -wave) ** 0.8
            theta = math.radians(80 - 160 * min(1.0, frac * 2))          # the sun sweeps east → west by day
        sun.rotation_euler = (math.radians(-22), theta, 0)
        sun.keyframe_insert("rotation_euler", frame=f)
        sun_data.energy = 6.0 * day
        sun_data.keyframe_insert("energy", frame=f)
        moon_data.energy = 1.1 * night
        moon_data.keyframe_insert("energy", frame=f)
    for f in range(d0, d1 + 1, 2):
        ph = 7 * (f - d0) / (d1 - d0)
        night = max(0.0, -math.sin(math.tau * (ph - math.floor(ph))))
        bg.inputs["Strength"].default_value = 0.55 * (1 - 0.45 * night)
        bg.inputs["Strength"].keyframe_insert("default_value", frame=f)
        if f < c("underground") - 45:   # the face dims a touch at night only while we still see the surface
            for ob in (key, fill):
                ob.data.energy = base[ob] * (1 - 0.15 * night)
                ob.data.keyframe_insert("energy", frame=f)
    for ob in (key, fill):
        ob.data.energy = base[ob]
        ob.data.keyframe_insert("energy", frame=d1 + 2)
    bg.inputs["Strength"].default_value = 0.55
    bg.inputs["Strength"].keyframe_insert("default_value", frame=d1 + 2)

    for light in (spot_data, glow_data, v.core_light.data):   # accent lights: no shadow maps (cheaper, softer)
        light.use_shadow = False
    for ob, first, last in ((sun, d0 - 1, d1 + 1), (moon, d0 - 1, d1 + 1), (spot, on - 1, END), (glow, on - 1, END)):
        A.show_from(ob, first)
        if last < END:
            A.hide_from(ob, last + 1)

    # ------------------------------------------------------------------ camera
    OPEN = K.pose((9, 2, -13.0), 10, -13, 100)
    OPEN2 = K.pose((8.5, 2, -13.5), 9, -12, 92)
    CORE = K.pose((0.5, 0.5, -30.5), 4, -2, 44)        # rods visible below the core
    CORE2 = K.pose((0.3, 0.5, -28.0), 2, -3, 37)       # core centred after the scram
    CORE3 = K.pose((0.3, 0.5, -27.6), 5, -4, 40)
    POOL = K.pose((2, 2, 0.0), 5, -12, 62)             # pool + ground line + top of the vessel below
    POOL2 = K.pose((2, 2, 0.5), 3, -11, 58)
    MID = K.pose((10, 1, -7), 8, -7, 80)               # the loop: pool, riser, return, upper vessel (subject left)
    MID2 = K.pose((10, 1, -6.8), 7, -7, 77)
    MID3 = K.pose((10.5, 1, -6.5), 6.5, -7.5, 74)
    HIGH = K.pose((10, 3, 0), 6, -28, 72)              # above the building: seven days pass over the surface
    PLUNGE = K.pose((2, 1, -12), 1, -6, 36)            # diving down the cut face, strata rushing past
    BOTTOM = K.pose((2.5, 0.5, -30.2), -7, 5, 44)      # the reactor at the bottom of the shaft (floor above captions)
    BOTTOM2 = K.pose((2.4, 0.5, -30.3), -8, 6, 41)
    u = c("underground")
    keys = [(1, OPEN, 35), (50, OPEN2, 35), (c("rodsIn") - 5, CORE, 50), (c("off") + 10, CORE2, 50), (c("decay") + 12, CORE3, 50),
            (c("ic") - 2, POOL, 40), (c("pools") + 32, POOL2, 40), (c("rise") - 5, MID, 35), (c("back") + 10, MID2, 35),
            (c("days") - 16, MID3, 35), (u - 69, HIGH, 35), (u - 28, PLUNGE, 32), (u + 8, BOTTOM, 28), (END, BOTTOM2, 28)]
    stops = {c("rodsIn") - 5, c("ic") - 2, c("rise") - 5, u - 69, u + 8}
    cam_at = K.hermite([(f, p[0]) for f, p, _ in keys], stops)
    tgt_at = K.hermite([(f, p[1]) for f, p, _ in keys], stops)
    lens_at = K.hermite([(f, (mm,)) for f, _, mm in keys], stops)
    cam, target = L.camera(OPEN[0], OPEN[1], lens=35, fstop=L.fstop(5.6))

    def shake(f):
        dt = f - impact
        if 0 <= dt <= 8:
            a = 0.22 * (1 - dt / 8)
            return Vector((0.3 * a * math.sin(dt * 2.7), 0, a * math.cos(dt * 2.1)))
        return Vector((0, 0, 0))

    K.bake_fn(cam, "location", 1, END, lambda f: tuple(Vector(cam_at(f)) + shake(f)))
    K.bake_fn(target, "location", 1, END, lambda f: tgt_at(f))
    K.bake_fn(cam.data, "lens", 1, END, lambda f: lens_at(f)[0])
    # real-world f-numbers at toy scale: tilt-shift wides, deep enough focus on the close-ups and the dive
    Cam.fstop(cam, [(1, L.fstop(5.6)), (52, L.fstop(5.6)), (c("rodsIn") - 5, L.fstop(11)), (c("ic") - 26, L.fstop(11)),
                    (c("ic") - 2, L.fstop(8)), (c("days") - 16, L.fstop(8)), (u - 69, L.fstop(6.3)), (u - 50, L.fstop(6.3)),
                    (u - 28, L.fstop(11)), (u + 8, L.fstop(9)), (END, L.fstop(9))])

    # ------------------------------------------------------------------ label anchors for Remotion
    anchors.anchor("pool", (-6.0, -0.9, 4.0))
    anchors.anchor("coil", (0.0, -0.5, z2))
    anchors.anchor("steam_line", (X, -0.5, (zs + z1) / 2))
    anchors.anchor("return_line", (-X, -0.5, (zf + z3) / 2))
    anchors.anchor("core", v.points["core"])
    anchors.anchor("ground", (K.SHAFT_X[0], -1.0, 0.0))
    anchors.anchor("shaft_bottom", (K.SHAFT_X[0], -1.0, K.FLOOR_TOP))
    anchors.anchor("houses", (29.0, 2.0, 3.0))
