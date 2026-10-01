import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import type { CaptionPage } from "../lib/captions";
import { enter } from "../lib/anim";
import type { SceneData } from "../lib/project";
import { BODY } from "../theme";

const SPOKEN = "#FFFFFF";
const UPCOMING = "#93A3BC";

const Page: React.FC<{ page: CaptionPage }> = ({ page }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const nowMs = page.startMs + (frame / fps) * 1000;
  const t = enter(frame, 0, fps, 6);

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 58,
        display: "flex",
        justifyContent: "center",
        opacity: t,
        transform: `translateY(${(1 - t) * 8}px)`,
      }}
    >
      <div
        style={{
          background: "rgba(4, 9, 18, 0.66)",
          border: "1px solid rgba(130, 160, 210, 0.14)",
          borderRadius: 20,
          padding: "14px 32px 16px",
          maxWidth: 1500,
          textAlign: "center",
          fontFamily: BODY,
          fontWeight: 700,
          fontSize: 44,
          lineHeight: 1.32,
          textShadow: "0 2px 12px rgba(0,0,0,0.5)",
        }}
      >
        {page.lines.map((line, li) => (
          <div key={li}>
            {line.map((w, wi) => (
              <span key={wi} style={{ color: nowMs >= w.startMs ? SPOKEN : UPCOMING }}>
                {(wi > 0 ? " " : "") + w.text}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

/** Caption overlay; `offset(scene)` = frame where that scene's voiceover starts on this timeline. */
export const Captions: React.FC<{ scenes: SceneData[]; offset: (s: SceneData) => number }> = ({ scenes, offset }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {scenes.flatMap((s) =>
        s.pages.map((page, i) => {
          const from = offset(s) + Math.round((page.startMs / 1000) * fps);
          const to = offset(s) + Math.round((page.endMs / 1000) * fps);
          return (
            <Sequence key={`${s.def.id}-${i}`} from={from} durationInFrames={Math.max(1, to - from)} layout="none">
              <Page page={page} />
            </Sequence>
          );
        }),
      )}
    </AbsoluteFill>
  );
};
