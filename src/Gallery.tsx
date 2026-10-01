import { AbsoluteFill } from "remotion";
import { HeatBurst, Neutron, Nucleus, Pellet } from "./components/Atoms";
import { Condenser, Generator, Pump, Turbine } from "./components/Machines";
import { Reactor } from "./components/Reactor";
import { Backdrop } from "./components/SceneShell";

/** Dev-only sheet of every primitive, rendered as a still for visual review. */
export const Gallery: React.FC = () => (
  <AbsoluteFill>
    <Backdrop />
    <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      <Reactor x={80} y={150} scale={1} frame={40} boil={1} downflow={1} rods={0.4} heat={0.8} />
      <Nucleus x={620} y={260} frame={10} />
      <Nucleus x={820} y={260} n={18} stretch={0.5} shake={1.5} frame={10} seed="b" />
      <Neutron x={980} y={260} dir={{ dx: 1, dy: 0 }} />
      <HeatBurst x={1150} y={260} t={0.4} />
      <Pellet x={1400} y={260} w={140} glow={0.6} />
      <Turbine x={700} y={640} r={150} angle={20} />
      <Generator x={900} y={560} w={300} h={170} angle={45} on={1} />
      <Condenser x={1280} y={520} w={340} h={240} frame={30} active={1} />
      <Pump x={1750} y={640} r={60} angle={30} crossed={1} />
    </svg>
  </AbsoluteFill>
);
