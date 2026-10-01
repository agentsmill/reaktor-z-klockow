import { Audio } from "@remotion/media";
import { interpolate, Sequence, staticFile } from "remotion";
import type { Timeline } from "../lib/timeline";

/**
 * Per-effect gain, set from measured loudness (ffmpeg ebur128) so every effect
 * sits ~8–10 LU under the -16 LUFS voiceover.
 */
const SFX_GAIN = {
  whoosh: 0.32,
  pop: 0.85,
  clunk: 0.6,
  hum: 0.07,
  powerdown: 0.3,
  sparkle: 0.6,
  tick: 1,
  click: 1,
  clatter: 0.14,
} as const;

export type SfxName = keyof typeof SFX_GAIN;

/** A sound effect starting at scene-relative frame `at`. */
export const Sfx: React.FC<{ at: number; name: SfxName; gain?: number; durationInFrames?: number; loop?: boolean }> = ({
  at,
  name,
  gain = 1,
  durationInFrames,
  loop = false,
}) => (
  <Sequence from={Math.max(0, Math.round(at))} durationInFrames={durationInFrames} layout="none">
    <Audio
      src={staticFile(`audio/sfx/${name}.mp3`)}
      loop={loop}
      volume={(f) =>
        SFX_GAIN[name] *
        gain *
        (loop && durationInFrames ? interpolate(f, [0, 20, durationInFrames - 20, durationInFrames], [0, 1, 1, 0], { extrapolateRight: "clamp" }) : 1)
      }
    />
  </Sequence>
);

// Score measured at -11.3 LUFS (ebur128): ~-23 dB under the voice, ~-12 dB in the open.
const MUSIC_UNDER_VOICE = 0.075;
const MUSIC_OPEN = 0.24;
const ATTACK = 10; // frames to duck before speech
const RELEASE = 24; // frames to recover after speech (slow, so short pauses don't pump)

export type MusicDip = { at: number; hold: number; release: number };

/** Music bed that ducks under every voiceover span, plus dramatic dips (e.g. the blackout). */
export const MusicBed: React.FC<{ timeline: Timeline; dips?: MusicDip[] }> = ({ timeline, dips = [] }) => {
  const spans = timeline.scenes.map((s) => [s.from + s.leadIn, s.from + s.leadIn + s.voFrames] as const);
  const total = timeline.total;
  return (
    <Audio
      src={staticFile("audio/music.mp3")}
      volume={(f) => {
        const duck = Math.max(
          0,
          ...spans.map(([a, b]) =>
            interpolate(f, [a - ATTACK, a, b, b + RELEASE], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          ),
        );
        const fades = interpolate(f, [0, 24, total - 60, total], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const dip = Math.min(
          1,
          ...dips.map((d) =>
            interpolate(f, [d.at - 6, d.at, d.at + d.hold, d.at + d.hold + d.release], [1, 0.12, 0.12, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          ),
        );
        return fades * dip * interpolate(duck, [0, 1], [MUSIC_OPEN, MUSIC_UNDER_VOICE]);
      }}
    />
  );
};
