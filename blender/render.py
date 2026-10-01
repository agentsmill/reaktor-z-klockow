"""Headless shot runner.

  blender -b -P blender/render.py -- --shot intro --preview --frames 1,60,120
  blender -b -P blender/render.py -- --shot intro             # full JPEG sequence → public/renders/intro/
  blender -b -P blender/render.py -- --shot intro --save      # also writes out/blend/intro.blend

Cue frames in blender/timeline.json are Remotion scene frames (0-based); Blender frame = cue + 1.
"""
import argparse
import importlib
import json
import os
import sys
import time

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--shot", required=True)
ap.add_argument("--preview", action="store_true", help="33% resolution, 16 samples")
ap.add_argument("--frames", default="", help="comma-separated Blender frames to render as stills")
ap.add_argument("--save", action="store_true", help="save the built scene as out/blend/<shot>.blend")
args = ap.parse_args(argv)

with open(os.path.join(HERE, "timeline.json")) as fh:
    timeline = json.load(fh)


class Shot:
    """What a shot script receives: duration in frames and cue lookups in Blender frames."""

    def __init__(self, data):
        self.duration = data["duration"]
        self.lead_in = data["leadIn"]
        self.vo_end = data["voEnd"] + 1
        self._cues = data["cues"]

    def cue(self, name, offset=0):
        return self._cues[name] + 1 + offset

    @property
    def end(self):
        return self.duration


bpy.ops.wm.read_factory_settings(use_empty=True)
from lib import anchors, look  # noqa: E402  (after factory reset)

shot = Shot(timeline["scenes"][args.shot])
module = importlib.import_module(f"shots.{args.shot}")
t0 = time.time()
module.build(shot)
look.render_settings(shot.duration, preview=args.preview)
print(f"[render] built {args.shot} in {time.time() - t0:.1f}s, {len(bpy.data.objects)} objects")

if not args.frames:
    os.makedirs(os.path.join(ROOT, "public/renders", args.shot), exist_ok=True)
    anchors.export(os.path.join(ROOT, "public/renders", args.shot, "anchors.json"), shot.duration)

if args.save:
    os.makedirs(os.path.join(ROOT, "out/blend"), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, f"out/blend/{args.shot}.blend"))

scene = bpy.context.scene
if args.frames:
    out_dir = os.path.join(ROOT, "out/previews", args.shot)
    os.makedirs(out_dir, exist_ok=True)
    for f in [int(x) for x in args.frames.split(",") if x]:
        t1 = time.time()
        scene.frame_set(f)
        scene.render.filepath = os.path.join(out_dir, f"{f:04d}.jpg")
        bpy.ops.render.render(write_still=True)
        print(f"[render] frame {f} in {time.time() - t1:.1f}s")
else:
    out_dir = os.path.join(ROOT, "public/renders", args.shot)
    os.makedirs(out_dir, exist_ok=True)
    scene.render.filepath = os.path.join(out_dir, "")
    t1 = time.time()
    bpy.ops.render.render(animation=True)
    print(f"[render] {shot.duration} frames in {time.time() - t1:.0f}s")
