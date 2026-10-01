import { Audio } from "@remotion/media";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { hasRender } from "./components/BrickPlate";
import { Captions } from "./components/Captions";
import { MusicBed, Sfx } from "./components/Sound";
import { SCENE_DATA, TIMELINE, type SceneData } from "./lib/project";
import { cueFrame } from "./lib/cues";
import { SceneProvider } from "./lib/SceneContext";
import { TRANSITION } from "./lib/timeline";
import { SCENE_COMPONENTS } from "./scenes";
import { SCENES_3D } from "./scenes3d";
import type { SceneId } from "./script";
import { C } from "./theme";

/** The score drops to a hush when the power fails in the safety scene, then swells back. */
const blackoutDip = () => {
  const safety = SCENE_DATA.find((s) => s.def.id === "safety")!;
  const cue = safety.def.cues.find((c) => c.id === "blackout")!;
  return { at: safety.timed.from + cueFrame(safety.timed, safety.words, cue), hold: 50, release: 70 };
};

/** A scene with its voiceover, delayed by the scene's lead-in. */
const SceneSlot: React.FC<{ data: SceneData }> = ({ data }) => {
  // 3D brick version when its Blender render is complete, otherwise the 2D version.
  const Scene = (hasRender(data.def.id) && SCENES_3D[data.def.id]) || SCENE_COMPONENTS[data.def.id];
  return (
    <SceneProvider value={data}>
      <Scene />
      <Sequence from={data.timed.leadIn} layout="none">
        <Audio src={staticFile(data.audio)} />
      </Sequence>
    </SceneProvider>
  );
};

export const Video: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.bg }}>
    <TransitionSeries>
      {SCENE_DATA.flatMap((s, i) => [
        ...(i > 0
          ? [
              <TransitionSeries.Transition
                key={`fade-${s.def.id}`}
                presentation={fade()}
                timing={linearTiming({ durationInFrames: TRANSITION })}
              />,
            ]
          : []),
        <TransitionSeries.Sequence key={s.def.id} durationInFrames={s.timed.duration}>
          <SceneSlot data={s} />
        </TransitionSeries.Sequence>,
      ])}
    </TransitionSeries>
    <Captions scenes={SCENE_DATA} offset={(s) => s.timed.from + s.timed.leadIn} />
    <MusicBed timeline={TIMELINE} dips={[blackoutDip()]} />
    {SCENE_DATA.slice(1).map((s) => (
      <Sfx key={s.def.id} at={s.timed.from - 4} name="whoosh" />
    ))}
  </AbsoluteFill>
);

/** One scene on its own timeline — frames are scene-relative, handy for stills at cue frames. */
export const SceneSolo: React.FC<{ id: SceneId }> = ({ id }) => {
  const data = SCENE_DATA.find((s) => s.def.id === id)!;
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <SceneSlot data={data} />
      <Captions scenes={[data]} offset={(s) => s.timed.leadIn} />
    </AbsoluteFill>
  );
};
