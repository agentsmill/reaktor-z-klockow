import { getLength, getPointAtLength } from "@remotion/paths";
import { useId, useMemo } from "react";

/** DOM-safe unique id prefix for SVG defs (gradients are global in the document). */
export const useUid = (): string => useId().replace(/[^a-zA-Z0-9_-]/g, "");

export type Pt = { x: number; y: number };

/** Samples a path once into evenly spaced points; positions are then O(1) lookups. */
export function samplePath(d: string, samples = 300): { points: Pt[]; length: number } {
  const length = getLength(d);
  const points = Array.from({ length: samples + 1 }, (_, i) => getPointAtLength(d, (i / samples) * length) ?? { x: 0, y: 0 });
  return { points, length };
}

export function pointAt(sampled: { points: Pt[] }, t: number): Pt {
  const n = sampled.points.length - 1;
  const f = Math.min(Math.max(t, 0), 1) * n;
  const i = Math.min(Math.floor(f), n - 1);
  const k = f - i;
  const a = sampled.points[i];
  const b = sampled.points[i + 1];
  return { x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k };
}

/** Dots travelling along a path — water, steam, electricity. */
export const FlowParticles: React.FC<{
  d: string;
  frame: number;
  count: number;
  /** Pixels per frame along the path. */
  speed: number;
  radius?: number | ((t: number, i: number) => number);
  color: string | ((t: number) => string);
  opacity?: number;
  /** Fraction of the path over which particles fade in/out at both ends. */
  edge?: number;
}> = ({ d, frame, count, speed, radius = 5, color, opacity = 1, edge = 0.06 }) => {
  const sampled = useMemo(() => samplePath(d), [d]);
  if (opacity <= 0) return null;
  return (
    <g opacity={opacity}>
      {Array.from({ length: count }, (_, i) => {
        const s = (((frame * speed) / sampled.length + i / count) % 1 + 1) % 1;
        const p = pointAt(sampled, s);
        const fade = edge > 0 ? Math.min(1, s / edge, (1 - s) / edge) : 1;
        const r = typeof radius === "function" ? radius(s, i) : radius;
        return (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r={r}
            fill={typeof color === "function" ? color(s) : color}
            opacity={fade}
          />
        );
      })}
    </g>
  );
};

/** Soft radial glow (cheap bloom, no filters). */
export const Glow: React.FC<{ x: number; y: number; r: number; color: string; opacity?: number }> = ({
  x,
  y,
  r,
  color,
  opacity = 1,
}) => {
  const id = useUid();
  if (opacity <= 0) return null;
  return (
    <>
      <defs>
        <radialGradient id={`g${id}`}>
          <stop offset="0%" stopColor={color} stopOpacity={0.55} />
          <stop offset="45%" stopColor={color} stopOpacity={0.18} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </radialGradient>
      </defs>
      <circle cx={x} cy={y} r={r} fill={`url(#g${id})`} opacity={opacity} />
    </>
  );
};

/** Arrow head pointing along the direction (dx, dy) at (x, y). */
export const ArrowHead: React.FC<{ x: number; y: number; dx: number; dy: number; size?: number; color: string }> = ({
  x,
  y,
  dx,
  dy,
  size = 14,
  color,
}) => {
  const a = Math.atan2(dy, dx);
  const p = (ang: number, r: number) => `${x + Math.cos(ang) * r},${y + Math.sin(ang) * r}`;
  return <polygon points={`${p(a, size)} ${p(a + 2.5, size * 0.75)} ${p(a - 2.5, size * 0.75)}`} fill={color} />;
};
