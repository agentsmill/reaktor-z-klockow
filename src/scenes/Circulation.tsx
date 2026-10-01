import { useCurrentFrame, useVideoConfig } from "remotion";
import { Pump } from "../components/Machines";
import { Reactor, RV, RV_ANCHORS, placeAnchor } from "../components/Reactor";
import { SceneShell } from "../components/SceneShell";
import { ArrowHead, Glow } from "../components/svg";
import { Tag } from "../components/Tag";
import { enter, lerp, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { C } from "../theme";

const RX = { x: 560, y: 110, scale: 0.92 };
const at = (a: { x: number; y: number }) => placeAnchor(a, RX);
const CHIMNEY_X = at(RV_ANCHORS.chimney).x;
const DOWN_L = at(RV_ANCHORS.downcomerL).x;
const DOWN_R = at(RV_ANCHORS.downcomerR).x;
const TOP = RX.y + (RV.chimney.y0 + 20) * RX.scale;
const BOTTOM = RX.y + (RV.core.y1 - 10) * RX.scale;

/** Column of chevrons scrolling up (dir −1) or down (dir 1). */
const Chevrons: React.FC<{ x: number; y0: number; y1: number; dir: 1 | -1; frame: number; color: string; t: number }> = ({
  x,
  y0,
  y1,
  dir,
  frame,
  color,
  t,
}) => {
  if (t <= 0) return null;
  const gap = 70;
  const n = Math.floor((y1 - y0) / gap);
  return (
    <g opacity={t}>
      {Array.from({ length: n }, (_, i) => {
        const offset = (((frame * 1.6 + i * gap) % (n * gap)) + n * gap) % (n * gap);
        const y = dir === 1 ? y0 + offset : y1 - offset;
        const edge = Math.min(1, (y - y0) / 50, (y1 - y) / 50);
        return (
          <path
            key={i}
            d={`M${x - 16},${y - dir * 9} L${x},${y + dir * 7} L${x + 16},${y - dir * 9}`}
            fill="none"
            stroke={color}
            strokeWidth={6}
            strokeLinecap="round"
            strokeLinejoin="round"
            opacity={Math.max(0, edge)}
          />
        );
      })}
    </g>
  );
};

/** Room with a radiator: warm air rises, cool air sinks — the same loop as inside the reactor. */
export const RadiatorAnalogy: React.FC<{ x: number; y: number; frame: number; t: number }> = ({ x, y, frame, t }) => {
  if (t <= 0) return null;
  const loop = `M${x + 120},${y + 300} L${x + 120},${y + 90} Q${x + 120},${y + 60} ${x + 150},${y + 60} L${x + 420},${y + 60} Q${x + 450},${y + 60} ${x + 450},${y + 90} L${x + 450},${y + 300} Q${x + 450},${y + 330} ${x + 420},${y + 330} L${x + 150},${y + 330} Q${x + 120},${y + 330} ${x + 120},${y + 300}`;
  return (
    <g opacity={t}>
      <rect x={x} y={y} width={540} height={400} rx={26} fill={C.panel} stroke={C.panelEdge} strokeWidth={2} />
      {/* radiator fins */}
      <Glow x={x + 120} y={y + 330} r={110} color={C.heat} opacity={0.6} />
      {Array.from({ length: 6 }, (_, i) => (
        <rect key={i} x={x + 70 + i * 18} y={y + 300} width={12} height={70} rx={5} fill="#C9D3E2" />
      ))}
      <rect x={x + 64} y={y + 296} width={114} height={8} rx={4} fill="#9AA7BB" />
      {/* air loop: warm up (orange), cool down (blue) */}
      <path d={loop} fill="none" stroke={C.line} strokeWidth={3} strokeDasharray="10 12" strokeDashoffset={frame * 2} opacity={0.6} />
      <Chevrons x={x + 120} y0={y + 90} y1={y + 280} dir={-1} frame={frame} color={C.heat} t={1} />
      <Chevrons x={x + 450} y0={y + 90} y1={y + 300} dir={1} frame={frame} color={C.water} t={1} />
      <ArrowHead x={x + 290} y={y + 60} dx={1} dy={0} size={18} color={C.muted} />
      <ArrowHead x={x + 290} y={y + 330} dx={-1} dy={0} size={18} color={C.muted} />
    </g>
  );
};

export const Circulation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();

  const boil = lerp(0.35, 1, progress(frame, cue("hot") - 10, cue("hot") + 30));
  const down = lerp(0.3, 1, progress(frame, cue("sink") - 10, cue("sink") + 20));
  const up = progress(frame, cue("rise") - 8, cue("rise") + 14);
  const sinkT = progress(frame, cue("sink") - 8, cue("sink") + 14);
  const pumpT = enter(frame, cue("noPumps") - 8, fps, 16);
  const crossT = progress(frame, cue("noPumps") + 2, cue("noPumps") + 14);
  const radiator = enter(frame, cue("radiator") - 10, fps, 18);
  const hotTint = progress(frame, cue("hot") - 6, cue("hot") + 20);

  return (
    <SceneShell schematic>
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <Reactor x={RX.x} y={RX.y} scale={RX.scale} frame={frame} boil={boil} downflow={down} heat={0.65} hot={0.7} />
        {/* warm tint in the chimney (orange = heat) */}
        <rect
          x={RX.x + RV.chimney.x0 * RX.scale}
          y={RX.y + RV.chimney.y0 * RX.scale}
          width={(RV.chimney.x1 - RV.chimney.x0) * RX.scale}
          height={(RV.core.y1 - RV.chimney.y0) * RX.scale}
          fill={C.heat}
          opacity={0.12 * hotTint}
        />
        <Chevrons x={CHIMNEY_X} y0={TOP} y1={BOTTOM} dir={-1} frame={frame} color={C.steam} t={up} />
        <Chevrons x={DOWN_L} y0={TOP} y1={BOTTOM} dir={1} frame={frame} color="#7FB2FF" t={sinkT} />
        <Chevrons x={DOWN_R} y0={TOP} y1={BOTTOM} dir={1} frame={frame} color="#7FB2FF" t={sinkT} />

        <g opacity={pumpT}>
          <Pump x={1530} y={190} r={56} angle={frame * 6 * (1 - crossT)} crossed={crossT} />
        </g>
        <RadiatorAnalogy x={1260} y={360} frame={frame} t={radiator} />
      </svg>

      <Tag x={RX.x + 120} y={84} text="Wnętrze reaktora" t={enter(frame, cue("inside") - 6, fps, 14)} color={C.water} anchor="center" />
      <Tag x={1530} y={285} text="bez pomp obiegowych" t={pumpT} color={C.accent} anchor="center" size={28} />
      <Tag x={RX.x + 290} y={300} text="gorąca woda z parą" sub="lżejsza — unosi się" t={enter(frame, cue("hot") - 4, fps, 14)} color={C.heat} size={28} />
      <Tag x={RX.x + 290} y={450} text="wysoki komin" t={enter(frame, cue("chimney") - 4, fps, 14)} color={C.steam} size={28} />
      <Tag x={RX.x - 30} y={560} text="chłodniejsza woda" sub="cięższa — opada" t={sinkT} color={C.water} anchor="right" size={28} />
      <Tag x={1530} y={800} text="jak powietrze nad kaloryferem" t={radiator} color={C.heat} anchor="center" size={28} />
    </SceneShell>
  );
};
