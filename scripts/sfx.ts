// Short, subtle sound effects (ElevenLabs SFX v2 via fal.ai).
import { existsSync } from "node:fs";
import { download, falRun, force, type FalAudio } from "./fal.ts";

const SFX: Record<string, { text: string; seconds: number }> = {
  whoosh: { text: "Soft airy whoosh transition, gentle and short, clean, no reverb tail", seconds: 1 },
  pop: { text: "Small soft energetic pop with a tiny shimmering sparkle, subtle sci-fi user-interface sound", seconds: 0.7 },
  clunk: { text: "Heavy metal rods sliding upward into place and locking with a solid mechanical clunk, short", seconds: 1.5 },
  hum: { text: "Smooth steady low hum of a large spinning steam turbine, calm, seamless", seconds: 6 },
  powerdown: { text: "Electrical power failure: a humming machine winds down to silence with a soft electric click", seconds: 2 },
  sparkle: { text: "Gentle electric sparkle as many house lights switch on, soft and pleasant", seconds: 1.2 },
  tick: { text: "Single soft clean user-interface tick, very short", seconds: 0.5 },
  click: { text: "A single small plastic toy brick snapping firmly onto another brick: crisp, satisfying click, close-up, dry", seconds: 0.5 },
  clatter: { text: "Many small plastic toy bricks raining down onto a table and clicking together, playful and light, no music", seconds: 4 },
};

await Promise.all(
  Object.entries(SFX).map(async ([name, { text, seconds }]) => {
    const dest = `public/audio/sfx/${name}.mp3`;
    if (!force && existsSync(dest)) return console.log(`skip ${dest}`);
    const result = await falRun<FalAudio>("fal-ai/elevenlabs/sound-effects/v2", {
      text,
      duration_seconds: seconds,
      prompt_influence: 0.5,
    });
    await download(result.audio.url, dest);
    console.log(`wrote ${dest}`);
  }),
);
