// Turns ElevenLabs character-level alignment into word timings.
// Kept dependency-free so the Node asset scripts can import it directly.

export type Alignment = {
  characters: string[];
  character_start_times_seconds: number[];
  character_end_times_seconds: number[];
};

export type Word = { text: string; startMs: number; endMs: number };

const toMs = (sec: number) => Math.round(sec * 1000);

export function wordsFromAlignment(chunks: Alignment[]): Word[] {
  const words: Word[] = [];
  let current: Word | null = null;
  let lastStartMs = -Infinity;

  for (const chunk of chunks) {
    for (let i = 0; i < chunk.characters.length; i++) {
      const ch = chunk.characters[i];
      const startMs = toMs(chunk.character_start_times_seconds[i]);
      const endMs = toMs(chunk.character_end_times_seconds[i]);
      if (startMs < lastStartMs) {
        throw new Error(`Alignment goes back in time at "${ch}" (${startMs} ms < ${lastStartMs} ms)`);
      }
      lastStartMs = startMs;

      if (/\s/.test(ch)) {
        if (current) words.push(current);
        current = null;
      } else if (current) {
        current.text += ch;
        current.endMs = endMs;
      } else {
        current = { text: ch, startMs, endMs };
      }
    }
  }
  if (current) words.push(current);
  return words;
}

export function normalizeToken(token: string): string {
  return token
    .toLowerCase()
    .replace(/[^\p{L}\p{N}-]+/gu, "")
    .replace(/^-+|-+$/g, "");
}

export const tokens = (text: string): string[] => text.split(/\s+/).filter(Boolean);
