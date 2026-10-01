import type { ReactNode } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { enter } from "../lib/anim";
import { useScene } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

const pad = (n: number) => String(n).padStart(2, "0");

export const Backdrop: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: C.bg,
      backgroundImage: [
        "radial-gradient(ellipse 75% 65% at 50% 40%, rgba(32, 62, 108, 0.55) 0%, rgba(11, 20, 36, 0) 70%)",
        "linear-gradient(rgba(130, 160, 210, 0.055) 1px, transparent 1px)",
        "linear-gradient(90deg, rgba(130, 160, 210, 0.055) 1px, transparent 1px)",
      ].join(","),
      backgroundSize: "100% 100%, 48px 48px, 48px 48px",
      backgroundPosition: "0 0, -1px -1px, -1px -1px",
    }}
  />
);

const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background: "radial-gradient(ellipse 85% 80% at 50% 45%, rgba(0,0,0,0) 55%, rgba(3, 6, 12, 0.55) 100%)",
      pointerEvents: "none",
    }}
  />
);

const Chip: React.FC = () => {
  const { def, index, count } = useScene();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = enter(frame, 4, fps, 16);
  if (!def.chip) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 72,
        top: 56,
        display: "flex",
        alignItems: "center",
        gap: 18,
        opacity: t,
        transform: `translateX(${(1 - t) * -16}px)`,
      }}
    >
      <div style={{ fontFamily: DISPLAY, fontSize: 22, fontWeight: 500, color: C.text, letterSpacing: 1 }}>
        {pad(index)}
        <span style={{ color: C.faint }}>/{pad(count - 1)}</span>
      </div>
      <div style={{ width: 1, height: 24, background: C.panelEdge }} />
      <div
        style={{
          fontFamily: BODY,
          fontSize: 22,
          fontWeight: 700,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: C.muted,
        }}
      >
        {def.chip}
      </div>
    </div>
  );
};

const SchematicTag: React.FC = () => (
  <div
    style={{
      position: "absolute",
      right: 72,
      top: 56,
      fontFamily: BODY,
      fontSize: 18,
      fontWeight: 600,
      letterSpacing: "0.08em",
      color: C.faint,
      border: `1px dashed ${C.faint}`,
      borderRadius: 999,
      padding: "6px 16px",
    }}
  >
    Schemat uproszczony
  </div>
);

export const SceneShell: React.FC<{
  children: ReactNode;
  schematic?: boolean;
  /** Replaces the blueprint backdrop (e.g. a photo). */
  background?: ReactNode;
}> = ({ children, schematic = false, background }) => (
  <AbsoluteFill>
    {background ?? <Backdrop />}
    {children}
    <Vignette />
    <Chip />
    {schematic && <SchematicTag />}
  </AbsoluteFill>
);
