// Scans public/renders/<shot>/ and writes src/generated/renders.json:
// { shot: { frames, anchors } } — Remotion uses a shot's 3D render only when it is complete.
// Run after Blender renders: npx tsx scripts/collect-renders.ts
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";

const timeline = JSON.parse(readFileSync("blender/timeline.json", "utf8")) as {
  scenes: Record<string, { duration: number }>;
};
const out: Record<string, { frames: number; anchors: Record<string, number[][]> }> = {};

for (const [shot, { duration }] of Object.entries(timeline.scenes)) {
  const dir = `public/renders/${shot}`;
  if (!existsSync(dir)) continue;
  const frames = readdirSync(dir).filter((f) => /^\d{4}\.jpg$/.test(f)).length;
  const status = frames >= duration ? "complete" : `incomplete (${frames}/${duration})`;
  console.log(`${shot.padEnd(12)} ${status}`);
  if (frames < duration) continue;
  const anchorsFile = `${dir}/anchors.json`;
  const anchors = existsSync(anchorsFile) ? JSON.parse(readFileSync(anchorsFile, "utf8")) : {};
  out[shot] = { frames, anchors };
}

writeFileSync("src/generated/renders.json", JSON.stringify(out));
console.log(`renders.json: ${Object.keys(out).join(", ") || "(none)"}`);
