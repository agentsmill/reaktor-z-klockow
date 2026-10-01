import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Badge } from "../components/Badge";
import { CoalPlant, SmrPlant } from "../components/Buildings";
import { SceneShell } from "../components/SceneShell";
import { enter, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

/** Lifecycle emissions, median g CO₂-eq/kWh — IPCC AR5 WGIII Annex III, Table A.III.2. */
export const CO2 = [
  { label: "Węgiel", value: 820 },
  { label: "Gaz ziemny", value: 490 },
  { label: "Fotowoltaika", value: 48 },
  { label: "Atom", value: 12, highlight: true },
  { label: "Wiatr", value: 11 },
];

export const WeatherIcon: React.FC<{ kind: "sun" | "rain" | "moon" | "snow" }> = ({ kind }) => (
  <svg width={84} height={84} viewBox="-42 -42 84 84">
    <circle r={40} fill={C.panel} stroke={C.panelEdge} strokeWidth={2} />
    {kind === "sun" && (
      <g stroke="#FFC861" strokeWidth={4} strokeLinecap="round">
        <circle r={11} fill="#FFC861" stroke="none" />
        {Array.from({ length: 8 }, (_, i) => {
          const a = (i * Math.PI) / 4;
          return <line key={i} x1={Math.cos(a) * 17} y1={Math.sin(a) * 17} x2={Math.cos(a) * 24} y2={Math.sin(a) * 24} />;
        })}
      </g>
    )}
    {kind === "rain" && (
      <g>
        <path d="M-20,4 a12,12 0 0 1 6,-20 a15,15 0 0 1 28,4 a10,10 0 0 1 4,16 Z" fill="#B9C5D8" />
        {[-12, 0, 12].map((x) => (
          <line key={x} x1={x} y1={12} x2={x - 4} y2={22} stroke={C.water} strokeWidth={4} strokeLinecap="round" />
        ))}
      </g>
    )}
    {kind === "moon" && <path d="M6,-22 a22,22 0 1 0 16,30 a17,17 0 1 1 -16,-30 Z" fill="#D8E1EE" />}
    {kind === "snow" && (
      <g stroke="#D8E1EE" strokeWidth={4} strokeLinecap="round">
        {[0, 60, 120].map((a) => (
          <line key={a} x1={0} y1={-20} x2={0} y2={20} transform={`rotate(${a})`} />
        ))}
      </g>
    )}
  </svg>
);

export const Why: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cue = useCues();

  const clockT = enter(frame, cue("allDay") - 8, fps, 16);
  const hand = progress(frame, cue("allDay"), cue("allDay") + 70, Easing.inOut(Easing.quad)) * 360;
  const weatherT = (i: number) => enter(frame, cue("weather") - 4 + i * 5, fps, 12);
  const chartT = enter(frame, cue("co2") - 10, fps, 16);
  const bar = (i: number) => progress(frame, cue("co2") + i * 6, cue("co2") + 30 + i * 6, Easing.out(Easing.cubic));
  const swap = progress(frame, cue("replace") + 4, cue("replace") + 30);
  const plantsT = enter(frame, cue("replace") - 10, fps, 14);

  const background = (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: C.bgDeep }}>
      <Img
        src={staticFile("img/why-town.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${interpolate(frame, [0, durationInFrames], [1.05, 1.12])})`,
        }}
      />
      <AbsoluteFill style={{ background: "rgba(6, 12, 23, 0.66)" }} />
    </AbsoluteFill>
  );

  return (
    <SceneShell background={background}>
      {/* 24/7 */}
      <div style={{ position: "absolute", left: 120, top: 190, display: "flex", alignItems: "center", gap: 34, ...riseStyle(clockT, 16) }}>
        <svg width={200} height={200} viewBox="-100 -100 200 200">
          <circle r={92} fill={C.panel} stroke={C.text} strokeWidth={5} />
          {Array.from({ length: 12 }, (_, i) => (
            <line key={i} x1={0} y1={-80} x2={0} y2={-68} stroke={C.muted} strokeWidth={4} strokeLinecap="round" transform={`rotate(${i * 30})`} />
          ))}
          <path d={`M0,0 L0,-84 A84,84 0 ${hand > 180 ? 1 : 0} 1 ${84 * Math.sin((hand * Math.PI) / 180)},${-84 * Math.cos((hand * Math.PI) / 180)} Z`} fill={C.electricity} opacity={0.18} />
          <line x1={0} y1={0} x2={0} y2={-70} stroke={C.electricity} strokeWidth={7} strokeLinecap="round" transform={`rotate(${hand})`} />
          <circle r={9} fill={C.electricity} />
        </svg>
        <div>
          <div style={{ fontFamily: DISPLAY, fontSize: 84, fontWeight: 700, color: C.text, lineHeight: 1 }}>24/7</div>
          <div style={{ fontFamily: BODY, fontSize: 30, fontWeight: 700, color: C.muted, marginTop: 8 }}>prąd przez całą dobę</div>
        </div>
      </div>

      {/* weather */}
      <div style={{ position: "absolute", left: 120, top: 450 }}>
        <div style={{ display: "flex", gap: 18 }}>
          {(["sun", "rain", "moon", "snow"] as const).map((k, i) => (
            <div key={k} style={riseStyle(weatherT(i), 14)}>
              <WeatherIcon kind={k} />
            </div>
          ))}
        </div>
        <div style={{ fontFamily: BODY, fontSize: 30, fontWeight: 700, color: C.muted, marginTop: 14, ...riseStyle(weatherT(3), 10) }}>
          bez względu na pogodę
        </div>
      </div>

      {/* CO2 chart */}
      <div
        style={{
          position: "absolute",
          left: 900,
          top: 170,
          width: 900,
          padding: "28px 36px",
          boxSizing: "border-box",
          borderRadius: 22,
          background: C.panel,
          border: `1px solid ${C.panelEdge}`,
          fontFamily: BODY,
          ...riseStyle(chartT, 20),
        }}
      >
        <div style={{ fontSize: 30, fontWeight: 800, color: C.text }}>Emisja CO₂ w całym cyklu życia</div>
        <div style={{ fontSize: 20, fontWeight: 600, color: C.muted, marginTop: 4 }}>gramy CO₂ na kWh · mediana wg IPCC (AR5)</div>
        <div style={{ marginTop: 22, display: "flex", flexDirection: "column", gap: 14 }}>
          {CO2.map((row, i) => {
            const w = (row.value / 820) * 520 * bar(i);
            const color = row.highlight ? C.uranium : C.steel;
            return (
              <div key={row.label} style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ width: 170, fontSize: 24, fontWeight: row.highlight ? 800 : 600, color: row.highlight ? C.text : C.muted }}>{row.label}</div>
                <div style={{ width: Math.max(4, w), height: 28, borderRadius: 6, background: color, opacity: 0.25 + 0.75 * bar(i) }} />
                <div style={{ fontSize: 24, fontWeight: 800, color: row.highlight ? C.uranium : C.text, opacity: bar(i) }}>{Math.round(row.value * bar(i))}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* coal plant replaced in place by an SMR */}
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <g opacity={plantsT}>
          <line x1={1000} x2={1700} y1={840} y2={840} stroke={C.line} strokeWidth={3} />
          <CoalPlant x={1180} y={840} s={0.62} frame={frame} smoke={1 - swap} opacity={1 - swap} />
          <g opacity={swap} transform={`translate(0, ${(1 - swap) * 30})`}>
            <SmrPlant x={1210} y={840} s={0.85} />
          </g>
        </g>
      </svg>
      <div
        style={{
          position: "absolute",
          left: 120,
          top: 700,
          width: 700,
          fontFamily: BODY,
          fontSize: 30,
          fontWeight: 700,
          color: C.text,
          ...riseStyle(plantsT, 12),
        }}
      >
        <span style={{ color: C.muted }}>może stanąć tam, gdzie dziś </span>
        <span style={{ opacity: 1 - swap * 0.5 }}>działa elektrownia węglowa</span>
      </div>
      <Badge text="Wizualizacja AI" opacity={0.85} />
    </SceneShell>
  );
};
