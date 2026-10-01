import { C } from "../theme";
import { Glow, useUid } from "./svg";

/** Cumulative rotation (degrees) for a speed (deg/frame) that changes over time. */
export const spinAngle = (frame: number, speedAt: (f: number) => number): number => {
  let angle = 0;
  for (let f = 0; f < frame; f++) angle += speedAt(f);
  return angle;
};

/** Front view of a turbine rotor in its casing — the "wiatraczek" viewers know. */
export const Turbine: React.FC<{ x: number; y: number; r: number; angle: number; blur?: number }> = ({
  x,
  y,
  r,
  angle,
  blur = 0,
}) => {
  const id = useUid();
  const blades = 12;
  const blade = `M0,${-r * 0.2} C${r * 0.16},${-r * 0.42} ${r * 0.14},${-r * 0.7} ${r * 0.05},${-r * 0.86} L${-r * 0.06},${-r * 0.86} C${-r * 0.02},${-r * 0.62} ${-r * 0.06},${-r * 0.4} ${-r * 0.1},${-r * 0.2} Z`;
  return (
    <g transform={`translate(${x},${y})`}>
      <defs>
        <radialGradient id={`case${id}`}>
          <stop offset="70%" stopColor="#101C30" />
          <stop offset="100%" stopColor="#1C2B44" />
        </radialGradient>
        <linearGradient id={`blade${id}`} x1="0" x2="1">
          <stop offset="0%" stopColor="#C9D3E2" />
          <stop offset="100%" stopColor="#6E7E98" />
        </linearGradient>
      </defs>
      <circle r={r} fill={`url(#case${id})`} stroke={C.steel} strokeWidth={r * 0.06} />
      <g transform={`rotate(${angle})`} opacity={1 - blur * 0.45}>
        {Array.from({ length: blades }, (_, i) => (
          <path key={i} d={blade} fill={`url(#blade${id})`} transform={`rotate(${(i * 360) / blades})`} />
        ))}
      </g>
      {/* motion blur disc when spinning fast */}
      <circle r={r * 0.53} fill="none" stroke="#B9C5D8" strokeWidth={r * 0.66} opacity={blur * 0.22} />
      <circle r={r * 0.2} fill="#2A3A55" stroke="#B4C0D2" strokeWidth={r * 0.04} />
      <circle r={r * 0.07} fill="#B4C0D2" />
    </g>
  );
};

/** Generator housing; `on` lights the output (yellow = electricity). */
export const Generator: React.FC<{ x: number; y: number; w: number; h: number; angle: number; on: number }> = ({
  x,
  y,
  w,
  h,
  angle,
  on,
}) => {
  const id = useUid();
  const r = h * 0.3;
  return (
    <g transform={`translate(${x},${y})`}>
      <defs>
        <linearGradient id={`gen${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#3A4A66" />
          <stop offset="100%" stopColor="#1A263B" />
        </linearGradient>
      </defs>
      <Glow x={w / 2} y={h / 2} r={w * 0.9} color={C.electricity} opacity={on * 0.7} />
      <rect width={w} height={h} rx={h * 0.16} fill={`url(#gen${id})`} stroke={C.steel} strokeWidth={3} />
      {/* copper windings */}
      {Array.from({ length: 7 }, (_, i) => (
        <rect key={i} x={w * 0.1 + i * w * 0.06} y={h * 0.18} width={w * 0.035} height={h * 0.64} rx={3} fill="#C98B4F" opacity={0.85} />
      ))}
      {/* rotor face */}
      <g transform={`translate(${w * 0.72},${h / 2}) rotate(${angle})`}>
        <circle r={r} fill="#24334C" stroke={C.steel} strokeWidth={3} />
        <rect x={-r * 0.85} y={-r * 0.22} width={r * 1.7} height={r * 0.44} rx={r * 0.2} fill="#8E9BB0" />
      </g>
      {/* lightning bolt */}
      <path
        d={`M${w * 0.5},${-h * 0.42} l${-w * 0.07},${h * 0.26} h${w * 0.06} l${-w * 0.04},${h * 0.24} l${w * 0.11},${-h * 0.31} h${-w * 0.06} l${w * 0.04},${-h * 0.19} Z`}
        fill={C.electricity}
        opacity={on}
      />
    </g>
  );
};

/** Condenser: steam in at the top, cold tubes inside, water collects at the bottom. */
export const Condenser: React.FC<{ x: number; y: number; w: number; h: number; frame: number; active: number }> = ({
  x,
  y,
  w,
  h,
  frame,
  active,
}) => {
  const rows = 4;
  return (
    <g transform={`translate(${x},${y})`}>
      <rect width={w} height={h} rx={18} fill="#0E1A2C" stroke={C.steel} strokeWidth={3} />
      {/* steam cloud at the top */}
      <rect x={6} y={6} width={w - 12} height={h * 0.32} rx={14} fill={C.steam} opacity={0.12 * active} />
      {/* cold water tubes with moving dashes */}
      {Array.from({ length: rows }, (_, i) => (
        <g key={i}>
          <line x1={14} x2={w - 14} y1={h * (0.28 + i * 0.12)} y2={h * (0.28 + i * 0.12)} stroke="#2A4A78" strokeWidth={9} strokeLinecap="round" />
          <line
            x1={14}
            x2={w - 14}
            y1={h * (0.28 + i * 0.12)}
            y2={h * (0.28 + i * 0.12)}
            stroke="#7FB2FF"
            strokeWidth={3}
            strokeDasharray="10 14"
            strokeDashoffset={-frame * 2.4}
            opacity={0.8 * active}
          />
        </g>
      ))}
      {/* droplets */}
      {Array.from({ length: 8 }, (_, i) => {
        const fall = ((frame * 1.6 + i * 23) % (h * 0.5)) / (h * 0.5);
        return (
          <circle key={i} cx={w * (0.12 + i * 0.11)} cy={h * (0.3 + fall * 0.48)} r={3.5} fill={C.water} opacity={active * (1 - fall * 0.3)} />
        );
      })}
      {/* collected water */}
      <rect x={6} y={h * 0.8} width={w - 12} height={h * 0.2 - 6} rx={12} fill={C.water} opacity={0.75 * active} />
    </g>
  );
};

/** Pump symbol (circle + rotating impeller); `crossed` draws a "no pump" slash. */
export const Pump: React.FC<{ x: number; y: number; r: number; angle?: number; crossed?: number }> = ({
  x,
  y,
  r,
  angle = 0,
  crossed = 0,
}) => (
  <g transform={`translate(${x},${y})`}>
    <circle r={r} fill="#14223A" stroke={C.steel} strokeWidth={r * 0.08} />
    <g transform={`rotate(${angle})`}>
      {[0, 120, 240].map((a) => (
        <path key={a} d={`M0,0 C${r * 0.3},${-r * 0.2} ${r * 0.5},${-r * 0.55} ${r * 0.2},${-r * 0.7}`} stroke="#B4C0D2" strokeWidth={r * 0.1} fill="none" strokeLinecap="round" transform={`rotate(${a})`} />
      ))}
    </g>
    <circle r={r * 0.12} fill="#B4C0D2" />
    {crossed > 0 && (
      <g opacity={crossed}>
        <circle r={r * 1.18} fill="none" stroke={C.accent} strokeWidth={r * 0.12} />
        <line x1={-r * 0.83} y1={r * 0.83} x2={r * 0.83} y2={-r * 0.83} stroke={C.accent} strokeWidth={r * 0.12} strokeLinecap="round" />
      </g>
    )}
  </g>
);
