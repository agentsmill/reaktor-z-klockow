import { Easing, interpolate, spring } from "remotion";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Smooth, bounce-free 0→1 entrance starting at frame `at`. */
export const enter = (frame: number, at: number, fps: number, durationInFrames = 20): number =>
  spring({ frame: frame - at, fps, config: { damping: 200 }, durationInFrames });

/** Eased 0→1 between two frames (clamped). */
export const progress = (frame: number, from: number, to: number, easing = Easing.inOut(Easing.cubic)): number =>
  interpolate(frame, [from, to], [0, 1], { ...CLAMP, easing });

/** Linear 0→1 between two frames (clamped). */
export const linear = (frame: number, from: number, to: number): number => interpolate(frame, [from, to], [0, 1], CLAMP);

export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

/** Fade+rise style for HTML elements driven by a 0→1 value. */
export const riseStyle = (t: number, distance = 24): React.CSSProperties => ({
  opacity: t,
  transform: `translateY(${(1 - t) * distance}px)`,
});
