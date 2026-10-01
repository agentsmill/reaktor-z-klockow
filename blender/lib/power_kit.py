"""Power-loop kit: brick pipes, turbine, generator, condenser, pump, pylon, houses, plus motion
helpers (emitted flows along paths, C1-smooth camera glides).

Everything is built from the shared generic bricks (lib.bricks) — no logos, no text.
Frames are Blender frames (1-based); motion is baked per frame like lib.anim.
"""
import math

import bpy
from mathutils import Matrix, Vector

from . import anim as A
from . import bricks as B
from . import look as L

DEG = math.pi / 180


# --- small helpers -----------------------------------------------------------
def empty(name, loc=(0, 0, 0), coll=None):
    ob = bpy.data.objects.new(name, None)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    return ob


def child(parent, ob):
    """Parent without changing the child's numbers: its location/rotation become parent-local."""
    ob.parent = parent
    ob.matrix_parent_inverse = Matrix.Identity(4)
    return ob


def smoothstep(t):
    t = A.clamp01(t)
    return t * t * (3 - 2 * t)


def point_light(name, loc, hex_color, energy=0.0, radius=1.0, coll=None, shadow=False):
    """Accent/glow light. Shadowless by default: shadow-casting point lights near the vessel's blended
    water volume made EEVEE renders ~3-4x slower (measured) with no visible benefit."""
    data = bpy.data.lights.new(name, "POINT")
    data.color = L.srgb(hex_color)[:3]
    data.energy = energy
    data.shadow_soft_size = radius
    data.use_shadow = shadow
    ob = bpy.data.objects.new(name, data)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    return ob


def key_light(light_ob, frame, energy):
    light_ob.data.energy = energy
    light_ob.data.keyframe_insert("energy", frame=frame)


def quiet_vessel_lights(vessel, *lights):
    """Render-time saver: no shadows from the vessel's core light or from extra fill lights."""
    vessel.core_light.data.use_shadow = False
    for ob in lights:
        ob.data.use_shadow = False


def steam_material():
    """White plastic with a soft inner glow — steam reads brighter than the grey pipes."""
    mat = L.glow("#FFFFFF", 0.35, name="steam", base=L.COL["white"])
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.22
    bsdf.inputs["Coat Weight"].default_value = 0.3
    return mat


# --- smooth camera / value glides -------------------------------------------
def _hermite(keys):
    """keys: [(frame, value_tuple[, hold])]. C1-continuous through every key; velocity is zero at the
    first/last key and at keys flagged hold=True. Returns fn(frame) -> tuple."""
    keys = sorted(keys, key=lambda k: k[0])
    fs = [k[0] for k in keys]
    ps = [Vector(k[1]) for k in keys]
    hold = [len(k) > 2 and k[2] for k in keys]
    n = len(keys)
    ms = []
    for i in range(n):
        if i in (0, n - 1) or hold[i]:
            ms.append(Vector([0.0] * len(ps[i])))
        else:
            ms.append((ps[i + 1] - ps[i - 1]) / (fs[i + 1] - fs[i - 1]))

    def fn(f):
        if f <= fs[0]:
            return tuple(ps[0])
        if f >= fs[-1]:
            return tuple(ps[-1])
        i = max(j for j in range(n - 1) if fs[j] <= f)
        dt = fs[i + 1] - fs[i]
        s = (f - fs[i]) / dt
        h00, h10 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s
        h01, h11 = -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
        return tuple(h00 * ps[i] + h10 * dt * ms[i] + h01 * ps[i + 1] + h11 * dt * ms[i + 1])

    return fn, fs[0], fs[-1]


def glide(ob, keys):
    """Smooth (no stop-and-go) location path through keyed poses: keys = [(frame, (x, y, z)[, hold])]."""
    fn, f0, f1 = _hermite(keys)
    for f in range(f0, f1 + 1):
        ob.location = fn(f)
        ob.keyframe_insert("location", frame=f)


def glide_lens(cam, keys):
    fn, f0, f1 = _hermite([(k[0], (k[1], 0.0)) + tuple(k[2:]) for k in keys])  # Vector needs ≥ 2 components
    for f in range(f0, f1 + 1):
        cam.data.lens = fn(f)[0]
        cam.data.keyframe_insert("lens", frame=f)


def glide_fstop(cam, keys):
    """Depth of field: keys = [(frame, real-world f-number)] → L.fstop() (toy-scale aperture), smooth."""
    fn, f0, f1 = _hermite([(k[0], (k[1], 0.0)) for k in keys])
    for f in range(f0, f1 + 1):
        cam.data.dof.aperture_fstop = L.fstop(fn(f)[0])
        cam.data.dof.keyframe_insert("aperture_fstop", frame=f)


def camera_tour(keys, fill=None):
    """keys: [(frame, camera_xyz, target_xyz, lens_mm, real_f_number)] → (cam, target), C1-smooth."""
    f0, c0, t0, lens0, fn0 = keys[0]
    cam, target = L.camera(c0, t0, lens=lens0, fstop=L.fstop(fn0))
    glide(cam, [(k[0], k[1]) for k in keys])
    glide(target, [(k[0], k[2]) for k in keys])
    glide_lens(cam, [(k[0], k[3]) for k in keys])
    glide_fstop(cam, [(k[0], k[4]) for k in keys])
    return cam, target


# --- paths & flows -----------------------------------------------------------
class Path:
    """Polyline parametrised by arc length. Optional per-point rotation (Euler tuple) is held per
    segment (taken from the segment's start point) — used to stand plates up on vertical pipes."""

    def __init__(self, points, rots=None):
        self.pts = [Vector(p) for p in points]
        self.rots = rots
        self.lens = [(b - a).length for a, b in zip(self.pts, self.pts[1:])]
        self.length = sum(self.lens)

    def at(self, u):
        d = A.clamp01(u) * self.length
        for i, seg in enumerate(self.lens):
            if d <= seg or i == len(self.lens) - 1:
                t = d / seg if seg > 1e-9 else 0.0
                p = self.pts[i].lerp(self.pts[i + 1], min(1.0, t))
                rot = self.rots[i] if self.rots else (0.0, 0.0, 0.0)
                return tuple(p), rot
            d -= seg
        return tuple(self.pts[-1]), (self.rots[-1] if self.rots else (0.0, 0.0, 0.0))

    def point(self, u):
        return self.at(u)[0]


def concat(*paths):
    """Join paths end to end (a straight bridge where they don't touch)."""
    pts, rots = [], []
    for p in paths:
        r = list(p.rots) if p.rots else [(0.0, 0.0, 0.0)] * (len(p.pts) - 1)
        if pts:
            if (pts[-1] - p.pts[0]).length > 1e-6:
                pts.append(p.pts[0])
                rots.append(r[0] if r else (0.0, 0.0, 0.0))
            pts += p.pts[1:]
        else:
            pts += p.pts
        rots += r
    return Path(pts, rots)


def flow(objs, start, end, path, period, scale_fn=None, last=None, jitter=None):
    """Emit objects one after another from the path start; each crosses the whole path in `period`
    frames. New trips start until `end`; trips under way finish. Each object is hidden for the frame
    before and after its trip, so the jump back to the start never shows (no motion-blur streak).

    scale_fn(u) -> uniform scale (e.g. shrink to 0 where the flow disappears into a machine).
    jitter(k, trip, u) -> (dx, dy, dz) small offsets (wobble).
    last: final frame to bake (defaults to end + period)."""
    n = len(objs)
    last = last if last is not None else end + period
    for k, ob in enumerate(objs):
        offset = round(k * period / n)
        base_rot = tuple(ob.rotation_euler)
        visible_prev = None
        ob.hide_render = True
        ob.keyframe_insert("hide_render", frame=min(0, start - 1))  # flows may be pre-rolled (start < 1)
        for f in range(start, last + 1):
            rel = f - start - offset
            if rel < 0:
                trip, i = -1, 0
            else:
                trip, i = divmod(rel, period)
            emitted = start + offset + trip * period
            active = trip >= 0 and emitted <= end
            if not active:
                if trip >= 0 and emitted > end:
                    trip = -2  # finished for good
                vis = False
                u = 0.0 if trip == -1 else 1.0
            else:
                # frames 1..period-2 travel, frame 0 / period-1 hidden at the ends
                vis = 1 <= i <= period - 2
                u = A.clamp01((i - 1) / max(1, period - 3))
            loc, rot = path.at(u)
            if jitter and active:
                d = jitter(k, trip, u)
                loc = (loc[0] + d[0], loc[1] + d[1], loc[2] + d[2])
            ob.location = loc
            ob.keyframe_insert("location", frame=f)
            if path.rots:
                ob.rotation_euler = tuple(base_rot[j] + rot[j] for j in range(3))
                ob.keyframe_insert("rotation_euler", frame=f)
            if scale_fn:
                s = max(0.001, scale_fn(u))
                ob.scale = (s, s, s)
                ob.keyframe_insert("scale", frame=f)
            if vis != visible_prev:
                ob.hide_render = not vis
                ob.keyframe_insert("hide_render", frame=f)
                visible_prev = vis
    return objs


def ends_scale(u, a=0.06, b=0.08):
    """Grow in over the first `a` of the path, shrink out over the last `b`."""
    return min(1.0, smoothstep(u / a) if a else 1.0, smoothstep((1 - u) / b) if b else 1.0)


def plates(n, mat, size=1, kind="round", coll=None, name="flow", h=1):
    part = B.part(size, size, h, kind)
    return [B.add(part, mat, (0, 0, -100), name=name, coll=coll) for _ in range(n)]


# --- brick pipes -------------------------------------------------------------
STAND_UP = (90 * DEG, 0.0, 0.0)  # plate stud faces -y (towards the camera side)


def _axis(a, b):
    d = Vector(b) - Vector(a)
    i = max(range(3), key=lambda k: abs(d[k]))
    return i, (1 if d[i] > 0 else -1), abs(d[i])


def pipe(points, mat, joint_mat=None, coll=None, joints=True):
    """Axis-aligned pipe of 1×1 round bricks along a polyline (pipe axis through the points).
    Horizontal runs: round bricks laid on their side (like the vessel nozzles); vertical runs:
    stacked round bricks; corners get a 1×1 joint block."""
    out = []
    seg_part = B.part(1, 1, 3, "round", studs=False)
    for a, b in zip(points, points[1:]):
        axis, sgn, length = _axis(a, b)
        a = Vector(a)
        if axis == 2:
            n = max(1, int(round(length / B.BRICK)))
            step = length / n
            z0 = min(a.z, b[2])
            for k in range(n):
                ob = B.add(seg_part, mat, (a.x, a.y, z0 + k * step), coll=coll)
                ob.scale = (1, 1, step / B.BRICK)
                out.append(ob)
        else:
            n = max(1, int(math.ceil((length - 0.2) / 1.0)))
            step = (length - B.BRICK) / max(1, n - 1) if n > 1 else 0
            lo = min(a[axis], b[axis])
            for k in range(n):
                p = Vector(a)
                p[axis] = lo + k * step
                ob = B.add(seg_part, mat, tuple(p), coll=coll)
                ob.rotation_euler = (0, 90 * DEG, 0) if axis == 0 else (-90 * DEG, 0, 0)
                if n == 1:
                    ob.scale = (1, 1, length / B.BRICK)
                out.append(ob)
    if joints:
        jm = joint_mat or mat
        for p in points[1:-1]:
            out.append(B.add(B.part(1, 1, 3, studs=False), jm, (p[0], p[1], p[2] - B.BRICK / 2), coll=coll))
    return out


def rider(points, lift=0.42, front=-0.36):
    """Path for plates riding a pipe: on top of horizontal runs, standing on the front (-y) face of
    vertical runs. Returns a Path with per-segment rotations."""
    pts, rots = [], []
    for a, b in zip(points, points[1:]):
        axis = _axis(a, b)[0]
        off = Vector((0, front, 0)) if axis == 2 else Vector((0, 0, lift))
        pa, pb = Vector(a) + off, Vector(b) + off
        if pts and (pts[-1] - pa).length > 1e-6:
            rots.append(rots[-1])  # short hop around the corner
            pts.append(pa)
        elif not pts:
            pts.append(pa)
        pts.append(pb)
        rots.append(STAND_UP if axis == 2 else (0.0, 0.0, 0.0))
    return Path(pts, rots)


# --- building blocks ---------------------------------------------------------
def slab(x0, y0, z0, w, d, levels, mat, coll=None, max_len=6, studs_top=True):
    """Solid w×d block of `levels` bricks (running bond along x). (x0, y0) = lower-left corner."""
    out = []
    for lv in range(levels):
        sizes, rem = [], w
        if lv % 2 and w > 3:
            first = max(1, min(max_len, w) // 2)
            sizes.append(first)
            rem -= first
        while rem > 0:
            s = min(max_len, rem)
            sizes.append(s)
            rem -= s
        x = x0
        for s in sizes:
            part = B.part(s, d, 3, studs=studs_top or lv < levels - 1)
            out.append(B.add(part, mat, (x + s / 2, y0 + d / 2, z0 + lv * B.BRICK), coll=coll))
            x += s
    return out


def wall_y(x0, y0, z0, d, levels, mat, coll=None, max_len=6, w=1):
    """Wall running along y (w studs thick)."""
    out = []
    for lv in range(levels):
        sizes, rem = [], d
        if lv % 2 and d > 3:
            first = max(1, min(max_len, d) // 2)
            sizes.append(first)
            rem -= first
        while rem > 0:
            s = min(max_len, rem)
            sizes.append(s)
            rem -= s
        y = y0
        for s in sizes:
            out.append(B.add(B.part(w, s, 3), mat, (x0 + w / 2, y + s / 2, z0 + lv * B.BRICK), coll=coll))
            y += s
    return out


def plate_grid(x0, y0, z, w, d, mat, coll=None, kind="box", skip=None, size=2, h=1):
    """Cover a rectangle with size×size plates/tiles, h plates thick (1-stud strips at odd edges)."""
    out = []
    for i in range(0, w, size):
        for j in range(0, d, size):
            pw, pd = min(size, w - i), min(size, d - j)
            cx, cy = x0 + i + pw / 2, y0 + j + pd / 2
            if skip and skip(cx, cy):
                continue
            out.append(B.add(B.part(pw, pd, h, kind), mat, (cx, cy, z), coll=coll))
    return out


# --- machines ----------------------------------------------------------------
class Turbine:
    """Steam turbine along the x axis: three blade wheels growing towards the exhaust (high → low
    pressure) on one shaft, inside a cut-away half casing (front open, orange cut edges like the
    vessel). The rotor is an empty `self.rotor` (spin it about X); shaft + coupling are its children
    and reach `shaft_to` (into the generator)."""

    def __init__(self, x0, x1, cy, cz, casing_r=5.6, shaft_to=None, coll=None):
        self.x0, self.x1, self.cy, self.cz = x0, x1, cy, cz
        self.coll = coll
        self.r = casing_r
        self.white = L.plastic(L.COL["white"])
        self.lg = L.plastic(L.COL["lightgrey"])
        self.mid = L.plastic(L.COL["grey"])
        self.dark = L.plastic(L.COL["darkgrey"])
        self.cut = L.plastic(L.COL["orange"])
        self.steel = L.plastic("#5D6675", rough=0.35)
        self.objects = {"casing": [], "rotor": [], "base": []}
        xm = (x0 + x1) / 2
        self.rotor = empty("turbine_rotor", (xm, cy, cz), coll)
        self._casing()
        span = x1 - x0
        # two wheels: small high-pressure wheel at the inlet, big low-pressure wheel at the exhaust
        self.hp_x, self.lp_x = x0 + 0.27 * span, x0 + 0.73 * span
        self.stages = [self._wheel(self.hp_x - xm, 2.6, 8, nose=True),
                       self._wheel(self.lp_x - xm, 3.8, 10)]
        self._shaft(x0 + 0.4 - xm, (shaft_to if shaft_to is not None else x1 + 2) - xm)
        self.points = {
            "inlet": (self.hp_x, cy, cz + casing_r + 1.2),
            "top": (xm, cy, cz + casing_r + 1.2),
            "center": (xm, cy, cz),
            "exhaust": (self.lp_x, cy, cz - casing_r),
            "stage1": (self.hp_x, cy, cz),
            "stage3": (self.lp_x, cy, cz),
        }

    def _casing(self):
        n = int(round(math.pi * (self.r + 0.6)))  # ~1 stud per strip around the back half
        length = int(round(self.x1 - self.x0))
        pieces = [length] if length <= 8 else [length // 2, length - length // 2]
        for k in range(n + 1):
            th = k / n * math.pi  # 0 = top, pi = bottom, through +y (back)
            mat = self.cut if k in (0, n) else self.steel
            x = self.x0
            for s in pieces:
                ob = B.add(B.part(s, 1, 3), mat, (x + s / 2, self.cy + math.sin(th) * self.r, self.cz + math.cos(th) * self.r),
                           coll=self.coll)
                ob.rotation_euler = (-th, 0, 0)  # studs point radially outwards
                self.objects["casing"].append(ob)
                x += s

    def _wheel(self, lx, blade_len, count, pitch=34 * DEG, nose=False):
        """Fan wheel in the y-z plane: wide paddle blades (2-stud tiles) on a round hub."""
        blades = []
        hub = B.add(B.part(2, 2, 3, "round"), self.mid, (lx - B.BRICK / 2, 0, 0), coll=self.coll)
        hub.rotation_euler = (0, 90 * DEG, 0)
        child(self.rotor, hub)
        self.objects["rotor"].append(hub)
        if nose:  # spinner cone pointing at the inlet side (-x)
            cone = B.add(B.part(2, 2, 3, "cone", studs=False), self.white, (lx - B.BRICK / 2, 0, 0), coll=self.coll)
            cone.rotation_euler = (0, -90 * DEG, 0)
            child(self.rotor, cone)
            self.objects["rotor"].append(cone)
        part = B.part(2, int(math.ceil(blade_len)), 1, "tile")
        root = 0.8
        for k in range(count):
            psi = k / count * math.tau
            rot = (Matrix.Rotation(psi, 3, "X") @ Matrix.Rotation(90 * DEG + pitch, 3, "Y")).to_euler("XYZ")
            rr = root + part_len(part) / 2
            mat = self.white if k % 2 == 0 else self.lg
            ob = B.add(part, mat, (lx, math.cos(psi) * rr, math.sin(psi) * rr), coll=self.coll)
            ob.rotation_euler = rot
            child(self.rotor, ob)
            blades.append(ob)
            self.objects["rotor"].append(ob)
        return blades

    def _shaft(self, lx0, lx1):
        seg = B.part(1, 1, 3, "round", studs=False)
        x = lx0
        while x < lx1 - 0.2:
            ob = B.add(seg, self.dark, (x, 0, 0), coll=self.coll)
            ob.rotation_euler = (0, 90 * DEG, 0)
            child(self.rotor, ob)
            self.objects["rotor"].append(ob)
            x += 1.0
        # coupling disc with a cross, just before the generator: shows the shaft turning
        cx = lx1 - 1.6
        disc = B.add(B.part(3, 3, 1, "round", studs=False), self.mid, (cx, 0, 0), coll=self.coll)
        disc.rotation_euler = (0, 90 * DEG, 0)
        child(self.rotor, disc)
        for ang in (0, 90 * DEG):
            bar = B.add(B.part(1, 3, 1, studs=False), self.cut, (cx - B.PLATE, 0, 0), coll=self.coll)
            bar.rotation_euler = (Matrix.Rotation(ang, 3, "X") @ Matrix.Rotation(90 * DEG, 3, "Y")).to_euler("XYZ")
            child(self.rotor, bar)
            self.objects["rotor"].append(bar)
        self.objects["rotor"].append(disc)

    def spin(self, start, end, peak_deg, ramp_frames=55):
        A.spin(self.rotor, start, end, lambda f: peak_deg * smoothstep((f - start) / ramp_frames), axis=0)


def part_len(mesh):
    """Length (y extent) of a part mesh, from its name part_{w}x{d}x{h}_…"""
    dims = mesh.name.split("_")[1].split("x")
    return float(dims[1]) - B.GAP


class Generator:
    """Box generator on the turbine shaft: white body, dark end caps, yellow coil stripes on the
    front and a yellow terminal on top that glow when it runs. Sits on dark feet at `z0`."""

    def __init__(self, x0, cy, z0, w=8, d=6, levels=8, coll=None):
        self.coll = coll
        self.body = L.plastic(L.COL["white"])
        self.cap = L.plastic(L.COL["darkgrey"])
        self.coil = L.glow(L.COL["electric"], 0.0, name="gen_coil", base=L.COL["yellow"])
        y0 = cy - d / 2
        self.objects = []
        self.objects += slab(x0 + 1, y0 + 1, z0, w - 2, d - 2, 1, self.cap, coll)  # feet
        zb = z0 + B.BRICK
        self.objects += slab(x0, y0, zb, 1, d, levels, self.cap, coll)
        self.objects += slab(x0 + 1, y0, zb, w - 2, d, levels, self.body, coll)
        self.objects += slab(x0 + w - 1, y0, zb, 1, d, levels, self.cap, coll)
        # yellow coil stripes on the front face (tiles standing on the face)
        stripe = B.part(w - 3, 1, 1, "tile")
        n = 3
        for k in range(n):
            z = zb + levels * B.BRICK * (k + 1) / (n + 1)
            ob = B.add(stripe, self.coil, (x0 + w / 2, y0, z), coll=coll)
            ob.rotation_euler = (90 * DEG, 0, 0)
            self.objects.append(ob)
        top = zb + levels * B.BRICK
        self.objects.append(B.add(B.part(w - 3, 2, 1, "tile"), self.coil, (x0 + w / 2, cy - 1, top), coll=coll))
        self.terminal_base = B.add(B.part(1, 1, 3, "round"), self.cap, (x0 + w - 2, cy + 1.5, top), coll=coll)
        self.terminal = B.add(B.part(1, 1, 3, "round"), self.coil, (x0 + w - 2, cy + 1.5, top + B.BRICK), coll=coll)
        self.objects += [self.terminal_base, self.terminal]
        cz = zb + levels * B.BRICK / 2
        self.light = point_light("gen_light", (x0 + w / 2, y0 - 3.0, cz), L.COL["electric"], 0.0, 2.0, coll)
        self.points = {
            "center": (x0 + w / 2, cy, cz),
            "top": (x0 + w / 2, cy, top + B.PLATE),
            "terminal": (x0 + w - 2, cy + 1.5, top + 2 * B.BRICK),
            "front": (x0 + w / 2, y0, cz),
        }
        self.top_z = top

    def power(self, start, dur=16, strength=6.0, light=900.0):
        L.key_emission(self.coil, 1, 0.0)
        L.key_emission(self.coil, start, 0.0)
        L.key_emission(self.coil, start + dur, strength)
        key_light(self.light, 1, 0.0)
        key_light(self.light, start, 0.0)
        key_light(self.light, start + dur, light)


class Condenser:
    """Cut-away box under the turbine: back wall, side walls with orange cut edges, a deck on top
    (with an opening for the exhaust), trans-blue cooling tubes inside and a hot-well of water."""

    def __init__(self, x0, x1, y0, y1, levels, opening=(0, 0), coll=None, extend_to=None):
        self.coll = coll
        grey = L.plastic(L.COL["lightgrey"])
        white = L.plastic(L.COL["white"])
        cut = L.plastic(L.COL["orange"])
        dark = L.plastic(L.COL["darkgrey"])
        self.water = L.trans(L.COL["trans_blue"])
        w, d = int(round(x1 - x0)), int(round(y1 - y0))
        self.objects = []
        # back wall
        self.objects += slab(x0, y1 - 1, 0, w, 1, levels, grey, coll)
        # side walls; the front-most column is the orange cut edge
        for xs in (x0, x1 - 1):
            self.objects += wall_y(xs, y0 + 1, 0, d - 2, levels, white, coll)
            for lv in range(levels):
                self.objects.append(B.add(B.part(1, 1, 3), cut, (xs + 0.5, y0 + 0.5, lv * B.BRICK), coll=coll))
        top = levels * B.BRICK
        if extend_to:  # closed foundation block continuing to the right (under the generator)
            ew = int(round(extend_to - x1))
            self.objects += slab(x1, y0, 0, ew, d, levels, white, coll)
            w_deck = w + ew
        else:
            w_deck = w
        ox0, ox1 = opening
        self.deck = plate_grid(x0, y0, top, w_deck, d, dark, coll,
                               skip=lambda cx, cy: ox0 <= cx <= ox1 and cy < y1 - 1.5)
        self.objects += self.deck
        # cooling tubes: trans-blue round bricks lying along y (their round ends face the camera)
        self.tubes = []
        tube = B.part(1, 1, 3, "round", studs=False)
        for row, z in enumerate((3.6, 5.0, 6.4, 7.8)):
            for i in range(w - 3):
                x = x0 + 2.0 + i + (0.5 if row % 2 else 0.0)
                if x > x1 - 1.6:
                    continue
                ob = B.add(tube, self.water, (x, y1 - 1 - B.BRICK, z), coll=coll)
                ob.rotation_euler = (-90 * DEG, 0, 0)
                self.tubes.append(ob)
        self.objects += self.tubes
        # hot-well: water tiles on the floor
        self.hotwell = plate_grid(x0 + 1, y0 + 1, 0.0, w - 2, d - 2, self.water, coll, kind="tile")
        self.objects += self.hotwell
        self.points = {
            "center": ((x0 + x1) / 2, y0, top / 2),
            "top": ((x0 + x1) / 2, y0, top),
            "front_low": ((x0 + x1) / 2, y0, 1.2),
        }
        self.top = top


def pump(x, y, z, coll=None):
    """Small feed pump: round casing facing the camera, motor block behind, and an impeller cross on
    the front (an empty to spin about Y). Returns (objects, impeller_empty)."""
    out = []
    dark = L.plastic(L.COL["darkgrey"])
    blue = L.plastic(L.COL["blue"])
    casing = B.add(B.part(3, 3, 3, "round", studs=False), blue, (x, y + 0.6, z), coll=coll)
    casing.rotation_euler = (90 * DEG, 0, 0)  # axis along y, round face towards -y
    out.append(casing)
    out += slab(x - 1.5, y + 0.6, 0, 3, 3, max(1, int(round((z + 0.6) / B.BRICK))), dark, coll)
    imp = empty("pump_impeller", (x, y - 0.65, z), coll)
    for ang in (0, 60 * DEG, 120 * DEG):
        bar = B.add(B.part(1, 3, 1, studs=False), L.plastic(L.COL["white"]), (0, 0, 0), coll=coll)
        bar.rotation_euler = (Matrix.Rotation(ang, 3, "Y") @ Matrix.Rotation(90 * DEG, 3, "X")).to_euler("XYZ")
        child(imp, bar)
        out.append(bar)
    hub = B.add(B.part(1, 1, 1, "round"), dark, (0, 0, 0), coll=coll)
    hub.rotation_euler = (90 * DEG, 0, 0)
    child(imp, hub)
    out.append(hub)
    return out, imp


def pylon(x, y, levels, mat, arm_mat, coll=None):
    out = []
    for lv in range(levels):
        for dx in (-0.5, 0.5):
            out.append(B.add(B.part(1, 1, 3, "round"), mat, (x + dx, y, lv * B.BRICK), coll=coll))
    top = levels * B.BRICK
    out.append(B.add(B.part(6, 1, 1), arm_mat, (x, y, top), coll=coll))
    out.append(B.add(B.part(4, 1, 1), arm_mat, (x, y, top - 2 * B.BRICK), coll=coll))
    return out, (x, y, top + B.PLATE)


def cable(points, mat, radius=0.07, sag=0.0, samples=8, coll=None, name="cable"):
    """Thin cable (curve) through points; `sag` droops each span (catenary-ish parabola).
    Returns (object, dense point list) — the dense list doubles as a flow path."""
    dense = []
    for a, b in zip(points, points[1:]):
        a, b = Vector(a), Vector(b)
        for s in range(samples):
            t = s / samples
            p = a.lerp(b, t)
            p.z -= sag * 4 * t * (1 - t)
            dense.append(tuple(p))
    dense.append(tuple(points[-1]))
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(dense) - 1)
    for p, (x, y, z) in zip(spline.points, dense):
        p.co = (x, y, z, 1)
    ob = bpy.data.objects.new(name, curve)
    (coll or bpy.context.scene.collection).objects.link(ob)
    curve.materials.append(mat)
    return ob, dense


def house(x0, y0, w, d, levels, wall, roof_mat, windows_mats, coll=None, trim=None, window_rows=(1,)):
    """Small house: walls of 1×1 bricks, windows on `window_rows` (each window gets the next material
    from `windows_mats`, a callable k -> material, so they can light up one by one), a door and a
    stepped gable roof (ridge along x). Returns (bricks, windows) — windows sorted left to right."""
    bricks, windows = [], []
    k = 0
    for lv in range(levels):
        for i in range(w):
            for j in range(d):
                if 0 < i < w - 1 and 0 < j < d - 1:
                    continue
                corner = i in (0, w - 1) and j in (0, d - 1)
                loc = (x0 + i + 0.5, y0 + j + 0.5, lv * B.BRICK)
                if lv == 0 and j == 0 and i == w // 2:  # door
                    bricks.append(B.add(B.part(1, 1, 3), trim or roof_mat, loc, coll=coll))
                    continue
                is_win = lv in window_rows and not corner and (
                    (i % 2 == 1 and j in (0, d - 1)) or (j % 2 == 1 and i in (0, w - 1)))
                if is_win:
                    ob = B.add(B.part(1, 1, 3, studs=lv == levels - 1), windows_mats(k), loc, coll=coll)
                    ob["win_order"] = (i + (0 if j == 0 else 0.3), lv)
                    windows.append(ob)
                    k += 1
                else:
                    bricks.append(B.add(B.part(1, 1, 3, studs=lv == levels - 1), wall, loc, coll=coll))
    z = levels * B.BRICK
    # stepped gable roof: each layer is one stud narrower front and back
    s = 0
    while d + 2 - 2 * s > 0:
        bricks += plate_grid(x0 - 1, y0 - 1 + s, z + s * 2 * B.PLATE, w + 2, d + 2 - 2 * s, roof_mat, coll, size=2, h=2)
        s += 1
    windows.sort(key=lambda o: o.location.x)
    return bricks, windows
