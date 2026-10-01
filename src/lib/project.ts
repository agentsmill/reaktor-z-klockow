// Everything derived from the script + generated voiceover, computed once.
import voiceoverJson from "../generated/voiceover.json";
import { SCENES, type SceneDef } from "../script";
import { buildCaptionPages, captionWords, type CaptionPage, type CaptionWord } from "./captions";
import { buildTimeline, type TimedScene, type VoiceoverData } from "./timeline";

export type SceneData = {
  def: SceneDef;
  timed: TimedScene;
  /** Display words with spoken timing (ms from voiceover start). */
  words: CaptionWord[];
  pages: CaptionPage[];
  audio: string;
  index: number;
  count: number;
};

export const VO = voiceoverJson as unknown as VoiceoverData;
export const TIMELINE = buildTimeline(SCENES, VO);

export const SCENE_DATA: SceneData[] = SCENES.map((def, index) => {
  const words = captionWords(def.show, VO.scenes[def.id].words);
  return {
    def,
    timed: TIMELINE.scenes[index],
    words,
    pages: buildCaptionPages(words),
    audio: VO.scenes[def.id].file,
    index,
    count: SCENES.length,
  };
});
