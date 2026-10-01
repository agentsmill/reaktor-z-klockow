import { describe, expect, it } from "vitest";
import { normalizeToken, tokens, wordsFromAlignment, type Alignment } from "./words";

const align = (text: string, startSec = 0, step = 0.1): Alignment => ({
  characters: [...text],
  character_start_times_seconds: [...text].map((_, i) => +(startSec + i * step).toFixed(3)),
  character_end_times_seconds: [...text].map((_, i) => +(startSec + (i + 1) * step).toFixed(3)),
});

describe("wordsFromAlignment", () => {
  it("groups characters into words, keeping punctuation and ignoring outer spaces", () => {
    const words = wordsFromAlignment([align(" Es-em-er to mały. ")]);
    expect(words.map((w) => w.text)).toEqual(["Es-em-er", "to", "mały."]);
    expect(words[0]).toMatchObject({ startMs: 100, endMs: 900 });
    expect(words[2]).toMatchObject({ startMs: 1300, endMs: 1800 });
  });

  it("concatenates chunks with absolute times", () => {
    const words = wordsFromAlignment([align("Ala ma ", 0), align("kota.", 0.7)]);
    expect(words.map((w) => w.text)).toEqual(["Ala", "ma", "kota."]);
    expect(words[2].startMs).toBe(700);
  });

  it("fails loudly when a chunk goes back in time", () => {
    expect(() => wordsFromAlignment([align("Ala ma ", 0), align("kota.", 0)])).toThrow(/back in time/);
  });
});

describe("normalizeToken / tokens", () => {
  it("lowercases and strips punctuation but keeps Polish letters and hyphens", () => {
    expect(normalizeToken("Łańcuchowa.")).toBe("łańcuchowa");
    expect(normalizeToken("BWRX-300")).toBe("bwrx-300");
    expect(normalizeToken("—")).toBe("");
  });

  it("splits text on any whitespace", () => {
    expect(tokens("  a  b\nc ")).toEqual(["a", "b", "c"]);
  });
});
