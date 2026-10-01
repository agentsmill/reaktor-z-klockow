"""Kit for the "fission" and "control" shots (also imported by lib/control_kit.py).

Centred brick meshes, nuclei (individual bricks for the hero, merged half-meshes for the field),
neutrons with light streaks, heat flashes, the chain-reaction cascade (port of src/lib/cascade.ts)
and a coal heap. Everything is baked per frame; per-object fades use the Object Info alpha
(`ob.color[3]`) so one material can serve many objects.
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

from . import bricks as B
from . import look as L

# ------------------------------------------------------------------ camera depth of field

# EEVEE Next (Blender 5.2) ignores unit_settings.scale_length for depth of field: it treats 1 BU as
# 1 m, so a "real" f/2.8 gives no visible blur at toy scale. Multiply real-world f-numbers by the unit
# scale (0.008 = 8 mm per stud) to get true miniature/macro blur.
DOF_SCALE = 0.008


def fstop(real_f_number):
    """Real-world f-number → aperture value (delegates to look.fstop when the shared helper exists)."""
    if hasattr(L, "fstop"):
        return L.fstop(real_f_number)
    return real_f_number * DOF_SCALE


# ------------------------------------------------------------------ maths / easing


def clamp01(x):
    return max(0.0, min(1.0, x))


def lerp(a, b, t):
    return a + (b - a) * t


def vlerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def ramp(f, f0, f1):
    return clamp01((f - f0) / max(1e-6, f1 - f0))


def smooth(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    t = clamp01(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_cubic(t):
    return 1 - (1 - clamp01(t)) ** 3


def ease_in_cubic(t):
    return clamp01(t) ** 3


def ease_out_expo(t):
    t = clamp01(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-9 * t)


def ease_out_back(t, s=1.2):
    t = clamp01(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def log_lerp(a, b, t):
    """Interpolate distances multiplicatively (zooms feel constant-speed)."""
    return math.exp(lerp(math.log(a), math.log(b), t))


def hermite(keys, f):
    """Smooth curve through keys [(frame, value|tuple), ...]: cubic Hermite with Catmull-Rom tangents,
    zero velocity at the first/last key. Values may be floats or tuples."""
    keys = sorted(keys, key=lambda k: k[0])
    scalar = not isinstance(keys[0][1], (tuple, list, Vector))
    vals = [Vector((k[1], 0.0)) if scalar else Vector(k[1]) for k in keys]  # mathutils needs size >= 2
    ts = [k[0] for k in keys]
    if f <= ts[0]:
        out = vals[0]
    elif f >= ts[-1]:
        out = vals[-1]
    else:
        i = max(j for j in range(len(ts) - 1) if ts[j] <= f)
        t0, t1 = ts[i], ts[i + 1]
        h = t1 - t0
        u = (f - t0) / h

        def tangent(j):
            if j == 0 or j == len(ts) - 1:
                return vals[j] * 0
            return (vals[j + 1] - vals[j - 1]) / (ts[j + 1] - ts[j - 1])

        m0, m1 = tangent(i) * h, tangent(i + 1) * h
        h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
        h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
        out = vals[i] * h00 + m0 * h10 + vals[i + 1] * h01 + m1 * h11
    return out[0] if scalar else out


def hash01(*xs):
    """Deterministic pseudo-random in [0, 1) from integers/floats."""
    h = 0
    for x in xs:
        h = (h * 1000003) ^ int(round(x * 1000)) & 0xFFFFFFFF
        h = (h ^ (h >> 13)) * 0x5BD1E995 & 0xFFFFFFFF
    return ((h ^ (h >> 15)) & 0xFFFFFF) / float(0x1000000)


# ------------------------------------------------------------------ keyframing


def bake(ob, f0, f1, fn, path="location"):
    """Key `path` on every frame of [f0, f1] with fn(frame)."""
    for f in range(f0, f1 + 1):
        setattr(ob, path, fn(f))
        ob.keyframe_insert(path, frame=f)


def key(ob, path, frame, value):
    setattr(ob, path, value)
    ob.keyframe_insert(path, frame=frame)


def visible_during(ob, intervals):
    """Render-visible only inside [start, end) intervals (hidden before, between and after)."""
    ob.hide_render = True
    ob.keyframe_insert("hide_render", frame=min([0] + [s - 1 for s, _ in intervals]))
    for s, e in sorted(intervals):
        ob.hide_render = False
        ob.keyframe_insert("hide_render", frame=s)
        if e is not None:
            ob.hide_render = True
            ob.keyframe_insert("hide_render", frame=e)


def clip_intervals(intervals, window):
    """Intersect [start, end) intervals (end None = open) with window [w0, w1) (None = no clipping)."""
    if window is None:
        return list(intervals)
    w0, w1 = window
    out = []
    for s, e in intervals:
        e = w1 if e is None else min(e, w1)
        s = max(s, w0)
        if s < e:
            out.append((s, e))
    return out


def key_energy(light_ob, frame, energy):
    light_ob.data.energy = energy
    light_ob.data.keyframe_insert("energy", frame=frame)


def bake_energy(light_ob, f0, f1, fn):
    for f in range(f0, f1 + 1):
        key_energy(light_ob, f, fn(f))


def key_alpha(ob, frame, alpha):
    c = list(ob.color)
    c[3] = alpha
    ob.color = c
    ob.keyframe_insert("color", frame=frame)


def key_world(frame, hex_color, strength):
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = L.srgb(hex_color)
    bg.inputs["Color"].keyframe_insert("default_value", frame=frame)
    bg.inputs["Strength"].default_value = strength
    bg.inputs["Strength"].keyframe_insert("default_value", frame=frame)


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def empty(name, loc=(0, 0, 0), coll=None, parent=None):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = 0.5
    link(ob, coll)
    ob.location = loc
    if parent is not None:
        ob.parent = parent
    return ob


def add(mesh, mat, loc=(0, 0, 0), name="brick", coll=None, parent=None):
    """Object with a per-object material (slot linked to OBJECT)."""
    ob = bpy.data.objects.new(name, mesh)
    link(ob, coll)
    ob.location = loc
    if parent is not None:
        ob.parent = parent
    if mat is not None:
        slot = ob.material_slots[0]
        slot.link = "OBJECT"
        slot.material = mat
    return ob


def point_light(name, loc, hex_color, energy=0.0, radius=0.4, shadow=False, coll=None):
    data = bpy.data.lights.new(name, "POINT")
    data.color = L.srgb(hex_color)[:3]
    data.energy = energy
    data.shadow_soft_size = radius
    data.use_shadow = shadow
    ob = bpy.data.objects.new(name, data)
    link(ob, coll)
    ob.location = loc
    return ob


# ------------------------------------------------------------------ meshes

_meshes: dict = {}


def centered(w=1, d=1, h=3, kind="round"):
    """Brick part with its origin at the geometric centre (for tumbling / flying bricks)."""
    k = ("c", w, d, h, kind)
    if k not in _meshes:
        me = B.part(w, d, h, kind).copy()
        me.name = f"cpart_{w}x{d}x{h}_{kind}"
        me.transform(Matrix.Translation((0, 0, -h * B.PLATE / 2)))
        _meshes[k] = me
    return _meshes[k]


def lowpoly_round(h=3, segments=12):
    """Light 1×1 round brick (centred) for merged meshes: few polygons, same silhouette."""
    k = ("lp", h, segments)
    if k in _meshes:
        return _meshes[k]
    bm = bmesh.new()
    height = h * B.PLATE
    r = 0.49
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r, radius2=r, depth=height)
    rim = [e for e in bm.edges if abs(abs(e.verts[0].co.z) - height / 2) < 1e-4 and abs(abs(e.verts[1].co.z) - height / 2) < 1e-4]
    bmesh.ops.bevel(bm, geom=rim, offset=0.045, segments=1, affect="EDGES")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=B.STUD_R, radius2=B.STUD_R, depth=B.STUD_H,
                          matrix=Matrix.Translation((0, 0, height / 2 + B.STUD_H / 2)))
    me = bpy.data.meshes.new(f"lp_round_{h}")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))
    _meshes[k] = me
    return me


def merged(name, items, part_me, materials):
    """One mesh made of many copies of `part_me`: items = [((x, y, z), material_index), ...]."""
    co = [v.co.copy() for v in part_me.vertices]
    polys = [tuple(p.vertices) for p in part_me.polygons]
    verts, faces, mats = [], [], []
    for off, mi in items:
        base = len(verts)
        verts += [(c.x + off[0], c.y + off[1], c.z + off[2]) for c in co]
        faces += [tuple(base + i for i in poly) for poly in polys]
        mats += [mi] * len(polys)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("material_index", mats)
    me.update()
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))
    for m in materials:
        me.materials.append(m)
    return me


def ico(subdiv=3):
    k = ("ico", subdiv)
    if k not in _meshes:
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
        me = bpy.data.meshes.new(f"ico{subdiv}")
        bm.to_mesh(me)
        bm.free()
        me.shade_smooth()
        me.materials.append(None)
        _meshes[k] = me
    return _meshes[k]


def streak_mesh():
    """Comet tail: a cone along +Z from z=-1 (thin tail) to z=0 (head); scale z = length."""
    if "streak" not in _meshes:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.04, radius2=0.42, depth=1.0,
                              matrix=Matrix.Translation((0, 0, -0.5)))
        me = bpy.data.meshes.new("streak")
        bm.to_mesh(me)
        bm.free()
        me.shade_smooth()
        me.materials.append(None)
        _meshes["streak"] = me
    return _meshes["streak"]


# ------------------------------------------------------------------ materials


def _clear(mat):
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return nt


def glow_obj(hex_color, strength, base=None, name="glow_obj", rough=0.25, coat=0.3):
    """Emissive plastic whose emission is multiplied by the object's alpha (ob.color[3])."""
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = L.srgb(base or hex_color)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Emission Color"].default_value = L.srgb(hex_color)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    nt.links.new(oi.outputs["Alpha"], mul.inputs[0])
    nt.links.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
    mat["strength_node"] = mul.name
    return mat


def set_glow_strength(mat, frame, strength):
    """Keyframe the base strength of a glow_obj material."""
    node = mat.node_tree.nodes[mat["strength_node"]]
    node.inputs[1].default_value = strength
    node.inputs[1].keyframe_insert("default_value", frame=frame)


def key_emission_color(mat, frame, hex_color):
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Color"].default_value = L.srgb(hex_color)
    bsdf.inputs["Emission Color"].keyframe_insert("default_value", frame=frame)


def bubble_mat(hex_color, strength, name="bubble", power=2.6):
    """Flash shell: object colour G = how solid the core is (1 = glowing ball, 0 = thin rim only),
    A = overall opacity. One material serves every flash."""
    mat = bpy.data.materials.new(name)
    nt = _clear(mat)
    n, ln = nt.nodes, nt.links
    out = n.new("ShaderNodeOutputMaterial")
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    pw = n.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = power
    ln.new(lw.outputs["Facing"], pw.inputs[0])
    oi = n.new("ShaderNodeObjectInfo")
    sep = n.new("ShaderNodeSeparateColor")
    ln.new(oi.outputs["Color"], sep.inputs[0])
    inv = n.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    ln.new(pw.outputs[0], inv.inputs[1])
    mad = n.new("ShaderNodeMath")  # rim + (1 - rim) * core
    mad.operation = "MULTIPLY_ADD"
    ln.new(inv.outputs[0], mad.inputs[0])
    ln.new(sep.outputs[1], mad.inputs[1])
    ln.new(pw.outputs[0], mad.inputs[2])
    fac = n.new("ShaderNodeMath")
    fac.operation = "MULTIPLY"
    fac.use_clamp = True
    ln.new(mad.outputs[0], fac.inputs[0])
    ln.new(oi.outputs["Alpha"], fac.inputs[1])
    em = n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = L.srgb(hex_color)
    em.inputs["Strength"].default_value = strength
    tr = n.new("ShaderNodeBsdfTransparent")
    mix = n.new("ShaderNodeMixShader")
    ln.new(fac.outputs[0], mix.inputs[0])
    ln.new(tr.outputs[0], mix.inputs[1])
    ln.new(em.outputs[0], mix.inputs[2])
    ln.new(mix.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    mat.use_backface_culling = True
    return mat


def key_color(ob, frame, rgba):
    ob.color = rgba
    ob.keyframe_insert("color", frame=frame)


def plastic_new(hex_color, rough=0.3, name="abs", coat=0.3):
    """Uncached ABS plastic (so a shot can animate it without touching shared materials)."""
    mat = bpy.data.materials.new(name)
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = L.srgb(hex_color)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = 0.08
    bsdf.inputs["Emission Color"].default_value = L.srgb(hex_color)
    bsdf.inputs["Emission Strength"].default_value = 0.0
    return mat


def trans_new(hex_color, alpha=0.5, emit=0.35, name="trans", rough=0.06):
    """Uncached translucent plastic with a little inner glow."""
    mat = bpy.data.materials.new(name)
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = L.srgb(hex_color)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Coat Weight"].default_value = 0.5
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["Emission Color"].default_value = L.srgb(hex_color)
    bsdf.inputs["Emission Strength"].default_value = emit
    mat.surface_render_method = "BLENDED"
    mat.use_transparency_overlap = False
    return mat


def key_bsdf(mat, frame, **values):
    """Keyframe Principled inputs, e.g. key_bsdf(m, 10, emission_strength=3, emission_color='#FF8A3D')."""
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    for k, v in values.items():
        sock = bsdf.inputs[k.replace("_", " ").title()]
        sock.default_value = L.srgb(v) if isinstance(v, str) else v
        sock.keyframe_insert("default_value", frame=frame)


def streak_mat(hex_color, strength, name="streak"):
    """Light trail: transparent at the tail, glowing at the head (Generated Z), soft edges."""
    mat = bpy.data.materials.new(name)
    nt = _clear(mat)
    n, ln = nt.nodes, nt.links
    out = n.new("ShaderNodeOutputMaterial")
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    ln.new(tc.outputs["Generated"], sep.inputs[0])
    pw = n.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 2.2
    ln.new(sep.outputs["Z"], pw.inputs[0])
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.45
    inv = n.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    ln.new(lw.outputs["Facing"], inv.inputs[1])
    m1 = n.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    ln.new(pw.outputs[0], m1.inputs[0])
    ln.new(inv.outputs[0], m1.inputs[1])
    oi = n.new("ShaderNodeObjectInfo")
    fac = n.new("ShaderNodeMath")
    fac.operation = "MULTIPLY"
    fac.use_clamp = True
    ln.new(m1.outputs[0], fac.inputs[0])
    ln.new(oi.outputs["Alpha"], fac.inputs[1])
    em = n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = L.srgb(hex_color)
    em.inputs["Strength"].default_value = strength
    tr = n.new("ShaderNodeBsdfTransparent")
    mix = n.new("ShaderNodeMixShader")
    ln.new(fac.outputs[0], mix.inputs[0])
    ln.new(tr.outputs[0], mix.inputs[1])
    ln.new(em.outputs[0], mix.inputs[2])
    ln.new(mix.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    return mat


def ceramic_pellet_mat(name="pellet"):
    """Dark UO2 ceramic with a uranium-green rim glow. Keys: 'rim' (rim glow) and 'body' (whole-surface glow)."""
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    n, ln = nt.nodes, nt.links
    bsdf = n["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = L.srgb("#3A4036")
    bsdf.inputs["Roughness"].default_value = 0.42
    bsdf.inputs["Coat Weight"].default_value = 0.35
    bsdf.inputs["Coat Roughness"].default_value = 0.12
    bsdf.inputs["Emission Color"].default_value = L.srgb(L.COL["uranium"])
    lw = n.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    pw = n.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 2.0
    ln.new(lw.outputs["Facing"], pw.inputs[0])
    rim = n.new("ShaderNodeMath")
    rim.name = "rim"
    rim.operation = "MULTIPLY"
    rim.inputs[1].default_value = 0.0
    ln.new(pw.outputs[0], rim.inputs[0])
    body = n.new("ShaderNodeMath")
    body.name = "body"
    body.operation = "ADD"
    body.inputs[1].default_value = 0.0
    ln.new(rim.outputs[0], body.inputs[0])
    ln.new(body.outputs[0], bsdf.inputs["Emission Strength"])
    return mat


def key_pellet(mat, frame, rim=None, body=None):
    nt = mat.node_tree
    if rim is not None:
        nt.nodes["rim"].inputs[1].default_value = rim
        nt.nodes["rim"].inputs[1].keyframe_insert("default_value", frame=frame)
    if body is not None:
        nt.nodes["body"].inputs[1].default_value = body
        nt.nodes["body"].inputs[1].keyframe_insert("default_value", frame=frame)


# ------------------------------------------------------------------ nuclei

U235 = 235  # nucleons in the hero nucleus — one brick each
BIG, SMALL = 143, 92  # fragments: Ba-141 (+2 prompt neutrons) and Kr-92 (+ the captured neutron, re-emitted)
BA, KR = 141, 92


def nucleus_offsets(n=U235):
    """Brick centres (stud units; z steps of one brick height) of the n lattice points nearest the centre."""
    cand = []
    for i in range(-6, 7):
        for j in range(-6, 7):
            for k in range(-5, 6):
                p = (float(i), float(j), k * B.BRICK)
                cand.append((p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + 1e-4 * hash01(i, j, k), p))
    cand.sort(key=lambda c: c[0])
    pts = [Vector(c[1]) for c in cand[:n]]
    cen = centroid(pts)
    return [p - cen for p in pts]


def split_partition(offsets, axis, n_small=SMALL, seed=0):
    """Indices of the small fragment (on the +axis side, jagged fracture) and of the big one."""
    axis = Vector(axis).normalized()
    score = [(p.dot(axis) + 0.9 * (hash01(p.x, p.y, p.z, seed) - 0.5), i) for i, p in enumerate(offsets)]
    score.sort(reverse=True)
    small = sorted(i for _, i in score[:n_small])
    big = sorted(i for _, i in score[n_small:])
    return big, small


def centroid(points):
    c = Vector((0, 0, 0))
    for p in points:
        c += p
    return c / max(1, len(points))


def assign_ball(local_pts, n=None):
    """Map each point (relative to its fragment centroid) to a slot of a compact ball of the same
    size: greedy, outermost slots first, so bricks travel little. Returns list of ball offsets."""
    ball = nucleus_offsets(n or len(local_pts))
    ball.sort(key=lambda q: -q.length)
    free = list(range(len(local_pts)))
    out = [None] * len(local_pts)
    for q in ball:
        j = min(free, key=lambda i: (local_pts[i] - q).length_squared)
        free.remove(j)
        out[j] = q
    return out


def nucleus_set(prefix, glow=1.1, bright=2.2):
    """(translucent, solid, glowing, bright) uranium bricks — uncached so shots can animate them."""
    return (
        trans_new("#3FC75C", alpha=0.5, emit=0.3, name=f"{prefix}_trans"),
        plastic_new("#24823A", rough=0.2, name=f"{prefix}_solid"),
        glow_obj("#7FD846", glow, base="#4FAE36", name=f"{prefix}_glow"),
        glow_obj("#C6FF86", bright, base="#93D85A", name=f"{prefix}_bright"),
    )


def pick_material(i, seed=0, weights=(0.3, 0.25, 0.33, 0.12)):
    r = hash01(i, seed, 7)
    acc = 0.0
    for k, w in enumerate(weights):
        acc += w
        if r < acc:
            return k
    return len(weights) - 1


class FieldNuclei:
    """Merged meshes for the field: intact U-235 balls (a few colour variants) and the two smaller
    fragment balls (Ba-141, Kr-92) that replace a nucleus when it splits (hidden by the flash)."""

    def __init__(self, mats, frag_mats, variants=3, seed=11):
        part = lowpoly_round()
        offs = nucleus_offsets()
        self.intact = [merged(f"u235_{v}", [(tuple(p), pick_material(i, seed + v)) for i, p in enumerate(offs)], part, mats)
                       for v in range(variants)]
        self.frags = {}
        for n, tag in ((BA, "ba"), (KR, "kr")):
            o = nucleus_offsets(n)
            self.frags[tag] = [merged(f"{tag}_{v}", [(tuple(p), pick_material(i, seed + 5 + v, (0.25, 0.35, 0.4))) for i, p in enumerate(o)],
                                      part, frag_mats) for v in range(variants)]
        self.radius = {"u": max(p.length for p in offs) + 0.6, "ba": max(p.length for p in nucleus_offsets(BA)) + 0.6,
                       "kr": max(p.length for p in nucleus_offsets(KR)) + 0.6}

    def place(self, center, variant, rot_z=0.0, coll=None, name="nuc"):
        v = variant % len(self.intact)
        ob = bpy.data.objects.new(name, self.intact[v])
        link(ob, coll)
        ob.visible_shadow = False
        ob.location = center
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = (0.0, 0.0, rot_z)
        ba = bpy.data.objects.new(f"{name}_ba", self.frags["ba"][v])
        kr = bpy.data.objects.new(f"{name}_kr", self.frags["kr"][v])
        for o in (ba, kr):
            link(o, coll)
            o.visible_shadow = False
            o.location = center
            o.rotation_mode = "QUATERNION"
        return {"ob": ob, "ba": ba, "kr": kr, "center": Vector(center), "split": None}


def split_field_nucleus(nuc, f, axis, push=7.0, tumble=0.9, seed=0, hot=1.0, cool=70):
    """At frame f the intact ball is swapped (under the flash) for two smaller hot balls flying
    apart along `axis` — Kr 1.55× farther than Ba (momentum) — tumbling, then cooling down.
    Visibility is returned in nuc["vis"] (apply once with visible_during, clipped to the shot)."""
    rnd = random.Random(seed)
    axis = Vector(axis).normalized()
    c = nuc["center"]
    nuc["split"] = f
    ob = nuc["ob"]
    key(ob, "scale", f - 4, (1, 1, 1))
    key(ob, "scale", f - 1, (1.1, 1.1, 1.1))
    for part, sign, reach in ((nuc["ba"], -1, push * KR / (BA + KR) * 2), (nuc["kr"], 1, push * BA / (BA + KR) * 2)):
        spin = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized()
        speed = tumble * (1.5 if sign > 0 else 1.0)
        for k in range(0, 61):
            t = k / 60
            e = ease_out_expo(t * 1.6)
            key(part, "location", f + k, c + axis * sign * (0.8 + reach * e + 0.6 * t))
            key(part, "rotation_quaternion", f + k, Quaternion(spin, speed * (ease_out_cubic(t * 1.4) + 0.4 * t)))
        key_alpha(part, f, hot)
        key_alpha(part, f + 10, hot * 0.75)
        key_alpha(part, f + cool, 0.06)
    nuc["vis"] = {"ob": [(0, f)], "ba": [(f, None)], "kr": [(f, None)]}


# ------------------------------------------------------------------ neutrons, flashes


class Neutron:
    """A glowing cyan brick with a comet streak (and optionally its own light)."""

    def __init__(self, name, mat, trail_mat, coll=None, part=(1, 1, 3, "round"), scale=1.0, light=0.0, streak=3.2):
        self.ob = add(centered(*part), mat, (0, 0, -1e4), name=name, coll=coll)
        self.ob.visible_shadow = False
        self.ob.scale = (scale,) * 3
        self.ob.rotation_mode = "XYZ"
        self.tail = add(streak_mesh(), trail_mat, (0, 0, -1e4), name=f"{name}_tail", coll=coll)
        self.tail.visible_shadow = False
        self.tail.rotation_mode = "QUATERNION"
        self.streak = streak * scale
        self.scale = scale
        self.light = point_light(f"{name}_light", (0, 0, -1e4), L.COL["neutron"], 0.0, 0.3, coll=coll) if light else None
        self.light_energy = light
        self.intervals = []

    def fly(self, f0, f1, p0, p1, ease=None, spin=14.0, fade_out=False):
        """Straight flight p0 → p1 between frames f0..f1 (visible), hidden from f1 + 1."""
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        dirn = d.normalized() if d.length > 1e-6 else Vector((1, 0, 0))
        q = dirn.to_track_quat("Z", "Y")
        span = max(1, f1 - f0)
        ease = ease or (lambda t: t)
        for f in range(f0, f1 + 1):
            t = (f - f0) / span
            pos = p0 + d * ease(t)
            key(self.ob, "location", f, pos)
            key(self.ob, "rotation_euler", f, (math.radians(spin * f), math.radians(spin * 0.7 * f), 0))
            travelled = (pos - p0).length
            length = max(0.05, min(self.streak, travelled))
            key(self.tail, "location", f, pos)
            key(self.tail, "rotation_quaternion", f, q)
            key(self.tail, "scale", f, (self.scale, self.scale, length))
            if fade_out:
                a = 1.0 - smooth(ramp(f, f1 - 10, f1))
                key_alpha(self.ob, f, a)
                key_alpha(self.tail, f, a)
            if self.light:
                key(self.light, "location", f, pos)
                key_energy(self.light, f, self.light_energy * (1 - (smooth(ramp(f, f1 - 10, f1)) if fade_out else 0)))
        if self.light:
            key_energy(self.light, f1 + 1, 0.0)
            key_energy(self.light, f0 - 1, 0.0)
        self.intervals.append((f0, f1 + 1))

    def finish(self, window=None):
        iv = clip_intervals(self.intervals, window)
        visible_during(self.ob, iv)
        visible_during(self.tail, iv)


class Flash:
    """Heat flash: a small white-hot core that pops and fades fast, a thin glowing shell racing
    outward, and a point light that lights up the neighbourhood. Both shapes share bubble_mat
    materials (object colour G = solid core amount, A = opacity)."""

    def __init__(self, name, shell_mat, core_mat, coll=None, light_color=None, shadow=False):
        self.shell = add(ico(3), shell_mat, (0, 0, -1e4), name=f"{name}_shell", coll=coll) if shell_mat else None
        self.core = add(ico(2), core_mat, (0, 0, -1e4), name=f"{name}_core", coll=coll)
        for ob in (self.shell, self.core):
            if ob is not None:
                ob.visible_shadow = False
        self.light = point_light(f"{name}_light", (0, 0, -1e4), light_color or L.COL["heat"], 0.0, 1.0, shadow=shadow, coll=coll) \
            if light_color is not False else None
        self.intervals, self.core_iv = [], []

    def fire(self, f, loc, size=10.0, dur=16, energy=20000.0, decay=10.0, core_size=None, core_dur=6, alpha=1.0):
        loc = Vector(loc)
        core_size = core_size or size * 0.38
        for ob in (self.shell, self.core):
            if ob is not None:
                key(ob, "location", f - 1, loc)
                key(ob, "location", f + dur, loc)
        for k in range(0, (dur + 1) if self.shell else 0):
            t = k / dur
            key(self.shell, "scale", f + k, ((size * (0.12 + 0.88 * ease_out_expo(t * 0.9))),) * 3)
            key_color(self.shell, f + k, (1.0, 0.0, 1.0, alpha * (1 - smooth(t)) ** 1.1))
        for k in range(0, core_dur + 1):
            t = k / core_dur
            grow = 0.6 + 0.4 * min(1.0, k / 1.5)
            key(self.core, "scale", f + k, ((core_size * grow * (1 - t) ** 0.9 + 0.01),) * 3)
            key_color(self.core, f + k, (1.0, 1.0, 1.0, 1.0 if k < 2 else (1 - t) ** 0.7))
        self.intervals.append((f, f + dur + 1))
        self.core_iv.append((f, f + core_dur + 1))
        if self.light:
            n = int(decay * 6)
            key(self.light, "location", f - 1, loc)
            key(self.light, "location", f + n, loc)
            key_energy(self.light, f - 1, 0.0)
            for k in range(0, n):
                key_energy(self.light, f + k, energy * math.exp(-k / decay) * min(1.0, (k + 1) / 2.0))
            key_energy(self.light, f + n, 0.0)

    def finish(self, window=None):
        if self.shell is not None:
            visible_during(self.shell, clip_intervals(self.intervals, window))
        visible_during(self.core, clip_intervals(self.core_iv, window))
        if self.light is not None and window is not None:
            visible_during(self.light, [window])


# ------------------------------------------------------------------ cascade (port of src/lib/cascade.ts)


def hex_lattice(spacing, x0, x1, z0, z1):
    """Hexagonal lattice points (x, z) with rows along x, containing (0, 0)."""
    row_h = spacing * math.sqrt(3) / 2
    pts = []
    rows = int(max(abs(z0), abs(z1)) / row_h) + 2
    cols = int(max(abs(x0), abs(x1)) / spacing) + 2
    for r in range(-rows, rows + 1):
        for c in range(-cols, cols + 1):
            x = c * spacing + (abs(r) % 2) * spacing * 0.5
            z = r * row_h
            if x0 <= x <= x1 and z0 <= z <= z1:
                pts.append((x, z))
    return pts


def build_cascade(points, root, first_targets, branching, start, gap, first_times=None):
    """Grow the chain outward. first_targets: indices hit by the root's neutrons (with first_times).
    branching[g] = how many nuclei each node of generation g+1 sets off. Returns nodes
    [{idx, gen, parent, split}] — root first."""
    dist = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])  # noqa: E731
    used = {root}
    nodes = [{"idx": root, "gen": 0, "parent": None, "split": start - gap}]

    def pick(frm, d):
        o = points[frm]
        best, best_s = None, float("inf")
        for i, p in enumerate(points):
            if i in used:
                continue
            dd = dist(p, o)
            if dd < 1:
                continue
            cos = ((p[0] - o[0]) * d[0] + (p[1] - o[1]) * d[1]) / dd
            if cos < 0.5:
                continue
            s = dd * (2 - cos)
            if s < best_s:
                best_s, best = s, i
        return best

    frontier = []
    for j, t in enumerate(first_targets):
        used.add(t)
        nodes.append({"idx": t, "gen": 1, "parent": 0, "split": (first_times or [start] * 9)[j]})
        frontier.append(len(nodes) - 1)
    for g, k in enumerate(branching):
        nxt = []
        for n in frontier:
            node = nodes[n]
            p = points[node["idx"]]
            o = points[nodes[node["parent"]]["idx"]]
            base = math.atan2(p[1] - o[1], p[0] - o[0])
            for j in range(k):
                a = base + (0 if k == 1 else (j / (k - 1) - 0.5) * 1.3)
                t = pick(node["idx"], (math.cos(a), math.sin(a)))
                if t is None:
                    continue
                used.add(t)
                nodes.append({"idx": t, "gen": node["gen"] + 1, "parent": n,
                              "split": node["split"] + gap + ((j * 5 + n * 3) % 9)})
                nxt.append(len(nodes) - 1)
        frontier = nxt
    return nodes


# ------------------------------------------------------------------ coal heap


def coal_heap(center, radius, height, mats, seed=5, coll=None, step=1.05):
    """Mound of tilted dark 1×1 / 1×2 / 2×2 bricks (paraboloid profile). Returns bricks bottom-up."""
    rnd = random.Random(seed)
    cx, cy, cz = center
    out = []
    z, layer = 0.0, 0
    while True:
        r = radius * math.sqrt(max(0.0, 1 - z / height))
        if r < 0.7:
            break
        n = int(r / step) + 1
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x = (i + (layer % 2) * 0.5) * step + rnd.uniform(-0.3, 0.3)
                y = (j + (layer % 3) * 0.33) * step + rnd.uniform(-0.3, 0.3)
                if x * x + y * y > r * r or rnd.random() < 0.18:
                    continue
                w, d = rnd.choice([(1, 1), (1, 2), (1, 2), (1, 1), (2, 2), (1, 3)])
                ob = B.add(B.part(w, d, 3), rnd.choice(mats), (cx + x, cy + y, cz + z + rnd.uniform(-0.25, 0.15)), coll=coll)
                rim = math.sqrt(x * x + y * y) / max(r, 1e-3)
                tilt = 0.12 + 0.5 * rim
                ob.rotation_euler = (rnd.uniform(-tilt, tilt), rnd.uniform(-tilt, tilt), rnd.uniform(0, math.tau))
                out.append(ob)
        z += 0.9
        layer += 1
    return out
