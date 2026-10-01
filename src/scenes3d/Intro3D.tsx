import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate } from "../components/BrickPlate";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { enter, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

/** Macro one-take: first brick lands, diorama assembles, cap clicks on at "Zbudujmy go z klocków!". */
export const Intro3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const out = progress(frame, 104, 132);
  const kicker = enter(frame, 4, fps);
  const line1 = enter(frame, 10, fps, 26);
  const line2 = enter(frame, 22, fps, 26);
  const sub = enter(frame, 40, fps);

  return (
    <SceneShell background={<BrickPlate shot="intro" />}>
      <Sfx at={12} name="click" />
      <Sfx at={36} name="clatter" />
      <Sfx at={110} name="clatter" gain={0.7} />
      <Sfx at={cue("build") - 6} name="click" />
      <AbsoluteFill
        style={{
          background: "linear-gradient(90deg, rgba(6,12,23,0.8) 0%, rgba(6,12,23,0.4) 36%, rgba(6,12,23,0) 62%)",
          opacity: 1 - out,
        }}
      />
      <div style={{ position: "absolute", left: 120, top: 290, width: 1040, opacity: 1 - out }}>
        <div style={{ ...riseStyle(kicker, 12), fontFamily: BODY, fontSize: 26, fontWeight: 800, letterSpacing: "0.22em", color: C.muted, marginBottom: 26 }}>
          SMR · BWRX-300
        </div>
        <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 92, lineHeight: 1.08, color: C.text, textShadow: "0 4px 30px rgba(6,12,23,0.6)" }}>
          <div style={riseStyle(line1, 30)}>Mały reaktor.</div>
          <div style={riseStyle(line2, 30)}>
            Wielka <span style={{ color: C.electricity }}>energia.</span>
          </div>
        </div>
        <div style={{ ...riseStyle(sub, 16), marginTop: 34, fontFamily: BODY, fontSize: 34, fontWeight: 600, color: C.muted }}>
          Jak działa reaktor SMR? Klocek po klocku.
        </div>
      </div>
    </SceneShell>
  );
};
