import { getLength } from "@remotion/paths";
import { useMemo } from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { POLAND_PATH, projectLonLat } from "../data/poland";
import { enter, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

const MAP_X = 150;
const MAP_Y = 150;

/** Sites with a 2023 government decision-in-principle (OSGE). Label side chosen to avoid overlaps. */
export const SITES = [
  { name: "Włocławek", lon: 19.068, lat: 52.648, side: "right" },
  { name: "Ostrołęka", lon: 21.575, lat: 53.086, side: "right" },
  { name: "Stalowa Wola", lon: 22.05, lat: 50.58, side: "right" },
  { name: "Dąbrowa Górnicza", lon: 19.19, lat: 50.33, side: "left" },
  { name: "Stawy Monowskie", lon: 19.29, lat: 50.03, side: "left" },
  { name: "Kraków-Nowa Huta", lon: 20.1, lat: 50.07, side: "right" },
] as const;

export const INVESTORS =
  "Rafał Brzoska · Krzysztof i Marta Pawińscy · Michał Wypychewicz · Dariusz Gałęzewski · Dominik Doliński · " +
  "Mati Staniszewski · Piotr Dąbkowski · Michał Brański · Bruno Wejchert";

export const Card: React.FC<{ top: number; height: number; t: number; children: React.ReactNode }> = ({ top, height, t, children }) => (
  <div
    style={{
      position: "absolute",
      left: 980,
      top,
      width: 820,
      height,
      boxSizing: "border-box",
      padding: "24px 34px",
      borderRadius: 22,
      background: C.panel,
      border: `1px solid ${C.panelEdge}`,
      fontFamily: BODY,
      color: C.text,
      opacity: t,
      transform: `translateX(${(1 - t) * 40}px)`,
    }}
  >
    {children}
  </div>
);

export const Pill: React.FC<{ children: React.ReactNode; t?: number; color?: string }> = ({ children, t = 1, color = C.text }) => (
  <span
    style={{
      display: "inline-block",
      padding: "6px 18px",
      borderRadius: 999,
      border: `2px solid ${color}`,
      color,
      fontFamily: DISPLAY,
      fontSize: 30,
      fontWeight: 700,
      opacity: t,
      transform: `scale(${0.9 + 0.1 * t})`,
    }}
  >
    {children}
  </span>
);

/** The three info cards (SGE/Orlen → OSGE, BWRX-300, Polish investors), timed to the narration. */
export const PolandCards: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const cardA = enter(frame, cue("solowow") - 4, fps, 18);
  const orlen = enter(frame, cue("orlen") - 2, fps, 14);
  const orlenNote = enter(frame, cue("orlen") + 16, fps, 14);
  const cardB = enter(frame, cue("tech") - 4, fps, 18);
  const power = enter(frame, cue("power") - 2, fps, 14);
  const cardC = enter(frame, cue("investors") - 4, fps, 18);
  const amountT = progress(frame, cue("amount") - 4, cue("amount") + 30, Easing.out(Easing.cubic));
  const amount = Math.round(interpolate(amountT, [0, 1], [0, 500]));

  return (
    <>
        <Card top={150} height={176} t={cardA}>
          <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
            <Pill>SGE</Pill>
            <span style={{ fontSize: 30, fontWeight: 700 }}>firma Michała Sołowowa</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 16, opacity: orlen, fontSize: 26, fontWeight: 600, color: C.muted }}>
            <span>część reaktorów z Orlenem</span>
            <span style={{ color: C.faint }}>→</span>
            <span style={{ color: C.text, fontWeight: 800 }}>OSGE</span>
            <span>(spółka 50/50)</span>
          </div>
          <div style={{ marginTop: 8, fontSize: 20, fontWeight: 600, color: C.faint, opacity: orlenNote }}>
            porozumienie po miesiącach sporu · wrzesień 2026
          </div>
        </Card>
  
        <Card top={346} height={150} t={cardB}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 18 }}>
            <span style={{ fontFamily: DISPLAY, fontSize: 46, fontWeight: 700 }}>BWRX-300</span>
            <span style={{ fontSize: 24, fontWeight: 600, color: C.muted }}>GE Vernova Hitachi (USA–Japonia)</span>
          </div>
          <div style={{ marginTop: 14, display: "flex", alignItems: "center", gap: 12, opacity: power, fontSize: 28, fontWeight: 800 }}>
            <span style={{ color: C.electricity, fontSize: 32 }}>⚡</span>
            300 MW mocy elektrycznej
          </div>
        </Card>
  
        <Card top={518} height={290} t={cardC}>
          <div style={{ fontSize: 22, fontWeight: 800, letterSpacing: "0.12em", color: C.muted, textTransform: "uppercase" }}>
            30.09.2026 · polscy przedsiębiorcy
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginTop: 10, opacity: Math.max(0.15, amountT) }}>
            <span style={{ fontFamily: DISPLAY, fontSize: 64, fontWeight: 700 }}>≈ {amount}</span>
            <span style={{ fontSize: 34, fontWeight: 800 }}>mln zł</span>
            <span style={{ fontSize: 22, fontWeight: 600, color: C.muted }}>dla SGE</span>
          </div>
          <div style={{ marginTop: 12, fontSize: 20, lineHeight: 1.45, fontWeight: 600, color: C.muted }}>m.in. {INVESTORS}</div>
        </Card>
    </>
  );
};

export const Poland: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const outlineLength = useMemo(() => getLength(POLAND_PATH), []);

  const draw = progress(frame, cue("map"), cue("map") + 45, Easing.inOut(Easing.quad));
  const fill = progress(frame, cue("map") + 25, cue("map") + 55);

  return (
    <SceneShell>
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <g transform={`translate(${MAP_X},${MAP_Y})`}>
          <path d={POLAND_PATH} fill="#2E5AA0" fillOpacity={0.2 * fill} stroke="none" />
          <path
            d={POLAND_PATH}
            fill="none"
            stroke="#7E9FD4"
            strokeWidth={3}
            strokeLinejoin="round"
            strokeDasharray={outlineLength}
            strokeDashoffset={outlineLength * (1 - draw)}
          />
          {/* Warsaw for orientation */}
          {(() => {
            const [wx, wy] = projectLonLat(21.01, 52.23);
            const t = progress(frame, cue("map") + 40, cue("map") + 55);
            return (
              <g opacity={t * 0.7}>
                <rect x={wx - 6} y={wy - 6} width={12} height={12} transform={`rotate(45 ${wx} ${wy})`} fill="none" stroke={C.muted} strokeWidth={2} />
                <text x={wx + 14} y={wy + 7} fill={C.muted} fontFamily={BODY} fontSize={20} fontWeight={600}>
                  Warszawa
                </text>
              </g>
            );
          })()}
          {SITES.map((site, i) => {
            const [x, y] = projectLonLat(site.lon, site.lat);
            const t = enter(frame, cue("map") + 38 + i * 6, fps, 14);
            const pulse = ((frame - (cue("map") + 38 + i * 6)) % 45) / 45;
            const right = site.side === "right";
            return (
              <g key={site.name} opacity={t}>
                <circle cx={x} cy={y} r={10 + pulse * 18} fill="none" stroke={C.accent} strokeWidth={2} opacity={t * (1 - pulse)} />
                <circle cx={x} cy={y} r={9 * t} fill={C.accent} stroke="#FFD9DA" strokeWidth={2} />
                <text
                  x={right ? x + 16 : x - 16}
                  y={y + 7}
                  textAnchor={right ? "start" : "end"}
                  fill={C.text}
                  fontFamily={BODY}
                  fontSize={21}
                  fontWeight={700}
                >
                  {site.name}
                </text>
              </g>
            );
          })}
        </g>
      </svg>

      <div
        style={{
          position: "absolute",
          left: MAP_X,
          top: 812,
          width: 676,
          textAlign: "center",
          fontFamily: BODY,
          fontSize: 22,
          fontWeight: 600,
          color: C.muted,
          ...riseStyle(progress(frame, cue("map") + 70, cue("map") + 90), 10),
        }}
      >
        6 lokalizacji z decyzją zasadniczą rządu (2023)
      </div>

      <PolandCards />
    </SceneShell>
  );
};
