import { useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate, useAnchor } from "../components/BrickPlate";
import { PowerChart } from "../components/PowerChart";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { Tag } from "../components/Tag";
import { enter, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { C } from "../theme";

/** Too many neutrons → rods rise from below and swallow them → steady 1→1 chain. */
export const Control3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const fuel = useAnchor("control", "fuel", { x: 440, y: 300 });
  const rods = useAnchor("control", "rods", { x: 900, y: 770 });
  const chain = useAnchor("control", "chain", { x: 900, y: 450 });
  const v = (p: { visible: boolean }) => (p.visible ? 1 : 0);

  return (
    <SceneShell schematic background={<BrickPlate shot="control" />}>
      <Sfx at={cue("rods") + 4} name="clunk" gain={0.7} />
      <Sfx at={123} name="clunk" />
      <Tag x={fuel.x} y={fuel.y - 40} anchor="center" text="paliwo (uran)" t={enter(frame, 8, fps, 16) * (1 - progress(frame, cue("rods") - 6, cue("rods") + 6)) * v(fuel)} color={C.uranium} size={26} />
      <Tag x={rods.x} y={rods.y - 20} anchor="center" text="pręty sterujące — wsuwane od dołu" t={enter(frame, cue("rods"), fps, 16) * v(rods)} color={C.rods} size={30} />
      <Tag x={chain.x} y={chain.y - 90} anchor="center" text="1 rozszczepienie → dokładnie 1 kolejne" t={enter(frame, cue("exactlyOne") - 4, fps, 16) * v(chain)} color={C.neutron} size={30} />
      <PowerChart />
    </SceneShell>
  );
};
