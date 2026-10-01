import { useMemo } from "react";
import { Easing, random, useCurrentFrame, useVideoConfig } from "remotion";
import { HeatBurst, Neutron, Nucleus, Pellet } from "../components/Atoms";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { Glow } from "../components/svg";
import { Tag } from "../components/Tag";
import { enter, lerp, linear, progress, riseStyle } from "../lib/anim";
import { buildCascade, hexLattice } from "../lib/cascade";
import { useCues } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

const CX = 960;
const CY = 440;
const SPACING = 120;
/** Directions of the 3 neutrons released by the first fission (reused by the cascade). */
const NEW_DIRS = [
  { dx: 0.93, dy: -0.37 },
  { dx: -0.29, dy: 0.96 },
  { dx: -0.93, dy: -0.37 },
];

export const Title: React.FC<{ text: string; t: number; color?: string }> = ({ text, t, color = C.text }) => (
  <div
    style={{
      position: "absolute",
      top: 128,
      left: 0,
      right: 0,
      textAlign: "center",
      fontFamily: DISPLAY,
      fontWeight: 700,
      fontSize: 56,
      letterSpacing: "0.04em",
      color,
      ...riseStyle(t, 16),
    }}
  >
    {text}
  </div>
);

/** Small uranium nucleus for the lattice; splits into two halves at `split` (0–1). */
const MiniNucleus: React.FC<{ x: number; y: number; split: number; dim: number; dir: number }> = ({ x, y, split, dim, dir }) => {
  if (split <= 0) {
    return <circle cx={x} cy={y} r={13} fill={C.uranium} opacity={dim} />;
  }
  const d = 6 + split * 22;
  const ox = Math.cos(dir) * d;
  const oy = Math.sin(dir) * d;
  const fade = 1 - split * 0.5;
  return (
    <g opacity={fade}>
      <circle cx={x + ox} cy={y + oy} r={9} fill={C.uranium} />
      <circle cx={x - ox} cy={y - oy} r={9} fill={C.uranium} />
    </g>
  );
};

/** Heap of irregular coal lumps (deterministic). Base centre at (x, y). */
const CoalHeap: React.FC<{ x: number; y: number; w: number; t: number }> = ({ x, y, w, t }) => {
  const lumps = useMemo(
    () =>
      Array.from({ length: 150 }, (_, i) => {
        const u = random(`c${i}`) * 2 - 1;
        const height = Math.pow(Math.max(0, 1 - u * u), 0.8);
        const v = Math.sqrt(random(`v${i}`));
        const cx = x + (u * w) / 2;
        const cy = y - 8 - (1 - v) * height * w * 0.36;
        const r = 9 + random(`r${i}`) * 13;
        const sides = 5 + Math.floor(random(`s${i}`) * 3);
        const rot = random(`a${i}`) * Math.PI;
        const pts = Array.from({ length: sides }, (_, k) => {
          const a = rot + (k / sides) * Math.PI * 2;
          const rr = r * (0.7 + random(`p${i}-${k}`) * 0.5);
          return `${(cx + Math.cos(a) * rr).toFixed(1)},${(cy + Math.sin(a) * rr * 0.8).toFixed(1)}`;
        }).join(" ");
        return { pts, shade: ["#1C1F24", "#2A2E35", "#363B44", "#22262C"][i % 4], order: cy };
      }).sort((a, b) => a.order - b.order),
    [x, y, w],
  );
  return (
    <g opacity={t}>
      <ellipse cx={x} cy={y} rx={w / 2 + 10} ry={14} fill="#05080F" opacity={0.6} />
      {lumps.map((l, i) => (
        <polygon key={i} points={l.pts} fill={l.shade} stroke="#4A515D" strokeWidth={1.2} strokeOpacity={0.6} />
      ))}
    </g>
  );
};

export const Fission: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();

  const points = useMemo(() => hexLattice({ x: CX, y: CY }, SPACING, { x0: 90, x1: 1830, y0: 150, y1: 800 }), []);
  const nodes = useMemo(() => buildCascade(points, { x: CX, y: CY }, NEW_DIRS, [3, 2, 2], cue("chain") + 6, 26), [points]); // eslint-disable-line react-hooks/exhaustive-deps
  const splitIdx = useMemo(() => new Map(nodes.map((n, i) => [n.idx, i])), [nodes]);

  // --- phase 1: pellet, then zoom into it ---
  const pelletIn = enter(frame, 4, fps, 24);
  const zoomIn = progress(frame, cue("pellet") + 22, cue("neutron") - 2, Easing.in(Easing.cubic));
  const pelletOpacity = pelletIn * (1 - zoomIn);

  // --- phase 2: single nucleus ---
  const closeUp = progress(frame, cue("pellet") + 30, cue("neutron") - 4) * (1 - progress(frame, cue("chain") - 10, cue("chain") + 8));
  const hitAt = cue("hit") + 4;
  const nIn = progress(frame, cue("neutron") - 2, hitAt, Easing.inOut(Easing.quad));
  const wobble = progress(frame, hitAt, cue("split"));
  const apart = progress(frame, cue("split"), cue("split") + 34, Easing.out(Easing.cubic));
  const heatT = linear(frame, cue("heat") - 2, cue("heat") + 46);
  const heatGlow = progress(frame, cue("heat") - 2, cue("heat") + 20);
  const newN = progress(frame, cue("newNeutrons") - 2, cue("newNeutrons") + 46, Easing.out(Easing.quad));
  const split = frame >= cue("split");

  // --- phase 3: zoom out to the lattice cascade ---
  const lattice = progress(frame, cue("chain") - 12, cue("chain") + 14) * (1 - progress(frame, cue("onePellet") - 14, cue("onePellet") + 4));
  const zoomOut = lerp(1.8, 1, progress(frame, cue("chain") - 12, cue("chain") + 26, Easing.out(Easing.cubic)));

  // --- phase 4: 1 pellet ≈ 1 t coal ---
  const cmpPellet = enter(frame, cue("onePellet"), fps, 18);
  const eq = enter(frame, cue("onePellet") + 30, fps, 14);
  const coal = enter(frame, cue("coal") - 6, fps, 18);

  const fragA = { x: CX - 280 * apart, y: CY - 80 * apart };
  const fragB = { x: CX + 280 * apart, y: CY + 80 * apart };

  return (
    <SceneShell>
      <Sfx at={cue("split")} name="pop" />
      <Sfx at={cue("heat") - 2} name="pop" gain={0.6} />
      <Sfx at={cue("chain") - 12} name="whoosh" gain={0.8} />
      {nodes
        .filter((n) => n.gen === 1 || n.gen === 2)
        .map((n, i) => (
          <Sfx key={i} at={n.splitAt} name="pop" gain={n.gen === 1 ? 0.45 : 0.25} />
        ))}
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        {/* phase 1 */}
        <g
          opacity={pelletOpacity}
          transform={`translate(${CX},${CY}) scale(${(0.6 + 0.4 * pelletIn) * (1 + zoomIn * 7)}) translate(${-CX},${-CY})`}
        >
          <Pellet x={CX} y={CY} w={190} glow={0.5} />
        </g>

        {/* phase 2 */}
        <g opacity={closeUp}>
          {!split && (
            <Nucleus x={CX} y={CY} n={40} r={15} stretch={wobble * 0.55} shake={wobble * 3.5} frame={frame} />
          )}
          {split && (
            <>
              <Glow x={fragA.x} y={fragA.y} r={160} color={C.heat} opacity={heatGlow * 0.8} />
              <Glow x={fragB.x} y={fragB.y} r={160} color={C.heat} opacity={heatGlow * 0.8} />
              <Nucleus x={fragA.x} y={fragA.y} n={20} r={15} frame={frame} seed="a" />
              <Nucleus x={fragB.x} y={fragB.y} n={19} r={15} frame={frame} seed="b" />
            </>
          )}
          <HeatBurst x={CX} y={CY} t={heatT} size={320} />
          {nIn > 0 && nIn < 1 && (
            <Neutron x={lerp(150, CX - 100, nIn)} y={CY} r={14} dir={{ dx: 1, dy: 0 }} trail={80} />
          )}
          {newN > 0 &&
            NEW_DIRS.map((d, i) => (
              <Neutron key={i} x={CX + d.dx * 360 * newN} y={CY + d.dy * 360 * newN} r={13} dir={d} trail={70} />
            ))}
        </g>

        {/* phase 3 */}
        {lattice > 0 && (
          <g opacity={lattice} transform={`translate(${CX},${CY}) scale(${zoomOut}) translate(${-CX},${-CY})`}>
            {points.map((p, i) => {
              const ni = splitIdx.get(i);
              const node = ni === undefined ? null : nodes[ni];
              const s = node ? linear(frame, node.splitAt, node.splitAt + 18) : 0;
              return <MiniNucleus key={i} x={p.x} y={p.y} split={node ? s : 0} dim={0.55} dir={i * 1.7} />;
            })}
            {nodes.map((n, i) =>
              n.splitAt <= frame && frame < n.splitAt + 22 ? (
                <HeatBurst key={`h${i}`} x={points[n.idx].x} y={points[n.idx].y} t={linear(frame, n.splitAt, n.splitAt + 22)} size={70} />
              ) : null,
            )}
            {nodes.map((n, i) => {
              if (n.parent === null) return null;
              const from = points[nodes[n.parent].idx];
              const to = points[n.idx];
              const start = nodes[n.parent].splitAt;
              if (frame < start || frame >= n.splitAt) return null;
              const t = linear(frame, start, n.splitAt);
              const len = Math.hypot(to.x - from.x, to.y - from.y);
              return (
                <Neutron
                  key={`n${i}`}
                  x={lerp(from.x, to.x, t)}
                  y={lerp(from.y, to.y, t)}
                  r={7}
                  dir={{ dx: (to.x - from.x) / len, dy: (to.y - from.y) / len }}
                  trail={30}
                />
              );
            })}
          </g>
        )}

        {/* phase 4 */}
        <g opacity={cmpPellet}>
          <Pellet x={560} y={560} w={60} glow={0.8} />
        </g>
        <text x={880} y={560} textAnchor="middle" fill={C.text} fontFamily={DISPLAY} fontSize={90} fontWeight={700} opacity={eq}>
          ≈
        </text>
        <CoalHeap x={1340} y={610} w={640} t={coal} />
      </svg>

      {/* labels */}
      <Tag x={CX + 150} y={CY + 280} text="pastylka paliwa (UO₂)" sub="ok. 1 cm" t={pelletIn * (1 - zoomIn) * enter(frame, cue("pellet") - 4, fps, 14)} color={C.uranium} anchor="center" />
      <Tag x={CX + 130} y={CY - 130} text="jądro uranu-235" t={closeUp * (1 - wobble) * (split ? 0 : 1)} color={C.uranium} />
      <Tag x={lerp(150, CX - 100, nIn)} y={CY - 60} text="neutron" t={nIn > 0 && nIn < 0.96 ? 1 : 0} color={C.neutron} anchor="center" />
      <Tag x={CX} y={CY + 250} text="dwa mniejsze jądra" t={closeUp * enter(frame, cue("split") + 20, fps, 14) * (1 - heatGlow)} color={C.uranium} anchor="center" />
      <Tag x={CX} y={CY + 250} text="ciepło" t={closeUp * heatGlow * (1 - newN)} color={C.heat} anchor="center" size={36} />
      <Tag x={CX} y={CY + 250} text="2–3 nowe neutrony" t={closeUp * newN} color={C.neutron} anchor="center" size={34} />

      <Title text="ROZSZCZEPIENIE" t={closeUp * enter(frame, cue("fission") - 4, fps, 16)} />
      <Title text="REAKCJA ŁAŃCUCHOWA" t={lattice * enter(frame, cue("chainLabel") - 4, fps, 16)} color={C.neutron} />

      <div style={{ position: "absolute", left: 410, top: 640, width: 300, textAlign: "center", fontFamily: BODY, ...riseStyle(cmpPellet, 12) }}>
        <div style={{ fontFamily: DISPLAY, fontSize: 40, fontWeight: 700, color: C.text }}>1 pastylka</div>
        <div style={{ fontSize: 24, fontWeight: 600, color: C.muted }}>uranu</div>
      </div>
      <div style={{ position: "absolute", left: 1130, top: 640, width: 420, textAlign: "center", fontFamily: BODY, ...riseStyle(coal, 12) }}>
        <div style={{ fontFamily: DISPLAY, fontSize: 40, fontWeight: 700, color: C.text }}>≈ 1 tona węgla</div>
        <div style={{ fontSize: 20, fontWeight: 600, color: C.faint, marginTop: 6 }}>źródło: World Nuclear Association</div>
      </div>
    </SceneShell>
  );
};
