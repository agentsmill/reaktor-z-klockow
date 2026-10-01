import { Composition, Folder, Still } from "remotion";
import { Gallery } from "./Gallery";
import { SCENE_DATA, TIMELINE } from "./lib/project";
import { FPS } from "./lib/timeline";
import { HEIGHT, WIDTH } from "./theme";
import { SceneSolo, Video } from "./Video";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="SMRExplainer"
      component={Video}
      durationInFrames={TIMELINE.total}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
    <Folder name="Scenes">
      {SCENE_DATA.map((s) => (
        <Composition
          key={s.def.id}
          id={`S${String(s.index).padStart(2, "0")}-${s.def.id}`}
          component={SceneSolo}
          defaultProps={{ id: s.def.id }}
          durationInFrames={s.timed.duration}
          fps={FPS}
          width={WIDTH}
          height={HEIGHT}
        />
      ))}
    </Folder>
    <Still id="Gallery" component={Gallery} width={WIDTH} height={HEIGHT} />
  </>
);
