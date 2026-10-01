import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { House, Pylon } from "../components/Buildings";
import { KettleAnalogy } from "../components/Kettle";
import { Condenser, Generator, Pump, spinAngle, Turbine } from "../components/Machines";
import { Pipe } from "../components/Pipe";
import { Reactor, RV_ANCHORS, placeAnchor } from "../components/Reactor";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { FlowParticles } from "../components/svg";
import { Tag } from "../components/Tag";
import { enter, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { C } from "../theme";

const RX = { x: 110, y: 150, scale: 0.8 };
const STEAM_OUT = placeAnchor(RV_ANCHORS.steamOut, RX);
const FEED_IN = placeAnchor(RV_ANCHORS.feedIn, RX);
const TURBINE = { x: 800, y: 330, r: 105 };
const GEN = { x: 985, y: 258, w: 260, h: 144 };
const COND = { x: 640, y: 570, w: 320, h: 190 };
const PUMP = { x: 520, y: 720, r: 30 };

const STEAM_PATH = `M${STEAM_OUT.x - 10},${STEAM_OUT.y} L640,${STEAM_OUT.y} C690,${STEAM_OUT.y} 705,236 716,262`;
const EXHAUST_PATH = `M${TURBINE.x},${TURBINE.y + TURBINE.r} L${TURBINE.x},${COND.y + 8}`;
const FEED_PATH = `M${COND.x},${COND.y + 150} L${PUMP.x + 40},720 L${PUMP.x - 40},720 L470,720 Q430,720 430,680 L430,${FEED_IN.y + 30} Q430,${FEED_IN.y} 400,${FEED_IN.y} L${FEED_IN.x - 10},${FEED_IN.y}`;
const POWER_PATH = `M${GEN.x + GEN.w},${GEN.y + 40} L1330,${GEN.y + 40} L1400,236 L1555,345`;

export const Power: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cue = useCues();

  const boil = progress(frame, cue("boil"), cue("boil") + 45);
  const steam = progress(frame, cue("steam") - 6, cue("steam") + 14);
  const speed = (f: number) =>
    interpolate(f, [cue("turbine") - 4, cue("turbine") + 50], [0, 9], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.quad),
    });
  const angle = spinAngle(frame, speed);
  const blur = speed(frame) / 9;
  const genOn = progress(frame, cue("generator") + 4, cue("generator") + 18);
  const power = progress(frame, cue("electricity") - 2, cue("electricity") + 12);
  const kettle = enter(frame, cue("kettle") - 6, fps, 18) * (1 - progress(frame, cue("condense") - 14, cue("condense") - 2));
  const exhaust = progress(frame, cue("condense") - 8, cue("condense") + 10);
  const feed = progress(frame, cue("return") - 4, cue("return") + 16);

  return (
    <SceneShell schematic>
      <Sfx at={cue("turbine") - 4} name="hum" loop durationInFrames={durationInFrames - cue("turbine") + 4} />
      <Sfx at={cue("electricity") + 6} name="sparkle" />
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        {/* pipes first, so machines sit on top */}
        <Pipe d={STEAM_PATH} width={26} />
        <Pipe d={EXHAUST_PATH} width={30} />
        <Pipe d={FEED_PATH} width={22} />
        <line x1={TURBINE.x + TURBINE.r} y1={TURBINE.y} x2={GEN.x} y2={TURBINE.y} stroke={C.steel} strokeWidth={14} />

        <FlowParticles d={STEAM_PATH} frame={frame} count={16} speed={6} radius={(t) => 6 + t * 3} color={C.steam} opacity={steam * 0.9} />
        <FlowParticles d={EXHAUST_PATH} frame={frame} count={6} speed={3} radius={7} color={C.steam} opacity={exhaust * 0.7} />
        <FlowParticles d={FEED_PATH} frame={frame} count={22} speed={3.4} radius={6} color={C.water} opacity={feed} />

        <Reactor x={RX.x} y={RX.y} scale={RX.scale} frame={frame} boil={boil} downflow={0.35 + feed * 0.65} heat={0.75} hot={0.7} />
        <Turbine x={TURBINE.x} y={TURBINE.y} r={TURBINE.r} angle={angle} blur={blur} />
        <Generator x={GEN.x} y={GEN.y} w={GEN.w} h={GEN.h} angle={angle} on={genOn} />
        <Condenser x={COND.x} y={COND.y} w={COND.w} h={COND.h} frame={frame} active={Math.max(0.25, exhaust)} />
        <Pump x={PUMP.x} y={PUMP.y} r={PUMP.r} angle={frame * 12 * feed} />

        {/* grid + homes */}
        <path d={POWER_PATH} fill="none" stroke={C.steel} strokeWidth={3} opacity={0.8} />
        <FlowParticles d={POWER_PATH} frame={frame} count={12} speed={9} radius={6} color={C.electricity} opacity={power} edge={0.02} />
        <Pylon x={1400} y={430} h={194} />
        <line x1={1500} x2={1860} y1={430} y2={430} stroke={C.line} strokeWidth={3} />
        {[1530, 1630, 1730].map((hx, i) => (
          <House key={hx} x={hx} y={430} s={1.05} lit={progress(frame, cue("electricity") + 6 + i * 6, cue("electricity") + 20 + i * 6)} />
        ))}

        <KettleAnalogy x={1340} y={500} frame={frame} t={kettle} />
      </svg>

      <Tag x={RX.x + 104} y={118} text="Reaktor" t={enter(frame, 6, fps, 16)} color={C.heat} anchor="center" />
      <Tag x={420} y={118} text="BWR = reaktor z wrzącą wodą" t={enter(frame, cue("name") - 6, fps, 16)} color={C.steam} size={28} />
      <Tag x={520} y={172} text="para" t={steam} color={C.steam} anchor="center" size={28} />
      <Tag x={TURBINE.x + 30} y={196} text="turbina" t={enter(frame, cue("turbine") - 4, fps, 14)} color={C.steel} size={28} />
      <Tag x={GEN.x + GEN.w / 2} y={GEN.y + GEN.h + 34} text="generator" t={enter(frame, cue("generator") - 4, fps, 14)} color={C.electricity} anchor="center" size={28} />
      <Tag x={1640} y={466} text="prąd do domów" t={power} color={C.electricity} anchor="center" size={28} />
      <Tag x={COND.x + COND.w + 24} y={COND.y + 60} text="skraplacz" sub="para → woda" t={enter(frame, cue("condense") - 6, fps, 14)} color={C.water} size={28} />
      <Tag x={446} y={560} text="woda wraca" t={feed} color={C.water} size={26} />
      <Tag x={1590} y={530} text="Jak para z czajnika…" t={kettle} color={C.heat} anchor="center" size={28} />
    </SceneShell>
  );
};
