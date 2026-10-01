import type { SceneId } from "../script";
import { Circulation } from "./Circulation";
import { Control } from "./Control";
import { Fission } from "./Fission";
import { Intro } from "./Intro";
import { Outro } from "./Outro";
import { Poland } from "./Poland";
import { Power } from "./Power";
import { Safety } from "./Safety";
import { Smr } from "./Smr";
import { Why } from "./Why";

export const SCENE_COMPONENTS: Record<SceneId, React.FC> = {
  intro: Intro,
  smr: Smr,
  poland: Poland,
  fission: Fission,
  control: Control,
  power: Power,
  circulation: Circulation,
  safety: Safety,
  why: Why,
  outro: Outro,
};
