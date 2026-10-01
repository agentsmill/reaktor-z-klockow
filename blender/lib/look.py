"""Materials, lights, world, camera and render settings — the shared visual style."""
import math

import bpy
from mathutils import Vector


def srgb(hex_color):
    """'#RRGGBB' → linear RGBA (Blender colours are linear)."""
    h = hex_color.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, 1.0)


_mats: dict = {}


def _principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


def plastic(hex_color, rough=0.32, name=None):
    key = ("abs", hex_color, rough)
    if key not in _mats:
        mat, bsdf = _principled(name or f"abs_{hex_color}")
        bsdf.inputs["Base Color"].default_value = srgb(hex_color)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Coat Weight"].default_value = 0.25
        bsdf.inputs["Coat Roughness"].default_value = 0.08
        _mats[key] = mat
    return _mats[key]


def trans(hex_color, name=None, rough=0.06):
    """Transparent plastic (water, fuel, glass)."""
    key = ("trans", hex_color, rough)
    if key not in _mats:
        mat, bsdf = _principled(name or f"trans_{hex_color}")
        bsdf.inputs["Base Color"].default_value = srgb(hex_color)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Coat Weight"].default_value = 0.4
        bsdf.inputs["Alpha"].default_value = 0.55
        bsdf.inputs["Emission Color"].default_value = srgb(hex_color)
        bsdf.inputs["Emission Strength"].default_value = 0.15  # a touch of inner glow, like lit trans plastic
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"
        if hasattr(mat, "use_transparency_overlap"):
            mat.use_transparency_overlap = False
        _mats[key] = mat
    return _mats[key]


def glow(hex_color, strength=6.0, name=None, base=None):
    """Emissive plastic (neutrons, lit windows, electricity). Strength can be keyframed later."""
    mat, bsdf = _principled(name or f"glow_{hex_color}_{len(_mats)}")
    bsdf.inputs["Base Color"].default_value = srgb(base or hex_color)
    bsdf.inputs["Roughness"].default_value = 0.25
    bsdf.inputs["Emission Color"].default_value = srgb(hex_color)
    bsdf.inputs["Emission Strength"].default_value = strength
    _mats[("glow", name or len(_mats))] = mat
    return mat


def key_emission(mat, frame, strength):
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Emission Strength"].keyframe_insert("default_value", frame=frame)


# Palette (sRGB hex). Colour = meaning, same as the 2D version.
COL = {
    "white": "#F2F3F2",
    "lightgrey": "#A0A5A9",
    "grey": "#6C6E68",
    "darkgrey": "#3E4447",
    "black": "#1B2A34",
    "green": "#3F9C35",
    "darkgreen": "#184632",
    "lime": "#BBE90B",
    "tan": "#E4CD9E",
    "brown": "#6B4226",
    "darkbrown": "#352100",
    "red": "#C91A09",
    "yellow": "#F2CD37",
    "orange": "#FE8A18",
    "blue": "#0055BF",
    "navy": "#0A3463",
    "trans_blue": "#4F8FE8",
    "trans_clear": "#EEEEEE",
    "trans_green": "#4CC85A",
    "trans_orange": "#F08F1C",
    "trans_yellow": "#F5CD2F",
    "neutron": "#5CE1FF",
    "uranium": "#9BE15D",
    "heat": "#FF8A3D",
    "electric": "#FFD447",
}


def world(hex_color="#1A2C4A", strength=0.55):
    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = srgb(hex_color)
    bg.inputs["Strength"].default_value = strength
    return w


def area_light(name, loc, target, size, energy, hex_color="#FFFFFF"):
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "DISK"
    data.size = size
    data.energy = energy
    data.color = srgb(hex_color)[:3]
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    direction = Vector(target) - Vector(loc)
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return ob


def studio(center=(0, 0, 0), scale=1.0, warmth="#FFE2B8"):
    """Warm key front-left, cool rim behind, soft fill right — toy-photography lighting."""
    cx, cy, cz = center
    s = scale
    key = area_light("key", (cx - 30 * s, cy - 34 * s, cz + 42 * s), center, 34 * s, 52000 * s * s, warmth)
    rim = area_light("rim", (cx + 26 * s, cy + 40 * s, cz + 26 * s), center, 20 * s, 60000 * s * s, "#9CC4FF")
    fill = area_light("fill", (cx + 40 * s, cy - 20 * s, cz + 14 * s), center, 40 * s, 9000 * s * s, "#DDE6FF")
    for ob in (key, rim, fill):
        ob["energy_scale"] = s * s  # lets day/night cycles re-key energies at the same scale
    return key, rim, fill


def sun(elevation=22.0, azimuth=-135.0, strength=4.0, hex_color="#FFB46B", softness=3.0, name="sun"):
    """Low golden-hour sun: long soft shadows and glinting studs. Azimuth 0° = light travelling towards +Y."""
    data = bpy.data.lights.new(name, "SUN")
    data.energy = strength
    data.color = srgb(hex_color)[:3]
    data.angle = math.radians(softness)
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(90 - elevation), 0, math.radians(azimuth))
    return ob


TOY_SCALE = 0.008  # 1 BU = 8 mm


def fstop(real_f_number):
    """Aperture value for a *real-world* f-number at toy scale. EEVEE (Blender 5.2) ignores
    unit_settings.scale_length for depth of field and treats 1 BU as 1 m, so a miniature look
    needs the f-number scaled by the toy scale (f/5.6 → 0.045)."""
    return real_f_number * TOY_SCALE


def camera(loc, target, lens=50, fstop=4.0, name="cam"):
    """Camera aimed at an empty (animate either); DOF focuses on the empty."""
    tgt = bpy.data.objects.new(f"{name}_target", None)
    bpy.context.scene.collection.objects.link(tgt)
    tgt.location = target
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.dof.use_dof = True
    data.dof.focus_object = tgt
    data.dof.aperture_fstop = fstop
    data.clip_start = 0.1
    data.clip_end = 2000
    cam = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam, tgt


def render_settings(frames, preview=False):
    sc = bpy.context.scene
    engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 33 if preview else 100
    sc.render.fps = 30
    sc.frame_start = 1
    sc.frame_end = frames
    ee = sc.eevee
    ee.taa_render_samples = 16 if preview else 24  # A/B-tested: 24 ≈ 32 visually, ~30% faster
    for attr, value in (("use_raytracing", True), ("use_shadows", True), ("shadow_ray_count", 1), ("shadow_step_count", 6),
                        ("bokeh_max_size", 50)):
        if hasattr(ee, attr):
            setattr(ee, attr, value)
    sc.render.use_motion_blur = not preview
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92
    sc.unit_settings.scale_length = 0.008  # 1 BU = 8 mm → real macro-photography depth of field
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Punchy"
    except TypeError:
        pass
    _glare(sc)


def _glare(sc):
    """Bloom for emissive bricks via compositor glare (API differs between Blender 4.x and 5.x)."""
    try:
        if hasattr(sc, "compositing_node_group"):  # Blender 5.x
            tree = bpy.data.node_groups.new("comp", "CompositorNodeTree")
            sc.compositing_node_group = tree
            rl = tree.nodes.new("CompositorNodeRLayers")
            gl = tree.nodes.new("CompositorNodeGlare")
            out = tree.nodes.new("NodeGroupOutput")
            tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
            for name, value in (("Type", "Bloom"), ("Threshold", 1.0), ("Strength", 0.6), ("Size", 0.6)):
                if name in gl.inputs:
                    try:
                        gl.inputs[name].default_value = value
                    except (TypeError, ValueError):
                        pass
            tree.links.new(rl.outputs["Image"], gl.inputs["Image"])
            tree.links.new(gl.outputs["Image"], out.inputs[0])
        else:  # Blender 4.x
            sc.use_nodes = True
            tree = sc.node_tree
            rl = tree.nodes.get("Render Layers") or tree.nodes.new("CompositorNodeRLayers")
            comp = tree.nodes.get("Composite") or tree.nodes.new("CompositorNodeComposite")
            gl = tree.nodes.new("CompositorNodeGlare")
            gl.glare_type = "BLOOM" if "BLOOM" in {i.identifier for i in gl.bl_rna.properties["glare_type"].enum_items} else "FOG_GLOW"
            gl.threshold = 1.0
            gl.mix = 0.0
            tree.links.new(rl.outputs["Image"], gl.inputs["Image"])
            tree.links.new(gl.outputs["Image"], comp.inputs["Image"])
    except Exception as exc:  # glare is a nicety; never block a render on it
        print(f"[look] glare setup skipped: {exc}")
