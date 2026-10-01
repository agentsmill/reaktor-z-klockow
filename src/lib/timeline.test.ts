import { describe, expect, it } from "vitest";
import type { SceneDef } from "../script";
import { buildTimeline, DEFAULT_LEAD_IN, DEFAULT_TAIL, TRANSITION, type VoiceoverData } from "./timeline";

const defs = [
  { id: "intro", chip: "", show: "a", cues: [], leadIn: 45 },
  { id: "smr", chip: "", show: "b", cues: [] },
  { id: "outro", chip: "", show: "c", cues: [], tail: 150 },
] as SceneDef[];

const vo = {
  voice: "test",
  scenes: {
    intro: { file: "intro.mp3", durationMs: 1000, words: [] },
    smr: { file: "smr.mp3", durationMs: 2010, words: [] },
    outro: { file: "outro.mp3", durationMs: 500, words: [] },
  },
} as unknown as VoiceoverData;

describe("buildTimeline", () => {
  const t = buildTimeline(defs, vo, 30);

  it("sizes each scene as lead-in + voiceover + tail (with overrides)", () => {
    expect(t.scenes[0].duration).toBe(45 + 30 + DEFAULT_TAIL);
    expect(t.scenes[1].duration).toBe(DEFAULT_LEAD_IN + 61 + DEFAULT_TAIL); // ceil(2.01 s × 30)
    expect(t.scenes[2].duration).toBe(DEFAULT_LEAD_IN + 15 + 150);
  });

  it("overlaps consecutive scenes by the transition length", () => {
    expect(t.scenes[0].from).toBe(0);
    expect(t.scenes[1].from).toBe(t.scenes[0].duration - TRANSITION);
    expect(t.scenes[2].from).toBe(t.scenes[1].from + t.scenes[1].duration - TRANSITION);
    expect(t.total).toBe(t.scenes[2].from + t.scenes[2].duration);
  });

  it("sizes by the end of the last spoken word, ignoring trailing silence in the file", () => {
    const withWords = {
      voice: "test",
      scenes: { ...vo.scenes, smr: { file: "smr.mp3", durationMs: 2010, words: [{ text: "b", startMs: 0, endMs: 1500 }] } },
    } as unknown as VoiceoverData;
    expect(buildTimeline(defs, withWords, 30).scenes[1].voFrames).toBe(45);
  });

  it("throws when a scene has no voiceover", () => {
    expect(() => buildTimeline([...defs, { id: "why", chip: "", show: "x", cues: [] }], vo)).toThrow(/why/);
  });
});
