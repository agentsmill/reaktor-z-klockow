import { describe, expect, it } from "vitest";
import { buildCaptionPages, captionWords } from "./captions";
import type { Word } from "./words";

const timed = (text: string): Word[] =>
  text.split(" ").map((t, i) => ({ text: t, startMs: i * 300, endMs: i * 300 + 250 }));

const lineText = (line: Word[]) => line.map((w) => w.text).join(" ");

describe("captionWords", () => {
  it("shows the display spelling with the spoken timing", () => {
    const said = timed("Es-em-er to mały reaktor.");
    const shown = captionWords("SMR to mały reaktor.", said);
    expect(shown.map((w) => w.text)).toEqual(["SMR", "to", "mały", "reaktor."]);
    expect(shown[0].startMs).toBe(said[0].startMs);
  });

  it("refuses mismatched token counts", () => {
    expect(() => captionWords("BWRX-300", timed("be wu er"))).toThrow(/mismatch/);
  });
});

describe("buildCaptionPages", () => {
  const text =
    "Para rozkręca turbinę, a turbina napędza generator prądu. Jak para z czajnika, która kręci wiatraczkiem. Potem para skrapla się i wraca do reaktora jako woda.";
  const pages = buildCaptionPages(timed(text));

  it("keeps lines within 42 characters and pages within 2 lines", () => {
    for (const p of pages) {
      expect(p.lines.length).toBeLessThanOrEqual(2);
      for (const l of p.lines) expect(lineText(l).length).toBeLessThanOrEqual(42);
    }
  });

  it("starts a new page after a sentence ends", () => {
    for (const p of pages) {
      const words = p.lines.flat();
      words.slice(0, -1).forEach((w) => expect(w.text).not.toMatch(/[.?!]$/));
    }
  });

  it("never ends a line with a one-letter Polish word", () => {
    for (const p of pages) for (const l of p.lines) expect(l[l.length - 1].text).not.toMatch(/^[aiouwz]$/i);
  });

  it("never starts a line with a dash", () => {
    const dashed = buildCaptionPages(timed("Ciepło zagotowuje wodę wprost w samym reaktorze — stąd nazwa: reaktor z wrzącą wodą."));
    for (const p of dashed) for (const l of p.lines) expect(l[0].text).not.toBe("—");
  });

  it("breaks pages at phrase boundaries (comma, dash) instead of mid-phrase", () => {
    const fission = buildCaptionPages(
      timed("Gdy neutron trafi w jądro uranu, jądro rozpada się na dwa mniejsze — to rozszczepienie."),
    );
    expect(fission.map((p) => p.lines.map(lineText).join(" / "))).toEqual([
      "Gdy neutron trafi w jądro uranu, / jądro rozpada się na dwa mniejsze —",
      "to rozszczepienie.",
    ]);
  });

  it("balances two lines instead of filling the first one greedily", () => {
    const [page] = buildCaptionPages(timed("Taki reaktor daje prąd całą dobę, bez względu na pogodę."));
    const [a, b] = page.lines.map(lineText);
    expect(Math.abs(a.length - b.length)).toBeLessThan(12);
  });

  it("ends each page when the next one starts, the last one 400 ms after its final word", () => {
    pages.slice(0, -1).forEach((p, i) => expect(p.endMs).toBe(pages[i + 1].startMs));
    const last = pages[pages.length - 1];
    expect(last.endMs).toBe(last.lines.flat().at(-1)!.endMs + 400);
  });
});
