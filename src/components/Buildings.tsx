import { C } from "../theme";
import { Glow, useUid } from "./svg";

const LIGHT = "#61718C";
const MID = "#4A5973";
const DARK = "#334058";

/** Hyperboloid cooling tower outline. */
const towerPath = (cx: number, baseY: number, h: number, wBase: number, wWaist: number, wTop: number) =>
  `M${cx - wBase / 2},${baseY} C${cx - wWaist / 2},${baseY - h * 0.45} ${cx - wWaist / 2},${baseY - h * 0.78} ${cx - wTop / 2},${baseY - h} ` +
  `L${cx + wTop / 2},${baseY - h} C${cx + wWaist / 2},${baseY - h * 0.78} ${cx + wWaist / 2},${baseY - h * 0.45} ${cx + wBase / 2},${baseY} Z`;

/** Large conventional nuclear plant: containment dome + 2 cooling towers + turbine hall. Base at (x, y). */
export const BigPlant: React.FC<{ x: number; y: number; s?: number; frame: number; opacity?: number }> = ({
  x,
  y,
  s = 1,
  frame,
  opacity = 1,
}) => {
  const id = useUid();
  return (
  <g transform={`translate(${x},${y}) scale(${s})`} opacity={opacity}>
    <defs>
      <radialGradient id={`plume${id}`}>
        <stop offset="0%" stopColor={C.steam} stopOpacity={0.5} />
        <stop offset="100%" stopColor={C.steam} stopOpacity={0} />
      </radialGradient>
    </defs>
    {/* soft steam plumes (water vapour, not smoke) */}
    {[150, 360].map((cx, i) =>
      [0, 1, 2, 3].map((k) => {
        const t = ((frame * 0.5 + k * 32 + i * 17) % 128) / 128;
        return <circle key={`${i}${k}`} cx={cx + t * 70} cy={-350 - t * 110} r={50 + t * 60} fill={`url(#plume${id})`} opacity={0.9 * (1 - t)} />;
      }),
    )}
    <path d={towerPath(150, 0, 360, 230, 118, 150)} fill={MID} />
    <path d={towerPath(360, 0, 360, 230, 118, 150)} fill={LIGHT} />
    {/* containment */}
    <rect x={470} y={-230} width={150} height={230} fill={MID} />
    <ellipse cx={545} cy={-230} rx={75} ry={60} fill={MID} />
    {/* turbine hall */}
    <rect x={600} y={-130} width={230} height={130} fill={DARK} />
    <rect x={600} y={-138} width={230} height={10} fill={LIGHT} />
  </g>
  );
};

/** Compact SMR plant (as in the AI visualisation): cylindrical reactor building + turbine hall. */
export const SmrPlant: React.FC<{
  x: number;
  y: number;
  s?: number;
  opacity?: number;
  /** 0–1: show the reactor building split into stacked modules. */
  modules?: number;
}> = ({ x, y, s = 1, opacity = 1, modules = 0 }) => (
  <g transform={`translate(${x},${y}) scale(${s})`} opacity={opacity}>
    <rect x={0} y={-190} width={100} height={190} fill={LIGHT} />
    <ellipse cx={50} cy={-190} rx={50} ry={14} fill="#7D8CA5" />
    <rect x={0} y={-190} width={22} height={190} fill="#7D8CA5" opacity={0.5} />
    {[1, 2, 3].map((i) => (
      <line key={i} x1={0} x2={100} y1={-190 + i * 47.5} y2={-190 + i * 47.5} stroke={C.steam} strokeWidth={3} strokeDasharray="8 6" opacity={modules * 0.9} />
    ))}
    <rect x={100} y={-95} width={170} height={95} fill={MID} />
    <rect x={100} y={-101} width={170} height={8} fill={LIGHT} />
    <rect x={270} y={-55} width={60} height={55} fill={DARK} />
  </g>
);

/** Factory with saw-tooth roof. Base at (x, y). */
export const Factory: React.FC<{ x: number; y: number; s?: number; opacity?: number }> = ({ x, y, s = 1, opacity = 1 }) => (
  <g transform={`translate(${x},${y}) scale(${s})`} opacity={opacity}>
    <path d="M0,0 L0,-110 L50,-150 L50,-110 L100,-150 L100,-110 L150,-150 L150,-110 L200,-150 L200,0 Z" fill={MID} />
    <rect x={160} y={-215} width={22} height={70} fill={DARK} />
    {[0, 1, 2].map((i) => (
      <rect key={i} x={20 + i * 60} y={-80} width={36} height={36} rx={3} fill={DARK} />
    ))}
  </g>
);

/** Isometric module box (prefabricated reactor building segment). */
export const ModuleBox: React.FC<{ x: number; y: number; w: number; opacity?: number }> = ({ x, y, w, opacity = 1 }) => {
  const h = w * 0.6;
  const d = w * 0.3;
  return (
    <g transform={`translate(${x},${y})`} opacity={opacity}>
      <path d={`M0,0 L${w},0 L${w},${-h} L0,${-h} Z`} fill={LIGHT} />
      <path d={`M0,${-h} L${d},${-h - d * 0.6} L${w + d},${-h - d * 0.6} L${w},${-h} Z`} fill="#8494AD" />
      <path d={`M${w},0 L${w + d},${-d * 0.6} L${w + d},${-h - d * 0.6} L${w},${-h} Z`} fill={MID} />
      <rect x={w * 0.1} y={-h * 0.8} width={w * 0.8} height={h * 0.6} fill="none" stroke={C.steam} strokeWidth={2} strokeDasharray="6 5" opacity={0.6} />
    </g>
  );
};

/** House whose windows light up with `lit` (yellow = electricity). Base at (x, y). */
export const House: React.FC<{ x: number; y: number; s?: number; lit?: number }> = ({ x, y, s = 1, lit = 0 }) => (
  <g transform={`translate(${x},${y}) scale(${s})`}>
    <Glow x={40} y={-40} r={90} color={C.electricity} opacity={lit * 0.55} />
    <rect x={5} y={-60} width={70} height={60} fill={MID} />
    <path d="M-4,-58 L40,-96 L84,-58 Z" fill={LIGHT} />
    <rect x={16} y={-46} width={18} height={18} fill={lit > 0 ? C.electricity : DARK} opacity={0.25 + lit * 0.75} />
    <rect x={46} y={-46} width={18} height={18} fill={lit > 0 ? C.electricity : DARK} opacity={0.25 + lit * 0.75} />
    <rect x={30} y={-22} width={20} height={22} fill={DARK} />
  </g>
);

/** Transmission pylon. Base at (x, y); returns nothing fancy, just a lattice silhouette. */
export const Pylon: React.FC<{ x: number; y: number; h?: number }> = ({ x, y, h = 170 }) => (
  <g transform={`translate(${x},${y})`} stroke={C.steel} strokeWidth={3} fill="none">
    <path d={`M-28,0 L-6,${-h} L6,${-h} L28,0`} />
    <path d={`M-40,${-h * 0.72} L40,${-h * 0.72} M-30,${-h * 0.88} L30,${-h * 0.88}`} />
    <path d={`M-22,${-h * 0.2} L16,${-h * 0.45} M22,${-h * 0.2} L-16,${-h * 0.45} M-14,${-h * 0.5} L10,${-h * 0.68} M14,${-h * 0.5} L-10,${-h * 0.68}`} strokeWidth={2} />
  </g>
);

/** Old coal power plant with a smoking chimney; `smoke` 0–1. Base at (x, y). */
export const CoalPlant: React.FC<{ x: number; y: number; s?: number; frame: number; smoke?: number; opacity?: number }> = ({
  x,
  y,
  s = 1,
  frame,
  smoke = 1,
  opacity = 1,
}) => {
  const id = useUid();
  return (
    <g transform={`translate(${x},${y}) scale(${s})`} opacity={opacity}>
      <defs>
        <radialGradient id={`smoke${id}`}>
          <stop offset="0%" stopColor="#6B6F78" stopOpacity={0.7} />
          <stop offset="100%" stopColor="#6B6F78" stopOpacity={0} />
        </radialGradient>
      </defs>
      {[0, 1, 2, 3, 4].map((k) => {
        const t = ((frame * 0.8 + k * 30) % 150) / 150;
        return <circle key={k} cx={190 + t * 90} cy={-300 - t * 110} r={30 + t * 60} fill={`url(#smoke${id})`} opacity={smoke * (1 - t)} />;
      })}
      <path d="M175,0 L182,-300 L204,-300 L211,0 Z" fill={MID} />
      <rect x={176} y={-280} width={34} height={10} fill={C.accent} opacity={0.6} />
      <rect x={0} y={-150} width={170} height={150} fill={DARK} />
      <rect x={20} y={-200} width={90} height={50} fill={MID} />
      <path d="M220,0 L220,-90 L330,-90 L330,0 Z" fill={MID} />
    </g>
  );
};
