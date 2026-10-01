// Picks the clearest Polish narrator objectively: synthesise the hardest paragraph
// with several calm male voices, transcribe each back with Whisper, compare to the
// script (character error rate). Lower CER = Whisper understood the Polish better.
import { download, falRun, probeDurationMs, type FalAudio } from "./fal.ts";
import { SCENES } from "../src/script.ts";

const VOICES = ["Brian", "George", "Bill", "Daniel", "Eric", "Roger"];
const OUT = "out/audition";
const text = SCENES.find((s) => s.id === "fission")!.show;

const norm = (s: string) =>
  s.toLowerCase().replace(/[^\p{L}\p{N}\s]+/gu, " ").replace(/\s+/g, " ").trim();

function levenshtein(a: string, b: string): number {
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) {
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
    prev = cur;
  }
  return prev[b.length];
}

const results = await Promise.all(
  VOICES.map(async (voice) => {
    const tts = await falRun<FalAudio>("fal-ai/elevenlabs/tts/multilingual-v2", {
      text,
      voice,
      language_code: "pl",
      stability: 0.55,
      similarity_boost: 0.75,
      style: 0.15,
    });
    const file = `${OUT}/${voice}.mp3`;
    await download(tts.audio.url, file);
    const stt = await falRun<{ text: string }>("fal-ai/whisper", {
      audio_url: tts.audio.url,
      task: "transcribe",
      language: "pl",
    });
    const cer = levenshtein(norm(stt.text), norm(text)) / norm(text).length;
    return { voice, cer, seconds: probeDurationMs(file) / 1000, heard: stt.text.trim() };
  }),
);

results.sort((a, b) => a.cer - b.cer);
for (const r of results) {
  console.log(`${r.voice.padEnd(8)} CER ${(r.cer * 100).toFixed(1).padStart(5)}%  ${r.seconds.toFixed(1)} s`);
}
console.log(`\nBest: ${results[0].voice}\nWhisper heard: ${results[0].heard}`);
