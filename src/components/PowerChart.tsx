import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { enter, lerp } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C } from "../theme";
import { Tag } from "./Tag";

/** Reactor power over the control scene: grows with excess neutrons, falls as rods go in, then flat. */
export const PowerChart: React.FC<{ x0?: number; x1?: number; y0?: number; y1?: number }> = ({ x0 = 1430, x1 = 1810, y0 = 560, y1 = 300 }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cue = useCues();
  const steadyStart = cue("fromBelow") + 30;
  const power = (f: number) => {
    if (f < cue("rods")) return 0.35 + 0.55 * Math.pow(f / cue("rods"), 2);
    return interpolate(f, [cue("rods"), steadyStart], [0.9, 0.55], { extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  };
  const pts = Array.from({ length: Math.max(2, frame + 1) }, (_, f) =>
    `${lerp(x0, x1, f / durationInFrames).toFixed(1)},${lerp(y0, y1, power(f)).toFixed(1)}`,
  ).join(" ");
  const cx = (x0 + x1) / 2;
  return (
    <>
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <g opacity={enter(frame, 6, fps, 18)}>
          <rect x={x0 - 30} y={y1 - 70} width={x1 - x0 + 60} height={y0 - y1 + 110} rx={18} fill={C.panel} stroke={C.panelEdge} />
          <line x1={x0} y1={y0} x2={x1} y2={y0} stroke={C.line} strokeWidth={2} />
          <line x1={x0} y1={y0} x2={x0} y2={y1 - 10} stroke={C.line} strokeWidth={2} />
          <polyline points={pts} fill="none" stroke={C.heat} strokeWidth={5} strokeLinejoin="round" strokeLinecap="round" />
          <text x={x0} y={y1 - 34} fill={C.muted} fontFamily={BODY} fontSize={22} fontWeight={700}>
            moc reaktora
          </text>
        </g>
      </svg>
      <Tag x={cx} y={y0 + 46} text="stabilnie" t={enter(frame, cue("stable") - 4, fps, 16)} color={C.heat} anchor="center" size={30} />
      <Tag x={cx} y={y0 + 46} text="za dużo neutronów" t={enter(frame, cue("excess"), fps, 12) * (1 - enter(frame, cue("fromBelow"), fps, 12))} color={C.neutron} anchor="center" size={26} />
    </>
  );
};
