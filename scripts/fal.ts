// Minimal fal.ai helpers shared by the asset scripts.
// Run scripts with `node --env-file=.env scripts/<name>.ts` so FAL_KEY is loaded (never logged).
import { fal } from "@fal-ai/client";
import { execFileSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

const key = process.env.FAL_KEY;
if (!key) throw new Error("FAL_KEY missing — put it in .env and run with `node --env-file=.env`");
fal.config({ credentials: key });

export async function falRun<T>(endpoint: string, input: Record<string, unknown>): Promise<T> {
  const { data } = await fal.subscribe(endpoint, { input });
  return data as T;
}

export async function download(url: string, dest: string): Promise<void> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Download failed (${res.status}) for ${url}`);
  await mkdir(dirname(dest), { recursive: true });
  await writeFile(dest, Buffer.from(await res.arrayBuffer()));
}

export function probeDurationMs(file: string): number {
  const out = execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]);
  return Math.round(parseFloat(out.toString().trim()) * 1000);
}

export type FalAudio = { audio: { url: string; content_type?: string } };

export const force = process.argv.includes("--force");
