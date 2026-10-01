// Generates one voiceover clip per scene (ElevenLabs multilingual v2 via fal.ai)
// with character timestamps, then writes src/generated/voiceover.json — the file
// the whole timeline is computed from. Existing clips are reused unless --force.
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { download, falRun, force, probeDurationMs, type FalAudio } from "./fal.ts";
import { SCENES, sayText } from "../src/script.ts";
import { tokens, wordsFromAlignment, type Alignment } from "../src/lib/words.ts";

export const VOICE = "Brian";
const SETTINGS = { stability: 0.55, similarity_boost: 0.75, style: 0.15, speed: 1.05 };
const AUDIO_DIR = "public/audio/vo";
const CACHE_DIR = "out/cache/vo";
const OUT_JSON = "src/generated/voiceover.json";

await mkdir(CACHE_DIR, { recursive: true });
await mkdir("src/generated", { recursive: true });

const scenes: Record<string, unknown> = {};

for (const [i, scene] of SCENES.entries()) {
  const text = sayText(scene);
  const mp3 = `${AUDIO_DIR}/${scene.id}.mp3`;
  const cache = `${CACHE_DIR}/${scene.id}.json`;

  let alignment: Alignment[];
  if (!force && existsSync(mp3) && existsSync(cache)) {
    alignment = JSON.parse(await readFile(cache, "utf8"));
  } else {
    const result = await falRun<FalAudio & { timestamps: Alignment[] }>("fal-ai/elevenlabs/tts/multilingual-v2", {
      text,
      voice: VOICE,
      language_code: "pl",
      timestamps: true,
      previous_text: i > 0 ? sayText(SCENES[i - 1]) : undefined,
      next_text: i < SCENES.length - 1 ? sayText(SCENES[i + 1]) : undefined,
      ...SETTINGS,
    });
    await download(result.audio.url, mp3);
    alignment = result.timestamps;
    await writeFile(cache, JSON.stringify(alignment));
  }

  const words = wordsFromAlignment(alignment);
  const expected = tokens(text).length;
  if (words.length !== expected) {
    throw new Error(`${scene.id}: TTS returned ${words.length} words, script has ${expected}`);
  }
  const durationMs = probeDurationMs(mp3);
  scenes[scene.id] = { file: `audio/vo/${scene.id}.mp3`, durationMs, words };
  console.log(`${scene.id.padEnd(12)} ${(durationMs / 1000).toFixed(2)} s  ${words.length} words`);
}

await writeFile(OUT_JSON, JSON.stringify({ voice: VOICE, scenes }, null, 1));
console.log(`\nWrote ${OUT_JSON}`);
