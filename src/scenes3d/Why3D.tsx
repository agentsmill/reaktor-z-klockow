import { Easing, useCurrentFrame, useVideoConfig } from "remotion";
import { BrickPlate, useAnchor } from "../components/BrickPlate";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { Tag } from "../components/Tag";
import { enter, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { CO2, WeatherIcon } from "../scenes/Why";
import { BODY, C, DISPLAY } from "../theme";

const panel: React.CSSProperties = {
  position: "absolute",
  borderRadius: 22,
  background: "rgba(10, 18, 32, 0.78)",
  border: `1px solid ${C.panelEdge}`,
  fontFamily: BODY,
  boxSizing: "border-box",
};

/** 24/7 + weather (left), compact IPCC chart (top-right), coal → SMR label following the 3D site. */
export const Why3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const clockT = enter(frame, cue("allDay") - 8, fps, 16);
  const hand = progress(frame, cue("allDay"), cue("allDay") + 92, Easing.inOut(Easing.quad)) * 360;
  const weatherT = (i: number) => enter(frame, cue("weather") - 4 + i * 5, fps, 12);
  const chartT = enter(frame, cue("co2") - 10, fps, 16);
  const bar = (i: number) => progress(frame, cue("co2") + i * 6, cue("co2") + 30 + i * 6, Easing.out(Easing.cubic));
  const site = useAnchor("why", "coal_site", { x: 640, y: 420 });
  const newSmr = enter(frame, cue("replace") + 52, fps, 16);

  return (
    <SceneShell background={<BrickPlate shot="why" />}>
      <Sfx at={cue("replace") - 4} name="clatter" gain={0.8} />
      <Sfx at={cue("replace") + 70} name="click" />

      <div style={{ ...panel, left: 110, top: 140, padding: "18px 26px", display: "flex", alignItems: "center", gap: 22, ...riseStyle(clockT, 14) }}>
        <svg width={120} height={120} viewBox="-100 -100 200 200">
          <circle r={92} fill={C.panel} stroke={C.text} strokeWidth={6} />
          {Array.from({ length: 12 }, (_, i) => (
            <line key={i} x1={0} y1={-80} x2={0} y2={-66} stroke={C.muted} strokeWidth={5} strokeLinecap="round" transform={`rotate(${i * 30})`} />
          ))}
          <line x1={0} y1={0} x2={0} y2={-70} stroke={C.electricity} strokeWidth={9} strokeLinecap="round" transform={`rotate(${hand})`} />
          <circle r={11} fill={C.electricity} />
        </svg>
        <div>
          <div style={{ fontFamily: DISPLAY, fontSize: 60, fontWeight: 700, color: C.text, lineHeight: 1 }}>24/7</div>
          <div style={{ fontSize: 24, fontWeight: 700, color: C.muted, marginTop: 6 }}>prąd przez całą dobę</div>
        </div>
      </div>

      <div style={{ ...panel, left: 110, top: 330, padding: "16px 22px", opacity: weatherT(0) }}>
        <div style={{ display: "flex", gap: 12 }}>
          {(["sun", "rain", "moon", "snow"] as const).map((k, i) => (
            <div key={k} style={{ ...riseStyle(weatherT(i), 12), transform: `scale(0.82) ${riseStyle(weatherT(i), 12).transform}` }}>
              <WeatherIcon kind={k} />
            </div>
          ))}
        </div>
        <div style={{ fontSize: 24, fontWeight: 700, color: C.muted, marginTop: 4 }}>bez względu na pogodę</div>
      </div>

      <div style={{ ...panel, left: 1190, top: 130, width: 620, padding: "22px 28px", ...riseStyle(chartT, 18) }}>
        <div style={{ fontSize: 24, fontWeight: 800, color: C.text }}>Emisja CO₂ w całym cyklu życia</div>
        <div style={{ fontSize: 17, fontWeight: 600, color: C.muted, marginTop: 2 }}>g CO₂ na kWh · mediana wg IPCC (AR5)</div>
        <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 9 }}>
          {CO2.map((row, i) => (
            <div key={row.label} style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 140, fontSize: 20, fontWeight: row.highlight ? 800 : 600, color: row.highlight ? C.text : C.muted }}>{row.label}</div>
              <div style={{ width: Math.max(4, (row.value / 820) * 330 * bar(i)), height: 22, borderRadius: 5, background: row.highlight ? C.uranium : C.steel, opacity: 0.25 + 0.75 * bar(i) }} />
              <div style={{ fontSize: 20, fontWeight: 800, color: row.highlight ? C.uranium : C.text, opacity: bar(i) }}>{Math.round(row.value * bar(i))}</div>
            </div>
          ))}
        </div>
      </div>

      <Tag x={site.x} y={site.y - 70} anchor="center" text="nowy SMR" sub="w miejscu starej elektrowni węglowej" t={newSmr * (site.visible ? 1 : 0)} color={C.uranium} size={30} />
    </SceneShell>
  );
};
