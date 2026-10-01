import { describe, expect, it } from "vitest";
import { findCueIndex } from "./lib/cues";
import { tokens } from "./lib/words";
import { SCENES, sayText } from "./script";

describe("script", () => {
  it("has 10 uniquely named scenes", () => {
    expect(SCENES).toHaveLength(10);
    expect(new Set(SCENES.map((s) => s.id)).size).toBe(10);
  });

  it.each(SCENES.map((s) => [s.id, s] as const))("%s: spoken and shown text align token-for-token", (_, s) => {
    expect(tokens(sayText(s)).length).toBe(tokens(s.show).length);
  });

  it.each(SCENES.map((s) => [s.id, s] as const))("%s: every cue word exists in the narration", (_, s) => {
    const words = tokens(s.show).map((text) => ({ text }));
    for (const cue of s.cues) expect(() => findCueIndex(words, cue)).not.toThrow();
  });

  it.each(SCENES.map((s) => [s.id, s] as const))("%s: cues are listed in narration order", (_, s) => {
    const words = tokens(s.show).map((text) => ({ text }));
    const order = s.cues.map((c) => findCueIndex(words, c));
    expect(order).toEqual([...order].sort((a, b) => a - b));
  });
});
