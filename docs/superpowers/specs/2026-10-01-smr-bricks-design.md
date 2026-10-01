# SMR explainer v2 — "Reaktor z klocków" (toy-brick diorama in Blender)

**Date:** 2026-10-01 · **Status:** approved (whole video in bricks, scripts now + Blender MCP later,
narration kept + 2 brick lines). Supersedes the 2D visuals of `2026-10-01-smr-explainer-design.md`;
narration, facts, captions, audio and timing pipeline stay.

## Concept

The BWRX-300 explained as a miniature world of glossy toy bricks on a dark studio table: tilt-shift
depth of field, warm key light, colourful plastic. Bricks are not decoration — "modułowy" literally
means "built from ready-made pieces", so the metaphor teaches. Generic bricks only: no logo on studs,
no brand name, no minifigures.

## Visual system

- **Units:** 1 stud pitch = 1.0 BU (8 mm; `unit scale 0.008` so DOF behaves like real macro photography).
  Brick height 1.2, plate 0.4, stud Ø0.6 × 0.2, bevel 0.03.
- **Colour = meaning (carried over):** uranium = trans-green · neutron = glowing cyan · heat = trans-orange glow ·
  water = trans-blue · steam = trans-clear/white · electricity = glowing yellow · control rods = dark grey ·
  buildings = white / light bluish-grey · ground = green baseplate · river = trans-blue tiles · soil = brown/tan ·
  Polish sites = red.
- **Materials:** ABS = Principled (roughness 0.3, coat 0.25); trans = transmission 1.0, roughness 0.05, IOR 1.55;
  glow = emission + compositor glare.
- **Light:** warm area key (front-left), cool rim (back), soft fill; dark navy world (#0B1424) so 2D overlays,
  captions and labels from v1 sit naturally on top.
- **Camera:** 50–85 mm, f/2.8–5.6 at miniature scale, slow dollies/cranes, motion blur.
- **Render:** EEVEE (Metal, M5), 1920×1080, 30 fps, JPEG sequences → `public/renders/<scene>/0001.jpg…`.

## Pipeline

`src/script.ts` → TTS → `voiceover.json` → `npx tsx scripts/export-timeline.ts` → `blender/timeline.json`
(scene length + cue frames) → `blender/shots/<scene>.py` keyframes events on cue frames →
headless render → Remotion scene = image sequence + v1 overlays (labels, cards, chart) + captions + audio.

## Shots (cue → event)

1. **intro** — empty baseplate, one brick drops (click); bricks rain in and assemble the SMR plant by a trans-blue
   river (`homes`: houses light up across the river; `build`: last brick snaps on the roof). Title overlay.
2. **smr** — big plant (2 hyperboloid cooling towers + dome, thousands of bricks) beside the small SMR (`compare`, `big`);
   factory builds modules, toy truck delivers, modules stack into the reactor building (`modules`, `factory`, `bricks`).
3. **poland** — Poland map voxelised from Natural Earth onto a white plate island; 6 red beacon bricks pop up;
   v1 info cards stay as 2D overlays.
4. **fission** — fuel pellet brick → camera dives in → nucleus = voxel sphere of green bricks; cyan neutron hits,
   wobble, split into two voxel halves + orange flash + new neutrons; chain across a field of nuclei; pellet vs coal heap.
5. **control** — trans-green fuel columns; dark-grey rods rise from below and swallow neutrons; steady 1→1 chain.
6. **power** — cutaway vessel → pipes of grey round bricks with white steam studs → slope-brick turbine spins →
   generator → pylon → brick houses' windows glow; condenser + blue return flow; kettle analogy as 2D inset.
7. **circulation** — vessel half-shell: white round plates rise in the chimney, blue sink down the sides; pump crossed out (2D).
8. **safety** — houses go dark (blackout), rods in, core glow fades, pool of trans-blue tiles above with grey coil;
   steam up / water down; camera cranes down through brown soil layers to the shaft (~35 m).
9. **why** — day→night light cycle over the diorama; coal plant dismantled brick by brick and rebuilt as an SMR;
   CO₂ chart as 2D overlay.
10. **outro** — pull-back over the whole lit diorama at night; recap chain + title + sources as 2D overlay.

## Blender MCP (for the next session)

Install the `blender-mcp` add-on into Blender and register `uvx blender-mcp` with Claude Code, so the
user can open the `.blend` scenes and iterate live. Scripts remain the source of truth.

## Verification

- Low-res (640×360) preview stills at cue frames per shot before full renders.
- Frame counts of every sequence = scene duration from `timeline.json`.
- Final render QA as v1: duration, loudness, Whisper transcript diff, one frame per scene.
