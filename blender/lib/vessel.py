"""BWRX-300 reactor pressure vessel as a brick cutaway (front half removed, orange cut edges).

Stylised proportions (real vessel ~1:6.5) — the shots carry a "Schemat uproszczony" tag.
Usage:
    v = vessel.Vessel(cx, cy)
    v.rods(start, end, inserted=True)   # control rods slide up from below
    v.bubbles(start, end)               # steam/water mixture rising in the chimney
    v.downflow(start, end)              # cooler water sinking along the sides
    v.glow(frame, strength)             # core glow (fuel emission + orange light)
    v.points["core"] etc.               # world positions for labels / camera targets
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix

from . import anim as A
from . import bricks as B
from . import build as S
from . import look as L

R = 5.0  # vessel radius (studs)
CHIMNEY_R = 3.0
LEVELS = 22  # body height in bricks (above the bottom head)
CORE = (3, 8)  # core spans these brick levels
WATER_LEVEL = 17
FUEL_X = (-3.0, -1.5, 0.0, 1.5, 3.0)
ROD_X = (-2.25, -0.75, 0.75, 2.25)


class Vessel:
    def __init__(self, cx=0.0, cy=0.0, z0=0.0, coll=None, seed=5):
        self.cx, self.cy, self.z0 = cx, cy, z0
        self.coll = coll
        self.rnd = random.Random(seed)
        self.steel = L.plastic("#5D6675", rough=0.35)
        self.cut = L.plastic(L.COL["orange"])
        self.light = L.plastic(L.COL["lightgrey"])
        self.dark = L.plastic(L.COL["darkgrey"])
        self.fuel = L.glow(L.COL["uranium"], 0.6, name="fuel_glow", base=L.COL["trans_green"])
        self.bubble_mat = L.plastic(L.COL["white"], rough=0.2)
        self.water_mat = L.trans(L.COL["trans_blue"])
        self.objects = {"shell": [], "chimney": [], "fuel": [], "rods": [], "internals": []}
        self._build()

    # --- geometry -------------------------------------------------------
    def z(self, level):
        return self.z0 + level * B.BRICK

    def _shell_ring(self, level, radius, mat_fn):
        return S.ring(self.cx, self.cy, self.z0, 1, radius, mat_fn, start_level=level, coll=self.coll, arc=(0.0, 0.5))

    def _build(self):
        cx, cy = self.cx, self.cy
        n = max(6, int(round(2 * math.pi * R)))  # same count as build.ring
        last = (n + 1) // 2 - 1  # last brick of the half ring (arc 0–0.5)
        edge = lambda level, k: self.cut if k in (0, last) else self.steel  # noqa: E731
        # bottom head, body, top head (back half only)
        for level, radius in ((0, 3.4), (1, 4.4)):
            self.objects["shell"] += self._shell_ring(level, radius, lambda *_: self.steel)
        for level in range(2, LEVELS):
            self.objects["shell"] += self._shell_ring(level, R, edge)
        for level, radius in ((LEVELS, 4.4), (LEVELS + 1, 3.4), (LEVELS + 2, 2.0)):
            self.objects["shell"] += self._shell_ring(level, radius, lambda *_: self.steel)
        # chimney (inner half-shell, light grey)
        for level in range(CORE[1] + 1, WATER_LEVEL - 1):
            self.objects["chimney"] += S.ring(cx, cy, self.z0, 1, CHIMNEY_R, lambda *_: self.light, start_level=level,
                                              coll=self.coll, arc=(0.0, 0.5))
        # core: two rows of trans-green fuel columns
        for x in FUEL_X:
            for dy in (0.0, 1.6):
                for level in range(*CORE):
                    self.objects["fuel"].append(B.add(B.part(1, 1, 3, "round"), self.fuel, (cx + x, cy + dy, self.z(level)), coll=self.coll))
        # core support plate + steam separators + dryer
        for x in range(-4, 5):
            self.objects["internals"].append(B.add(B.part(1, 2, 1), self.dark, (cx + x, cy + 0.8, self.z(CORE[0]) - B.PLATE), coll=self.coll))
        for x in (-2, -1, 0, 1, 2):
            for level in (WATER_LEVEL - 1, WATER_LEVEL):
                self.objects["internals"].append(B.add(B.part(1, 1, 3, "round"), self.light, (cx + x, cy + 0.8, self.z(level)), coll=self.coll))
        for x in range(-3, 4):
            self.objects["internals"].append(B.add(B.part(1, 2, 1, "tile"), self.dark, (cx + x, cy + 0.8, self.z(WATER_LEVEL + 2)), coll=self.coll))
        # control rods (start below the core) + drive housings under the vessel
        self.rod_cols = []
        for x in ROD_X:
            col = [B.add(B.part(1, 1, 3), self.dark, (cx + x, cy + 0.8, self.z(level - (CORE[1] - CORE[0]))), coll=self.coll)
                   for level in range(*CORE)]
            self.rod_cols.append(col)
            self.objects["rods"] += col
            for level in (-3, -2, -1):
                self.objects["internals"].append(B.add(B.part(1, 1, 3, "round"), self.steel, (cx + x, cy + 0.8, self.z(level)), coll=self.coll))
        # nozzles: steam out (top) and feedwater in, pointing right (+x)
        self.steam_nozzle = self._nozzle(LEVELS - 2)
        self.feed_nozzle = self._nozzle(WATER_LEVEL - 3)
        # water volume (smooth, translucent) up to the water level
        self.water = self._water_volume()
        # orange light inside the core for the glow
        light = bpy.data.lights.new("core_light", "POINT")
        light.color = L.srgb(L.COL["heat"])[:3]
        light.energy = 0
        light.shadow_soft_size = 2.0
        light.use_shadow = False  # a shadow-casting light inside the transparent water costs 3–4× render time
        self.core_light = bpy.data.objects.new("core_light", light)
        (self.coll or bpy.context.scene.collection).objects.link(self.core_light)
        self.core_light.location = (cx, cy + 0.5, self.z((CORE[0] + CORE[1]) / 2))

        zc = lambda level: self.z(level)  # noqa: E731
        self.points = {
            "core": (cx, cy, zc((CORE[0] + CORE[1]) / 2)),
            "chimney": (cx, cy, zc((CORE[1] + WATER_LEVEL) / 2)),
            "downcomer_l": (cx - R + 1, cy, zc(12)),
            "downcomer_r": (cx + R - 1, cy, zc(12)),
            "dome": (cx, cy, zc(LEVELS + 1)),
            "steam_out": (cx + R + 3, cy, zc(LEVELS - 2) + B.BRICK / 2),
            "feed_in": (cx + R + 3, cy, zc(WATER_LEVEL - 3) + B.BRICK / 2),
            "rods": (cx, cy, zc(1)),
            "top": (cx, cy, zc(LEVELS + 3)),
            "bottom": (cx, cy, zc(-3)),
        }

    def _nozzle(self, level):
        obs = []
        for k in range(4):
            ob = B.add(B.part(1, 1, 3, "round", studs=False), self.steel, (self.cx + R - 0.5 + k, self.cy, self.z(level) + B.BRICK / 2), coll=self.coll)
            ob.rotation_euler = (0, math.radians(90), 0)
            obs.append(ob)
        return obs

    def _water_volume(self):
        bm = bmesh.new()
        height = self.z(WATER_LEVEL) - self.z(1)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=R - 0.55, radius2=R - 0.55, depth=height,
                              matrix=Matrix.Translation((0, 0, height / 2)))
        # keep only the back half (y >= 0) so the cutaway stays open
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, -0.2, 0), plane_no=(0, 1, 0), clear_inner=True)
        me = bpy.data.meshes.new("water_volume")
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("water_volume", me)
        (self.coll or bpy.context.scene.collection).objects.link(ob)
        ob.location = (self.cx, self.cy, self.z(1))
        ob.data.materials.append(self.water_mat)
        return ob

    # --- animation ------------------------------------------------------
    def rods(self, start, end, inserted=True):
        """Slide the control rod columns up into the core (or back down)."""
        lift = (CORE[1] - CORE[0]) * B.BRICK
        for col in self.rod_cols:
            for ob in col:
                x, y, z = ob.location
                lo, hi = (z, z + lift) if inserted else (z + lift, z)
                A.bake(ob, start, end, lambda t, x=x, y=y, lo=lo, hi=hi: (x, y, lo + (hi - lo) * A.ease_in_out_cubic(t)))

    def bubbles(self, start, end, columns=(-1.6, -0.5, 0.6, 1.7), per_column=7, period=60):
        """White round plates rising from the core top to the separators (two-phase flow)."""
        z_lo, z_hi = self.z(CORE[1]), self.z(WATER_LEVEL - 1)
        for c in columns:
            obs = [B.add(B.part(1, 1, 1, "round"), self.bubble_mat, (self.cx + c, self.cy + 0.3, z_lo), coll=self.coll)
                   for _ in range(per_column)]
            wob = self.rnd.uniform(0, 6)
            A.stream(obs, start, end, lambda u, c=c, wob=wob: (
                self.cx + c + 0.25 * math.sin(u * 9 + wob), self.cy + 0.3, z_lo + (z_hi - z_lo) * u), period + self.rnd.randint(-8, 8))

    def downflow(self, start, end, per_side=8, period=90):
        """Trans-blue round plates sinking down the gap between chimney and wall, both sides."""
        z_hi, z_lo = self.z(WATER_LEVEL - 2), self.z(CORE[0])
        for side in (-1, 1):
            x = self.cx + side * (CHIMNEY_R + 1.0)
            obs = [B.add(B.part(1, 1, 1, "round"), self.water_mat, (x, self.cy + 0.3, z_hi), coll=self.coll) for _ in range(per_side)]
            A.stream(obs, start, end, lambda u, x=x: (x, self.cy + 0.3, z_hi + (z_lo - z_hi) * u), period)

    def glow(self, frame, strength):
        """Keyframe core glow: fuel emission and the orange core light."""
        L.key_emission(self.fuel, frame, 0.6 + strength * 3.0)
        self.core_light.data.energy = strength * 4000
        self.core_light.data.keyframe_insert("energy", frame=frame)
