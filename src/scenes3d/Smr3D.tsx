import { useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate, useAnchor } from "../components/BrickPlate";
import { SceneShell } from "../components/SceneShell";
import { SmrLetters } from "../components/SmrLetters";
import { Sfx } from "../components/Sound";
import { Tag } from "../components/Tag";
import { enter, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { C } from "../theme";

/** Small SMR vs a big plant; modules ride from the factory and click into place on "klocków". */
export const Smr3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const big = useAnchor("smr", "big_plant", { x: 780, y: 400 });
  const smr = useAnchor("smr", "smr_plant", { x: 1160, y: 565 });
  const fac = useAnchor("smr", "factory", { x: 1440, y: 290 });
  const bigT = enter(frame, cue("big") + 10, fps, 16) * (1 - progress(frame, cue("modules") - 40, cue("modules") - 20));
  const smrT = enter(frame, cue("compare") + 30, fps, 16) * (1 - progress(frame, cue("modules") - 40, cue("modules") - 20));
  const facT = enter(frame, cue("factory") - 4, fps, 14);

  return (
    <SceneShell background={<BrickPlate shot="smr" />}>
      <Sfx at={cue("compare") + 8} name="clatter" />
      <Sfx at={178} name="clatter" gain={0.6} />
      {[257, 269, cue("bricks")].map((f) => (
        <Sfx key={f} at={f} name="click" />
      ))}
      <SmrLetters topFrom={170} topTo={110} />
      <Tag x={big.x} y={big.y} anchor="center" text="Duży blok jądrowy" sub="ponad 1000 MW" t={bigT * (big.visible ? 1 : 0)} color={C.steel} />
      <Tag x={smr.x} y={smr.y - 70} anchor="center" text="SMR" sub="ok. 300 MW · kilka razy mniejszy" t={smrT * (smr.visible ? 1 : 0)} color={C.uranium} />
      <Tag x={fac.x} y={fac.y - 40} anchor="center" text="Fabryka" sub="gotowe moduły" t={facT * (fac.visible ? 1 : 0)} color={C.steam} />
    </SceneShell>
  );
};
