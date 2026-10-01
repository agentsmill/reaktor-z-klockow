"""Fission: a uranium pellet on a dark table → the camera dives into its green glow → a field of
uranium-235 nuclei (235 bricks each) → a cyan neutron is captured by one → it wobbles and splits
unequally (Ba-141 + Kr-92, the light one flies farther) → orange heat flash lights the scene →
3 prompt neutrons leave the fragments → chain reaction spreads across the field like a wave →
back out of the pellet → 1 pellet vs a heap of coal.

Two "worlds" share the scene: OUTER (table, pellet, coal) around the origin and INNER (nuclei) far
away at INNER. The camera passes between them through a bright green glow (pellet glow + world haze).
"""
import math
import random

from mathutils import Quaternion, Vector

from lib import anchors
from lib import anim as A
from lib import bricks as B
from lib import fission_kit as K
from lib import look as L

INNER = Vector((0.0, 1000.0, 0.0))
SPACING = 26.0
HAZE = "#C9FFB8"
HAZE_DEEP = "#123F1C"
NAVY = "#1A2C4A"
SPACE = "#0F1D33"


def build(shot):
    c = shot.cue
    end = shot.end
    T = {
        "drop": 6,
        "glow": c("pellet"),                # pellets light up on "pastylki"
        "dive0": c("pellet") + 6,           # 50: camera starts diving into the pellet
        "cross_in": c("neutron") - 21,      # 72: through the glow into the nucleus world
        "zoomed": c("neutron") - 3,         # 90: close-up reached
        "n_in": c("neutron") - 9,           # 84: neutron enters from the left (in frame by the cue)
        "hit": c("hit") + 4,                # 112: captured
        "split": c("split"),                # 169
        "heat": c("heat"),                  # 298
        "charge": c("newNeutrons") - 2,     # 342: 3 bricks light up cyan
        "emit": c("newNeutrons") + 3,       # 347: prompt neutrons leave the fragments
        "arrive": c("chain") - 3,           # ~402: they reach the next nuclei on "kolejne"
        "pull0": c("newNeutrons") + 2,      # 346: start pulling back
        "field": c("chainLabel") - 16,      # 446: wide view of the chain reaction
        "out0": c("onePellet") - 16,        # 477: pull out of the pellet
        "cross_out": c("onePellet") - 5,    # 488
        "cmp": c("onePellet") + 34,         # 527: comparison framing reached
        "coal": c("coal") - 12,             # 546: coal starts raining in
    }
    hit, split = T["hit"], T["split"]
    inner_win = (T["cross_in"], T["cross_out"])
    L.world()
    rnd = random.Random(42)
    vis = {}  # object → visibility intervals (applied once at the end)

    # ================================================================ OUTER world: table + pellets
    outer = []
    table = L.plastic("#202428", rough=0.55)
    plate, studs = B.baseplate(64, 44, table, loc=(-23.5, -19.5, 0))
    outer += [plate, studs]
    pellet_mat = K.ceramic_pellet_mat()
    pellet = B.add(B.part(2, 2, 3, "round"), pellet_mat, (0, 0, 0), name="pellet")
    A.drop_in(pellet, T["drop"] + 8, dur=12, height=9)
    bg_mat = K.ceramic_pellet_mat("pellet_bg")
    for k, (x, y, lv) in enumerate(((3, 6, 0), (6, 3, 0), (6, 3, 1), (-3, 7, 0), (-7, 12, 0), (9, 10, 0), (1, 14, 0),
                                    (12, 5, 0), (12, 5, 1), (12, 5, 2), (-11, 6, 0))):
        ob = B.add(B.part(2, 2, 3, "round"), bg_mat, (x, y, lv * B.BRICK), name="pellet_bg")
        A.drop_in(ob, 1 + k * 2 + lv * 3, dur=12, height=8)
        A.hide_from(ob, T["cross_in"])
    for mat, rim in ((pellet_mat, 3.2), (bg_mat, 1.6)):
        K.key_pellet(mat, 1, rim=rim * 0.35, body=0.0)
        K.key_pellet(mat, T["glow"] - 6, rim=rim * 0.35)
        K.key_pellet(mat, T["glow"] + 10, rim=rim)
    K.key_pellet(pellet_mat, T["dive0"] + 4, body=0.0)
    K.key_pellet(pellet_mat, T["cross_in"], body=9.0)
    K.key_pellet(pellet_mat, T["cross_out"], body=9.0)
    K.key_pellet(pellet_mat, T["cross_out"] + 14, body=0.0)
    K.key_pellet(pellet_mat, T["cross_out"] + 15, rim=2.4)
    K.key_pellet(pellet_mat, c("onePellet") + 4, rim=3.6)
    K.key_pellet(pellet_mat, c("onePellet") + 30, rim=2.6)
    glow = K.point_light("pellet_glow", (0, 0, 0.7), L.COL["uranium"], 0.0, radius=1.0)
    for f, e in ((1, 60), (T["glow"] - 6, 60), (T["glow"] + 10, 170), (T["cross_in"], 250), (T["cross_out"], 250),
                 (T["cross_out"] + 16, 60), (c("onePellet") + 4, 120), (c("onePellet") + 30, 80)):
        K.key_energy(glow, f, e)
    outer.append(glow)

    # coal heap (rains in on "tona")
    coal_mats = [L.plastic("#15171A", rough=0.22), L.plastic("#202326", rough=0.25), L.plastic("#2B2F33", rough=0.3),
                 L.plastic(L.COL["black"], rough=0.22)]
    heap_c = (15.5, 4.0, 0.0)
    coal = K.coal_heap(heap_c, 8.2, 6.8, coal_mats, seed=9)
    coal.sort(key=lambda o: (o.location.z, rnd.random()))
    for k, ob in enumerate(coal):
        A.drop_in(ob, T["coal"] + int(k / len(coal) * 34) + rnd.randint(0, 3), dur=11, height=16)
    heap_top = max(o.location.z for o in coal) + 1.2
    outer += list(L.studio(center=(8, 4, 1), scale=0.6))

    # ================================================================ INNER world: the hero nucleus
    inner = []
    hero_mats = K.nucleus_set("hero")
    offs = K.nucleus_offsets()
    big_idx, small_idx = K.split_partition(offs, (1, 0, 0), seed=3)
    small_set = set(small_idx)
    c_big = K.centroid([offs[i] for i in big_idx])
    c_small = K.centroid([offs[i] for i in small_idx])
    root = K.empty("hero_root", INNER)
    half = {"big": K.empty("hero_big", c_big, parent=root), "small": K.empty("hero_small", c_small, parent=root)}
    for h in half.values():
        h.rotation_mode = "QUATERNION"
    cen = {"big": c_big, "small": c_small}
    x_split = (max(offs[i].x for i in big_idx) + min(offs[i].x for i in small_idx)) / 2
    # after the split each half re-forms into a compact ball: two smaller nuclei
    ball = {}
    for which, idx in (("big", big_idx), ("small", small_idx)):
        ball.update(dict(zip(idx, K.assign_ball([offs[i] - cen[which] for i in idx]))))
    r_ball = {"big": max(q.length for q in K.nucleus_offsets(K.BIG)) + 0.6, "small": max(q.length for q in K.nucleus_offsets(K.SMALL)) + 0.6}

    def deform(p, f, i):
        """Root-space position of brick i: idle jiggle → jolt → growing wobble → peanut."""
        t = K.ramp(f, hit, split)
        e = 0.42 * t ** 1.6
        osc = 0.075 * (0.35 + t) * math.sin((f - hit) * math.tau / 7.0) if f >= hit else 0.0
        sx = 1 + e + osc
        syz = 1 / math.sqrt(sx)
        neck = 0.34 * t ** 2 * math.exp(-((p.x - x_split) / 2.3) ** 2)
        q = Vector((p.x * sx, p.y * syz * (1 - neck), p.z * syz * (1 - neck)))
        if f >= hit:
            jt = f - hit
            q.x += 0.75 * (jt / 2.5) * math.exp(1 - jt / 2.5)  # kick from the captured neutron
        amp = 0.03 + 0.17 * t ** 2
        ph = f // 2
        q += Vector((K.hash01(i, ph, 1) - 0.5, K.hash01(i, ph, 2) - 0.5, K.hash01(i, ph, 3) - 0.5)) * 2 * amp
        return q

    reform = (split + 4, split + 40)

    def local(i, f):
        """Brick i relative to its half's empty."""
        which = "small" if i in small_set else "big"
        p = offs[i]
        if f < split:
            return deform(p, f, i) - cen[which]
        relaxed = deform(p, split, i).lerp(p, K.ease_out_cubic((f - split) / 10)) - cen[which]
        return relaxed.lerp(ball[i], K.ease_in_out(K.ramp(f, *reform)))

    # fragments: momentum conservation → the light Kr-92 flies 1.55× farther than Ba-141
    dirs = {"small": Vector((1.0, -0.06, -0.12)).normalized(), "big": Vector((-1.0, 0.06, 0.12)).normalized()}
    reach = {"small": 10.0, "big": 10.0 * K.SMALL / K.BIG}
    drift = {"small": 0.010, "big": 0.0065}
    spin_axis = {"small": Vector((0.35, 1.0, 0.55)).normalized(), "big": Vector((-0.2, 0.7, -1.0)).normalized()}
    spin = {"small": (1.3, 0.0050), "big": (0.85, 0.0032)}

    def half_loc(which, f):
        if f <= split:
            return Vector(cen[which])
        k = f - split
        return Vector(cen[which]) + dirs[which] * (reach[which] * K.ease_out_expo(min(1.0, k / 36)) + drift[which] * max(0, k - 36))

    def half_rot(which, f):
        if f <= split:
            return Quaternion()
        k = f - split
        a, v = spin[which]
        return Quaternion(spin_axis[which], a * K.ease_out_expo(min(1.0, k / 40)) + v * max(0, k - 40))

    for which in ("big", "small"):
        K.bake(half[which], split - 1, T["cross_out"], lambda f, w=which: half_loc(w, f))
        K.bake(half[which], split - 1, T["cross_out"], lambda f, w=which: half_rot(w, f), "rotation_quaternion")

    bricks = []
    for i, p in enumerate(offs):
        which = "small" if i in small_set else "big"
        ob = K.add(K.centered(1, 1, 3, "round"), hero_mats[K.pick_material(i, 3)], local(i, T["cross_in"]),
                   name=f"u235_{which}", parent=half[which])
        for f in range(T["cross_in"], reform[1] + 1):
            K.key(ob, "location", f, local(i, f))
        bricks.append({"ob": ob, "i": i, "which": which})
        vis[ob] = [inner_win]

    def brick_world(i, f):
        which = "small" if i in small_set else "big"
        return INNER + half_loc(which, f) + half_rot(which, f) @ local(i, f)

    def frag_center(which, f):
        return INNER + half_loc(which, f)

    # ================================================================ the field of nuclei
    field_mats = K.nucleus_set("field")
    frag_mats = (K.trans_new("#79A85A", alpha=0.5, emit=0.12, name="frag_trans"),
                 K.plastic_new("#3E5F30", rough=0.3, name="frag_solid"),
                 K.glow_obj("#FF6A1E", 5.0, base="#4A6B35", name="frag_hot"))
    field = K.FieldNuclei(field_mats, frag_mats, variants=3, seed=21)
    pts = K.hex_lattice(SPACING, -142, 142, -80, 80)
    root_idx = min(range(len(pts)), key=lambda i: pts[i][0] ** 2 + pts[i][1] ** 2)
    depth = [0.0 if i == root_idx else rnd.uniform(-5.0, 5.0) for i in range(len(pts))]

    def lattice_pos(i):
        return INNER + Vector((pts[i][0], depth[i], pts[i][1]))

    nuclei = {}
    for i in range(len(pts)):
        if i == root_idx:
            continue
        nuc = field.place(lattice_pos(i), rnd.randrange(3), rot_z=rnd.uniform(0, math.tau), name=f"nuc{i}")
        K.key(nuc["ob"], "rotation_euler", T["cross_in"], (0, 0, nuc["ob"].rotation_euler.z))
        K.key(nuc["ob"], "rotation_euler", T["cross_out"], (0, 0, nuc["ob"].rotation_euler.z + rnd.uniform(-0.6, 0.6)))
        nuclei[i] = nuc
    # a dim second layer far behind: depth, and soft bokeh behind the close-up
    for k, (x, z) in enumerate(K.hex_lattice(34.0, -190, 190, -110, 110)):
        far = field.place(INNER + Vector((x + 17, 75 + rnd.uniform(-8, 8), z + 9)), k, rot_z=rnd.uniform(0, 6.3), name="far")
        K.key_alpha(far["ob"], 1, 0.45)
        # only needed as bokeh behind the close-up: shrink away while the camera pulls back
        f_out = T["pull0"] + 6 + rnd.randint(0, 14)
        K.key(far["ob"], "scale", f_out, (1, 1, 1))
        K.key(far["ob"], "scale", f_out + 14, (0.02, 0.02, 0.02))
        vis[far["ob"]] = [(T["cross_in"], f_out + 15)]
        vis[far["ba"]] = []
        vis[far["kr"]] = []

    # ================================================================ neutrons, flashes
    n_mat = K.glow_obj(L.COL["neutron"], 14.0, base="#BDF4FF", name="neutron")
    tail_mat = K.streak_mat(L.COL["neutron"], 7.0, name="neutron_tail")
    spark_mat = K.glow_obj(L.COL["neutron"], 9.0, base="#BDF4FF", name="spark")
    flash_mat = K.bubble_mat("#FF9440", 7.0, name="flash_shell", power=3.2)
    core_mat = K.bubble_mat("#FFE2B0", 18.0, name="flash_core")

    def sparkle(path, f0, f1, every=1, life=11, size=0.7, seed=0):
        """Breadcrumb light trail: tiny glowing round plates left behind, shrinking and fading."""
        r = random.Random(seed)
        for fs in range(f0, f1 + 1, every):
            ob = K.add(K.centered(1, 1, 1, "round"), spark_mat, path(fs), name="spark")
            ob.visible_shadow = False
            jitter = Vector((r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3)))
            ob.rotation_euler = (r.uniform(0, 3), r.uniform(0, 3), r.uniform(0, 3))
            for k in range(life + 1):
                t = k / life
                K.key(ob, "location", fs + k, path(fs) + jitter * t)
                K.key(ob, "scale", fs + k, (size * (1 - t) ** 0.8,) * 3)
                K.key_alpha(ob, fs + k, (1 - t) ** 1.5)
            vis[ob] = [(fs, fs + life)]

    # 1) the incoming neutron (from the left), captured at `hit`
    n_start = INNER + Vector((-20.5, -4.0, -1.9))
    n_end = INNER + Vector((-4.3, -0.3, 0.3))
    hero_n = K.Neutron("neutron", n_mat, tail_mat, light=650.0, streak=7.0)
    hero_n.fly(T["n_in"], hit, n_start, n_end)
    hero_n.finish(inner_win)
    sparkle(lambda f: n_start.lerp(n_end, K.ramp(f, T["n_in"], hit)), T["n_in"], hit - 1, seed=1)
    heart = K.point_light("heart", INNER, L.COL["neutron"], 0.0, radius=1.5)
    K.key_energy(heart, hit - 1, 0.0)
    K.bake_energy(heart, hit, split, lambda f: 900 * math.exp(-(f - hit) / 6) + 260 * (0.6 + 0.4 * math.sin((f - hit) * 0.9)) * K.ramp(f, hit, hit + 8))
    K.key_energy(heart, split + 3, 0.0)

    # 2) split pop, 3) heat flash: light, shell, warm haze, fragments glowing hot then cooling
    pop = K.Flash("split_pop", None, core_mat, light_color="#DFFFD0")
    pop.fire(split, INNER + Vector((x_split, 0, 0)), size=15.0, dur=14, energy=14000.0, decay=4.0, core_size=4.5, core_dur=5)
    pop.finish(inner_win)
    heat_c = (frag_center("big", T["heat"]) + frag_center("small", T["heat"])) / 2
    heat = K.Flash("heat", flash_mat, core_mat, light_color=L.COL["heat"], shadow=True)
    heat.fire(T["heat"], heat_c, size=38.0, dur=30, energy=70000.0, decay=20.0, core_size=5.5, core_dur=5)
    heat.finish(inner_win)
    h0 = T["heat"]
    cool = c("chain") + 10
    for m, base_e in ((hero_mats[2], 1.1), (hero_mats[3], 2.2)):
        K.key_emission_color(m, h0 - 1, "#7FD846" if m is hero_mats[2] else "#C6FF86")
        K.key_emission_color(m, h0 + 3, "#FF5E12")
        K.key_emission_color(m, cool, "#FF5410")
        K.set_glow_strength(m, h0 - 1, base_e)
        K.set_glow_strength(m, h0 + 3, base_e * 1.6)
        K.set_glow_strength(m, h0 + 40, base_e * 1.1)
        K.set_glow_strength(m, cool, 0.35)
    K.key_bsdf(hero_mats[0], h0 - 1, emission_color="#3FC75C", emission_strength=0.3, base_color="#3FC75C")
    K.key_bsdf(hero_mats[0], h0 + 3, emission_color="#FF5E12", emission_strength=0.9)
    K.key_bsdf(hero_mats[0], cool, emission_color="#7A8F40", emission_strength=0.15, base_color="#79A85A")
    K.key_bsdf(hero_mats[1], h0 - 1, base_color="#24823A")
    K.key_bsdf(hero_mats[1], cool, base_color="#3E5F30")
    K.key_world(h0 - 1, SPACE, 0.35)
    K.key_world(h0 + 2, "#4A1D08", 0.8)
    K.key_world(h0 + 45, SPACE, 0.35)

    # 4) three prompt neutrons: two leave Ba-141, one (the captured neutron) leaves Kr-92
    def nearest(x, z):
        return min(nuclei, key=lambda i: (pts[i][0] - x) ** 2 + (pts[i][1] - z) ** 2)

    first_targets = [nearest(-SPACING * 0.5, SPACING * 0.866), nearest(-SPACING, 0.0), nearest(SPACING * 0.5, -SPACING * 0.866)]
    emit = T["emit"]
    first_times = []
    hidden_bricks = set()
    for k, (tgt, src) in enumerate(zip(first_targets, ("big", "big", "small"))):
        tpos = lattice_pos(tgt)
        fc = frag_center(src, emit)
        dirn = (tpos - fc).normalized()
        if src == "big":
            cand = [b for b in bricks if b["which"] == "big" and b["i"] not in hidden_bricks]
            b = max(cand, key=lambda b: (brick_world(b["i"], emit) - fc).dot(dirn))
            hidden_bricks.add(b["i"])
            at = lambda f, i=b["i"]: brick_world(i, f)  # noqa: E731
        else:
            at = lambda f, src=src, dirn=dirn: frag_center(src, f) + dirn * (r_ball["small"] + 0.2)  # noqa: E731
        p0 = at(emit)
        arrive = T["arrive"] + (0, 2, 4)[k]
        p1 = tpos - (tpos - p0).normalized() * (field.radius["u"] + 0.2)
        first_times.append(arrive + 3)
        nn = K.Neutron(f"prompt{k}", n_mat, tail_mat, light=380.0, streak=6.0)
        for f in range(T["charge"], emit):  # the brick lights up cyan in place before it leaves
            K.key(nn.ob, "location", f, at(f))
        nn.intervals.append((T["charge"], emit))
        nn.fly(emit, arrive, p0, p1, ease=lambda t: 1 - (1 - t) ** 1.8)
        nn.finish(inner_win)
        sparkle(lambda f, p0=p0, p1=p1, a=arrive: p0.lerp(p1, 1 - (1 - K.ramp(f, emit, a)) ** 1.8), emit, arrive - 1, seed=10 + k)
    for b in bricks:
        if b["i"] in hidden_bricks:
            vis[b["ob"]] = [(T["cross_in"], T["charge"])]

    # 5) the chain reaction over the field
    nodes = K.build_cascade(pts, root_idx, first_targets, [2, 2, 2, 2], T["emit"] + 30, 20, first_times=first_times)
    gens = {}
    for n in nodes:
        gens.setdefault(n["gen"], []).append(n["split"])
    print("[fission] cascade:", {g: (len(v), min(v), max(v)) for g, v in sorted(gens.items())})
    for n_i, node in enumerate(nodes):
        if node["parent"] is None:
            continue
        idx, f = node["idx"], node["split"]
        if f >= T["cross_out"]:
            continue
        nuc = nuclei[idx]
        src = lattice_pos(idx)
        fl = K.Flash(f"flash{n_i}", flash_mat, core_mat, light_color=L.COL["heat"])
        fl.fire(f, src, size=12.0, dur=16, energy=16000.0, decay=8.0, core_size=5.0, core_dur=5)
        fl.finish(inner_win)
        a = rnd.uniform(0, math.pi)
        K.split_field_nucleus(nuc, f, (math.cos(a), rnd.uniform(-0.2, 0.2), math.sin(a)), push=6.5, seed=n_i)
        kids = [m for m in nodes if m["parent"] == n_i]
        for kk, kid in enumerate(kids):
            dst = lattice_pos(kid["idx"])
            d = (dst - src).normalized()
            nn = K.Neutron(f"n{n_i}_{kk}", n_mat, tail_mat, streak=5.0)
            nn.fly(f + 1, min(kid["split"] - 3, T["cross_out"] + 2), src + d * 2.5, dst - d * (field.radius["u"] + 0.2))
            nn.finish(inner_win)
        if kids and len(kids) < 3 and rnd.random() < 0.5:  # a third neutron escapes through a lattice gap
            par = lattice_pos(nodes[node["parent"]]["idx"])
            base = math.atan2((src - par).z, (src - par).x)
            ang = base + rnd.choice([-1, 1]) * math.radians(30)
            d = Vector((math.cos(ang), rnd.uniform(-0.25, 0.25), math.sin(ang))).normalized()
            nn = K.Neutron(f"stray{n_i}", n_mat, tail_mat, streak=5.0)
            nn.fly(f + 1, f + 31, src + d * 2.5, src + d * 26.0, fade_out=True)
            nn.finish(inner_win)
    for nuc in nuclei.values():
        v = nuc.get("vis", {"ob": [(0, None)], "ba": [], "kr": []})
        for key_ in ("ob", "ba", "kr"):
            vis[nuc[key_]] = K.clip_intervals(v[key_], inner_win)

    inner_lights = list(L.studio(center=tuple(INNER), scale=2.4))
    inner_lights[0].data.energy *= 1.4
    inner += inner_lights + [heart]

    # ================================================================ visibility of the two worlds
    for ob in inner:
        vis.setdefault(ob, [inner_win])
    for ob in outer:
        vis.setdefault(ob, [(0, T["cross_in"]), (T["cross_out"], end + 1)])
    for ob, iv in vis.items():
        K.visible_during(ob, iv)
    K.key(pellet, "hide_render", T["cross_in"], True)
    K.key(pellet, "hide_render", T["cross_out"], False)

    # green haze at both crossings (inner "space" is a touch darker than the studio)
    K.key_world(1, NAVY, 0.55)
    K.key_world(T["cross_in"] - 8, NAVY, 0.55)
    K.key_world(T["cross_in"], HAZE, 1.6)
    K.key_world(T["cross_in"] + 1, HAZE, 1.3)
    K.key_world(T["cross_in"] + 4, HAZE_DEEP, 0.9)
    K.key_world(T["cross_in"] + 10, SPACE, 0.35)
    K.key_world(T["cross_out"] - 8, SPACE, 0.35)
    K.key_world(T["cross_out"] - 4, HAZE_DEEP, 0.9)
    K.key_world(T["cross_out"] - 1, HAZE, 1.6)
    K.key_world(T["cross_out"] + 1, HAZE, 1.3)
    K.key_world(T["cross_out"] + 14, NAVY, 0.55)

    # ================================================================ camera
    cam, target = L.camera((0, -30, 10), (0, 0, 0.6), lens=85, fstop=K.fstop(4.5))
    pc = Vector((0, 0, 0.6))
    ptop = Vector((0, 0, 1.3))
    cmp_t = Vector((8.2, 1.8, 2.7))

    def orbit(center, d, yaw, pitch):
        yaw, pitch = math.radians(yaw), math.radians(pitch)
        return Vector(center) + Vector((-math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch))) * d

    def shake(f, f0, amp, tau=4.0):
        if f < f0:
            return Vector()
        a = amp * math.exp(-(f - f0) / tau)
        return Vector((K.hash01(f, 1) - 0.5, K.hash01(f, 2) - 0.5, K.hash01(f, 3) - 0.5)) * 2 * a

    inner_keys = [(T["zoomed"], (math.log(46), 16, 15, 5.0)), (hit, (math.log(44), 15, 15, 5.6)),
                  (split, (math.log(38), 12, 14, 5.6)), (split + 30, (math.log(50), 10, 12, 5.6)),
                  (T["heat"], (math.log(54), 6, 11, 5.6)), (T["pull0"], (math.log(56), 4, 10, 5.6)),
                  (T["arrive"] - 12, (math.log(150), 10, 12, 4.0)), (T["field"], (math.log(250), 18, 14, 5.6)),
                  (T["out0"], (math.log(262), 20, 14, 5.6))]

    def cam_at(f):
        """(position, target, lens, fstop) for frame f."""
        if f < T["dive0"]:
            t = K.ramp(f, 1, T["dive0"])
            return orbit(pc, K.lerp(23, 20, K.ease_in_out(t)), K.lerp(30, 23, t), K.lerp(8, 11, t)), pc + Vector((0, 0, 0.1)), 85, K.fstop(4.5)
        if f < T["cross_in"]:
            t = K.ramp(f, T["dive0"], T["cross_in"])
            tgt = pc.lerp(ptop, K.smooth(t * 1.4))
            return (orbit(tgt, K.log_lerp(26, 0.35, K.ease_in_cubic(t)), K.lerp(24, 12, K.smooth(t)), K.lerp(13, 56, K.smooth(t))),
                    tgt, K.lerp(85, 50, K.smooth(t)), K.fstop(K.lerp(4.5, 2.8, t)))
        if f < T["cross_out"]:
            if f < T["zoomed"]:
                t = K.ease_out_cubic(K.ramp(f, T["cross_in"], T["zoomed"]))
                return orbit(INNER, K.log_lerp(1100, 46, t), K.lerp(6, 16, t), K.lerp(4, 15, t)), INNER, 50, K.fstop(K.lerp(8, 5.0, t))
            if f < T["out0"]:
                ld, yaw, pitch, fs = K.hermite(inner_keys, f)
                pos = orbit(INNER, math.exp(ld), yaw, pitch) + shake(f, split, 0.35) + shake(f, T["heat"], 0.6, 5.0)
                focus = INNER + Vector((0, 0, 0.6))
                focus = focus + (pos - focus).normalized() * 1.8 * (1 - K.ramp(f, T["pull0"], T["arrive"]))  # front half sharp
                return pos, focus, 50, K.fstop(fs)
            t = K.ease_in_cubic(K.ramp(f, T["out0"], T["cross_out"]))
            return orbit(INNER, K.log_lerp(262, 1600, t), 20, 14), INNER, 50, K.fstop(5.6)
        if f < T["cross_out"] + 12:  # back outside: rise out of the pellet's top
            t = K.ease_out_cubic(K.ramp(f, T["cross_out"], T["cross_out"] + 12))
            return orbit(ptop, K.log_lerp(0.35, 9.0, t), 12, K.lerp(56, 34, t)), ptop.lerp(pc, t), 50, K.fstop(5.6)
        t = K.ease_in_out(K.ramp(f, T["cross_out"] + 12, T["cmp"]))
        drift = K.ramp(f, T["cmp"], end)
        p_b = orbit(cmp_t, K.lerp(56, 53, drift), K.lerp(6, 4, drift), 17)
        return orbit(ptop, 9.0, 12, 34).lerp(p_b, t), pc.lerp(cmp_t, t), 50, K.fstop(K.lerp(5.6, 8, t))

    for f in range(1, end + 1):
        pos, tgt, lens, fs = cam_at(f)
        K.key(cam, "location", f, pos)
        K.key(target, "location", f, tgt)
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=f)
        cam.data.dof.aperture_fstop = fs
        cam.data.dof.keyframe_insert("aperture_fstop", frame=f)

    # ================================================================ anchors for Remotion labels
    away = Vector((0, -5000, 0))
    inside = lambda f: T["cross_in"] <= f < T["cross_out"]  # noqa: E731

    def track(name, fn):
        e = K.empty(f"anchor_{name}")
        K.bake(e, 1, end, lambda f: fn(f) if fn(f) is not None else away)
        anchors.anchor(name, e)

    track("pellet", lambda f: None if inside(f) else Vector((0, 0, 1.6)))
    track("coal", lambda f: Vector((heap_c[0], heap_c[1], heap_top)) if f >= T["coal"] else None)
    track("nucleus", lambda f: INNER + Vector((0, 0, 4.6)) if inside(f) and f < split else None)
    track("neutron", lambda f: n_start.lerp(n_end, K.ramp(f, T["n_in"], hit)) if T["n_in"] <= f <= hit else None)
    track("fragments", lambda f: (frag_center("big", f) + frag_center("small", f)) / 2 if inside(f) and f >= split else None)
    track("fragment_big", lambda f: frag_center("big", f) if inside(f) and f >= split else None)
    track("fragment_small", lambda f: frag_center("small", f) if inside(f) and f >= split else None)
    track("heat", lambda f: heat_c if inside(f) and f >= T["heat"] else None)
    track("chain", lambda f: INNER if inside(f) and f >= T["pull0"] else None)
