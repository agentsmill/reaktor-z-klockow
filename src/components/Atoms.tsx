import { random } from "remotion";
import { C } from "../theme";
import { Glow, useUid } from "./svg";

/** Free neutron: bright cyan dot with bloom and an optional motion trail. */
export const Neutron: React.FC<{
  x: number;
  y: number;
  r?: number;
  opacity?: number;
  /** Unit direction of travel; draws a fading trail behind the neutron. */
  dir?: { dx: number; dy: number };
  trail?: number;
}> = ({ x, y, r = 9, opacity = 1, dir, trail = 46 }) => {
  if (opacity <= 0) return null;
  return (
    <g opacity={opacity}>
      {dir && (
        <line
          x1={x - dir.dx * trail}
          y1={y - dir.dy * trail}
          x2={x}
          y2={y}
          stroke={C.neutron}
          strokeWidth={r * 0.9}
          strokeLinecap="round"
          opacity={0.28}
        />
      )}
      <Glow x={x} y={y} r={r * 4.2} color={C.neutron} />
      <circle cx={x} cy={y} r={r} fill="#E4FAFF" stroke={C.neutron} strokeWidth={r * 0.35} />
    </g>
  );
};

/** Uranium nucleus: a sunflower-packed cluster of nucleons (green = uranium). */
export const Nucleus: React.FC<{
  x: number;
  y: number;
  n?: number;
  /** Nucleon radius. */
  r?: number;
  /** Horizontal elongation before splitting (0 = round). */
  stretch?: number;
  /** Vibration amplitude in px. */
  shake?: number;
  frame?: number;
  opacity?: number;
  seed?: string;
}> = ({ x, y, n = 36, r = 9, stretch = 0, shake = 0, frame = 0, opacity = 1, seed = "u" }) => {
  const id = useUid();
  if (opacity <= 0) return null;
  const spacing = r * 0.98;
  const nucleons = Array.from({ length: n }, (_, i) => {
    const rho = spacing * Math.sqrt(i + 0.5);
    const theta = i * 2.39996;
    return { i, px: Math.cos(theta) * rho, py: Math.sin(theta) * rho, dark: random(`${seed}-${i}`) > 0.5 };
  }).reverse(); // outer first, so the centre reads as nearest to the viewer

  const sx = 1 + stretch;
  const sy = 1 / (1 + stretch * 0.45);
  return (
    <g opacity={opacity}>
      <defs>
        <radialGradient id={`p${id}`} cx="35%" cy="30%" r="75%">
          <stop offset="0%" stopColor="#E9FFD2" />
          <stop offset="45%" stopColor={C.uranium} />
          <stop offset="100%" stopColor="#3F7A22" />
        </radialGradient>
        <radialGradient id={`n${id}`} cx="35%" cy="30%" r="75%">
          <stop offset="0%" stopColor="#F4FFE9" />
          <stop offset="50%" stopColor="#BFE59A" />
          <stop offset="100%" stopColor="#5E8A45" />
        </radialGradient>
      </defs>
      <Glow x={x} y={y} r={spacing * Math.sqrt(n) * 2.2} color={C.uranium} opacity={0.5} />
      {nucleons.map((p) => {
        const jx = shake ? Math.sin(frame * 1.9 + p.i * 1.3) * shake : 0;
        const jy = shake ? Math.cos(frame * 2.3 + p.i * 0.7) * shake : 0;
        return (
          <circle
            key={p.i}
            cx={x + p.px * sx + jx}
            cy={y + p.py * sy + jy}
            r={r}
            fill={`url(#${p.dark ? "p" : "n"}${id})`}
          />
        );
      })}
    </g>
  );
};

/** Expanding ring + glow of released heat; `t` 0→1 over the burst. */
export const HeatBurst: React.FC<{ x: number; y: number; t: number; size?: number }> = ({ x, y, t, size = 170 }) => {
  if (t <= 0 || t >= 1) return null;
  const ease = 1 - Math.pow(1 - t, 3);
  const r = size * (0.15 + 0.85 * ease);
  return (
    <g>
      <Glow x={x} y={y} r={r * 1.5} color={C.heat} opacity={1 - t} />
      <circle cx={x} cy={y} r={r} fill="none" stroke={C.heat} strokeWidth={10 * (1 - t)} opacity={1 - t} />
      <circle cx={x} cy={y} r={r * 0.62} fill="none" stroke="#FFC08F" strokeWidth={4 * (1 - t)} opacity={(1 - t) * 0.8} />
    </g>
  );
};

/** Ceramic UO₂ fuel pellet seen at an angle. Width = w; height ≈ 1.2·w. */
export const Pellet: React.FC<{ x: number; y: number; w: number; glow?: number }> = ({ x, y, w, glow = 0 }) => {
  const id = useUid();
  const h = w * 1.15;
  const ry = w * 0.22;
  return (
    <g>
      <defs>
        <linearGradient id={`body${id}`} x1="0" x2="1">
          <stop offset="0%" stopColor="#2C3329" />
          <stop offset="35%" stopColor="#5B6A55" />
          <stop offset="70%" stopColor="#3A4536" />
          <stop offset="100%" stopColor="#20261E" />
        </linearGradient>
      </defs>
      <Glow x={x} y={y} r={w * 1.6} color={C.uranium} opacity={glow} />
      <path
        d={`M${x - w / 2},${y - h / 2} L${x - w / 2},${y + h / 2} A${w / 2},${ry} 0 0 0 ${x + w / 2},${y + h / 2} L${x + w / 2},${y - h / 2} Z`}
        fill={`url(#body${id})`}
      />
      <ellipse cx={x} cy={y - h / 2} rx={w / 2} ry={ry} fill="#6E7D66" stroke={C.uranium} strokeWidth={w * 0.02} strokeOpacity={0.7} />
      <ellipse cx={x} cy={y - h / 2} rx={w * 0.36} ry={ry * 0.62} fill="none" stroke="#86967D" strokeWidth={w * 0.015} opacity={0.6} />
    </g>
  );
};
