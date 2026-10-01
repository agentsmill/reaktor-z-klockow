import { interpolateColors } from "remotion";
import { C } from "../theme";
import { FlowParticles, Glow, useUid } from "./svg";

// Local geometry of a stylised BWRX-300 pressure vessel (real proportions are ~1:6.5;
// widened here for readability — scenes carry the "Schemat uproszczony" tag).
export const RV = {
  W: 260,
  H: 760,
  wall: 12,
  headRy: 70,
  waterLine: 205,
  chimney: { x0: 62, x1: 198, y0: 228, y1: 532 },
  core: { x0: 48, x1: 212, y0: 540, y1: 672 },
  bundles: [52, 72, 92, 112, 132, 152, 172, 192],
  bundleW: 15,
  fuelTop: 548,
  fuelBottom: 664,
  steamNozzleY: 72,
  feedNozzleY: 256,
} as const;

/** Anchor points in local coordinates (multiply by scale and add x/y to place labels). */
export const RV_ANCHORS = {
  dome: { x: 130, y: 72 },
  separators: { x: 130, y: 190 },
  chimney: { x: 130, y: 380 },
  downcomerL: { x: 37, y: 380 },
  downcomerR: { x: 223, y: 380 },
  core: { x: 130, y: 606 },
  rods: { x: 130, y: 760 },
  steamOut: { x: RV.W + 44, y: RV.steamNozzleY },
  feedIn: { x: RV.W + 44, y: RV.feedNozzleY },
} as const;

export const placeAnchor = (
  a: { x: number; y: number },
  at: { x: number; y: number; scale?: number },
): { x: number; y: number } => ({ x: at.x + a.x * (at.scale ?? 1), y: at.y + a.y * (at.scale ?? 1) });

const capsule = (x0: number, y0: number, x1: number, y1: number, ry: number) => {
  const rx = (x1 - x0) / 2;
  return `M${x0},${y0 + ry} A${rx},${ry} 0 0 1 ${x1},${y0 + ry} L${x1},${y1 - ry} A${rx},${ry} 0 0 1 ${x0},${y1 - ry} Z`;
};

export type ReactorProps = {
  x: number;
  y: number;
  scale?: number;
  frame: number;
  /** Opacity of the water fill. */
  water?: number;
  /** Bubbly upflow through core + chimney (0–1). */
  boil?: number;
  /** Cooler water going down the sides (0–1). */
  downflow?: number;
  /** Control blade insertion into the core (0 = out, 1 = fully in). */
  rods?: number;
  /** Core glow (0–1). */
  heat?: number;
  /** Fission glow colour mix: 0 = green fuel, 1 = hot orange. */
  hot?: number;
  /** Dims everything except one region. */
  focus?: "chimney" | "core" | null;
};

export const Reactor: React.FC<ReactorProps> = ({
  x,
  y,
  scale = 1,
  frame,
  water = 1,
  boil = 0,
  downflow = 0,
  rods = 0,
  heat = 0,
  hot = 0.6,
  focus = null,
}) => {
  const id = useUid();
  const { W, H, wall, headRy, waterLine, chimney: ch, core } = RV;
  const inner = capsule(wall, wall, W - wall, H - wall, headRy - wall * 0.6);
  const fuelColor = interpolateColors(hot, [0, 1], [C.uranium, "#FFB066"]);
  const rodTop = RV.fuelBottom - rods * (RV.fuelBottom - RV.fuelTop + 6);
  const dimOutside = focus ? 0.35 : 1;

  // Flow paths (local coordinates).
  const downL = `M37,${ch.y0 + 14} L37,700 Q37,724 70,724 L104,724`;
  const downR = `M223,${ch.y0 + 14} L223,700 Q223,724 190,724 L156,724`;
  const ups = [86, 112, 130, 148, 174].map((cx) => `M${cx},${core.y1 + 30} L${cx},${ch.y0 - 6}`);

  return (
    <g transform={`translate(${x},${y}) scale(${scale})`}>
      <defs>
        <linearGradient id={`steel${id}`} x1="0" x2="1">
          <stop offset="0%" stopColor="#56657E" />
          <stop offset="18%" stopColor="#B4C0D2" />
          <stop offset="45%" stopColor="#7C8BA3" />
          <stop offset="100%" stopColor="#3B4A63" />
        </linearGradient>
        <linearGradient id={`water${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={C.water} stopOpacity={0.42} />
          <stop offset="100%" stopColor={C.waterDeep} stopOpacity={0.7} />
        </linearGradient>
        <clipPath id={`in${id}`}>
          <path d={inner} />
        </clipPath>
      </defs>

      {/* control rod drives under the vessel */}
      <g opacity={dimOutside}>
        {RV.bundles.slice(0, -1).map((bx, i) => (
          <g key={i}>
            <line x1={bx + 17.5} y1={H - 14} x2={bx + 17.5} y2={H + 58} stroke={C.steelDark} strokeWidth={5} />
            <rect x={bx + 12} y={H + 52} width={11} height={20} rx={2} fill={C.steelDark} />
          </g>
        ))}
      </g>

      {/* vessel wall */}
      <path d={capsule(0, 0, W, H, headRy)} fill={`url(#steel${id})`} />
      <path d={inner} fill="#0A1322" />

      <g clipPath={`url(#in${id})`}>
        {/* steam dome + water */}
        <rect x={0} y={0} width={W} height={waterLine} fill={C.steam} opacity={0.1 * water} />
        <rect x={0} y={waterLine} width={W} height={H - waterLine} fill={`url(#water${id})`} opacity={water} />
        <line x1={0} y1={waterLine} x2={W} y2={waterLine} stroke="#9CC2FF" strokeWidth={2} opacity={0.6 * water} />

        {/* two-phase mixture inside the chimney */}
        <rect
          x={ch.x0}
          y={ch.y0}
          width={ch.x1 - ch.x0}
          height={core.y1 - ch.y0}
          fill={C.steam}
          opacity={0.1 + 0.12 * boil}
        />

        {/* core glow */}
        <Glow x={130} y={(core.y0 + core.y1) / 2} r={150} color={C.heat} opacity={heat} />

        {/* downflow (cooler water) */}
        <FlowParticles d={downL} frame={frame} count={14} speed={2.2} radius={5} color={C.water} opacity={downflow} />
        <FlowParticles d={downR} frame={frame + 9} count={14} speed={2.2} radius={5} color={C.water} opacity={downflow} />

        {/* bubbly upflow: bubbles grow as pressure drops on the way up */}
        {ups.map((d, i) => (
          <FlowParticles
            key={i}
            d={d}
            frame={frame + i * 7}
            count={9}
            speed={3 + (i % 2) * 0.6}
            radius={(t) => 2.5 + t * 6}
            color={C.steam}
            opacity={boil * 0.85}
          />
        ))}
      </g>

      {/* internals */}
      <g opacity={focus === "core" ? 0.35 : 1}>
        {/* dryer */}
        <rect x={52} y={104} width={156} height={30} rx={4} fill="none" stroke={C.steel} strokeWidth={2} opacity={0.8} />
        {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
          <line key={i} x1={60 + i * 20} y1={106} x2={70 + i * 20} y2={132} stroke={C.steel} strokeWidth={2} opacity={0.6} />
        ))}
        {/* steam separators */}
        {[80, 105, 130, 155, 180].map((sx) => (
          <rect key={sx} x={sx - 7} y={162} width={14} height={ch.y0 - 160} rx={4} fill="#22314A" stroke={C.steel} strokeWidth={2} />
        ))}
      </g>
      {/* chimney walls */}
      <g opacity={focus === "core" ? 0.35 : 1}>
        <line x1={ch.x0} y1={ch.y0} x2={ch.x0} y2={ch.y1} stroke={C.steel} strokeWidth={4} />
        <line x1={ch.x1} y1={ch.y0} x2={ch.x1} y2={ch.y1} stroke={C.steel} strokeWidth={4} />
        <line x1={ch.x0 - 8} y1={ch.y0} x2={ch.x1 + 8} y2={ch.y0} stroke={C.steel} strokeWidth={4} />
      </g>

      {/* core: fuel bundles + control blades rising from below */}
      <g opacity={focus === "chimney" ? 0.45 : 1}>
        <rect x={core.x0} y={core.y0} width={core.x1 - core.x0} height={core.y1 - core.y0} rx={6} fill="none" stroke={C.steel} strokeWidth={3} />
        {RV.bundles.map((bx) => (
          <rect key={bx} x={bx} y={RV.fuelTop} width={RV.bundleW} height={RV.fuelBottom - RV.fuelTop} rx={3} fill={fuelColor} opacity={0.9} />
        ))}
        {RV.bundles.slice(0, -1).map((bx, i) => (
          <rect key={i} x={bx + RV.bundleW + 0.5} y={rodTop} width={4} height={H + 60 - rodTop} fill={C.rods} />
        ))}
      </g>

      {/* nozzles */}
      <rect x={W - 6} y={RV.steamNozzleY - 14} width={50} height={28} rx={4} fill={`url(#steel${id})`} />
      <rect x={W - 6} y={RV.feedNozzleY - 10} width={50} height={20} rx={4} fill={`url(#steel${id})`} />
    </g>
  );
};
