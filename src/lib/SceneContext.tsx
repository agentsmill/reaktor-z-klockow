import { createContext, useContext } from "react";
import { useVideoConfig } from "remotion";
import { cueFrame } from "./cues";
import type { SceneData } from "./project";

const SceneCtx = createContext<SceneData | null>(null);
export const SceneProvider = SceneCtx.Provider;

export function useScene(): SceneData {
  const scene = useContext(SceneCtx);
  if (!scene) throw new Error("useScene() must be used inside a scene");
  return scene;
}

/** Returns cue(id) → scene-relative frame when the cue word is spoken. */
export function useCues(): (id: string) => number {
  const scene = useScene();
  const { fps } = useVideoConfig();
  return (id: string) => {
    const cue = scene.def.cues.find((c) => c.id === id);
    if (!cue) throw new Error(`Scene "${scene.def.id}" has no cue "${id}"`);
    return cueFrame(scene.timed, scene.words, cue, fps);
  };
}
