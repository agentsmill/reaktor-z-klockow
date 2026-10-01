import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// SVG-heavy scenes render faster with a few parallel tabs; leave headroom for the OS.
Config.setConcurrency(6);
