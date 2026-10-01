"""Named 3D points projected to screen space for every frame, so Remotion labels can follow
3D objects. Written to public/renders/<shot>/anchors.json as {name: [[x, y, visible], ...]}
in 1920×1080 pixels, index 0 = Blender frame 1 = Remotion scene frame 0."""
import json

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

_points: dict = {}


def anchor(name, target):
    """target: (x, y, z) or an object (its location, following animation)."""
    _points[name] = target


def export(path, frames):
    if not _points:
        return
    scene = bpy.context.scene
    cam = scene.camera
    out = {name: [] for name in _points}
    for f in range(1, frames + 1):
        scene.frame_set(f)
        for name, target in _points.items():
            loc = target.matrix_world.translation if hasattr(target, "matrix_world") else Vector(target)
            co = world_to_camera_view(scene, cam, loc)
            visible = co.z > 0 and 0 <= co.x <= 1 and 0 <= co.y <= 1
            out[name].append([round(co.x * 1920, 1), round((1 - co.y) * 1080, 1), int(visible)])
    with open(path, "w") as fh:
        json.dump(out, fh)
    _points.clear()
