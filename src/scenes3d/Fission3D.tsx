import { useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate, useAnchor } from "../components/BrickPlate";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { Tag } from "../components/Tag";
import { enter, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { Title } from "../scenes/Fission";
import { BODY, C } from "../theme";

/** Pellet → nucleus → neutron hit → split (Ba-141 + Kr-92) → heat → new neutrons → chain → pellet vs coal. */
export const Fission3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const shot = "fission" as const;
  const a = {
    pellet: useAnchor(shot, "pellet", { x: 560, y: 600 }),
    nucleus: useAnchor(shot, "nucleus", { x: 960, y: 320 }),
    neutron: useAnchor(shot, "neutron", { x: 500, y: 450 }),
    fragments: useAnchor(shot, "fragments", { x: 960, y: 450 }),
    big: useAnchor(shot, "fragment_big", { x: 700, y: 420 }),
    small: useAnchor(shot, "fragment_small", { x: 1220, y: 480 }),
    heat: useAnchor(shot, "heat", { x: 960, y: 450 }),
    coal: useAnchor(shot, "coal", { x: 1296, y: 275 }),
  };
  const v = (p: { visible: boolean }) => (p.visible ? 1 : 0);
  const span = (from: number, to: number) => Math.min(progress(frame, from - 6, from + 6), 1 - progress(frame, to - 6, to + 6));

  return (
    <SceneShell background={<BrickPlate shot="fission" />}>
      <Sfx at={25} name="click" />
      <Sfx at={cue("split")} name="pop" />
      <Sfx at={cue("heat") - 2} name="pop" gain={0.6} />
      <Sfx at={cue("chain") - 12} name="whoosh" gain={0.8} />
      {[0, 25, 50, 74].map((d) => (
        <Sfx key={d} at={cue("chain") + d} name="pop" gain={0.35} />
      ))}
      <Sfx at={cue("coal") - 12} name="clatter" />

      <Tag x={a.pellet.x} y={a.pellet.y - 50} anchor="center" text="pastylka paliwa (UO₂)" sub="ok. 1 cm" t={span(cue("pellet"), 68) * v(a.pellet)} color={C.uranium} />
      <Tag x={a.nucleus.x} y={a.nucleus.y - 30} anchor="center" text="jądro uranu-235" t={span(76, cue("hit") + 6) * v(a.nucleus)} color={C.uranium} />
      <Tag x={a.neutron.x} y={a.neutron.y - 44} anchor="center" text="neutron" t={span(cue("neutron"), cue("hit")) * v(a.neutron)} color={C.neutron} size={28} />
      <Tag x={a.fragments.x} y={a.fragments.y + 150} anchor="center" text="dwa mniejsze jądra" t={span(cue("split") + 22, cue("fission"))} color={C.uranium} />
      <Tag x={a.big.x} y={a.big.y + 250} anchor="center" text="bar" sub="Ba-141" t={span(cue("fission") + 6, cue("heat") - 4) * v(a.big)} color={C.uranium} size={28} />
      <Tag x={a.small.x} y={a.small.y + 190} anchor="center" text="krypton" sub="Kr-92" t={span(cue("fission") + 10, cue("heat") - 4) * v(a.small)} color={C.uranium} size={28} />
      <Tag x={a.heat.x} y={a.heat.y + 170} anchor="center" text="ciepło" t={span(cue("heat"), cue("newNeutrons") - 4)} color={C.heat} size={38} />
      <Tag x={a.fragments.x} y={a.fragments.y + 170} anchor="center" text="2–3 nowe neutrony" t={span(cue("newNeutrons"), cue("chain") - 6)} color={C.neutron} size={34} />

      <Title text="ROZSZCZEPIENIE" t={span(cue("fission") - 4, cue("heat") - 8)} />
      <Title text="REAKCJA ŁAŃCUCHOWA" t={span(cue("chainLabel") - 4, cue("onePellet") - 12)} color={C.neutron} />

      <Tag x={a.pellet.x} y={a.pellet.y + 80} anchor="center" text="1 pastylka" sub="uranu" t={enter(frame, cue("onePellet") + 30, fps, 16) * v(a.pellet)} color={C.uranium} size={34} />
      <Tag x={a.coal.x} y={a.coal.y - 50} anchor="center" text="≈ 1 tona węgla" t={enter(frame, cue("coal") + 18, fps, 16) * v(a.coal)} color={C.steel} size={34} />
      <div style={{ position: "absolute", right: 80, top: 800, fontFamily: BODY, fontSize: 18, fontWeight: 600, color: C.faint, opacity: enter(frame, cue("coal") + 30, fps, 16) }}>
        źródło: World Nuclear Association
      </div>
    </SceneShell>
  );
};
