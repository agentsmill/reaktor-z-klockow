import type { SceneDef, SceneId } from "../script";
import type { Word } from "./words";

export const FPS = 30;
/** Cross-fade length between scenes (frames). */
export const TRANSITION = 12;
/** Silence before a scene's voiceover starts (frames) — equals TRANSITION so speech starts once the fade is done. */
export const DEFAULT_LEAD_IN = 12;
/** Hold after the voiceover ends (frames); TAIL − TRANSITION + LEAD_IN ≈ 0.7 s pause between sentences. */
export const DEFAULT_TAIL = 21;

export type VoScene = { file: string; durationMs: number; words: Word[] };
export type VoiceoverData = { voice: string; scenes: Record<SceneId, VoScene> };

export type TimedScene = {
  id: SceneId;
  /** Absolute start frame in the composition. */
  from: number;
  duration: number;
  /** Frames between scene start and voiceover start. */
  leadIn: number;
  voFrames: number;
};

export type Timeline = { scenes: TimedScene[]; total: number };

export function buildTimeline(defs: SceneDef[], vo: VoiceoverData, fps = FPS): Timeline {
  const scenes: TimedScene[] = [];
  let end = 0;

  defs.forEach((def, i) => {
    const voScene = vo.scenes[def.id];
    if (!voScene) throw new Error(`No voiceover for scene "${def.id}" — run npm run assets:voice`);

    const leadIn = def.leadIn ?? DEFAULT_LEAD_IN;
    // TTS files end with ~0.5 s of silence; time the scene by the last spoken word instead.
    const speechEndMs = voScene.words.at(-1)?.endMs ?? voScene.durationMs;
    const voFrames = Math.ceil((speechEndMs / 1000) * fps);
    const duration = leadIn + voFrames + (def.tail ?? DEFAULT_TAIL);
    const from = i === 0 ? 0 : end - TRANSITION;

    scenes.push({ id: def.id, from, duration, leadIn, voFrames });
    end = from + duration;
  });

  return { scenes, total: end };
}
