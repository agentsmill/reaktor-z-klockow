"""Control: inside the core, a row of fuel rods (stacks of translucent 2×2 "pellets" around a glowing
core). Too many neutrons — fissions multiply and the core glows hotter. Dark control rods (light tips)
slide up heavily from below between the fuel rods and swallow the neutrons that touch them (dim flash).
Then a steady chain: one fission per step moving left → right; from each fission one neutron goes on
to the next fuel rod and two are caught by the rods; it loops (in from the left edge). Calm glow.

Layout keeps the right third of the frame empty for Remotion's power chart (top-right)."""
import math
import random

from mathutils import Vector

from lib import anchors
from lib import bricks as B
from lib import control_kit as C
from lib import fission_kit as K
from lib import look as L

N_COLS = 5
PITCH = 5.5
LEVELS = 10                      # fuel height: 10 pellets = 12 BU
Z_TOP = LEVELS * B.BRICK
TIP = 6.4                        # working height of the rod tips
Z_CHAIN = 8.5                    # the steady chain runs just above the rod tips
SPACE = "#0F1D33"


def build(shot):
    c = shot.cue
    end = shot.end
    rnd = random.Random(7)
    L.world(SPACE, 0.4)

    # ------------------------------------------------------------ materials
    fuel_trans = K.trans_new("#3FBF5A", alpha=0.42, emit=0.25, name="fuel_trans")
    fuel_glow = K.glow_obj("#9BE15D", 2.0, base="#7FD04A", name="fuel_glow")
    back_glow = K.glow_obj("#9BE15D", 1.0, base="#5DA83F", name="fuel_glow_back")
    rod_mat = L.plastic("#4B5359", rough=0.18)
    tip_mat = L.plastic("#9AA3AA", rough=0.2)
    plate_mat = L.plastic("#2A2F33", rough=0.45)
    n_mat = K.glow_obj(L.COL["neutron"], 7.0, base="#8FEBFF", name="neutron")
    tail_mat = K.streak_mat(L.COL["neutron"], 6.0, name="neutron_tail")
    flash_mat = K.bubble_mat("#FF9440", 7.0, name="flash_shell", power=3.0)
    core_mat = K.bubble_mat("#FFE2B0", 16.0, name="flash_core")
    absorb_mat = K.bubble_mat("#8FB0C4", 2.6, name="absorb")

    # ------------------------------------------------------------ geometry: fuel, rods, plate
    for i in range(N_COLS):
        C.fuel_column(f"fuel{i}", i * PITCH, 0.0, LEVELS, fuel_trans, fuel_glow)
        C.fuel_column(f"fuel_back{i}", i * PITCH - PITCH / 2, 18.0, LEVELS, fuel_trans, back_glow)  # blurred depth
    rod_x = [(r - 0.5) * PITCH for r in range(N_COLS + 1)]
    rods = [C.control_rod(f"rod{r}", x, 0.0, 20, rod_mat, tip_mat) for r, x in enumerate(rod_x)]
    back_rods = [C.control_rod(f"rod_back{r}", (r - 1) * PITCH, 18.0, 20, rod_mat, tip_mat) for r in range(1, N_COLS)]
    C.support_plate("support", -7, 30, -2, 20, [(x, 0) for x in rod_x] + [((r - 1) * PITCH, 18) for r in range(1, N_COLS)], plate_mat)

    # ------------------------------------------------------------ rods: heavy slide up from below
    r0, r1 = c("absorb") - 5, c("fromBelow") + 16          # 40 → 123
    start_z = -1.6
    # tip height keys: hidden below the caption line until "pręty", halfway up by "wsuwane", heavy brake
    tip_keys = [(r0, start_z), (c("rods"), 2.2), (c("fromBelow"), 5.7), (r1, TIP)]

    def rod_tip(f, r):
        f = f - 2 * r  # rods follow each other left → right
        if f <= r0:
            return start_z
        if f >= r1:
            k = f - r1
            return TIP + 0.3 * math.exp(-k / 3.0) * math.sin(k * 1.25)
        return K.hermite(tip_keys, f)

    for r, rod in enumerate(rods):
        K.bake(rod, r0 - 1, r1 + 2 * r + 18, lambda f, r=r: Vector((rod_x[r], 0.0, rod_tip(f, r))))
    for k, rod in enumerate(back_rods):
        K.bake(rod, r0 + 2, r1 + 2 * k + 20, lambda f, k=k: Vector(((k) * PITCH, 18.0, rod_tip(f - 3, k + 1))))

    # ------------------------------------------------------------ power level: glow + warm light
    heat = K.point_light("core_heat", (14, 5.0, 7), L.COL["heat"], 0.0, radius=6.0)

    def power(f):
        if f < c("rods") - 4:
            return 1.0 + 1.6 * (max(0, f) / (c("rods") - 4)) ** 1.6
        return 1.3 + 1.3 * (1 - K.smooth(K.ramp(f, c("rods") - 4, c("fromBelow") + 30)))

    for f in range(1, end + 1, 2):
        p = power(f)
        K.set_glow_strength(fuel_glow, f, 0.9 + 1.1 * p)
        K.set_glow_strength(back_glow, f, 0.5 + 0.5 * p)
        K.key_energy(heat, f, 1800 * p)

    # ------------------------------------------------------------ pools
    neutrons = C.Pool(lambda i: K.Neutron(f"n{i}", n_mat, tail_mat, scale=0.95, streak=3.6))
    flashes = C.Pool(lambda i: K.Flash(f"fl{i}", flash_mat, core_mat, light_color=L.COL["heat"]))
    absorbs = C.Pool(lambda i: K.Flash(f"ab{i}", None, absorb_mat, light_color=False))

    def fission_flash(f, x, z, big=1.0):
        fl = flashes.get(f, f + 16)
        fl.fire(f, (x, -1.3, z), size=2.8 * big, dur=14, energy=1500.0 * big, decay=6.0, core_size=0.9 * big, core_dur=5)

    def absorb_flash(f, p):
        ab = absorbs.get(f, f + 8)
        ab.fire(f, (p.x, p.y - 0.55, p.z), size=1.0, dur=6, energy=0.0, core_size=0.95, core_dur=8)

    def flight(fl):
        nn = neutrons.get(fl["t0"], fl["t1"])
        nn.fly(fl["t0"], fl["t1"], fl["p0"], fl["p1"], fade_out=fl["out"] == "escape")
        return nn

    # ------------------------------------------------------------ 1) too many neutrons (pre-roll from -40)
    core = C.Core(N_COLS, PITCH, 0.0, Z_TOP, rod_tip)

    def p_fission(f):
        return K.lerp(0.95, 0.25, K.ramp(f, c("fromBelow") - 6, r1 + 8))

    stop = c("fromBelow") + 30
    seeds = [(2, 6.0, -12), (4, 9.0, -7), (1, 3.5, -2), (3, 10.0, 3)]
    fissions, flights = C.simulate_chaos(core, seeds, p_fission, stop, max_flying=26, seed=5)
    print(f"[control] chaos: {len(fissions)} fissions, {len(flights)} flights, "
          f"rod hits {sum(1 for f in flights if f['out'] == 'rod')}, last fission {max(f[2] for f in fissions)}")
    for cc, z, f in fissions:
        if f >= -16:
            fission_flash(f, core.col_x(cc), z, big=0.8)
    # while the rods come up, every fission also sends one of its neutrons into a nearby rod
    extra = 0
    for cc, z, f in fissions:
        if not (c("rods") - 6 <= f < stop) or rnd.random() > 0.75:
            continue
        side = rnd.choice([-1, 1])
        r = cc + (1 if side > 0 else 0)
        tip = rod_tip(f + 8, r)
        if tip < 1.0:
            continue
        zt = rnd.uniform(max(0.6, tip - 4.0), tip - 0.4)
        p0 = Vector((core.col_x(cc) + side * 1.0, 0, z))
        p1 = Vector((rod_x[r] - side * 0.5, 0, zt))
        t1 = f + 1 + max(4, int(round((p1 - p0).length / 0.42)))
        flights.append({"p0": p0, "p1": p1, "t0": f + 1, "t1": t1, "out": "rod"})
        extra += 1
    print(f"[control] extra rod captures: {extra}")
    for fl in flights:
        if fl["t1"] < -2:
            continue
        flight(fl)
        if fl["out"] == "rod":
            absorb_flash(fl["t1"] + 1, fl["p1"])

    # ------------------------------------------------------------ 2) steady chain: 1 → 1, 2 caught by rods
    step = 22
    s0 = c("fromBelow") + 42                                  # 149: first link of the steady chain
    lead = K.Neutron("chain_n", n_mat, tail_mat, scale=1.1, streak=4.5, light=220.0)
    events = []
    f = s0
    k = 0
    while f <= end:
        events.append((k % N_COLS, f))
        f += step
        k += 1
    for i, (col, f) in enumerate(events):
        x = core.col_x(col)
        if col == 0:  # the chain comes in from the rest of the core on the left
            p0, p1 = Vector((x - 7.5, 0, Z_CHAIN)), Vector((x - 1.0, 0, Z_CHAIN))
            lead.fly(f - step + 2, f - 1, p0, p1)
            for ob in (lead.ob, lead.tail):  # fade in from the left edge, full strength otherwise
                K.key_alpha(ob, f - step + 1, 1.0)
                K.key_alpha(ob, f - step + 2, 0.0)
                K.key_alpha(ob, f - step + 8, 1.0)
        fission_flash(f, x, Z_CHAIN, big=1.5)
        if col < N_COLS - 1:
            nxt_f = events[i + 1][1] if i + 1 < len(events) else f + step
            lead.fly(f + 1, min(nxt_f - 1, end), Vector((x + 1.0, 0, Z_CHAIN)), Vector((core.col_x(col + 1) - 1.0, 0, Z_CHAIN)))
        else:  # last bundle in view: the chain carries on out of frame to the right
            nn = neutrons.get(f + 1, f + 14)
            nn.fly(f + 1, f + 12, Vector((x + 1.0, 0, Z_CHAIN)), Vector((x + 3.2, 0, Z_CHAIN)), fade_out=True)
        for side in (-1, 1):  # the two spare neutrons dive into the neighbouring rods
            rx = rod_x[col + (1 if side > 0 else 0)]
            p0 = Vector((x + side * 1.0, 0, Z_CHAIN - 0.2))
            p1 = Vector((rx - side * 0.5, 0, TIP - 1.1 + rnd.uniform(-0.3, 0.3)))
            t1 = f + 1 + int(round((p1 - p0).length / 0.3))
            if t1 > end:
                continue
            nn = neutrons.get(f + 1, t1)
            nn.fly(f + 1, t1, p0, p1)
            absorb_flash(t1 + 1, p1)
    lead.finish()

    for nn in neutrons.all():
        nn.finish()
    for fl in flashes.all() + absorbs.all():
        fl.finish()
    print(f"[control] pools: {len(neutrons.items)} neutrons, {len(flashes.items)} flashes, {len(absorbs.items)} absorbs; "
          f"steady events {len(events)} from {s0}")

    # ------------------------------------------------------------ light + camera
    L.studio(center=(15, 0, 9), scale=0.95)
    cam, target = L.camera((20, -70, 22), (20, 0, 10), lens=50, fstop=K.fstop(2.8))

    def orbit(center, d, yaw, pitch):
        yaw, pitch = math.radians(yaw), math.radians(pitch)
        return Vector(center) + Vector((-math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch))) * d

    keys = [(1, (14.6, 7.0, math.log(47), 7.0, 4.0)),
            (c("rods"), (14.8, 6.6, math.log(49), 6.0, 4.0)),
            (r1, (15.0, 6.2, math.log(51.5), 4.5, 5.0)),
            (s0 + 20, (15.0, 6.8, math.log(50.5), 3.0, 4.0)),
            (end, (15.0, 6.8, math.log(48.5), 2.0, 3.5))]
    stop_f = r1 + 2 * N_COLS

    def shake(f):
        if f < stop_f:
            return Vector()
        a = 0.16 * math.exp(-(f - stop_f) / 3.5)
        return Vector((K.hash01(f, 1) - 0.5, 0, K.hash01(f, 3) - 0.5)) * 2 * a

    for f in range(1, end + 1):
        tx, tz, ld, yaw, pitch = K.hermite(keys, f)
        tgt = Vector((tx, 0, tz))
        K.key(cam, "location", f, orbit(tgt, math.exp(ld), yaw, pitch) + shake(f))
        K.key(target, "location", f, tgt)

    # ------------------------------------------------------------ anchors
    anchors.anchor("fuel", (core.col_x(1), 0.0, Z_TOP - 1.0))
    anchors.anchor("rods", (rod_x[3], 0.0, 2.4))
    anchors.anchor("chain", (core.col_x(2) + PITCH / 2, 0.0, Z_CHAIN))
    anchors.anchor("chain_start", (core.col_x(0), 0.0, Z_CHAIN))
    anchors.anchor("chain_end", (core.col_x(N_COLS - 1), 0.0, Z_CHAIN))
