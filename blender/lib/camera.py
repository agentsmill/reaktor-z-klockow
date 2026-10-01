"""Camera moves: smooth piecewise paths through keyed poses (baked per frame)."""
from . import anim as A


def path(ob, keys):
    """keys: list of (frame, (x, y, z)) — eases in/out between consecutive poses."""
    keys = sorted(keys)
    for (f0, p0), (f1, p1) in zip(keys, keys[1:]):
        A.bake(ob, f0, f1, lambda t, p0=p0, p1=p1: tuple(p0[i] + (p1[i] - p0[i]) * A.ease_in_out_cubic(t) for i in range(3)))


def fstop(cam, keys):
    """Animate aperture (depth of field): keys = [(frame, f-number), ...]."""
    keys = sorted(keys)
    for (f0, a0), (f1, a1) in zip(keys, keys[1:]):
        for f in range(f0, f1 + 1):
            cam.data.dof.aperture_fstop = a0 + (a1 - a0) * A.ease_in_out_cubic((f - f0) / max(1, f1 - f0))
            cam.data.dof.keyframe_insert("aperture_fstop", frame=f)


def lens(cam, keys):
    """Animate focal length: keys = [(frame, mm), ...]."""
    keys = sorted(keys)
    for (f0, l0), (f1, l1) in zip(keys, keys[1:]):
        for f in range(f0, f1 + 1):
            cam.data.lens = l0 + (l1 - l0) * A.ease_in_out_cubic((f - f0) / max(1, f1 - f0))
            cam.data.keyframe_insert("lens", frame=f)
