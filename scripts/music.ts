// Instrumental score (ElevenLabs Music via fal.ai) whose sections follow the scenes' dramatic arc.
// Section lengths come from blender/timeline.json so musical changes land on scene changes.
import { existsSync, readFileSync } from "node:fs";
import { download, falRun, force, probeDurationMs, type FalAudio } from "./fal.ts";

const DEST = "public/audio/music.mp3";
const FPS = 30;
const TRANSITION = 12;

const tl = JSON.parse(readFileSync("blender/timeline.json", "utf8")) as { scenes: Record<string, { duration: number }> };
const order = ["intro", "smr", "poland", "fission", "control", "power", "circulation", "safety", "why", "outro"];
const starts: Record<string, number> = {};
let cursor = 0;
for (const [i, id] of order.entries()) {
  starts[id] = i === 0 ? 0 : cursor - TRANSITION;
  cursor = starts[id] + tl.scenes[id].duration;
}
const ms = (frames: number) => Math.round((frames / FPS) * 1000);
const at = (id: string) => ms(starts[id]);
const total = ms(cursor) + 2500;

const sections = [
  { section_name: "First brick", until: at("smr"), styles: ["delicate solo felt piano notes", "tiny glockenspiel plucks", "sense of wonder", "very sparse"] },
  { section_name: "Building", until: at("fission"), styles: ["playful marimba ostinato", "pizzicato strings", "light shaker percussion", "growing energy", "curious and joyful"] },
  { section_name: "Inside the atom", until: at("power"), styles: ["mysterious shimmering synth arpeggios", "soft pulsing bass", "scientific wonder", "glassy textures"] },
  { section_name: "Engine", until: at("safety") + 1200, styles: ["confident driving rhythm", "warm cellos", "steady kick and claps, soft", "momentum"] },
  { section_name: "Blackout", until: at("safety") + 7000, styles: ["sudden quiet", "suspended low string pad", "single held note", "gentle tension, not scary"] },
  { section_name: "Passive safety", until: at("why"), styles: ["reassuring warm strings swell", "calm piano", "hopeful"] },
  { section_name: "Finale", until: total, styles: ["uplifting cinematic finale", "full warm strings and piano", "inspiring", "gentle resolve and soft ending"] },
];

let prev = 0;
const plan = {
  positive_global_styles: ["cinematic educational score", "major key", "instrumental", "modern and optimistic", "around 100 BPM"],
  negative_global_styles: ["vocals", "lyrics", "aggressive drums", "horror", "distorted guitars"],
  sections: sections.map((s) => {
    const duration_ms = Math.max(3000, s.until - prev);
    prev = s.until;
    return { section_name: s.section_name, positive_local_styles: s.styles, negative_local_styles: ["vocals"], duration_ms, lines: [] };
  }),
};

if (!force && existsSync(DEST)) {
  console.log(`skip ${DEST} (use --force)`);
} else {
  console.log(plan.sections.map((s) => `${s.section_name}: ${(s.duration_ms / 1000).toFixed(1)} s`).join("\n"));
  const result = await falRun<FalAudio>("fal-ai/elevenlabs/music", {
    composition_plan: plan,
    respect_sections_durations: true, // instrumental via empty `lines` + negative "vocals" (force_instrumental is not allowed with a plan)
  });
  await download(result.audio.url, DEST);
  console.log(`wrote ${DEST} (${(probeDurationMs(DEST) / 1000).toFixed(1)} s)`);
}
