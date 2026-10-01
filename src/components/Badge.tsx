import { BODY, C } from "../theme";

/** Small top-right pill, e.g. "Wizualizacja AI". */
export const Badge: React.FC<{ text: string; opacity?: number }> = ({ text, opacity = 1 }) => (
  <div
    style={{
      position: "absolute",
      right: 72,
      top: 56,
      opacity,
      fontFamily: BODY,
      fontSize: 18,
      fontWeight: 700,
      letterSpacing: "0.08em",
      color: C.text,
      background: "rgba(6, 12, 23, 0.55)",
      border: "1px solid rgba(238, 242, 247, 0.25)",
      borderRadius: 999,
      padding: "6px 16px",
    }}
  >
    {text}
  </div>
);
