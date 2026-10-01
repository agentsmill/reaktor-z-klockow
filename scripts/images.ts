// Two atmospheric stills (Nano Banana Pro via fal.ai). Always shown with a "Wizualizacja AI" label.
import { existsSync } from "node:fs";
import { download, falRun, force } from "./fal.ts";

const IMAGES: Record<string, string> = {
  "intro-plant":
    "Photorealistic aerial drone photograph at dawn of a compact, modern small modular nuclear power plant in the Polish lowlands: " +
    "one tall cylindrical light-grey concrete reactor building with a flat roof, a long rectangular turbine hall beside it, " +
    "a small electrical switchyard with transmission lines leaving towards the horizon. No large cooling towers, no smoke. " +
    "The plant stands on the bank of a wide, calm river with soft morning mist over the water, flat green and golden fields, " +
    "birch and pine trees, a small town with a church tower far away in the haze. Soft golden-hour light, natural colours, " +
    "cinematic 35mm lens, realistic scale, high detail. No text, no logos, no people.",
  "why-town":
    "Photorealistic wide photograph at blue hour of a peaceful Polish town in early autumn: warm lights glowing in apartment blocks " +
    "and family houses, a brick church tower, street lamps along a quiet road, high-voltage power lines on the horizon leading into town. " +
    "Deep blue sky with the last light of dusk, cinematic 35mm lens, natural colours, high detail. No text, no logos, no people.",
};

await Promise.all(
  Object.entries(IMAGES).map(async ([name, prompt]) => {
    const dest = `public/img/${name}.jpg`;
    if (!force && existsSync(dest)) return console.log(`skip ${dest}`);
    const result = await falRun<{ images: { url: string }[] }>("fal-ai/nano-banana-pro", {
      prompt,
      aspect_ratio: "16:9",
      resolution: "2K",
      output_format: "jpeg",
      num_images: 1,
    });
    await download(result.images[0].url, dest);
    console.log(`wrote ${dest}`);
  }),
);
