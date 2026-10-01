import { useMemo } from "react";
import { Easing, random, useCurrentFrame, useVideoConfig } from "remotion";
import { HeatBurst, Neutron } from "../components/Atoms";
import { PowerChart } from "../components/PowerChart";
import { SceneShell } from "../components/SceneShell";
import { Sfx } from "../components/Sound";
import { ArrowHead, Glow } from "../components/svg";
import { Tag } from "../components/Tag";
import { enter, lerp, linear, progress } from "../lib/anim";
import { useCues } from "../lib/SceneContext";
import { C } from "../theme";

const COLS = [210, 410, 610, 810, 1010, 1210];
const ROWS = [330, 500, 670];
const RODS = COLS.slice(0, -1).map((x) => x + 100);
const ROD_TOP = 228;
const STEP = 22; // frames between links of the steady chain

/** Steady chain: fission hops one column to the right every STEP frames; the 2 spare neutrons hit the rod. */
const steadyFissions = (start: number, end: number) => {
  const events: { col: number; at: number }[] = [];
  for (let at = start, i = 0; at < end; at += STEP, i++) events.push({ col: i % COLS.length, at });
  return events;
};

export const Control: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const cue = useCues();

  const rodsIn = progress(frame, cue("rods") - 4, cue("fromBelow") + 22, Easing.inOut(Easing.cubic));
  const rodTopY = lerp(1000, ROD_TOP, rodsIn);
  const steadyStart = cue("fromBelow") + 30;

  // Phase A: too many neutrons — fissions get denser until the rods arrive.
  const chaos = useMemo(
    () =>
      Array.from({ length: 30 }, (_, k) => ({
        at: Math.round(2 + Math.pow(k / 30, 0.65) * (cue("rods") + 10)),
        col: Math.floor(random(`col${k}`) * COLS.length),
        row: Math.floor(random(`row${k}`) * ROWS.length),
        angle: random(`ang${k}`) * Math.PI * 2,
      })),
    [], // eslint-disable-line react-hooks/exhaustive-deps
  );
  const steady = useMemo(() => steadyFissions(steadyStart, durationInFrames), [steadyStart, durationInFrames]);

  const labelOne = enter(frame, cue("exactlyOne") - 4, fps, 16);

  return (
    <SceneShell schematic>
      <Sfx at={cue("rods") + 8} name="clunk" />
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
        {/* fuel rods (tubes) with uranium nuclei */}
        {COLS.map((x) => (
          <g key={x}>
            <rect x={x - 30} y={240} width={60} height={520} rx={30} fill={C.uranium} opacity={0.08} />
            <rect x={x - 30} y={240} width={60} height={520} rx={30} fill="none" stroke={C.uranium} strokeOpacity={0.35} strokeWidth={2} />
            {ROWS.map((y) => (
              <circle key={y} cx={x} cy={y} r={17} fill={C.uranium} opacity={0.9} />
            ))}
          </g>
        ))}

        {/* control rods rising from below */}
        {RODS.map((x) => (
          <g key={x}>
            <rect x={x - 14} y={rodTopY} width={28} height={1100 - rodTopY} rx={6} fill={C.rods} />
            <rect x={x - 14} y={rodTopY} width={8} height={1100 - rodTopY} rx={4} fill="#B7C1D1" opacity={0.5} />
          </g>
        ))}

        {/* phase A: chaotic, growing activity */}
        {chaos.map((e, k) => {
          const t = linear(frame, e.at, e.at + 26);
          if (t <= 0 || t >= 1) return null;
          const x = COLS[e.col];
          const y = ROWS[e.row];
          return (
            <g key={k}>
              <HeatBurst x={x} y={y} t={t} size={60} />
              {[0, 1, 2].map((j) => {
                const a = e.angle + (j * Math.PI * 2) / 3;
                const d = 30 + t * 150;
                return <Neutron key={j} x={x + Math.cos(a) * d} y={y + Math.sin(a) * d} r={7} opacity={1 - t} />;
              })}
            </g>
          );
        })}

        {/* phase C: steady chain — 1 neutron continues, 2 are absorbed by the rod */}
        {steady.map((e, k) => {
          const x = COLS[e.col];
          const y = ROWS[1];
          const t = linear(frame, e.at, e.at + STEP);
          if (t <= 0 || t >= 1 || e.col === COLS.length - 1) {
            return t > 0 && t < 1 ? <HeatBurst key={k} x={x} y={y} t={t} size={70} /> : null;
          }
          const rodX = RODS[e.col];
          const absorbed = Math.min(1, t * 1.25);
          return (
            <g key={k}>
              <HeatBurst x={x} y={y} t={t} size={70} />
              <Neutron x={lerp(x, COLS[e.col + 1], t)} y={y} r={9} dir={{ dx: 1, dy: 0 }} trail={36} />
              {[-1, 1].map((s) => (
                <Neutron
                  key={s}
                  x={lerp(x, rodX - 14, absorbed)}
                  y={lerp(y, y + s * 90, absorbed)}
                  r={8}
                  opacity={absorbed < 1 ? 1 : 0}
                />
              ))}
              {absorbed >= 1 && [-1, 1].map((s) => <Glow key={s} x={rodX - 10} y={y + s * 90} r={34} color={C.rods} opacity={1 - t} />)}
            </g>
          );
        })}
        {frame >= steadyStart && (
          <rect
            x={COLS[0] - 46}
            y={ROWS[1] - 46}
            width={COLS[COLS.length - 1] - COLS[0] + 92}
            height={92}
            rx={46}
            fill="none"
            stroke={C.neutron}
            strokeWidth={2}
            strokeDasharray="10 10"
            opacity={labelOne * 0.7}
          />
        )}

        {/* "from below" arrows */}
        <g opacity={progress(frame, cue("fromBelow") - 8, cue("fromBelow") + 4)}>
          {RODS.map((x) => (
            <ArrowHead key={x} x={x} y={800 - progress(frame, cue("fromBelow") - 6, cue("fromBelow") + 12) * 14} dx={0} dy={-1} size={18} color={C.rods} />
          ))}
        </g>

      </svg>

      <Tag x={COLS[0]} y={205} text="paliwo (uran)" t={enter(frame, 8, fps, 16)} color={C.uranium} anchor="center" size={26} />
      <Tag x={RODS[2]} y={835} text="pręty sterujące — wsuwane od dołu" t={enter(frame, cue("rods"), fps, 16)} color={C.rods} anchor="center" size={30} />
      <Tag x={COLS[0] + 10} y={ROWS[1] - 86} text="1 rozszczepienie → dokładnie 1 kolejne" t={labelOne} color={C.neutron} size={28} />
      <PowerChart />
    </SceneShell>
  );
};
