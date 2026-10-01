// Deterministic chain-reaction tree on a hex lattice of uranium nuclei.
// Remotion renders frames independently, so the whole cascade is precomputed
// once and each frame just looks up "has node i split yet?".

export type LatticePoint = { x: number; y: number };
export type CascadeNode = { idx: number; gen: number; parent: number | null; splitAt: number };

export function hexLattice(
  center: LatticePoint,
  spacing: number,
  bounds: { x0: number; x1: number; y0: number; y1: number },
): LatticePoint[] {
  const rowH = spacing * 0.866;
  const points: LatticePoint[] = [];
  const rows = Math.ceil((bounds.y1 - bounds.y0) / rowH) + 2;
  const cols = Math.ceil((bounds.x1 - bounds.x0) / spacing) + 2;
  for (let r = -rows; r <= rows; r++) {
    for (let c = -cols; c <= cols; c++) {
      const x = center.x + c * spacing + (Math.abs(r) % 2) * spacing * 0.5;
      const y = center.y + r * rowH;
      if (x >= bounds.x0 && x <= bounds.x1 && y >= bounds.y0 && y <= bounds.y1) points.push({ x, y });
    }
  }
  return points;
}

/**
 * Grows the tree outward from the point nearest `center`.
 * `branching[g]` = how many nuclei each node of generation g sets off.
 */
export function buildCascade(
  points: LatticePoint[],
  center: LatticePoint,
  firstDirs: { dx: number; dy: number }[],
  branching: number[],
  start: number,
  genGap: number,
): CascadeNode[] {
  const dist = (a: LatticePoint, b: LatticePoint) => Math.hypot(a.x - b.x, a.y - b.y);
  const root = points.reduce((best, p, i) => (dist(p, center) < dist(points[best], center) ? i : best), 0);
  const used = new Set([root]);
  const nodes: CascadeNode[] = [{ idx: root, gen: 0, parent: null, splitAt: start - genGap }];

  const pick = (from: number, dir: { dx: number; dy: number }): number | null => {
    const o = points[from];
    let best: number | null = null;
    let bestScore = Infinity;
    points.forEach((p, i) => {
      if (used.has(i)) return;
      const d = dist(p, o);
      if (d < 1) return;
      const cos = ((p.x - o.x) * dir.dx + (p.y - o.y) * dir.dy) / d;
      if (cos < 0.5) return;
      const score = d * (2 - cos);
      if (score < bestScore) {
        bestScore = score;
        best = i;
      }
    });
    return best;
  };

  let frontier = [0];
  branching.forEach((k, g) => {
    const next: number[] = [];
    for (const n of frontier) {
      const node = nodes[n];
      const p = points[node.idx];
      const out = node.parent === null ? null : points[nodes[node.parent].idx];
      const base = out ? Math.atan2(p.y - out.y, p.x - out.x) : 0;
      const dirs =
        node.parent === null
          ? firstDirs
          : Array.from({ length: k }, (_, j) => {
              const a = base + (k === 1 ? 0 : (j / (k - 1) - 0.5) * 1.3);
              return { dx: Math.cos(a), dy: Math.sin(a) };
            });
      dirs.slice(0, node.parent === null ? firstDirs.length : k).forEach((dir, j) => {
        const target = pick(node.idx, dir);
        if (target === null) return;
        used.add(target);
        nodes.push({ idx: target, gen: g + 1, parent: n, splitAt: start + g * genGap + ((j * 5 + n * 3) % 9) });
        next.push(nodes.length - 1);
      });
    }
    frontier = next;
  });
  return nodes;
}
