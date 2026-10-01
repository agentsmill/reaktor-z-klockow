import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate } from "../components/BrickPlate";
import { spinAngle } from "../components/Machines";
import { RecapChain } from "../components/RecapChain";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { enter, lerp, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { CREDITS_3D, SOURCES, STEPS } from "../scenes/Outro";
import { BODY, C, DISPLAY } from "../theme";

/** Night pull-back over the finished diorama: recap chain, title, sources. */
export const Outro3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cue = useCues();
  const lift = progress(frame, cue("title") - 6, cue("title") + 20);
  const titleT = enter(frame, cue("title") - 2, fps, 22);
  const sourcesT = enter(frame, cue("title") + 75, fps, 24);
  const fadeOut = interpolate(frame, [durationInFrames - 30, durationInFrames], [0, 1], { extrapolateLeft: "clamp" });
  const angle = spinAngle(frame, (f) => (f > cue("turbine") ? 8 : 0));

  return (
    <SceneShell background={<BrickPlate shot="outro" />}>
      {STEPS.map((s) => (
        <Sfx key={s.cue} at={cue(s.cue) - 4} name="tick" />
      ))}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(6,12,23,0.55) 0%, rgba(6,12,23,0) 45%, rgba(6,12,23,0) 70%, rgba(6,12,23,0.7) 100%)" }} />
      <RecapChain y={lerp(250, 175, lift)} scale={lerp(0.85, 0.66, lift)} at={STEPS.map((s) => cue(s.cue))} turbineAngle={angle} />
      {/* soft dark halo so the title reads over the lit diorama */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 34% 16% at 50% 37%, rgba(6,12,23,0.78) 0%, rgba(6,12,23,0.45) 55%, rgba(6,12,23,0) 100%)",
          opacity: titleT,
        }}
      />
      <div style={{ position: "absolute", top: 330, left: 0, right: 0, textAlign: "center", ...riseStyle(titleT, 24) }}>
        <div style={{ fontFamily: DISPLAY, fontSize: 86, fontWeight: 700, color: C.text, textShadow: "0 4px 30px rgba(6,12,23,0.7)" }}>Tak działa SMR.</div>
        <div style={{ fontFamily: BODY, fontSize: 36, fontWeight: 700, color: C.muted, marginTop: 10 }}>
          Mały reaktor. <span style={{ color: C.electricity }}>Wielka energia.</span>
        </div>
      </div>
      <div style={{ position: "absolute", bottom: 70, left: 160, right: 160, textAlign: "center", fontFamily: BODY, color: C.muted, ...riseStyle(sourcesT, 10) }}>
        <div style={{ fontSize: 21, fontWeight: 600, lineHeight: 1.5 }}>{SOURCES}</div>
        <div style={{ fontSize: 19, fontWeight: 600, marginTop: 8 }}>{CREDITS_3D}</div>
      </div>
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: fadeOut }} />
    </SceneShell>
  );
};
