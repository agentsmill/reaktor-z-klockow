import { loadFont as loadUnbounded } from "@remotion/google-fonts/Unbounded";
import { loadFont as loadManrope } from "@remotion/google-fonts/Manrope";

// latin-ext carries the Polish letters (ą ć ę ł ń ó ś ź ż).
export const DISPLAY = loadUnbounded("normal", { weights: ["500", "700"], subsets: ["latin", "latin-ext"] }).fontFamily;
export const BODY = loadManrope("normal", { weights: ["500", "600", "700", "800"], subsets: ["latin", "latin-ext"] })
  .fontFamily;

/** Colour = meaning. Never reuse a semantic colour for decoration. */
export const C = {
  bg: "#0B1424",
  bgDeep: "#060C17",
  bgGlow: "#12233D",
  panel: "rgba(16, 28, 48, 0.88)",
  panelEdge: "rgba(130, 160, 210, 0.22)",
  text: "#EEF2F7",
  muted: "#9FB0C8",
  faint: "#5B6B85",
  line: "#4A5F80",
  steel: "#7C8BA3",
  steelDark: "#3B4A63",

  neutron: "#5CE1FF",
  uranium: "#9BE15D",
  heat: "#FF8A3D",
  water: "#2F7BFF",
  waterDeep: "#1A4FB8",
  steam: "#E8F0F8",
  electricity: "#FFD447",
  rods: "#8A96A8",
  accent: "#E5484D",
  ground: "#1D2B24",
  grass: "#3E6B45",
  concrete: "#2B3A52",
} as const;

export const WIDTH = 1920;
export const HEIGHT = 1080;
