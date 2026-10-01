import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import rendersJson from "../generated/renders.json";
import type { SceneId } from "../script";

type ShotRender = { frames: number; anchors: Record<string, number[][]> };
export const RENDERS = rendersJson as Partial<Record<SceneId, ShotRender>>;

export const hasRender = (shot: SceneId): boolean => Boolean(RENDERS[shot]);

/** The Blender image sequence for a shot; scene frame 0 ↔ Blender frame 0001. */
export const BrickPlate: React.FC<{ shot: SceneId }> = ({ shot }) => {
  const frame = useCurrentFrame();
  const info = RENDERS[shot];
  if (!info) return null;
  const index = Math.min(info.frames, Math.max(1, frame + 1));
  return (
    <AbsoluteFill>
      <Img
        src={staticFile(`renders/${shot}/${String(index).padStart(4, "0")}.jpg`)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </AbsoluteFill>
  );
};

/** Screen position (1920×1080 px) of a named 3D anchor at the current frame, or a fallback. */
export function useAnchor(shot: SceneId, name: string, fallback: { x: number; y: number }): { x: number; y: number; visible: boolean } {
  const frame = useCurrentFrame();
  const track = RENDERS[shot]?.anchors?.[name];
  if (!track || track.length === 0) return { ...fallback, visible: true };
  const [x, y, visible] = track[Math.min(track.length - 1, Math.max(0, frame))];
  return { x, y, visible: visible === 1 };
}
