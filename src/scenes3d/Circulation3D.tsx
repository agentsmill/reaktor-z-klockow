import { useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate, useAnchor } from "../components/BrickPlate";
import { Pump } from "../components/Machines";
import { SceneShell } from "../components/SceneShell";
import { Tag } from "../components/Tag";
import { enter, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { RadiatorAnalogy } from "../scenes/Circulation";
import { C } from "../theme";

/** Natural circulation inside the brick vessel: hot mixture rises, cooler water sinks — no pumps. */
export const Circulation3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const chimney = useAnchor("circulation", "chimney", { x: 760, y: 420 });
  const down = useAnchor("circulation", "downcomer_l", { x: 640, y: 560 });
  const pumpT = enter(frame, cue("noPumps") - 8, fps, 16);
  const crossT = progress(frame, cue("noPumps") + 2, cue("noPumps") + 14);
  const radiator = enter(frame, cue("radiator") - 10, fps, 18);
  const v = (p: { visible: boolean }) => (p.visible ? 1 : 0);

  return (
    <SceneShell schematic background={<BrickPlate shot="circulation" />}>
      <Tag x={960} y={120} anchor="center" text="Wnętrze reaktora" t={enter(frame, cue("inside") - 6, fps, 14) * (1 - progress(frame, cue("hot") - 10, cue("hot")))} color={C.water} />
      <Tag x={chimney.x + 230} y={chimney.y - 60} text="gorąca woda z parą" sub="lżejsza — unosi się" t={enter(frame, cue("hot") - 4, fps, 14) * v(chimney)} color={C.heat} size={28} />
      <Tag x={chimney.x + 230} y={chimney.y + 40} text="wysoki komin" t={enter(frame, cue("chimney") - 4, fps, 14) * v(chimney)} color={C.steam} size={28} />
      <Tag x={down.x - 40} y={down.y} anchor="right" text="chłodniejsza woda" sub="cięższa — opada" t={enter(frame, cue("sink") - 8, fps, 14) * v(down)} color={C.water} size={28} />
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <g opacity={pumpT}>
          <Pump x={1530} y={190} r={56} angle={frame * 6 * (1 - crossT)} crossed={crossT} />
        </g>
        <RadiatorAnalogy x={1260} y={360} frame={frame} t={radiator} />
      </svg>
      <Tag x={1530} y={285} text="bez pomp obiegowych" t={pumpT} color={C.accent} anchor="center" size={28} />
      <Tag x={1530} y={800} text="jak powietrze nad kaloryferem" t={radiator} color={C.heat} anchor="center" size={28} />
    </SceneShell>
  );
};
