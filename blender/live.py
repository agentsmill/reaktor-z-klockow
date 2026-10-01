"""Send Python to the *running* Blender through the Blender Lab MCP add-on (localhost:9876).

Same wire protocol the official `blender-mcp` server uses (JSON request + NUL byte), so the
scene appears live in the user's Blender window. Code sets `result = {...}` to return data.

  python3 blender/live.py ping
  python3 blender/live.py shot intro        # build a shot's scene in the open Blender
  python3 blender/live.py -c "import bpy; result = {'n': len(bpy.data.objects)}"
"""
import json
import os
import socket
import sys

HOST = os.environ.get("BLENDER_MCP_HOST", "localhost")
PORT = int(os.environ.get("BLENDER_MCP_PORT", "9876"))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def send(code: str, timeout: float = 600.0) -> dict:
    request = json.dumps({"type": "execute", "code": code, "strict_json": True}) + "\0"
    with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
        sock.sendall(request.encode("utf-8"))
        buf = bytearray()
        while b"\0" not in buf:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf.extend(chunk)
    return json.loads(buf.split(b"\0", 1)[0].decode("utf-8"))


def build_shot_code(shot: str, play: bool = True) -> str:
    """Code that builds one shot in a NEW scene of the running Blender (never touches the user's
    scenes), points the 3D views at its camera in Rendered mode and starts playback."""
    return f"""
import importlib, json, sys, bpy
sys.path.insert(0, {os.path.join(ROOT, "blender")!r})
for name in [m for m in list(sys.modules) if m == "lib" or m.startswith(("lib.", "shots."))]:
    del sys.modules[name]
win = bpy.context.window_manager.windows[0]
old = bpy.data.scenes.get("SMR {shot}")
if old is not None:
    bpy.data.scenes.remove(old)
scene = bpy.data.scenes.new("SMR {shot}")
win.scene = scene
from lib import look
data = json.load(open({os.path.join(ROOT, "blender", "timeline.json")!r}))["scenes"][{shot!r}]
class Shot:
    duration = data["duration"]; lead_in = data["leadIn"]; vo_end = data["voEnd"] + 1
    def cue(self, name, offset=0): return data["cues"][name] + 1 + offset
    @property
    def end(self): return self.duration
with bpy.context.temp_override(window=win, scene=scene):
    importlib.import_module("shots.{shot}").build(Shot())
    look.render_settings(Shot.duration, preview=True)
scene.frame_set(1)
views = 0
for area in win.screen.areas:
    if area.type == "VIEW_3D":
        space = area.spaces.active
        space.shading.type = "RENDERED"
        space.region_3d.view_perspective = "CAMERA"
        views += 1
if {play!r}:
    for area in win.screen.areas:
        if area.type == "VIEW_3D":
            with bpy.context.temp_override(window=win, area=area):
                bpy.ops.screen.animation_play()
            break
result = {{"scene": scene.name, "objects": len(scene.objects), "frames": Shot.duration, "views": views}}
"""


if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        if not args or args[0] == "ping":
            reply = send("import bpy; result = {'blender': bpy.app.version_string, 'file': bpy.data.filepath or '(unsaved)'}")
        elif args[0] == "shot":
            reply = send(build_shot_code(args[1], play="--no-play" not in args))
        elif args[0] == "-c":
            reply = send(args[1])
        elif args[0] == "-f":
            reply = send(open(args[1]).read())
        else:
            raise SystemExit(__doc__)
    except ConnectionError as ex:
        raise SystemExit(f"Blender not reachable on {HOST}:{PORT} — is the MCP add-on server started? ({ex})")
    except OSError as ex:
        raise SystemExit(f"Blender not reachable on {HOST}:{PORT} — is the MCP add-on server started? ({ex})")
    print(json.dumps(reply, indent=1, ensure_ascii=False)[:4000])
