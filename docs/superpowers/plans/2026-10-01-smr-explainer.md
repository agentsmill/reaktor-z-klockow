# SMR Explainer Animation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render a ~2-minute Polish educational animation (1920×1080 MP4) explaining how the BWRX-300 SMR backed by Michał Sołowow's SGE works.

**Architecture:** Remotion 4 project. Narration lives in `src/script.ts`; asset scripts call fal.ai (ElevenLabs TTS/Music/SFX, Nano Banana Pro) and write `public/` files plus `src/generated/voiceover.json`. Pure, unit-tested modules turn TTS character alignment into words, scene timing, visual cue frames and caption pages; scenes are SVG/React components whose animations are keyed to narration cues.

**Tech Stack:** Remotion 4.0.532 (`remotion`, `@remotion/cli`, `@remotion/transitions`, `@remotion/media`, `@remotion/google-fonts`, `@remotion/paths`), React 19, TypeScript, Vitest, `@fal-ai/client`, `world-atlas` + `topojson-client` (Poland outline), Node 25 (native TS for scripts), ffmpeg/ffprobe.

## Global Constraints

- Output: 1920×1080, 30 fps, H.264, duration ≈ 2:00–2:15.
- All on-screen and spoken text in Polish; fonts loaded with `latin-ext` subset (ą ć ę ł ń ó ś ź ż).
- Colour = meaning: neutron `#5CE1FF`, uranium `#9BE15D`, heat `#FF8A3D`, water `#2F7BFF`, steam `#E8F0F8`, electricity `#FFD447`, rods `#8A96A8`, PL accent `#E5484D`; bg `#0B1424`.
- AI stills labelled "Wizualizacja AI"; diagrams labelled "Schemat uproszczony".
- `say` and `show` texts must have the same number of whitespace-separated tokens (1:1 caption mapping).
- `FAL_KEY` only from `.env` via `node --env-file=.env`; never printed.
- No git commits (folder is not a repository; user did not ask for VCS).

---

### Task 1: Scaffold + tooling

**Files:** Create `package.json`, `tsconfig.json`, `remotion.config.ts`, `vitest.config.ts`, `src/index.ts`, `src/Root.tsx`.

- [ ] Install deps: `npm i remotion@4.0.532 @remotion/cli@4.0.532 @remotion/transitions@4.0.532 @remotion/media@4.0.532 @remotion/google-fonts@4.0.532 @remotion/paths@4.0.532 react react-dom @fal-ai/client world-atlas topojson-client` and dev `typescript @types/react @types/node vitest @types/topojson-client`.
- [ ] `src/Root.tsx` registers `SMRExplainer` (placeholder `AbsoluteFill`).
- [ ] Verify: `npx tsc --noEmit` exits 0; `npx remotion compositions src/index.ts` lists `SMRExplainer`.

### Task 2: Script (single source of truth)

**Files:** Create `src/script.ts`, Test `src/script.test.ts`.

**Interfaces — Produces:**
```ts
export type SceneId = "intro"|"smr"|"poland"|"fission"|"control"|"power"|"circulation"|"safety"|"why"|"outro";
export type CueDef = { id: string; word: string; nth?: number }; // prefix match on normalised token, nth is 1-based
export type SceneDef = { id: SceneId; chip: string; show: string; say?: string; cues: CueDef[]; leadIn?: number; tail?: number };
export const SCENES: SceneDef[];
export const sayText: (s: SceneDef) => string; // s.say ?? s.show
```
- [ ] Test (fails first): ids unique; for every scene `tokens(sayText(s)).length === tokens(s.show).length`; every cue word resolves in `sayText(s)` (uses `findCueIndex` from Task 4 — write this test in Task 4 if ordering matters).
- [ ] Fill `SCENES` with the narration from the spec (`docs/superpowers/specs/2026-10-01-smr-explainer-design.md`), `say` overrides: `SMR`→`Es-em-er`, `BWRX-300`→`be-wu-er-iks-trzysta`.

### Task 3: Timing core (TDD)

**Files:** Create `src/lib/words.ts`, `src/lib/timeline.ts`, `src/lib/cues.ts`, `src/lib/captions.ts` + `*.test.ts`.

**Interfaces — Produces:**
```ts
// words.ts
export type Alignment = { characters: string[]; character_start_times_seconds: number[]; character_end_times_seconds: number[] };
export type Word = { text: string; startMs: number; endMs: number };
export function wordsFromAlignment(chunks: Alignment[]): Word[];        // split on whitespace, keep punctuation
export function normalizeToken(t: string): string;                     // lowercase, strip non-letters/digits (keeps hyphen)
// timeline.ts
export type VoScene = { file: string; durationMs: number; words: Word[] };
export type VoiceoverData = { voice: string; scenes: Record<SceneId, VoScene> };
export type TimedScene = { id: SceneId; from: number; duration: number; leadIn: number };
export type Timeline = { scenes: TimedScene[]; total: number };
export const FPS = 30, TRANSITION = 12, DEFAULT_LEAD_IN = 12, DEFAULT_TAIL = 21;
export function buildTimeline(defs: SceneDef[], vo: VoiceoverData): Timeline;
// cues.ts
export function findCueIndex(words: {text: string}[], cue: CueDef): number;   // throws Error(`Cue "${cue.id}" ("${cue.word}" #n) not found`)
export function cueFrame(scene: TimedScene, words: Word[], cue: CueDef, fps?: number): number; // scene-relative frame
// captions.ts
export type CaptionWord = Word;                                        // text from `show`, timing from `say`
export type CaptionPage = { startMs: number; endMs: number; lines: CaptionWord[][] };
export function captionWords(show: string, sayWords: Word[]): CaptionWord[];
export function buildCaptionPages(words: CaptionWord[], opts?: { maxLineChars?: number; maxLines?: number }): CaptionPage[];
```
- [ ] **wordsFromAlignment** tests: `" Es-em-er to mały."` alignment → `[{Es-em-er,0,…},{to},{mały.}]`, multi-chunk concatenation, leading/trailing spaces ignored.
- [ ] **buildTimeline** tests: scene duration = `leadIn + ceil(durationMs·fps/1000) + tail`; `from[i] = from[i-1] + duration[i-1] − TRANSITION`; `total = from[last] + duration[last]`; per-scene `leadIn/tail` overrides respected.
- [ ] **findCueIndex** tests: prefix match handles inflection (`neutron` matches `neutronów,`), `nth: 2` picks second occurrence, missing cue throws with scene-readable message.
- [ ] **buildCaptionPages** tests: no line > 42 chars; ≤ 2 lines/page; page break after `.?!`; a line never ends with a one-letter word (`a i o u w z`, case-insensitive) — it moves to the next line; page `endMs` = next page `startMs` (last page: last word end + 400 ms).
- [ ] Implement until `npx vitest run` is green.

### Task 4: fal pipeline — voiceover

**Files:** Create `scripts/fal.ts`, `scripts/voiceover.ts`, `scripts/voice-audition.ts`; output `public/audio/vo/<id>.mp3`, `src/generated/voiceover.json`.

**Interfaces — Consumes:** `SCENES`, `sayText`, `wordsFromAlignment`. **Produces:** `voiceover.json` (`VoiceoverData`).
- [ ] `fal.ts`: `falRun<T>(endpoint, input): Promise<T>` (fal client `subscribe`, credentials from `process.env.FAL_KEY`, throws if missing), `download(url, dest)`, `probeDurationMs(file)` (ffprobe).
- [ ] `voice-audition.ts`: same Polish test paragraph (scene 4) with voices Brian, George, Bill, Daniel, Eric, Roger → transcribe each with `fal-ai/whisper` (`language: "pl"`) → print character-error-rate vs input + seconds; pick lowest CER among calm voices.
- [ ] `voiceover.ts`: per scene call `fal-ai/elevenlabs/tts/multilingual-v2` `{ text, voice, language_code: "pl", timestamps: true, stability: 0.55, similarity_boost: 0.75, style: 0.15, speed: 1.0, previous_text, next_text }`; skip existing unless `--force`; write JSON.
- [ ] Verify: 10 mp3 files; JSON word counts equal `tokens(say)`; total VO ≈ 110–130 s.

### Task 5: Theme + primitives + gallery

**Files:** `src/theme.ts`, `src/components/{SceneShell,Label,Neutron,Nucleus,FlowAlongPath,Turbine,Generator,House,ReactorVessel,PolandMap,Icons}.tsx`, `src/data/poland.ts` (generated by `scripts/poland-path.ts`), `src/Gallery.tsx` (still composition).
- [ ] `scripts/poland-path.ts` → projects `world-atlas/countries-50m.json` feature id `616` with equirectangular·cos(52°) into a 900×860 box → exports `POLAND_PATH`, `projectLonLat(lon, lat)`.
- [ ] Gallery still renders every primitive; Verify: `npx remotion still src/index.ts Gallery out/gallery.png` and inspect.

### Task 6: Assembly — Video.tsx + captions overlay

**Files:** `src/Video.tsx`, `src/components/Captions.tsx`, `src/lib/SceneContext.tsx` (`useCue(id) → frame`), update `Root.tsx` (duration from `buildTimeline`).
- [ ] TransitionSeries with `fade()` `linearTiming({durationInFrames: TRANSITION})`; each scene wraps its VO `<Audio>` in `<Sequence from={leadIn}>`; captions overlay uses absolute ms.
- [ ] Verify: draft render with placeholder scenes (`--scale=0.5`) — captions in sync with VO.

### Tasks 7–11: Scenes (visual TDD: render stills at cue frames → inspect → adjust)

| Task | Scenes | Key visuals (cue → action) |
|---|---|---|
| 7 | intro, smr | AI still Ken Burns + title; big plant vs SMR silhouettes (`kilka`), S/M/R letter mapping, factory→modules (`moduły`,`fabryce`) |
| 8 | poland, fission | map draw + 6 site dots; SGE+Orlen→OSGE (`Orlenem`); BWRX-300 card (`technologię`); investors card + 500 mln counter (`przedsiębiorcy`,`pół`); pellet→nucleus→neutron→split→heat→cascade→"1 pastylka ≈ 1 t węgla" |
| 9 | control, power | rods rise from below (`wsuwane`), 2 of 3 neutrons absorbed, k=1 meter (`dokładnie`); full BWR loop with particles, turbine spin, homes light up, kettle inset |
| 10 | circulation, safety | RPV close-up up/down flows, crossed pump, radiator inset; blackout, rods in, decay glow, IC pools gravity loop, 7-day counter, 35 m cutaway |
| 11 | why, outro | 24 h clock, weather, IPCC CO₂ bars, coal→SMR swap; icon chain recap, title, sources card |

Each task: implement scene files in `src/scenes/`, render 3–4 stills at the cue frames listed in the spec, inspect, fix.

### Task 12: Music, SFX, images

**Files:** `scripts/music.ts`, `scripts/sfx.ts`, `scripts/images.ts`; outputs under `public/audio/` and `public/img/`.
- [ ] Music: `fal-ai/elevenlabs/music` `{ prompt, music_length_ms: total + 2000, force_instrumental: true }`; mixed at 0.14 under VO, 0.35 in intro/outro, 1 s fades.
- [ ] SFX (`fal-ai/elevenlabs/sound-effects/v2`): whoosh, fission pop, rods clunk, turbine hum, power-down, sparkle.
- [ ] Images (`fal-ai/nano-banana-pro`, 16:9, 2K): intro plant at dawn; lit town at dusk.

### Task 13: Final render + QA

- [ ] `npx remotion render src/index.ts SMRExplainer out/smr-bwrx300.mp4 --codec=h264 --crf=18`.
- [ ] ffprobe duration/streams; `ffmpeg -af ebur128` integrated loudness ≈ −16…−14 LUFS.
- [ ] Whisper transcript of the rendered audio vs script (no mispronounced key terms).
- [ ] Extract 10 frames (one per scene) and inspect.
