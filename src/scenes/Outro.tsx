import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { spinAngle } from "../components/Machines";
import { RecapChain } from "../components/RecapChain";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { enter, lerp, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

export const STEPS = [
  { cue: "uranium", label: "uran", color: C.uranium },
  { cue: "heat", label: "ciepło", color: C.heat },
  { cue: "steam", label: "para", color: C.steam },
  { cue: "turbine", label: "turbina", color: C.steel },
  { cue: "electricity", label: "prąd", color: C.electricity },
] as const;
export const XS = [400, 680, 960, 1240, 1520];

export const SOURCES =
  "Źródła: GE Vernova Hitachi — BWRX-300 General Description (06/2026) · OSGE · World Nuclear Association · " +
  "IPCC AR5 WGIII · energetyka24.com, XYZ, Rzeczpospolita, PAP/Bankier (30.09–01.10.2026)";
export const CREDITS = "Animacja edukacyjna · schematy uproszczone · wizualizacje AI (fal.ai) · głos AI (ElevenLabs)";
export const CREDITS_3D = "Animacja edukacyjna · schematy uproszczone · grafika 3D: Blender · głos i muzyka: AI (ElevenLabs, fal.ai)";

export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cue = useCues();

  const lift = progress(frame, cue("title") - 6, cue("title") + 20);
  const chainY = lerp(420, 300, lift);
  const chainScale = lerp(1, 0.82, lift);
  const titleT = enter(frame, cue("title") - 2, fps, 22);
  const sourcesT = enter(frame, cue("title") + 75, fps, 24);
  const fadeOut = interpolate(frame, [durationInFrames - 30, durationInFrames], [0, 1], { extrapolateLeft: "clamp" });
  const angle = spinAngle(frame, (f) => (f > cue("turbine") ? 8 : 0));

  return (
    <SceneShell>
      {STEPS.map((s) => (
        <Sfx key={s.cue} at={cue(s.cue) - 4} name="tick" />
      ))}
      <RecapChain y={chainY} scale={chainScale} at={STEPS.map((st) => cue(st.cue))} turbineAngle={angle} />

      <div style={{ position: "absolute", top: 560, left: 0, right: 0, textAlign: "center", ...riseStyle(titleT, 24) }}>
        <div style={{ fontFamily: DISPLAY, fontSize: 86, fontWeight: 700, color: C.text }}>Tak działa SMR.</div>
        <div style={{ fontFamily: BODY, fontSize: 36, fontWeight: 700, color: C.muted, marginTop: 10 }}>
          Mały reaktor. <span style={{ color: C.electricity }}>Wielka energia.</span>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 70,
          left: 160,
          right: 160,
          textAlign: "center",
          fontFamily: BODY,
          color: C.faint,
          ...riseStyle(sourcesT, 10),
        }}
      >
        <div style={{ fontSize: 21, fontWeight: 600, lineHeight: 1.5 }}>{SOURCES}</div>
        <div style={{ fontSize: 19, fontWeight: 600, marginTop: 8 }}>{CREDITS}</div>
      </div>

      <AbsoluteFill style={{ backgroundColor: "#000", opacity: fadeOut }} />
    </SceneShell>
  );
};
