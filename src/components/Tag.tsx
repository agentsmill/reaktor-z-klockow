import { BODY, C } from "../theme";

/**
 * HTML label positioned in frame pixels (scenes use full-frame 1920×1080 SVGs,
 * so SVG coordinates and CSS pixels coincide). `t` drives the entrance (0→1).
 */
export const Tag: React.FC<{
  x: number;
  y: number;
  text: string;
  t: number;
  color?: string;
  /** Which point of the label sits at (x, y). */
  anchor?: "left" | "right" | "center";
  size?: number;
  sub?: string;
}> = ({ x, y, text, t, color = C.text, anchor = "left", size = 30, sub }) => {
  if (t <= 0) return null;
  const shift = anchor === "left" ? "0%" : anchor === "right" ? "-100%" : "-50%";
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `translate(${shift}, -50%) translateY(${(1 - t) * 10}px)`,
        opacity: t,
        fontFamily: BODY,
        whiteSpace: "nowrap",
        textAlign: anchor === "center" ? "center" : anchor,
        textShadow: "0 2px 10px rgba(6,12,23,0.95), 0 0 3px rgba(6,12,23,0.9)",
      }}
    >
      <div style={{ display: "inline-flex", alignItems: "center", gap: 10, fontSize: size, fontWeight: 800, color: C.text }}>
        <span style={{ width: size * 0.34, height: size * 0.34, borderRadius: 999, background: color, flexShrink: 0 }} />
        {text}
      </div>
      {sub && (
        <div style={{ fontSize: size * 0.62, fontWeight: 600, color: C.muted, marginTop: 2, paddingLeft: anchor === "left" ? size * 0.34 + 10 : 0 }}>
          {sub}
        </div>
      )}
    </div>
  );
};
