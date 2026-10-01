"""Kit for the "control" shot: fuel bundles and control rods as merged brick meshes, pooled
neutrons/flashes, and a deterministic neutron-population simulation (too many neutrons → rods slide
up and swallow them → a steady 1→1 chain)."""
import math
import random

import bpy
from mathutils import Vector

from . import bricks as B
from . import fission_kit as K


# ------------------------------------------------------------------ geometry


def fuel_column(name, x, y, levels, shell_mat, core_mat, coll=None):
    """Fuel rod = a stack of 2×2 round translucent "pellets" (one merged mesh) around a thin glowing
    core (1×1 round bricks, merged). Bottom at z=0. Returns (shell, core)."""
    shell = K.merged(f"{name}_shell", [((0, 0, lv * B.BRICK + B.BRICK / 2), 0) for lv in range(levels)],
                     K.centered(2, 2, 3, "round"), [shell_mat])
    core = K.merged(f"{name}_core", [((0, 0, lv * B.BRICK + B.BRICK / 2), 0) for lv in range(levels)],
                    K.lowpoly_round(), [core_mat])
    out = []
    for me, sc in ((shell, 1.0), (core, 0.82)):
        ob = bpy.data.objects.new(me.name, me)
        K.link(ob, coll)
        ob.location = (x, y, 0)
        ob.scale = (sc, sc, 1.0)
        out.append(ob)
    return out


def control_rod(name, x, y, length_levels, mat, tip_mat=None, coll=None):
    """Column of dark 1×1 bricks (one merged mesh) whose TIP is at the object origin, hanging down;
    the top brick can use a lighter tip material so the rising rods read clearly."""
    part = K.centered(1, 1, 3, "box")
    items = [((0, 0, -(lv + 0.5) * B.BRICK), 1 if (lv == 0 and tip_mat) else 0) for lv in range(length_levels)]
    me = K.merged(name, items, part, [mat] + ([tip_mat] if tip_mat else []))
    ob = bpy.data.objects.new(name, me)
    K.link(ob, coll)
    ob.location = (x, y, -40)
    return ob


def support_plate(name, x0, x1, y0, y1, holes, mat, z=-0.4, coll=None):
    """Core support plate of 1×1 plates with holes where the rods pass (one merged mesh)."""
    part = K.centered(1, 1, 1, "box")
    items = []
    for i in range(int(x0), int(x1) + 1):
        for j in range(int(y0), int(y1) + 1):
            if any(abs(i - hx) < 0.6 and abs(j - hy) < 0.6 for hx, hy in holes):
                continue
            items.append(((i, j, z + B.PLATE / 2), 0))
    me = K.merged(name, items, part, [mat])
    ob = bpy.data.objects.new(name, me)
    K.link(ob, coll)
    return ob


# ------------------------------------------------------------------ pools


class Pool:
    """Reuse objects whose previous use has ended (keeps the object count low)."""

    def __init__(self, make):
        self.make = make
        self.items = []  # [obj, busy_until]

    def get(self, f0, f1):
        for it in self.items:
            if it[1] < f0 - 1:
                it[1] = f1
                return it[0]
        obj = self.make(len(self.items))
        self.items.append([obj, f1])
        return obj

    def all(self):
        return [it[0] for it in self.items]


# ------------------------------------------------------------------ neutron population


class Core:
    """Row of fuel columns at x = c*pitch (c = 0..n-1) with rods half-way between (and at both ends):
    rod r sits at x = (r - 0.5)*pitch, r = 0..n. rod_tip(frame, r) gives its tip height."""

    def __init__(self, n, pitch, z_lo, z_hi, rod_tip, half_width=1.0, rod_half=0.5, speed=0.42):
        self.n, self.pitch = n, pitch
        self.z_lo, self.z_hi = z_lo, z_hi
        self.rod_tip = rod_tip
        self.hw, self.rh = half_width, rod_half
        self.speed = speed

    def col_x(self, c):
        return c * self.pitch

    def trace(self, c, z, t, ang):
        """Neutron leaving column c at height z, frame t, angle ang (x-z plane). Returns a dict with
        p0, p1, t0, t1 and outcome: 'fission' (+ column, z), 'rod' (absorbed), 'escape' (leaves view)."""
        dx = 1 if math.cos(ang) >= 0 else -1
        d = Vector((math.cos(ang), 0.0, math.sin(ang)))
        x0 = self.col_x(c) + dx * self.hw
        p0 = Vector((x0, 0.0, z))
        rod_x = self.col_x(c) + dx * self.pitch / 2
        s_rod = (rod_x - dx * self.rh - x0) / d.x
        z_rod = z + d.z * s_rod
        t_rod = t + s_rod / self.speed
        nxt = c + dx
        rod = c + (1 if dx > 0 else 0)
        if z_rod < self.rod_tip(int(round(t_rod)), rod) - 0.1 and self.z_lo - 1.5 < z_rod:
            return {"p0": p0, "p1": p0 + d * s_rod, "t0": t, "t1": int(round(t_rod)), "out": "rod", "rod": rod}
        if not (0 <= nxt < self.n):
            s = 6.0
            return {"p0": p0, "p1": p0 + d * s, "t0": t, "t1": int(round(t + s / self.speed)), "out": "escape"}
        s_col = (self.col_x(nxt) - dx * self.hw - x0) / d.x
        z_col = z + d.z * s_col
        if not (self.z_lo + 0.3 < z_col < self.z_hi - 0.3):
            s = s_col
            return {"p0": p0, "p1": p0 + d * s, "t0": t, "t1": int(round(t + s / self.speed)), "out": "escape"}
        return {"p0": p0, "p1": p0 + d * s_col, "t0": t, "t1": int(round(t + s_col / self.speed)), "out": "fission",
                "col": nxt, "z": z_col}


def simulate_chaos(core, seed_events, p_fission, f_stop, max_flying=40, seed=1):
    """Branching process: each fission emits 2–3 neutrons in random directions; a neutron that reaches
    another column splits it with probability p_fission(frame). Returns (fissions, flights)."""
    rnd = random.Random(seed)
    queue = sorted(seed_events, key=lambda e: e[2])  # (column, z, frame)
    fissions, flights = [], []
    while queue:
        c, z, t = queue.pop(0)
        if t >= f_stop:
            continue
        fissions.append((c, z, t))
        for _ in range(3 if rnd.random() < 0.55 else 2):
            ang = rnd.choice([0.0, math.pi]) + rnd.uniform(-0.75, 0.75)
            fl = core.trace(c, z, t + 1, ang)
            flying = sum(1 for f in flights if f["t0"] <= fl["t0"] <= f["t1"])
            if flying >= max_flying:
                continue
            flights.append(fl)
            if fl["out"] == "fission" and rnd.random() < p_fission(fl["t1"]):
                queue.append((fl["col"], fl["z"], fl["t1"] + 1))
                queue.sort(key=lambda e: e[2])
            elif fl["out"] == "fission":
                fl["out"] = "fuel"  # swallowed by the fuel without splitting
    return fissions, flights
