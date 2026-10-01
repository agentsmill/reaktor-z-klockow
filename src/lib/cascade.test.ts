import { describe, expect, it } from "vitest";
import { buildCascade, hexLattice } from "./cascade";

const center = { x: 960, y: 440 };
const points = hexLattice(center, 120, { x0: 100, x1: 1820, y0: 150, y1: 800 });
const dirs = [
  { dx: 1, dy: -0.4 },
  { dx: -0.3, dy: 1 },
  { dx: -1, dy: -0.4 },
];
const nodes = buildCascade(points, center, dirs, [3, 2, 2], 400, 26);

describe("chain-reaction cascade", () => {
  it("starts at the lattice point under the centre", () => {
    expect(points[nodes[0].idx]).toEqual(center);
  });

  it("never splits the same nucleus twice", () => {
    expect(new Set(nodes.map((n) => n.idx)).size).toBe(nodes.length);
  });

  it("grows generation by generation, children after parents", () => {
    for (const n of nodes.slice(1)) {
      const parent = nodes[n.parent!];
      expect(n.gen).toBe(parent.gen + 1);
      expect(n.splitAt).toBeGreaterThan(parent.splitAt);
    }
    expect(nodes.filter((n) => n.gen === 1)).toHaveLength(3);
    expect(nodes.filter((n) => n.gen === 3).length).toBeGreaterThanOrEqual(8);
  });
});
