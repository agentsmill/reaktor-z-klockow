import { scoreLineBreak } from "./lineBreak";
import { tokens, type Word } from "./words";

export type CaptionWord = Word;
export type CaptionPage = { startMs: number; endMs: number; lines: CaptionWord[][] };

/** Display spelling from `show`, timing from the spoken words (token counts must match 1:1). */
export function captionWords(show: string, sayWords: Word[]): CaptionWord[] {
  const shown = tokens(show);
  if (shown.length !== sayWords.length) {
    throw new Error(`Caption/voice token mismatch: ${shown.length} shown vs ${sayWords.length} spoken ("${show.slice(0, 40)}…")`);
  }
  return sayWords.map((w, i) => ({ ...w, text: shown[i] }));
}

const SENTENCE_END = /[.?!…]$/;
const PHRASE_END = /[,;:]$/;
const DASH = "—";
/** Polish typography: one-letter words must not hang at the end of a line (or page). */
const ORPHAN = /^[aiouwz]$/i;
const LAST_PAGE_HOLD_MS = 400;
/** Don't leave a caption on screen through long visual pauses. */
const MAX_LINGER_MS = 1200;

const join = (words: CaptionWord[]) => words.map((w) => w.text).join(" ");

/** Splits after every word matching `isEnd`. */
function splitAfter(words: CaptionWord[], isEnd: (w: CaptionWord) => boolean): CaptionWord[][] {
  const groups: CaptionWord[][] = [[]];
  for (const w of words) {
    groups[groups.length - 1].push(w);
    if (isEnd(w)) groups.push([]);
  }
  return groups.filter((g) => g.length > 0);
}

/** Best layout of `words` on one or two lines, or null if it can't fit legally. */
function layout(words: CaptionWord[], maxLineChars: number): CaptionWord[][] | null {
  if (join(words).length <= maxLineChars) return [words];

  let best: { lines: CaptionWord[][]; score: number } | null = null;
  for (let i = 1; i < words.length; i++) {
    const first = words.slice(0, i);
    const second = words.slice(i);
    const a = join(first);
    const b = join(second);
    if (a.length > maxLineChars || b.length > maxLineChars) continue;
    if (ORPHAN.test(first[first.length - 1].text) || second[0].text === DASH) continue;
    const score = scoreLineBreak(a, b);
    if (!best || score < best.score) best = { lines: [first, second], score };
  }
  return best?.lines ?? null;
}

export function buildCaptionPages(
  words: CaptionWord[],
  { maxLineChars = 42 }: { maxLineChars?: number } = {},
): CaptionPage[] {
  const pages: CaptionWord[][][] = [];
  const fits = (ws: CaptionWord[]) => layout(ws, maxLineChars) !== null;
  const push = (ws: CaptionWord[]) => {
    if (ws.length > 0) pages.push(layout(ws, maxLineChars)!);
  };

  for (const sentence of splitAfter(words, (w) => SENTENCE_END.test(w.text))) {
    let page: CaptionWord[] = [];
    for (const phrase of splitAfter(sentence, (w) => PHRASE_END.test(w.text) || w.text === DASH)) {
      if (fits([...page, ...phrase])) {
        page.push(...phrase);
        continue;
      }
      push(page);
      page = [];
      // A phrase too long for one page is split word by word, never ending a page on an orphan.
      for (const w of phrase) {
        if (fits([...page, w])) {
          page.push(w);
          continue;
        }
        const carry = page.length > 1 && ORPHAN.test(page[page.length - 1].text) ? [page.pop()!] : [];
        push(page);
        page = [...carry, w];
      }
    }
    push(page);
  }

  return pages.map((pageLines, i) => {
    const lastWord = pageLines[pageLines.length - 1].at(-1)!;
    const next = pages[i + 1]?.[0][0];
    return {
      startMs: pageLines[0][0].startMs,
      endMs: next ? Math.min(next.startMs, lastWord.endMs + MAX_LINGER_MS) : lastWord.endMs + LAST_PAGE_HOLD_MS,
      lines: pageLines,
    };
  });
}
