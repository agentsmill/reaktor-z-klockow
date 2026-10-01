import { describe, expect, it } from "vitest";
import { cueFrame, findCueIndex } from "./cues";

const words = ["Gdy", "neutron", "trafi", "w", "jądro,", "powstają", "nowe", "neutrony,", "i", "nowe", "ciepło."].map(
  (text, i) => ({ text, startMs: i * 500, endMs: i * 500 + 400 }),
);

describe("findCueIndex", () => {
  it("matches by normalised prefix, so Polish inflections still hit", () => {
    expect(findCueIndex(words, { id: "n", word: "jądr" })).toBe(4);
    expect(findCueIndex(words, { id: "h", word: "Ciepło" })).toBe(10);
  });

  it("picks the nth occurrence", () => {
    expect(findCueIndex(words, { id: "n2", word: "neutron", nth: 2 })).toBe(7);
    expect(findCueIndex(words, { id: "x", word: "nowe", nth: 2 })).toBe(9);
  });

  it("throws a readable error for a missing cue", () => {
    expect(() => findCueIndex(words, { id: "rods", word: "pręty" })).toThrow('Cue "rods" ("pręty" #1) not found');
  });
});

describe("cueFrame", () => {
  it("returns a scene-relative frame including the lead-in", () => {
    const scene = { id: "fission" as const, from: 500, duration: 300, leadIn: 12, voFrames: 200 };
    // "trafi" starts at 1000 ms → 30 frames, + 12 lead-in
    expect(cueFrame(scene, words, { id: "hit", word: "trafi" }, 30)).toBe(42);
  });
});
