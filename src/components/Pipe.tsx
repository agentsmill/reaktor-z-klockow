import { C } from "../theme";

/** A pipe drawn along an SVG path: dark casing + lighter bore. */
export const Pipe: React.FC<{ d: string; width?: number; opacity?: number; tint?: string }> = ({
  d,
  width = 22,
  opacity = 1,
  tint = "#16233A",
}) => (
  <g opacity={opacity} fill="none" strokeLinecap="round" strokeLinejoin="round">
    <path d={d} stroke={C.steelDark} strokeWidth={width} />
    <path d={d} stroke={tint} strokeWidth={width - 8} />
  </g>
);
