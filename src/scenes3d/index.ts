import type { SceneId } from "../script";
import { Circulation3D } from "./Circulation3D";
import { Control3D } from "./Control3D";
import { Fission3D } from "./Fission3D";
import { Intro3D } from "./Intro3D";
import { Outro3D } from "./Outro3D";
import { Poland3D } from "./Poland3D";
import { Power3D } from "./Power3D";
import { Safety3D } from "./Safety3D";
import { Smr3D } from "./Smr3D";
import { Why3D } from "./Why3D";

/** 3D (Blender) versions of the scenes; used only when the shot's render is complete. */
export const SCENES_3D: Partial<Record<SceneId, React.FC>> = {
  intro: Intro3D,
  smr: Smr3D,
  poland: Poland3D,
  fission: Fission3D,
  control: Control3D,
  power: Power3D,
  circulation: Circulation3D,
  safety: Safety3D,
  why: Why3D,
  outro: Outro3D,
};
