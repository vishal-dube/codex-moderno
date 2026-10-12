"""Helpers shared by the folio pages."""

from __future__ import annotations

import math

from codex import Page, _inside, ellipse_pts, form_tone, rrect_pts, rotate_pts


def visible(pts, occluders, closed=True):
    """Runs of `pts` not hidden behind any of the occluding shapes."""
    if not occluders:
        return [pts]
    flags = [not any(_inside(q, o) for o in occluders) for q in pts]
    if all(flags):
        return [pts]
    if not any(flags):
        return []
    if closed:
        k = flags.index(False)
        pts, flags = pts[k:] + pts[:k], flags[k:] + flags[:k]
    runs, cur = [], []
    for q, ok in zip(pts, flags):
        if ok:
            cur.append(q)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def draw_visible(p: Page, pts, occluders, closed=True, **kw):
    kw.setdefault("overshoot", 1)
    for run in visible(pts, occluders, closed):
        p.contour(run, closed=False, **kw)


def not_in(occluders):
    """Multiply into a tone so hatching skips anything in front."""
    return lambda q: 0.0 if any(_inside(q, o) for o in occluders) else 1.0


def place(pts, angle, origin):
    """Rotate local points (drawn around 0,0) by `angle` degrees and move them to `origin`."""
    return [(x + origin[0], y + origin[1]) for x, y in rotate_pts(pts, angle, (0, 0))]


def gear(cx, cy, r, teeth, depth=10.0, rot=0.0):
    """Outline of a toothed wheel, as Leonardo drew them: square-ish teeth on a rim."""
    pts = []
    step = 2 * math.pi / teeth
    for k in range(teeth):
        a = math.radians(rot) + k * step
        for frac, rad in ((0.0, r), (0.18, r + depth), (0.52, r + depth), (0.7, r)):
            t = a + frac * step
            pts.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))
    return pts


def cylinder_h(x0, x1, cy, r, cap=0.32):
    """Horizontal cylinder outline (seen from the side, ends slightly elliptical)."""
    return ([(x0, cy - r), (x1, cy - r)] + ellipse_pts(x1, cy, r * cap, r, 0, -90, 90)[1:-1] +
            [(x1, cy + r), (x0, cy + r)] + ellipse_pts(x0, cy, r * cap, r, 0, 90, 270)[1:-1])


def smooth_closed(pts, n=8):
    """A closed Catmull-Rom curve through `pts`, sampled into a dense outline."""
    out = []
    k = len(pts)
    for i in range(k):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % k], pts[(i + 2) % k]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    return out


def zigzag(x0, x1, y, amp, step, rng):
    pts, x, sgn = [], x0, 1
    while x <= x1:
        pts.append((x, y + sgn * amp * rng.uniform(0.3, 1.0)))
        x += step * rng.uniform(0.6, 1.4)
        sgn = -sgn
    return pts


__all__ = ["visible", "draw_visible", "not_in", "place", "gear", "cylinder_h", "zigzag",
           "ellipse_pts", "rrect_pts", "form_tone", "_inside"]
