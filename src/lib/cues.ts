import type { CueDef } from "../script";
import type { TimedScene } from "./timeline";
import { normalizeToken } from "./words";

/** Index of the nth word whose normalised form starts with the cue word (prefix = inflection-safe for Polish). */
export function findCueIndex(words: { text: string }[], cue: CueDef): number {
  const target = normalizeToken(cue.word);
  const nth = cue.nth ?? 1;
  let seen = 0;

  for (let i = 0; i < words.length; i++) {
    if (normalizeToken(words[i].text).startsWith(target) && ++seen === nth) return i;
  }
  throw new Error(`Cue "${cue.id}" ("${cue.word}" #${nth}) not found`);
}

/** Scene-relative frame at which the cue word starts being spoken. */
export function cueFrame(
  scene: TimedScene,
  words: { text: string; startMs: number }[],
  cue: CueDef,
  fps = 30,
): number {
  const word = words[findCueIndex(words, cue)];
  return scene.leadIn + Math.round((word.startMs / 1000) * fps);
}
