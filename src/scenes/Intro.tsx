import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Badge } from "../components/Badge";
import { SceneShell } from "../components/SceneShell";
import { enter, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cue = useCues();

  // Slow Ken Burns that accelerates into the plant on "Jak to działa?".
  const drift = interpolate(frame, [0, durationInFrames], [1.04, 1.13]);
  const push = progress(frame, cue("question"), durationInFrames + 10, Easing.in(Easing.cubic));
  const scale = drift + push * 0.14;

  const background = (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: C.bgDeep }}>
      <Img
        src={staticFile("img/intro-plant.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: "50% 62%",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(90deg, rgba(6,12,23,0.9) 0%, rgba(6,12,23,0.62) 34%, rgba(6,12,23,0.05) 62%, rgba(6,12,23,0) 100%)",
        }}
      />
      <AbsoluteFill style={{ background: "linear-gradient(0deg, rgba(6,12,23,0.7) 0%, rgba(6,12,23,0) 28%)" }} />
    </AbsoluteFill>
  );

  const kicker = enter(frame, 6, fps);
  const line1 = enter(frame, 14, fps, 26);
  const line2 = enter(frame, 28, fps, 26);
  const sub = enter(frame, 46, fps);

  return (
    <SceneShell background={background}>
      <div style={{ position: "absolute", left: 120, top: 300, width: 1040 }}>
        <div
          style={{
            ...riseStyle(kicker, 12),
            fontFamily: BODY,
            fontSize: 26,
            fontWeight: 800,
            letterSpacing: "0.22em",
            color: C.muted,
            marginBottom: 26,
          }}
        >
          SMR · BWRX-300
        </div>
        <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 92, lineHeight: 1.08, color: C.text }}>
          <div style={riseStyle(line1, 30)}>Mały reaktor.</div>
          <div style={riseStyle(line2, 30)}>
            Wielka <span style={{ color: C.electricity }}>energia.</span>
          </div>
        </div>
        <div
          style={{
            ...riseStyle(sub, 16),
            marginTop: 34,
            fontFamily: BODY,
            fontSize: 34,
            fontWeight: 600,
            color: C.muted,
          }}
        >
          Jak działa reaktor SMR? Krok po kroku.
        </div>
      </div>
      <Badge text="Wizualizacja AI" />
    </SceneShell>
  );
};
