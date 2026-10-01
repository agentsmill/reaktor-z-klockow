import { useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate, useAnchor } from "../components/BrickPlate";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { enter, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { PolandCards } from "../scenes/Poland";
import { BODY, C } from "../theme";

/** Anchor names exported by blender/shots/poland.py; label side avoids collisions in the south. */
const SITES = [
  { anchor: "wloclawek", name: "Włocławek", side: "right" },
  { anchor: "ostroleka", name: "Ostrołęka", side: "right" },
  { anchor: "stalowa_wola", name: "Stalowa Wola", side: "right" },
  { anchor: "krakow", name: "Kraków-Nowa Huta", side: "right" },
  { anchor: "dabrowa", name: "Dąbrowa Górnicza", side: "left" },
  { anchor: "stawy", name: "Stawy Monowskie", side: "left", dy: 22 },
  { anchor: "warszawa", name: "Warszawa", side: "right", muted: true },
] as const;

const SiteLabel: React.FC<{ site: (typeof SITES)[number]; t: number }> = ({ site, t }) => {
  const p = useAnchor("poland", site.anchor, { x: 500, y: 400 });
  if (t <= 0 || !p.visible) return null;
  const right = site.side === "right";
  const dy = "dy" in site ? site.dy : 0;
  return (
    <div
      style={{
        position: "absolute",
        left: p.x + (right ? 22 : -22),
        top: p.y - 34 + dy,
        transform: `translate(${right ? "0" : "-100%"}, -50%)`,
        opacity: t,
        fontFamily: BODY,
        fontSize: 21,
        fontWeight: 800,
        color: "muted" in site ? C.muted : C.text,
        whiteSpace: "nowrap",
        textShadow: "0 2px 8px rgba(6,12,23,0.95), 0 0 2px rgba(6,12,23,0.9)",
      }}
    >
      {site.name}
    </div>
  );
};

/** Brick map of Poland with site beacons (left half) and the three info cards (right). */
export const Poland3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const legend = enter(frame, cue("map") + 85, fps, 16);

  return (
    <SceneShell background={<BrickPlate shot="poland" />}>
      <Sfx at={28} name="clatter" />
      {[72, 76, 80, 84, 88, 92].map((f) => (
        <Sfx key={f} at={f} name="click" gain={0.7} />
      ))}
      <Sfx at={cue("investors") + 2} name="tick" />
      <Sfx at={cue("amount") + 2} name="tick" />
      {SITES.map((site, i) => (
        <SiteLabel key={site.anchor} site={site} t={enter(frame, 80 + i * 4, fps, 12)} />
      ))}
      <div style={{ position: "absolute", left: 110, top: 806, fontFamily: BODY, fontSize: 22, fontWeight: 700, color: C.muted, ...riseStyle(legend, 10) }}>
        <span style={{ color: C.accent }}>●</span> 6 lokalizacji z decyzją zasadniczą rządu (2023)
      </div>
      <PolandCards />
    </SceneShell>
  );
};
