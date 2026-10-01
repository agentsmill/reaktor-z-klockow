import { useCurrentFrame, useVideoConfig } from "remotion";
import { enter } from "../lib/anim";
import { BODY, C } from "../theme";
import { Pellet } from "./Atoms";
import { Turbine } from "./Machines";
import { ArrowHead, Glow } from "./svg";

export const RECAP_STEPS = [
  { label: "uran", color: C.uranium },
  { label: "ciepło", color: C.heat },
  { label: "para", color: C.steam },
  { label: "turbina", color: C.steel },
  { label: "prąd", color: C.electricity },
] as const;
const XS = [400, 680, 960, 1240, 1520];

/** uran → ciepło → para → turbina → prąd; each step pops in at its frame. */
export const RecapChain: React.FC<{ y: number; scale?: number; at: number[]; turbineAngle: number }> = ({
  y,
  scale = 1,
  at,
  turbineAngle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      <g transform={`translate(960,${y}) scale(${scale}) translate(-960,0)`}>
        {RECAP_STEPS.map((s, i) => {
          const t = enter(frame, at[i] - 4, fps, 14);
          const x = XS[i];
          return (
            <g key={s.label} opacity={t} transform={`translate(${x},0) scale(${0.8 + 0.2 * t}) translate(${-x},0)`}>
              {i > 0 && (
                <g opacity={t}>
                  <line x1={XS[i - 1] + 96} x2={x - 104} y1={0} y2={0} stroke={C.line} strokeWidth={4} strokeLinecap="round" />
                  <ArrowHead x={x - 98} y={0} dx={1} dy={0} size={16} color={C.line} />
                </g>
              )}
              <Glow x={x} y={0} r={130} color={s.color} opacity={0.45} />
              <circle cx={x} cy={0} r={82} fill={C.panel} stroke={s.color} strokeWidth={4} />
              {i === 0 && <Pellet x={x} y={6} w={56} glow={0.4} />}
              {i === 1 && <path d={`M${x},-46 C${x + 34},-10 ${x + 30},30 ${x},40 C${x - 30},30 ${x - 34},-10 ${x},-46 Z`} fill={C.heat} />}
              {i === 2 &&
                [-24, 0, 24].map((dx, k) => (
                  <circle key={k} cx={x + dx} cy={(k === 1 ? -12 : 6) + Math.sin(frame * 0.1 + k) * 3} r={k === 1 ? 26 : 20} fill={C.steam} opacity={0.9} />
                ))}
              {i === 3 && <Turbine x={x} y={0} r={56} angle={turbineAngle} />}
              {i === 4 && <path d={`M${x + 8},-48 l-30,52 h24 l-12,44 l40,-60 h-24 l18,-36 Z`} fill={C.electricity} />}
              <text x={x} y={128} textAnchor="middle" fill={C.text} fontFamily={BODY} fontSize={34} fontWeight={800}
                style={{ textShadow: "0 2px 10px rgba(6,12,23,0.9)" }}>
                {s.label}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
};
