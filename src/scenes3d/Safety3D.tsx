import { useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate, useAnchor } from "../components/BrickPlate";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { Tag } from "../components/Tag";
import { enter, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { PassiveSafetyPanel } from "../scenes/Safety";
import { BODY, C } from "../theme";

/** Visible from `from` to `to` (scene frames) with short fades. */
const during = (frame: number, from: number, to: number) =>
  Math.min(progress(frame, from - 6, from + 6), 1 - progress(frame, to - 6, to + 6));

const Status: React.FC<{ text: string; sub?: string; t: number; color: string }> = ({ text, sub, t, color }) =>
  t <= 0 ? null : (
    <div style={{ position: "absolute", top: 120, left: 0, right: 0, textAlign: "center", fontFamily: BODY, ...riseStyle(t, 12) }}>
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 14,
          padding: "12px 26px",
          borderRadius: 999,
          background: "rgba(6, 12, 23, 0.72)",
          border: `1px solid ${C.panelEdge}`,
          fontSize: 34,
          fontWeight: 800,
          color: C.text,
        }}
      >
        <span style={{ width: 14, height: 14, borderRadius: 999, background: color }} />
        {text}
        {sub && <span style={{ fontSize: 24, fontWeight: 600, color: C.muted }}>· {sub}</span>}
      </span>
    </div>
  );

/** Blackout → rods in → decay heat → isolation condensers in the pool → 7 days → 35 m underground. */
export const Safety3D: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCues();
  const { fps } = useVideoConfig();
  const houses = useAnchor("safety", "houses", { x: 1500, y: 260 });
  const coil = useAnchor("safety", "coil", { x: 960, y: 240 });
  const pool = useAnchor("safety", "pool", { x: 960, y: 300 });
  const steam = useAnchor("safety", "steam_line", { x: 1240, y: 520 });
  const ret = useAnchor("safety", "return_line", { x: 640, y: 520 });
  const bottom = useAnchor("safety", "shaft_bottom", { x: 960, y: 760 });
  const vis = (a: { visible: boolean }) => (a.visible ? 1 : 0);

  return (
    <SceneShell schematic background={<BrickPlate shot="safety" />}>
      <Sfx at={cue("blackout") - 2} name="powerdown" />
      <Sfx at={111} name="clunk" />
      <Tag x={houses.x} y={houses.y - 50} anchor="center" text="brak zasilania z sieci" t={during(frame, cue("blackout") + 4, 60) * vis(houses)} color={C.accent} size={26} />

      <Status text="Pręty wsuwają się automatycznie" t={during(frame, cue("rodsIn"), cue("off"))} color={C.rods} />
      <Status text="Reakcja gaśnie" t={during(frame, cue("off"), cue("decay"))} color={C.neutron} />
      <Status text="Paliwo nadal trochę grzeje" sub="ciepło powyłączeniowe" t={during(frame, cue("decay"), cue("ic") - 8)} color={C.heat} />

      <Tag x={coil.x} y={coil.y - 80} anchor="center" text="skraplacz" t={during(frame, cue("ic"), cue("rise") - 10) * vis(coil)} color={C.steam} size={28} />
      {/* outside the building's right wall, so it never collides with the condenser label */}
      <Tag x={coil.x + 250} y={coil.y - 20} text="basen z wodą" sub="nad reaktorem" t={during(frame, cue("pools"), cue("rise") - 10) * vis(pool)} color={C.water} size={28} />
      <Tag x={steam.x + 34} y={steam.y} text="para w górę" t={during(frame, cue("rise"), cue("noPower")) * vis(steam)} color={C.steam} size={28} />
      <Tag x={ret.x - 34} y={ret.y} anchor="right" text="woda w dół" sub="grawitacja, bez pomp" t={during(frame, cue("back"), cue("days")) * vis(ret)} color={C.water} size={28} />

      {frame >= cue("noPower") - 10 && frame < cue("underground") - 10 && <PassiveSafetyPanel left={1240} top={420} />}

      <Tag x={bottom.x} y={bottom.y - 90} anchor="center" text="ok. 35 m" sub="pod ziemią" t={enter(frame, cue("underground"), fps, 16) * vis(bottom)} color={C.text} size={40} />
    </SceneShell>
  );
};
