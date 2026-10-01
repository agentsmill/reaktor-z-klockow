// QA: transcribe the rendered video's mixed audio with Whisper (fal.ai) and diff it
// against the narration script. Catches mispronunciations and music masking speech.
// Usage: node --env-file=.env scripts/qa-transcript.ts out/smr-bwrx300.mp4
import { fal } from "@fal-ai/client";
import { execFileSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import { falRun } from "./fal.ts";
import { SCENES } from "../src/script.ts";

const video = process.argv[2] ?? "out/smr-bwrx300.mp4";
const audio = "out/cache/qa-audio.mp3";
execFileSync("ffmpeg", ["-y", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", audio]);

const url = await fal.storage.upload(new Blob([await readFile(audio)], { type: "audio/mpeg" }));
const { text } = await falRun<{ text: string }>("fal-ai/whisper", { audio_url: url, task: "transcribe", language: "pl" });

const norm = (s: string) =>
  s.toLowerCase().replace(/[^\p{L}\p{N}\s]+/gu, " ").split(/\s+/).filter(Boolean);
const expected = norm(SCENES.map((s) => s.show).join(" "));
const heard = norm(text);

// Word-level edit distance with backtrace, to list what differs.
const n = expected.length;
const m = heard.length;
const d = Array.from({ length: n + 1 }, (_, i) => Array.from({ length: m + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0)));
for (let i = 1; i <= n; i++)
  for (let j = 1; j <= m; j++)
    d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (expected[i - 1] === heard[j - 1] ? 0 : 1));

const diffs: string[] = [];
for (let i = n, j = m; i > 0 || j > 0; ) {
  if (i > 0 && j > 0 && expected[i - 1] === heard[j - 1]) {
    i--;
    j--;
  } else if (i > 0 && j > 0 && d[i][j] === d[i - 1][j - 1] + 1) {
    diffs.unshift(`  "${expected[i - 1]}" → heard "${heard[j - 1]}"`);
    i--;
    j--;
  } else if (i > 0 && d[i][j] === d[i - 1][j] + 1) {
    diffs.unshift(`  missing "${expected[i - 1]}"`);
    i--;
  } else {
    diffs.unshift(`  extra "${heard[j - 1]}"`);
    j--;
  }
}

console.log(`Script words: ${n} · heard: ${m} · word error rate: ${((d[n][m] / n) * 100).toFixed(1)}%`);
console.log(diffs.length ? `Differences:\n${diffs.join("\n")}` : "No differences.");
