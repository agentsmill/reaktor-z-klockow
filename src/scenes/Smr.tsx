import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BigPlant, Factory, ModuleBox, SmrPlant } from "../components/Buildings";
import { SceneShell } from "../components/SceneShell";
import { SmrLetters } from "../components/SmrLetters";
import { Tag } from "../components/Tag";
import { enter, lerp, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C } from "../theme";

const GROUND = 770;


export const Smr: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();

  const smrIn = enter(frame, cue("compare"), fps, 24);
  const bigIn = enter(frame, cue("big"), fps, 28);
  const modulesIn = progress(frame, cue("modules"), cue("modules") + 14);
  const factoryIn = enter(frame, cue("factory") - 4, fps, 16);

  return (
    <SceneShell>
      <SmrLetters />

      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        {/* ground */}
        <line x1={120} x2={1800} y1={GROUND} y2={GROUND} stroke={C.line} strokeWidth={3} opacity={Math.max(smrIn, bigIn)} />

        <g opacity={bigIn} transform={`translate(0, ${(1 - bigIn) * 40})`}>
          <BigPlant x={170} y={GROUND} frame={frame} />
        </g>
        <g opacity={smrIn} transform={`translate(0, ${(1 - smrIn) * 40})`}>
          <SmrPlant x={1120} y={GROUND} modules={modulesIn} />
        </g>

        <Factory x={1560} y={GROUND} s={0.9} opacity={factoryIn} />
        {/* prefabricated modules travel from the factory to the site */}
        {[0, 1, 2].map((i) => {
          const t = progress(frame, cue("factory") + i * 8, cue("factory") + 26 + i * 8);
          if (t <= 0 || t >= 1) return null;
          const x = lerp(1600, 1150, t);
          const y = GROUND - 40 - Math.sin(t * Math.PI) * 120;
          return <ModuleBox key={i} x={x} y={y} w={56} opacity={Math.min(1, t * 4, (1 - t) * 4)} />;
        })}
      </svg>

      <Tag x={590} y={GROUND + 52} anchor="center" text="Duży blok jądrowy" sub="ponad 1000 MW" t={bigIn} color={C.steel} />
      <Tag x={1270} y={GROUND + 52} anchor="center" text="SMR" sub="ok. 300 MW" t={smrIn} color={C.text} />
      <Tag
        x={1650}
        y={GROUND + 52}
        anchor="center"
        text="Fabryka"
        sub="gotowe moduły"
        t={factoryIn}
        color={C.steam}
      />
      <div
        style={{
          position: "absolute",
          left: 1120,
          top: interpolate(smrIn, [0, 1], [430, 410]),
          width: 300,
          textAlign: "center",
          fontFamily: BODY,
          fontSize: 26,
          fontWeight: 700,
          color: C.muted,
          opacity: progress(frame, cue("big") + 10, cue("big") + 30) * (1 - modulesIn * 0.4),
        }}
      >
        kilka razy mniejszy
      </div>
    </SceneShell>
  );
};
