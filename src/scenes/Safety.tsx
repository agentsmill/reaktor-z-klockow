import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Pylon } from "../components/Buildings";
import { Pump } from "../components/Machines";
import { Pipe } from "../components/Pipe";
import { Reactor } from "../components/Reactor";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { ArrowHead, FlowParticles, Glow } from "../components/svg";
import { Tag } from "../components/Tag";
import { enter, lerp, progress, riseStyle } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { BODY, C, DISPLAY } from "../theme";

const GROUND = 300;
const RX = { x: 790, y: 340, scale: 0.62 };
const COIL = "M1060,190 L860,190 A18,18 0 0 0 860,226 L1060,226 A18,18 0 0 1 1060,262 L860,262";
const STEAM_UP = "M968,385 L1095,385 Q1110,385 1110,370 L1110,205 Q1110,190 1095,190 L1060,190";
const WATER_DOWN = "M860,262 L775,262 Q760,262 760,277 L760,505 Q760,520 775,520 L796,520";
const GRID = "M1408,178 L1180,172";

const Badge: React.FC<{ label: string; t: number; children: React.ReactNode }> = ({ label, t, children }) => (
  <div style={{ width: 170, textAlign: "center", ...riseStyle(t, 18) }}>
    <svg width={110} height={110} viewBox="-55 -55 110 110">
      <circle r={50} fill={C.panel} stroke={C.panelEdge} strokeWidth={2} />
      {children}
      <line x1={-30} y1={30} x2={30} y2={-30} stroke={C.accent} strokeWidth={6} strokeLinecap="round" />
    </svg>
    <div style={{ fontFamily: BODY, fontSize: 26, fontWeight: 800, color: C.text, marginTop: 8 }}>{label}</div>
  </div>
);

/** "bez prądu / bez pomp / bez ludzi" badges + the 7-day counter (right third). */
export const PassiveSafetyPanel: React.FC<{ left?: number; top?: number }> = ({ left = 1240, top = 400 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();
  const days = progress(frame, cue("days") - 4, cue("days") + 48, Easing.out(Easing.quad));
  const dayCount = Math.max(1, Math.round(days * 7));
  return (
    <div style={{ position: "absolute", left, top, width: 0, height: 0 }}>
      <div style={{ position: "absolute", left: 0, top: 0, display: "flex", gap: 22 }}>
        <Badge label="bez prądu" t={enter(frame, cue("noPower") - 4, fps, 14)}>
          <path d="M4,-30 l-16,32 h14 l-8,28 l26,-38 h-14 l10,-22 Z" fill={C.electricity} />
        </Badge>
        <Badge label="bez pomp" t={enter(frame, cue("noPower") + 8, fps, 14)}>
          <g transform="scale(0.55)">
            <Pump x={0} y={0} r={48} />
          </g>
        </Badge>
        <Badge label="bez ludzi" t={enter(frame, cue("noPower") + 20, fps, 14)}>
          <circle cx={0} cy={-16} r={11} fill={C.muted} />
          <path d="M-20,26 Q-20,0 0,0 Q20,0 20,26 Z" fill={C.muted} />
        </Badge>
      </div>
      <div style={{ position: "absolute", left: 10, top: 240, width: 560, ...riseStyle(enter(frame, cue("days") - 6, fps, 16), 16) }}>
        <div style={{ fontFamily: BODY, fontSize: 26, fontWeight: 700, color: C.muted }}>co najmniej</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 18 }}>
          <span style={{ fontFamily: DISPLAY, fontSize: 104, fontWeight: 700, color: C.text, lineHeight: 1 }}>{dayCount}</span>
          <span style={{ fontFamily: DISPLAY, fontSize: 48, fontWeight: 700, color: C.text }}>dni</span>
        </div>
        <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
          {Array.from({ length: 7 }, (_, i) => (
            <div key={i} style={{ width: 52, height: 10, borderRadius: 5, background: i < dayCount ? C.water : C.panelEdge }} />
          ))}
        </div>
      </div>
    </div>
  );
};

export const Safety: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCues();

  const gridOn = 1 - progress(frame, cue("blackout") - 2, cue("blackout") + 10);
  const warn = enter(frame, cue("blackout") + 2, fps, 12);
  const rods = progress(frame, cue("rodsIn") - 2, cue("rodsIn") + 18, Easing.out(Easing.cubic));
  const off = progress(frame, cue("off") - 4, cue("off") + 40);
  const decayPulse = progress(frame, cue("decay") - 6, cue("decay") + 10) * (0.06 * Math.sin(frame * 0.18));
  const heat = lerp(0.85, 0.32, off) + decayPulse;
  const icOn = progress(frame, cue("ic") - 6, cue("ic") + 16);
  const poolT = progress(frame, cue("pools") - 6, cue("pools") + 14);
  const up = progress(frame, cue("rise") - 6, cue("rise") + 14);
  const back = progress(frame, cue("back") - 6, cue("back") + 14);
  const boil = interpolate(frame, [0, cue("off"), cue("off") + 40, cue("rise"), cue("rise") + 30], [0.8, 0.8, 0.12, 0.12, 0.45], {
    extrapolateRight: "clamp",
  });
  const depth = progress(frame, cue("underground") - 6, cue("underground") + 22);
  const leftLabels = 1 - progress(frame, cue("ic") - 10, cue("ic") + 4);

  return (
    <SceneShell schematic>
      <Sfx at={cue("blackout") - 2} name="powerdown" />
      <Sfx at={cue("rodsIn")} name="clunk" />
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        <defs>
          <linearGradient id="soil" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#1C1813" />
            <stop offset="100%" stopColor="#0C0A08" />
          </linearGradient>
          <radialGradient id="vapor">
            <stop offset="0%" stopColor={C.steam} stopOpacity={0.6} />
            <stop offset="100%" stopColor={C.steam} stopOpacity={0} />
          </radialGradient>
          <linearGradient id="pool" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={C.water} stopOpacity={0.55} />
            <stop offset="100%" stopColor={C.waterDeep} stopOpacity={0.8} />
          </linearGradient>
        </defs>

        {/* ground and shaft */}
        <rect x={0} y={GROUND} width={1920} height={1080 - GROUND} fill="url(#soil)" />
        <rect x={0} y={GROUND - 4} width={1920} height={8} fill={C.grass} />
        <rect x={700} y={GROUND} width={360} height={800} fill="#0A1322" />
        <rect x={700} y={GROUND} width={20} height={800} fill={C.concrete} />
        <rect x={1040} y={GROUND} width={20} height={800} fill={C.concrete} />

        {/* reactor building above ground with the cooling pool */}
        <rect x={600} y={110} width={580} height={GROUND - 110} fill="#101B2E" stroke={C.concrete} strokeWidth={14} />
        <rect x={628} y={150} width={524} height={GROUND - 156} fill="url(#pool)" opacity={0.55 + 0.45 * poolT} />
        <line x1={628} x2={1152} y1={150} y2={150} stroke="#9CC2FF" strokeWidth={2} opacity={0.7} />
        {/* the pool slowly boils off — that's where the heat goes */}
        {Array.from({ length: 6 }, (_, i) => {
          const p = ((frame * 0.02 + i / 6) % 1 + 1) % 1;
          return <circle key={i} cx={680 + i * 85 + Math.sin(frame * 0.05 + i) * 10} cy={140 - p * 70} r={20 + p * 30} fill="url(#vapor)" opacity={up * 0.8 * (1 - p)} />;
        })}

        {/* isolation condenser loop */}
        <Pipe d={STEAM_UP} width={20} />
        <Pipe d={WATER_DOWN} width={20} />
        <Glow x={960} y={226} r={170} color={C.steam} opacity={icOn * 0.5} />
        <path d={COIL} fill="none" stroke={icOn > 0 ? "#E8F0F8" : C.steel} strokeOpacity={0.5 + 0.5 * icOn} strokeWidth={9} strokeLinecap="round" />
        <FlowParticles d={STEAM_UP} frame={frame} count={12} speed={3.2} radius={6} color={C.steam} opacity={up} />
        <FlowParticles d={COIL} frame={frame} count={14} speed={3.2} radius={5} color={(t) => (t < 0.5 ? C.steam : "#7FB2FF")} opacity={up} />
        <FlowParticles d={WATER_DOWN} frame={frame} count={12} speed={2.8} radius={6} color={C.water} opacity={back} />

        <Reactor x={RX.x} y={RX.y} scale={RX.scale} frame={frame} boil={boil} downflow={0.4} rods={rods} heat={heat} hot={lerp(0.75, 0.9, off)} />

        {/* grid connection */}
        <Pylon x={1450} y={GROUND} h={170} />
        <path d={GRID} stroke={C.steel} strokeWidth={3} fill="none" />
        <FlowParticles d={GRID} frame={frame} count={6} speed={6} radius={5} color={C.electricity} opacity={gridOn} edge={0.02} />
        <g opacity={warn} transform="translate(1300,236)">
          <path d="M-14,-24 l-10,26 h12 l-6,24 l22,-32 h-12 l8,-18 Z" fill={C.electricity} opacity={0.5} />
          <line x1={-24} y1={20} x2={20} y2={-26} stroke={C.accent} strokeWidth={5} strokeLinecap="round" />
        </g>

        {/* depth marker */}
        <g opacity={depth}>
          <line x1={640} x2={640} y1={GROUND + 8} y2={GROUND + 8 + 540 * depth} stroke={C.text} strokeWidth={3} />
          <ArrowHead x={640} y={GROUND + 8} dx={0} dy={-1} size={14} color={C.text} />
          <ArrowHead x={640} y={GROUND + 8 + 540 * depth} dx={0} dy={1} size={14} color={C.text} />
        </g>
        {back > 0 && <ArrowHead x={760} y={430} dx={0} dy={1} size={20} color={C.water} />}
      </svg>

      <Tag x={1300} y={290} text="brak zasilania z sieci" t={warn} color={C.accent} anchor="center" size={26} />
      <Tag x={680} y={600} text="pręty wsuwają się automatycznie" t={enter(frame, cue("rodsIn") - 4, fps, 12) * (1 - progress(frame, cue("off") - 8, cue("off"))) * leftLabels} color={C.rods} anchor="right" size={28} />
      <Tag x={680} y={600} text="reakcja gaśnie" t={progress(frame, cue("off") - 6, cue("off") + 4) * (1 - progress(frame, cue("decay") - 8, cue("decay"))) * leftLabels} color={C.neutron} anchor="right" size={28} />
      <Tag x={680} y={600} text="paliwo nadal trochę grzeje" sub="ciepło powyłączeniowe" t={progress(frame, cue("decay") - 6, cue("decay") + 4) * leftLabels} color={C.heat} anchor="right" size={28} />
      <Tag x={1200} y={226} text="skraplacz" t={icOn} color={C.steam} size={28} />
      <Tag x={590} y={200} text="basen z wodą" sub="nad reaktorem" t={poolT} color={C.water} anchor="right" size={28} />
      <Tag x={1130} y={330} text="para w górę" t={up} color={C.steam} size={26} />
      <Tag x={740} y={420} text="woda w dół — grawitacja" t={back} color={C.water} anchor="right" size={26} />
      <Tag x={620} y={GROUND + 280} text="ok. 35 m" sub="pod ziemią" t={depth} color={C.text} anchor="right" size={34} />

      <PassiveSafetyPanel />
    </SceneShell>
  );
};
