"""Generic toy-brick library (no logos, no brand). 1 stud pitch = 1.0 Blender unit (8 mm).

Meshes are cached per part type and shared by every brick object (linked data), with the
material linked per object, so thousands of bricks stay light.
"""
import math

import bmesh
import bpy
from mathutils import Matrix

P = 1.0  # stud pitch
PLATE = 0.4  # plate height; a brick is 3 plates
BRICK = 3 * PLATE
STUD_R = 0.3
STUD_H = 0.2
GAP = 0.02  # tiny gap so neighbouring bricks read as separate pieces
BEVEL = 0.035

_meshes: dict = {}


def _stud(bm, x, y, z):
    res = bmesh.ops.create_cone(
        bm, cap_ends=True, segments=24, radius1=STUD_R, radius2=STUD_R, depth=STUD_H,
        matrix=Matrix.Translation((x, y, z + STUD_H / 2)),
    )
    top = z + STUD_H
    verts = set(res["verts"])
    ring = [e for e in bm.edges if e.verts[0] in verts and e.verts[1] in verts
            and abs(e.verts[0].co.z - top) < 1e-4 and abs(e.verts[1].co.z - top) < 1e-4]
    bmesh.ops.bevel(bm, geom=ring, offset=0.04, segments=2, affect="EDGES", profile=0.5)


def stud_mesh():
    """A single stud (for baseplate arrays)."""
    if "stud" not in _meshes:
        bm = bmesh.new()
        _stud(bm, 0, 0, 0)
        me = bpy.data.meshes.new("part_stud")
        bm.to_mesh(me)
        bm.free()
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(35))
        me.materials.append(None)
        _meshes["stud"] = me
    return _meshes["stud"]


def part(w=1, d=1, h=3, kind="box", studs=True):
    """Mesh for a w×d part, h plates tall. kind: box | round | tile | cone."""
    key = (w, d, h, kind, studs)
    if key in _meshes:
        return _meshes[key]
    bm = bmesh.new()
    height = h * PLATE
    sx, sy = w * P - GAP, d * P - GAP
    if kind in ("round", "cone"):
        top_r = sx / 2 if kind == "round" else max(STUD_R + 0.05, sx * 0.18)
        bmesh.ops.create_cone(
            bm, cap_ends=True, segments=36, radius1=sx / 2, radius2=top_r, depth=height,
            matrix=Matrix.Translation((0, 0, height / 2)),
        )
    else:
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(sx, sy, height), verts=res["verts"])
        bmesh.ops.translate(bm, vec=(0, 0, height / 2), verts=res["verts"])
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=BEVEL, segments=2, affect="EDGES", profile=0.5)
    if studs and kind != "tile":
        if kind == "cone" or (kind == "round" and w == 1):
            _stud(bm, 0, 0, height)
        else:
            for i in range(w):
                for j in range(d):
                    _stud(bm, (i - (w - 1) / 2) * P, (j - (d - 1) / 2) * P, height)
    me = bpy.data.meshes.new(f"part_{w}x{d}x{h}_{kind}{'' if studs else '_flat'}")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))
    me.materials.append(None)
    _meshes[key] = me
    return me


def baseplate(w, d, mat, name="baseplate", loc=(0, 0, 0)):
    """Thin plate with a stud grid via array modifiers (cheap to build, fine to render)."""
    plate = add(part(1, 1, 1, "tile", studs=False), mat, (0, 0, 0), name=name)
    plate.scale = (w * P, d * P, 0.5)
    plate.location = (loc[0] + (w - 1) * P / 2, loc[1] + (d - 1) * P / 2, loc[2] - 0.2)
    studs = add(stud_mesh(), mat, (loc[0], loc[1], loc[2]), name=f"{name}_studs")
    for axis, count in ((0, w), (1, d)):
        mod = studs.modifiers.new(f"arr{axis}", "ARRAY")
        mod.count = count
        mod.use_relative_offset = False
        mod.use_constant_offset = True
        mod.constant_offset_displace = (P if axis == 0 else 0, P if axis == 1 else 0, 0)
    return plate, studs


def add(mesh, mat, loc, rot_z=0.0, name="brick", coll=None):
    """Place a part. `loc` = centre of the part's footprint at its bottom face."""
    ob = bpy.data.objects.new(name, mesh)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (0, 0, rot_z)
    slot = ob.material_slots[0]
    slot.link = "OBJECT"
    slot.material = mat
    return ob


def at(i, j, level=0):
    """Grid → world: stud column i, row j, height in plates."""
    return (i * P, j * P, level * PLATE)


def collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll
