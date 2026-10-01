import { useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate, useAnchor } from "../components/BrickPlate";
import { KettleAnalogy } from "../components/Kettle";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { Tag } from "../components/Tag";
import { enter, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { C } from "../theme";

/** The whole BWR loop as one brick diorama; labels ride on the 3D anchors. */
export const Power3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cue = useCues();
  const a = {
    reactor: useAnchor("power", "reactor", { x: 300, y: 500 }),
    steam: useAnchor("power", "steam_pipe", { x: 560, y: 220 }),
    turbine: useAnchor("power", "turbine", { x: 860, y: 260 }),
    generator: useAnchor("power", "generator", { x: 1120, y: 260 }),
    houses: useAnchor("power", "houses", { x: 1500, y: 360 }),
    condenser: useAnchor("power", "condenser", { x: 820, y: 600 }),
    ret: useAnchor("power", "return_pipe", { x: 560, y: 560 }),
  };
  const v = (p: { visible: boolean }) => (p.visible ? 1 : 0);
  const kettle = enter(frame, cue("kettle") - 6, fps, 18) * (1 - progress(frame, cue("condense") - 14, cue("condense") - 2));
  const until = (to: number) => 1 - progress(frame, to - 8, to + 4);

  return (
    <SceneShell schematic background={<BrickPlate shot="power" />}>
      <Sfx at={cue("turbine") - 4} name="hum" loop durationInFrames={durationInFrames - cue("turbine") + 4} />
      <Sfx at={cue("electricity") + 16} name="sparkle" />
      <Tag x={a.reactor.x - 24} y={a.reactor.y} anchor="right" text="Reaktor" sub="BWR — z wrzącą wodą" t={enter(frame, cue("name") - 6, fps, 16) * v(a.reactor) * until(cue("kettle"))} color={C.heat} />
      <Tag x={a.steam.x} y={a.steam.y - 34} anchor="center" text="para" t={enter(frame, cue("steam"), fps, 14) * v(a.steam) * until(cue("kettle"))} color={C.steam} size={28} />
      <Tag x={a.turbine.x} y={a.turbine.y - 34} anchor="center" text="turbina" t={enter(frame, cue("turbine"), fps, 14) * v(a.turbine)} color={C.steel} size={28} />
      <Tag x={a.generator.x} y={a.generator.y - 34} anchor="center" text="generator" t={enter(frame, cue("generator"), fps, 14) * v(a.generator)} color={C.electricity} size={28} />
      <Tag x={a.houses.x} y={a.houses.y - 40} anchor="center" text="prąd do domów" t={enter(frame, cue("electricity") + 10, fps, 14) * v(a.houses) * until(cue("kettle"))} color={C.electricity} size={28} />
      <Tag x={a.condenser.x} y={a.condenser.y} anchor="center" text="skraplacz" sub="para → woda" t={enter(frame, cue("condense") - 4, fps, 14) * v(a.condenser)} color={C.water} size={28} />
      <Tag x={a.ret.x - 24} y={a.ret.y} anchor="right" text="woda wraca" t={enter(frame, cue("return"), fps, 14) * v(a.ret)} color={C.water} size={28} />
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <KettleAnalogy x={1340} y={500} frame={frame} t={kettle} />
      </svg>
      <Tag x={1590} y={530} text="Jak para z czajnika…" t={kettle} color={C.heat} anchor="center" size={28} />
    </SceneShell>
  );
};
