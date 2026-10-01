"""Animation helpers. Motion is baked per frame (no reliance on F-curve easing APIs, which
changed in Blender 4.4/5.x with slotted actions). Frames are Blender frames (1-based)."""
import math


def ease_out_back(t, s=1.4):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t):
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_bounce(t):
    n, d = 7.5625, 2.75
    if t < 1 / d:
        return n * t * t
    if t < 2 / d:
        t -= 1.5 / d
        return n * t * t + 0.75
    if t < 2.5 / d:
        t -= 2.25 / d
        return n * t * t + 0.9375
    t -= 2.625 / d
    return n * t * t + 0.984375


def clamp01(x):
    return max(0.0, min(1.0, x))


def show_from(ob, frame):
    """Hidden before `frame`, visible from it (boolean keys are constant)."""
    ob.hide_render = True
    ob.keyframe_insert("hide_render", frame=0)
    ob.hide_render = False
    ob.keyframe_insert("hide_render", frame=frame)


def hide_from(ob, frame):
    ob.hide_render = False
    ob.keyframe_insert("hide_render", frame=max(0, frame - 1))
    ob.hide_render = True
    ob.keyframe_insert("hide_render", frame=frame)


def bake(ob, start, end, fn, path="location"):
    """Keyframe `path` on every frame in [start, end] with value fn(t in 0..1)."""
    span = max(1, end - start)
    for f in range(start, end + 1):
        setattr(ob, path, fn(clamp01((f - start) / span)))
        ob.keyframe_insert(path, frame=f)


def drop_in(ob, start, dur=12, height=14.0, spin=0.0):
    """Brick falls from above and clicks into place with a little overshoot."""
    x, y, z = ob.location
    rz = ob.rotation_euler.z
    show_from(ob, start)
    bake(ob, start, start + dur, lambda t: (x, y, z + height * (1 - ease_out_bounce(t))))
    if spin:
        bake(ob, start, start + dur, lambda t: (0, 0, rz + spin * (1 - ease_out_cubic(t))), "rotation_euler")


def fly(ob, start, dur, frm, to, ease=ease_in_out_cubic, arc=0.0):
    """Move from `frm` to `to`, optionally along a vertical arc."""
    def pos(t):
        e = ease(t)
        return tuple(frm[i] + (to[i] - frm[i]) * e for i in range(3))[:2] + (
            frm[2] + (to[2] - frm[2]) * e + arc * math.sin(math.pi * t),
        )
    bake(ob, start, start + dur, pos)


def pop_scale(ob, start, dur=10, to=1.0):
    show_from(ob, start)
    bake(ob, start, start + dur, lambda t: (to * ease_out_back(t),) * 3, "scale")


def spin(ob, start, end, deg_per_frame_at, axis=2):
    """Rotation with a time-varying speed: deg_per_frame_at(f) integrated per frame."""
    angle = 0.0
    base = list(ob.rotation_euler)
    for f in range(start, end + 1):
        angle += math.radians(deg_per_frame_at(f))
        rot = list(base)
        rot[axis] = base[axis] + angle
        ob.rotation_euler = rot
        ob.keyframe_insert("rotation_euler", frame=f)


def hide_span(ob, first, last, end):
    """Hide on frames first..last (inclusive), visible again after — never past `end`."""
    ob.hide_render = True
    ob.keyframe_insert("hide_render", frame=first)
    if last + 1 <= end:
        ob.hide_render = False
        ob.keyframe_insert("hide_render", frame=last + 1)


def stream(objs, start, end, path_fn, period):
    """Objects travel a looping path: object k is offset by k/len(objs) of the loop.
    path_fn(u in 0..1) → (x, y, z). Hidden outside [start, end], and hidden for the two
    frames around each loop restart so motion blur never smears the jump back to the start."""
    n = len(objs)
    for k, ob in enumerate(objs):
        show_from(ob, start)
        hide_from(ob, end + 1)
        prev = None
        for f in range(start, end + 1):
            u = ((f - start) / period + k / n) % 1.0
            ob.location = path_fn(u)
            ob.keyframe_insert("location", frame=f)
            if prev is not None and u < prev and f - 1 >= start:  # wrapped between f-1 and f
                hide_span(ob, f - 1, f, end)
            prev = u
