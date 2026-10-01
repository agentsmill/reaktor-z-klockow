import { useCurrentFrame, useVideoConfig } from "remotion";
import { enter, lerp, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

const LETTERS = [
  { letter: "S", en: "Small", pl: "mały", cue: "small" },
  { letter: "M", en: "Modular", pl: "modułowy", cue: "modular" },
  { letter: "R", en: "Reactor", pl: "reaktor", cue: "reactor" },
] as const;

/** S · M · R with Polish meanings; big and centred, shrinking to the top when the comparison starts. */
export const SmrLetters: React.FC<{ topFrom?: number; topTo?: number }> = ({ topFrom = 300, topTo = 120 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const shrink = progress(frame, cue("compare") - 6, cue("compare") + 18);
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: lerp(topFrom, topTo, shrink),
        display: "flex",
        justifyContent: "center",
        gap: 140,
        transform: `scale(${lerp(1, 0.5, shrink)})`,
        transformOrigin: "50% 0%",
        textShadow: "0 4px 24px rgba(6,12,23,0.8)",
      }}
    >
      {LETTERS.map(({ letter, en, pl, cue: c }, i) => {
        const t = enter(frame, cue(c) - 3, fps, 14);
        const letterIn = enter(frame, 6 + i * 4, fps, 16);
        return (
          <div key={letter} style={{ textAlign: "center", width: 300, ...riseStyle(letterIn, 20) }}>
            <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 190, lineHeight: 1, color: t > 0.5 ? C.text : C.faint }}>{letter}</div>
            <div style={{ ...riseStyle(t, 14), fontFamily: BODY, fontSize: 32, fontWeight: 600, color: C.muted, marginTop: 18 }}>{en}</div>
            <div style={{ ...riseStyle(t, 14), fontFamily: BODY, fontSize: 52, fontWeight: 800, color: C.text, marginTop: 4 }}>{pl}</div>
          </div>
        );
      })}
    </div>
  );
};
