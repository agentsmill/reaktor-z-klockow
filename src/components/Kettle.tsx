import { C } from "../theme";
import { Glow } from "./svg";

/** Analogy inset: flame → kettle → steam → spinning pinwheel (heat → steam → turbine). Origin = panel top-left. */
export const KettleAnalogy: React.FC<{ x: number; y: number; frame: number; t: number }> = ({ x, y, frame, t }) => {
  if (t <= 0) return null;
  const spin = frame * 14;
  return (
    <g transform={`translate(${x},${y})`} opacity={t}>
      <rect width={500} height={300} rx={26} fill={C.panel} stroke={C.panelEdge} strokeWidth={2} />
      {/* flame */}
      <Glow x={150} y={255} r={70} color={C.heat} opacity={0.8} />
      {[0, 1, 2].map((i) => {
        const flick = Math.sin(frame * 0.6 + i * 2) * 4;
        return (
          <path
            key={i}
            d={`M${125 + i * 25},${270} Q${118 + i * 25},${248 + flick} ${130 + i * 25},${230 + flick} Q${142 + i * 25},${248 - flick} ${135 + i * 25},${270} Z`}
            fill={i === 1 ? "#FFC08F" : C.heat}
          />
        );
      })}
      {/* kettle */}
      <path d="M80,225 Q72,140 150,128 Q228,140 220,225 Z" fill="#AEB9CA" />
      <path d="M100,140 Q150,96 200,140" fill="none" stroke="#8E9AAE" strokeWidth={10} strokeLinecap="round" />
      <path d="M212,178 L262,138 L270,148 L222,198 Z" fill="#AEB9CA" />
      <ellipse cx={150} cy={128} rx={30} ry={8} fill="#8E9AAE" />
      {/* steam from the spout towards the pinwheel */}
      {Array.from({ length: 7 }, (_, i) => {
        const p = ((frame * 0.035 + i / 7) % 1 + 1) % 1;
        return (
          <circle key={i} cx={272 + p * 110} cy={136 - p * 34 + Math.sin(frame * 0.2 + i) * 4} r={8 + p * 14} fill={C.steam} opacity={0.55 * (1 - p)} />
        );
      })}
      {/* pinwheel */}
      <line x1={410} y1={120} x2={410} y2={268} stroke={C.steel} strokeWidth={6} strokeLinecap="round" />
      <g transform={`translate(410,120) rotate(${spin})`}>
        {[0, 90, 180, 270].map((a, i) => (
          <path key={a} d="M0,0 L0,-58 Q36,-40 0,0 Z" fill={i % 2 ? "#DDE5F0" : "#8FA0BA"} transform={`rotate(${a})`} />
        ))}
        <circle r={7} fill={C.steel} />
      </g>
    </g>
  );
};
