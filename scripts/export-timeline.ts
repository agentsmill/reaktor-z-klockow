// Exports scene timing + cue frames for the Blender shot scripts (blender/timeline.json).
// Run: npx tsx scripts/export-timeline.ts   (tsx resolves the extensionless src imports)
import { readFileSync, writeFileSync } from "node:fs";
import { SCENES } from "../src/script";
import { captionWords } from "../src/lib/captions";
import { cueFrame } from "../src/lib/cues";
import { buildTimeline, FPS, type VoiceoverData } from "../src/lib/timeline";

const vo = JSON.parse(readFileSync("src/generated/voiceover.json", "utf8")) as VoiceoverData;
const timeline = buildTimeline(SCENES, vo);

const scenes = Object.fromEntries(
  SCENES.map((def, i) => {
    const timed = timeline.scenes[i];
    const words = captionWords(def.show, vo.scenes[def.id].words);
    const cues = Object.fromEntries(def.cues.map((c) => [c.id, cueFrame(timed, words, c, FPS)]));
    return [def.id, { duration: timed.duration, leadIn: timed.leadIn, voEnd: timed.leadIn + timed.voFrames, cues }];
  }),
);

writeFileSync("blender/timeline.json", JSON.stringify({ fps: FPS, total: timeline.total, scenes }, null, 1));
for (const [id, s] of Object.entries(scenes)) console.log(`${id.padEnd(12)} ${String(s.duration).padStart(4)}f  ${JSON.stringify(s.cues)}`);
console.log(`total ${timeline.total} frames (${(timeline.total / FPS).toFixed(1)} s)`);
