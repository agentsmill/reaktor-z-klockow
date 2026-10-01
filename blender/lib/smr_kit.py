"""Helpers for the "smr" shot (some reused by "poland"):

- merge(): join many brick objects into one mesh object (big structures stay light and
  animate as units — a cooling-tower ring, a factory wall, a prefab module);
- lowpoly_part(): the same brick at a fraction of the polygons, for far-away bulk;
- slope(): a sloped roof brick (saw-tooth factory roof) with a glazed vertical face;
- truck(): a small toy truck (parent empty + parts) with spinning wheels;
- puff()/plume(): cotton-wool steam, the classic toy-photography trick;
- smooth()/camera_rig(): camera moves through keyed poses with continuous velocity
  (eases only at the ends), orbiting around an animated target;
- golden_sun(): low warm key light for long soft shadows.
Everything animated is baked per frame (no F-curve easing APIs)."""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import anim as A
from . import bricks as B
from . import look as L

_cache: dict = {}


# --- baking ---------------------------------------------------------------
def bake_fn(ob, f0, f1, fn, path="location"):
    """Keyframe `path` on every frame f in [f0, f1] with value fn(f)."""
    for f in range(f0, f1 + 1):
        setattr(ob, path, fn(f))
        ob.keyframe_insert(path, frame=f)


def smooth(keys, f):
    """Monotone cubic Hermite through keyed values [(frame, value|tuple)]: continuous
    velocity through inner keys, ease in at the first key and out at the last."""
    keys = sorted(keys, key=lambda k: k[0])
    scalar = not isinstance(keys[0][1], (tuple, list))
    vals = [(k[1],) if scalar else tuple(k[1]) for k in keys]
    fr = [k[0] for k in keys]
    if f <= fr[0] or len(keys) == 1:
        out = vals[0]
    elif f >= fr[-1]:
        out = vals[-1]
    else:
        i = max(j for j in range(len(fr) - 1) if fr[j] <= f)
        h = fr[i + 1] - fr[i]
        t = (f - fr[i]) / h

        def tangent(j):
            if j == 0 or j == len(fr) - 1:
                return [0.0] * len(vals[0])
            d0 = [(b - a) / (fr[j] - fr[j - 1]) for a, b in zip(vals[j - 1], vals[j])]
            d1 = [(b - a) / (fr[j + 1] - fr[j]) for a, b in zip(vals[j], vals[j + 1])]
            return [2 * x * y / (x + y) if x * y > 0 else 0.0 for x, y in zip(d0, d1)]

        m0, m1 = tangent(i), tangent(i + 1)
        h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
        h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
        out = tuple(h00 * p0 + h10 * h * a + h01 * p1 + h11 * h * b
                    for p0, p1, a, b in zip(vals[i], vals[i + 1], m0, m1))
    return out[0] if scalar else out


def orbit_point(target, r, az_deg, el_deg):
    """Camera position around `target`: azimuth 0 = due south (-y), + = towards +x."""
    az, el = math.radians(az_deg), math.radians(el_deg)
    t = Vector(target)
    return t + Vector((r * math.cos(el) * math.sin(az), -r * math.cos(el) * math.cos(az), r * math.sin(el)))


def camera_rig(cam, tgt, end, target_keys, orbit_keys, lens_keys=None, fstop_keys=None, shift_keys=None, start=1):
    """Bake camera + aim target per frame. orbit_keys: [(frame, (radius, azimuth°, elevation°))]
    relative to the (animated) target; shift_keys: [(frame, (shift_x, shift_y))]."""
    for f in range(start, end + 1):
        t = Vector(smooth(target_keys, f))
        tgt.location = t
        cam.location = orbit_point(t, *smooth(orbit_keys, f))
        tgt.keyframe_insert("location", frame=f)
        cam.keyframe_insert("location", frame=f)
        if lens_keys:
            cam.data.lens = smooth(lens_keys, f)
            cam.data.keyframe_insert("lens", frame=f)
        if fstop_keys:
            cam.data.dof.aperture_fstop = smooth(fstop_keys, f)
            cam.data.dof.keyframe_insert("aperture_fstop", frame=f)
        if shift_keys:
            cam.data.shift_x, cam.data.shift_y = smooth(shift_keys, f)
            cam.data.keyframe_insert("shift_x", frame=f)
            cam.data.keyframe_insert("shift_y", frame=f)


# --- light ----------------------------------------------------------------
def golden_sun(az_deg=-50.0, el_deg=24.0, strength=4.0, color="#FFC27A", angle_deg=7.0, name="sun_key"):
    """Low warm sun (key) coming from azimuth/elevation (same convention as orbit_point)."""
    data = bpy.data.lights.new(name, "SUN")
    data.energy = strength
    data.color = L.srgb(color)[:3]
    data.angle = math.radians(angle_deg)
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    to_sun = orbit_point((0, 0, 0), 1.0, az_deg, el_deg)
    ob.rotation_euler = (-to_sun).to_track_quat("-Z", "Y").to_euler()
    ob.location = to_sun * 80
    return ob


def lighting(center, scale, sun_az=-50.0, sun_el=24.0, sun_strength=4.0, key_dim=0.35, sun_color="#FFC27A"):
    """Shared studio rig (rim + fill) with the area key dimmed into a soft front fill and
    a low golden sun as the real key → warm light, long soft shadows."""
    key, rim, fill = L.studio(center=center, scale=scale, warmth="#FFE6C4")
    key.data.energy *= key_dim
    rim.data.energy *= 0.7
    for lamp in (rim, fill):
        lamp.data.specular_factor = 0.25  # keep the edge light, lose the glare on glossy baseplates
    sun = golden_sun(sun_az, sun_el, sun_strength, color=sun_color)
    return sun, key, rim, fill


# --- materials --------------------------------------------------------------
def cotton(name="cotton_steam"):
    """Soft steam puffs: cotton-white, edges fade out (facing-based alpha) so overlapping
    puffs read as one soft plume instead of hard balls."""
    if name in _cache:
        return _cache[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = L.srgb("#F4F6F8")
    bsdf.inputs["Roughness"].default_value = 0.95
    bsdf.inputs["Sheen Weight"].default_value = 0.8
    bsdf.inputs["Subsurface Weight"].default_value = 0.25
    bsdf.inputs["Subsurface Scale"].default_value = 0.6
    bsdf.inputs["Emission Color"].default_value = L.srgb("#FFF2E2")
    bsdf.inputs["Emission Strength"].default_value = 0.12
    out = nt.nodes["Material Output"]
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs["Facing"], inv.inputs[1])
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 1.6
    nt.links.new(inv.outputs[0], pw.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.92
    nt.links.new(pw.outputs[0], mul.inputs[0])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mul.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(bsdf.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    _cache[name] = mat
    return mat


def rubber():
    return L.plastic("#1C1D20", rough=0.6)


# --- meshes ---------------------------------------------------------------
def _key_of(mesh):
    for k, m in B._meshes.items():
        if m == mesh:
            return k
    return None


def lowpoly_part(w=1, d=1, h=3, kind="round", studs=True, seg=14):
    """Same footprint/height as bricks.part but ~6× lighter (for distant bulk)."""
    key = ("lp", w, d, h, kind, studs, seg)
    if key in _cache:
        return _cache[key]
    bm = bmesh.new()
    height = h * B.PLATE
    sx, sy = w * B.P - B.GAP, d * B.P - B.GAP
    if kind in ("round", "cone"):
        top_r = sx / 2 if kind == "round" else max(B.STUD_R + 0.05, sx * 0.18)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=sx / 2, radius2=top_r, depth=height,
                              matrix=Matrix.Translation((0, 0, height / 2)))
        rims = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-5]
    else:
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(sx, sy, height), verts=res["verts"])
        bmesh.ops.translate(bm, vec=(0, 0, height / 2), verts=res["verts"])
        rims = list(bm.edges)
    bmesh.ops.bevel(bm, geom=rims, offset=B.BEVEL, segments=1, affect="EDGES", profile=0.5)
    if studs and kind != "tile":
        spots = [(0, 0)] if (kind == "cone" or (kind == "round" and w == 1)) else [
            ((i - (w - 1) / 2) * B.P, (j - (d - 1) / 2) * B.P) for i in range(w) for j in range(d)]
        for x, y in spots:
            bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=B.STUD_R, radius2=B.STUD_R, depth=B.STUD_H,
                                  matrix=Matrix.Translation((x, y, height + B.STUD_H / 2)))
    me = bpy.data.meshes.new(f"lp_{w}x{d}x{h}_{kind}")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))
    _cache[key] = me
    return me


def merge(objs, name, origin=(0.0, 0.0, 0.0), lowpoly=False, mat_fn=None, coll=None):
    """Join brick objects into ONE object (origin at `origin`), keeping each brick's
    material per face. Source objects are deleted. mat_fn(ob) may override materials."""
    bm = bmesh.new()
    mats = []
    org = Vector(origin)
    for ob in objs:
        mat = mat_fn(ob) if mat_fn else (ob.material_slots[0].material if ob.material_slots else None)
        if mat not in mats:
            mats.append(mat)
        src = ob.data
        if lowpoly:
            key = _key_of(src)
            if key and key != "stud":
                src = lowpoly_part(*key)
        nv, nf = len(bm.verts), len(bm.faces)
        bm.from_mesh(src)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        mw = Matrix.Translation(Vector(ob.location) - org) @ ob.rotation_euler.to_matrix().to_4x4() @ Matrix.Diagonal((*ob.scale, 1.0))
        bmesh.ops.transform(bm, matrix=mw, verts=bm.verts[nv:])
        mi = mats.index(mat)
        for fc in bm.faces[nf:]:
            fc.material_index = mi
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    out = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(out)
    out.location = org
    for ob in objs:
        bpy.data.objects.remove(ob, do_unlink=True)
    return out


def by_level(objs, z0=0.0, step=B.BRICK):
    """Group bricks into lists by their brick level (bottom-up)."""
    levels = {}
    for ob in objs:
        levels.setdefault(int(round((ob.location.z - z0) / step)), []).append(ob)
    return [levels[k] for k in sorted(levels)]


def slope(w, d, h_lo, h_hi, roof_mat, glass_mat, flat=1.0, name="slope", coll=None):
    """Slope brick w (x) × d (y): low lip h_lo at -x rising to h_hi, a flat studded strip
    `flat` wide at +x, and a glazed vertical face at +x (saw-tooth roof tooth)."""
    key = ("slope", w, d, h_lo, h_hi, flat)
    if key not in _cache:
        bm = bmesh.new()
        sx, sy = w - B.GAP, d - B.GAP
        x0, x1, xf = -sx / 2, sx / 2, sx / 2 - flat
        y0, y1 = -sy / 2, sy / 2
        prof = [(x0, 0.0), (x1, 0.0), (x1, h_hi), (xf, h_hi), (x0, h_lo)]  # side profile (x, z)
        front = [bm.verts.new((x, y0, z)) for x, z in prof]
        back = [bm.verts.new((x, y1, z)) for x, z in prof]
        bm.faces.new(list(reversed(front)))
        bm.faces.new(back)
        n = len(prof)
        quads = []
        for k in range(n):
            a, b = k, (k + 1) % n
            quads.append(bm.faces.new((front[a], front[b], back[b], back[a])))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        quads[1].material_index = 1  # the vertical +x face = glazing
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=B.BEVEL, segments=2, affect="EDGES", profile=0.5)
        for j in range(d):
            yy = (j - (d - 1) / 2)
            res = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=B.STUD_R, radius2=B.STUD_R, depth=B.STUD_H,
                                        matrix=Matrix.Translation((x1 - flat / 2, yy, h_hi + B.STUD_H / 2)))
            for v in res["verts"]:
                for fc in v.link_faces:
                    fc.material_index = 0
        me = bpy.data.meshes.new(f"slope_{w}x{d}")
        bm.to_mesh(me)
        bm.free()
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(35))
        _cache[key] = me
    me = _cache[key].copy()
    me.materials.clear()
    me.materials.append(roof_mat)
    me.materials.append(glass_mat)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def wheel_mesh(radius=0.72, width=0.55):
    key = ("wheel", radius, width)
    if key in _cache:
        return _cache[key]
    bm = bmesh.new()
    rot = Matrix.Rotation(math.radians(90), 4, "X")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=radius, radius2=radius, depth=width, matrix=rot)
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if abs(abs(e.verts[0].co.y) - width / 2) < 1e-4
                              and abs(abs(e.verts[1].co.y) - width / 2) < 1e-4],
                    offset=0.08, segments=2, affect="EDGES", profile=0.5)
    nf = len(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=radius * 0.48, radius2=radius * 0.48,
                          depth=width + 0.08, matrix=rot)
    bm.faces.ensure_lookup_table()
    for fc in bm.faces[nf:]:
        fc.material_index = 1
    me = bpy.data.meshes.new("wheel")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))
    me.materials.append(rubber())
    me.materials.append(L.plastic(L.COL["lightgrey"]))
    _cache[key] = me
    return me


def puff_meshes(n=3, seed=11):
    """A few cotton-ball clusters (merged icospheres) to cycle through."""
    if "puffs" in _cache:
        return _cache["puffs"]
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        bm = bmesh.new()
        for s in range(3):
            r = rnd.uniform(0.75, 1.0)
            off = (rnd.uniform(-0.55, 0.55), rnd.uniform(-0.55, 0.55), rnd.uniform(-0.3, 0.35)) if s else (0, 0, 0)
            bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r, matrix=Matrix.Translation(off))
        me = bpy.data.meshes.new(f"puff_{k}")
        bm.to_mesh(me)
        bm.free()
        me.shade_smooth()
        me.materials.append(cotton())
        out.append(me)
    _cache["puffs"] = out
    return out


def plume(origin, start, end, n=10, period=84, rise=13.0, drift=(4.0, 2.5), size=(1.6, 4.2), seed=3, coll=None):
    """Steam plume: puffs emitted one by one from `origin` from frame `start`, each rising,
    swelling and drifting downwind, shrinking away at the top. Returns the puff objects."""
    rnd = random.Random(seed)
    meshes = puff_meshes()
    ox, oy, oz = origin
    obs = []
    for k in range(n):
        ob = bpy.data.objects.new(f"puff_{seed}_{k}", meshes[k % len(meshes)])
        (coll or bpy.context.scene.collection).objects.link(ob)
        born = start + int(k * period / n)
        jx, jy = rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8)
        spin0 = rnd.uniform(0, math.tau)
        A.show_from(ob, born)
        A.hide_from(ob, end + 1)
        for f in range(born, end + 1):
            u = ((f - born) / period) % 1.0
            grow = A.ease_out_cubic(min(1.0, u / 0.18))
            fade = 1.0 - A.clamp01((u - 0.72) / 0.28) ** 1.6
            s = (size[0] + (size[1] - size[0]) * u ** 0.8) * grow * fade
            ob.location = (ox + jx + drift[0] * u ** 1.4, oy + jy + drift[1] * u ** 1.4, oz + rise * u ** 0.85)
            ob.scale = (s, s, s * 0.85)
            ob.rotation_euler = (0, 0, spin0 + u * 0.8)
            ob.keyframe_insert("location", frame=f)
            ob.keyframe_insert("scale", frame=f)
            ob.keyframe_insert("rotation_euler", frame=f)
        obs.append(ob)
    return obs


# --- vehicles -------------------------------------------------------------------
WHEEL_R = 0.72


LOAD_X = (-3.5, 0.5, 4.5)  # local x of the three module slots on the low-loader


def truck(name, cab_mat, coll=None):
    """Toy low-loader facing -x: parent empty at ground centre, children in local space.
    Bed top at z = 1.4; module slots at LOAD_X (4 studs apart). Returns (root, wheels)."""
    root = bpy.data.objects.new(name, None)
    (coll or bpy.context.scene.collection).objects.link(root)
    dark = L.plastic(L.COL["darkgrey"])
    glass = L.trans("#BFD7F2")
    white = L.plastic(L.COL["white"])
    light = L.plastic(L.COL["lightgrey"])

    def part(mesh, mat, loc):
        ob = B.add(mesh, mat, loc, coll=coll)
        ob.parent = root
        return ob

    part(B.part(17, 4, 1), dark, (0.0, 0.0, 1.0))                    # chassis + bed (x -8.5..8.5)
    part(B.part(3, 4, 3, studs=False), cab_mat, (-7.0, 0.0, 1.4))    # cab body
    part(B.part(1, 4, 3, studs=False), glass, (-8.0, 0.0, 2.6))      # windscreen
    part(B.part(2, 4, 3), cab_mat, (-6.5, 0.0, 2.6))                 # cab top
    part(B.part(3, 4, 1, "tile"), white, (-7.0, 0.0, 3.8))           # roof
    part(B.part(1, 4, 1, "tile"), light, (-9.0, 0.0, 0.6))           # bumper
    part(B.part(1, 4, 3, studs=False), light, (8.0, 0.0, 1.4))       # tail gate
    wheels = []
    for x in (-7.0, 4.6, 6.6):
        for y in (-2.2, 2.2):
            ob = bpy.data.objects.new(f"{name}_wheel", wheel_mesh(WHEEL_R))
            (coll or bpy.context.scene.collection).objects.link(ob)
            ob.parent = root
            ob.location = (x, y, WHEEL_R)
            wheels.append(ob)
    return root, wheels


def drive(root, wheels, f0, f1, x0, x1, y, ease=A.ease_in_out_cubic):
    """Truck drives along x from x0 to x1 (frames f0..f1), wheels rolling. Returns x(f)."""
    def x_at(f):
        t = A.clamp01((f - f0) / max(1, f1 - f0))
        return x0 + (x1 - x0) * ease(t)
    bake_fn(root, f0, f1, lambda f: (x_at(f), y, 0.0))
    for w in wheels:
        bake_fn(w, f0, f1, lambda f: (0.0, (x_at(f) - x0) / WHEEL_R, 0.0), "rotation_euler")
    return x_at


def squash(ob, f, amount=0.12, frames=6):
    """Little click-in squash after landing (origin must be at the bottom)."""
    wave = [1.0, 0.45, -0.18, 0.06, 0.0, 0.0][:frames]
    for k, s in enumerate(wave):
        ob.scale = (1 + amount * 0.45 * s, 1 + amount * 0.45 * s, 1 - amount * s)
        ob.keyframe_insert("scale", frame=f + k)


def hop(ob, f0, f1, p0, p1, arc=4.0, wiggle=0.18):
    """Lift a module off the truck and set it down: arc with a little wobble, lands with a
    click (squash)."""
    def t_at(f):
        return A.clamp01((f - f0) / max(1, f1 - f0))

    def pos(f):
        t = t_at(f)
        e = A.ease_in_out_cubic(t)
        return tuple(p0[i] + (p1[i] - p0[i]) * e for i in range(2)) + (
            p0[2] + (p1[2] - p0[2]) * e + arc * math.sin(math.pi * t),)
    bake_fn(ob, f0, f1, pos)
    bake_fn(ob, f0, f1, lambda f: (wiggle * 0.5 * math.sin(2 * math.pi * t_at(f)), 0.0, wiggle * math.sin(math.pi * t_at(f))),
            "rotation_euler")
    squash(ob, f1)
