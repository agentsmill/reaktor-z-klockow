# SMR explainer animation — design

**Date:** 2026-10-01 · **Status:** approved storyboard (10 scenes, ~2 min, 16:9, male PL voice)

## Goal

A short, strongly educational animation (Polish) explaining how the small modular reactor
that Michał Sołowow's SGE is developing in Poland works — GE Vernova Hitachi **BWRX-300** —
digestible for viewers with no technical background.

## Audience & success criteria

- Lay Polish audience; no prior knowledge of physics or energy.
- After watching, a viewer can retell: *uranium → heat → steam → turbine → electricity*,
  name 2 BWRX-300 traits (boiling water / natural circulation / passive cooling for 7 days),
  and knows who is behind the Polish project.
- Every factual claim traceable to a source (end card).

## Format

- 1920×1080, 30 fps, H.264 MP4, ~2:00–2:15.
- Polish voiceover (ElevenLabs multilingual v2 via fal.ai, calm male voice) + burned-in Polish captions
  synced from TTS word timestamps.
- Instrumental music bed (ElevenLabs Music via fal.ai) + a few subtle SFX (ElevenLabs SFX via fal.ai).
- 2 photoreal stills (Nano Banana Pro via fal.ai), always labelled "Wizualizacja AI".
- All technical diagrams are drawn in code (SVG) — labelled "Schemat uproszczony".

## Facts used (sources on end card)

| Fact | Source |
|---|---|
| BWRX-300: 870 MWt, ~300 MWe net; direct cycle; natural circulation (no recirculation pumps, tall chimney) | GE Vernova Hitachi, BWRX-300 General Description Rev. J (06/2026) |
| Isolation condensers in pools above the reactor: 7 days cooling with no power, no operator action | same |
| 57 control blades inserted from below; 240 GNF2 bundles; core 3.8 m; RPV ~27 m × 4.2 m | same |
| Reactor building ~35 m below ground (Darlington) | World Nuclear News, 04/2026 |
| OSGE = 50/50 Orlen + SGE (Sołowow); 6 sites with decisions-in-principle (Ostrołęka, Włocławek, Stawy Monowskie, Dąbrowa Górnicza, Kraków-Nowa Huta, Stalowa Wola) | osge.com; MKiŚ 12/2023 |
| After a long dispute, agreement confirmed 30.09.2026; Orlen stays partner in only 2 reactors, SGE develops the first unit (Stawy Monowskie, ~2031/32) on its own | XYZ 30.09.2026; Rzeczpospolita 01.10.2026 |
| 30.09.2026: Polish entrepreneurs declare ~PLN 500 m for SGE (Brzoska, Pawińscy, Wypychewicz, Gałęzewski & Doliński, Staniszewski & Dąbkowski, Brański, Wejchert); total raised ~PLN 2 bn | energetyka24.com, PAP/Bankier, 30.09–01.10.2026 |
| ~300–350 k households per unit | OSGE (2023), GE Vernova |
| 1 pellet ≈ energy of 1 t of coal | World Nuclear Association |
| Lifecycle CO₂ (median g/kWh): coal 820, gas 490, solar 48, nuclear 12, wind 11 | IPCC AR5 WGIII Annex III |

Deliberately **not** claimed: which Polish site is first (sources conflict: Włocławek vs Stawy Monowskie);
exact first-power date (only "początek lat 30.").

## Storyboard & narration

`show` = caption text; `say` = TTS text (differs only where acronyms need phonetic spelling).
Cues = words whose timestamps trigger visuals (prefix match, Polish inflection-safe).

1. **intro** — AI still (compact plant at dawn, Ken Burns) + title "Mały reaktor. Wielka energia."
   - *Mały reaktor jądrowy, który może zasilić setki tysięcy domów. Jak to działa?*
2. **smr** — big unit (>1000 MW) vs SMR (300 MW) silhouettes; factory → modules.
   - *SMR to mały reaktor modułowy: ma kilka razy mniejszą moc niż duży blok jądrowy, a jego moduły można produkować seryjnie w fabryce.* (say: "Es-em-er …")
   - cues: `mały`, `kilka`, `moduły`, `fabryce`
3. **poland** — map of Poland, 6 site dots; cards: SGE+Orlen → OSGE; BWRX-300; investors card 30.09.2026.
   - *W Polsce takie reaktory chce budować firma Michała Sołowowa — część z nich wspólnie z Orlenem. Wybrano technologię BWRX-300 o mocy trzystu megawatów. Projekt wsparli też polscy przedsiębiorcy: zainwestują w firmę Sołowowa około pół miliarda złotych.* (say: "be-wu-er-iks trzysta")
   - cues: `Sołowowa`, `Orlenem`, `technologię`, `przedsiębiorcy`, `pół`
4. **fission** — pellet → zoom → U-235 nucleus; neutron hits; split + heat flash + new neutrons; chain; "1 pastylka ≈ 1 t węgla".
   - *Paliwem są małe pastylki uranu. Gdy neutron trafi w jądro uranu, jądro rozpada się na dwa mniejsze — to rozszczepienie. Uwalnia się mnóstwo ciepła i dwa, trzy nowe neutrony, które rozbijają kolejne jądra. To reakcja łańcuchowa. Jedna pastylka daje tyle energii, co tona węgla.*
   - cues: `pastylki`, `neutron`, `rozpada`, `ciepła`, `nowe`, `kolejne`, `łańcuchowa`, `tona`
5. **control** — fuel lattice; control blades rise from below; surplus neutrons absorbed; k = 1 gauge.
   - *Nadmiar neutronów pochłaniają pręty sterujące, wsuwane od dołu. Gdy każde rozszczepienie wywołuje dokładnie jedno kolejne, reaktor pracuje stabilnie.*
   - cues: `pochłaniają`, `wsuwane`, `dokładnie`, `stabilnie`
6. **power** — full loop: RPV → steam line → turbine → generator → grid → homes; condenser → feedwater; kettle+pinwheel inset.
   - *Ciepło zagotowuje wodę wprost w reaktorze — stąd nazwa: reaktor z wrzącą wodą. Para rozkręca turbinę, a turbina napędza generator prądu. Jak para z czajnika, która kręci wiatraczkiem. Potem para skrapla się i wraca do reaktora jako woda.*
   - cues: `zagotowuje`, `wrzącą`, `turbinę`, `generator`, `czajnika`, `skrapla`, `wraca`
7. **circulation** — RPV close-up: up through chimney, down the downcomer; crossed-out pump; radiator inset.
   - *Co ciekawe, w środku reaktora woda krąży bez pomp. Gorąca i pełna pary unosi się wysokim kominem, a chłodniejsza opada po bokach — jak powietrze nad kaloryferem.*
   - cues: `pomp`, `unosi`, `opada`, `kaloryferem`
8. **safety** — blackout; rods in; decay-heat glow; isolation condensers in pools above; gravity loop; "7 dni" counter; underground cutaway "~35 m".
   - *A co, jeśli zabraknie prądu? Pręty wsuwają się automatycznie i reakcja gaśnie. Paliwo nadal trochę grzeje, więc ciepło odbierają skraplacze w basenach z wodą nad reaktorem. Para unosi się, skrapla i sama spływa z powrotem. Bez prądu i bez ludzi — przez co najmniej siedem dni. A sam reaktor stoi głęboko pod ziemią.*
   - cues: `zabraknie`, `wsuwają`, `grzeje`, `skraplacze`, `unosi`, `spływa`, `siedem`, `ziemią`
9. **why** — 24 h clock; weather icons; lifecycle CO₂ bar chart (IPCC); coal plant → SMR swap; AI still of lit town.
   - *Taki reaktor daje prąd całą dobę, bez względu na pogodę, i nie emituje dwutlenku węgla podczas pracy. Może też zastąpić stare elektrownie węglowe.*
   - cues: `dobę`, `pogodę`, `dwutlenku`, `zastąpić`
10. **outro** — icon chain uran → ciepło → para → turbina → prąd; title; sources card.
    - *Podsumujmy: uran daje ciepło, ciepło zamienia wodę w parę, para kręci turbiną, a turbina wytwarza prąd. Tak działa mały reaktor modułowy.*
    - cues: `uran`, `ciepło`(2nd), `parę`, `turbiną`, `prąd`, `Tak`

## Visual system

- Background `#0B1424` + faint 48 px blueprint grid + vignette. Text `#EEF2F7` / `#9FB0C8`.
- **Colour = meaning, everywhere:** neutron `#5CE1FF` · uranium `#9BE15D` · heat `#FF8A3D` · water `#2F7BFF` ·
  steam `#E8F0F8` · electricity `#FFD447` · control rods `#8A96A8` · Polish accent `#E5484D` (map only).
- Type: **Unbounded** (titles) + **Manrope** (body, captions) — both with `latin-ext` for ą ć ę ł ń ó ś ź ż.
- Scene chip top-left ("4/10 · Rozszczepienie"); "Schemat uproszczony" tag on diagrams.
- Motion: `spring({damping: 200})` reveals, particles along SVG paths (`@remotion/paths`), 12-frame fades between scenes.
- Captions: bottom-centre, ≤ 2 lines (~42 chars/line), split at phrase boundaries, active word highlighted in electricity-yellow;
  Polish rule: one-letter words (a, i, o, u, w, z) never end a line.

## Architecture

```
scripts/            asset generation (Node 25 native TS, `node --env-file=.env`)
  fal.ts            tiny wrapper: run endpoint, download file
  voiceover.ts      per-scene TTS + word timestamps → public/audio/vo/*.mp3, src/generated/voiceover.json
  music.ts          instrumental bed sized to the final timeline → public/audio/music.mp3
  sfx.ts            ~6 short effects → public/audio/sfx/*.mp3
  images.ts         2 stills → public/img/*.jpg
src/
  script.ts         ⟵ single source of truth: scenes, show/say text, cues
  timeline.ts       scene starts/durations from VO lengths (+lead-in/tail, transition overlap)
  cues.ts           word → frame resolution (useCue hook via SceneContext)
  captions.ts       word timestamps → caption pages
  theme.ts          colours, fonts
  components/       primitives (Atom, Neutron, ReactorVessel, Turbine, PolandMap, …)
  scenes/           one file per scene (10)
  Video.tsx         TransitionSeries + VO + music + SFX + caption overlay
  Root.tsx          <Composition id="SMRExplainer">
```

Data flow: `script.ts` → `voiceover.ts` (fal) → `voiceover.json` → `timeline.ts` → `Video.tsx`.
Visual timing follows the narration automatically (cues), so editing a sentence and regenerating VO re-syncs everything.

## Error handling

- Asset scripts are idempotent: skip files that exist unless `--force`; fail loudly on non-2xx from fal.
- Missing cue word → throw at render time with scene id + word (no silent desync).
- `FAL_KEY` only read from `.env`; never logged.

## Verification

- `tsc --noEmit` clean; Remotion Studio loads.
- Render stills at each scene's key cue frames and inspect visually.
- Transcribe the final VO with Whisper (fal) and compare with `say` text to catch mispronunciations.
- Final render: check duration, audio streams and loudness (ffprobe / ffmpeg ebur128).
