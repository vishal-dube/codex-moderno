"""Drawing primitives for Leonardo-style notebook pages, rendered as SVG.

Every mark is generated: contours are re-traced with a slow random drift,
hatching is computed by intersecting parallel lines with the shape (so the
strokes can fade out instead of stopping at a hard clip edge), and the
whole ink layer is pushed through a displacement filter so no line is
perfectly straight.
"""

from __future__ import annotations

import math
import random
from contextlib import contextmanager
from xml.sax.saxutils import escape

W, H = 1600, 1200

INK = "#3a2313"
CHALK = "#a5462b"
FONT = "'Apple Chancery', 'Snell Roundhand', 'Palatino', serif"

Point = tuple[float, float]


def _f(v: float) -> str:
    return f"{v:.1f}"


# ---------- geometry helpers ----------

def ellipse_pts(cx, cy, rx, ry, rot=0.0, a0=0.0, a1=360.0, step=7.0) -> list[Point]:
    r = math.radians(rot)
    span = math.radians(a1 - a0)
    n = max(8, int(abs(span) * max(rx, ry) / step))
    pts = []
    for i in range(n + 1):
        t = math.radians(a0) + span * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    if a1 - a0 >= 360:
        pts.pop()
    return pts


def rrect_pts(x, y, w, h, radii) -> list[Point]:
    """Rounded rect, clockwise from top-left. radii = r or (tl, tr, br, bl)."""
    if isinstance(radii, (int, float)):
        radii = (radii,) * 4
    tl, tr, br, bl = radii
    pts: list[Point] = []

    def corner(cx, cy, r, a0):
        if r <= 0:
            pts.append((cx, cy))
            return
        n = max(3, int(r / 4))
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    corner(x + tl, y + tl, tl, 180) if tl else pts.append((x, y))
    corner(x + w - tr, y + tr, tr, 270) if tr else pts.append((x + w, y))
    corner(x + w - br, y + h - br, br, 0) if br else pts.append((x + w, y + h))
    corner(x + bl, y + h - bl, bl, 90) if bl else pts.append((x, y + h))
    return pts


def rotate_pts(pts, angle, center) -> list[Point]:
    a = math.radians(angle)
    cx, cy = center
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def transform(pts, scale=1.0, rot=0.0, dx=0.0, dy=0.0, mirror=False) -> list[Point]:
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        if mirror:
            x = -x
        x, y = x * scale, y * scale
        out.append((dx + x * c - y * s, dy + x * s + y * c))
    return out


def lin_tone(p0: Point, p1: Point, gamma=1.0, lo=0.0):
    """0 at p0, 1 at p1, measured along the p0->p1 direction."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L2 = dx * dx + dy * dy

    def tone(p):
        t = ((p[0] - p0[0]) * dx + (p[1] - p0[1]) * dy) / L2
        t = min(1.0, max(0.0, t))
        return lo + (1 - lo) * t ** gamma
    return tone


def radial_tone(c: Point, r0, r1, gamma=1.0):
    def tone(p):
        d = math.dist(p, c)
        t = min(1.0, max(0.0, (d - r0) / (r1 - r0)))
        return t ** gamma
    return tone


def form_tone(poly, light=(-1.0, -1.2), rim=30.0, base=0.0, gamma=1.0, strength=1.0):
    """Shade a rounded object lit from `light`: darker away from the light,
    plus a band along the outline that darkens on the shadow side, which is
    what makes a flat outline read as a solid with volume."""
    xs = [x for x, _ in poly]
    ys = [y for _, y in poly]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2
    ll = math.hypot(*light)
    lx, ly = light[0] / ll, light[1] / ll
    edge_pts = _subdivide(poly, True, 6)

    def tone(p):
        s = -((p[0] - cx) * lx + (p[1] - cy) * ly) / half
        d = (s + 1) / 2
        e = max(0.0, 1 - min(math.dist(p, q) for q in edge_pts) / rim)
        raw = 0.72 * d + e * (0.15 + 0.85 * d)
        t = base + strength * (raw - 0.3) / 0.7
        return min(1.0, max(0.0, t)) ** gamma
    return tone


def union_outline(a, b):
    """Outline of two overlapping closed shapes as one closed path."""
    def run(x, y):
        k = next(i for i in range(len(x)) if _inside(x[i - 1], y) and not _inside(x[i], y))
        out = []
        for q in x[k:] + x[:k]:
            if _inside(q, y):
                break
            out.append(q)
        return out
    return run(a, b) + run(b, a)


def _inside(p, poly) -> bool:
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _polylen(pts) -> float:
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def _subdivide(pts, closed, step):
    out = []
    n = len(pts)
    segs = n if closed else n - 1
    for i in range(segs):
        a, b = pts[i], pts[(i + 1) % n]
        k = max(1, int(math.dist(a, b) / step))
        for j in range(k):
            t = j / k
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    if not closed:
        out.append(pts[-1])
    return out


def _catmull(pts) -> str:
    if len(pts) < 2:
        return ""
    d = [f"M{_f(pts[0][0])} {_f(pts[0][1])}"]
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}")
    return "".join(d)


# ---------- the page ----------

class Page:
    def __init__(self, seed: int, folio: str):
        self.rng = random.Random(seed)
        self.seed = seed
        self.folio = folio
        # Every mark in the order it was made, so the page can also be
        # replayed stroke by stroke (see svg(progress=...)).
        self.marks: list[dict] = []
        self._xf: tuple[float, float, float] | None = None  # (scale, dx, dy) for transformed()

    @contextmanager
    def transformed(self, scale=1.0, dx=0.0, dy=0.0):
        """Draw a group at another size and place: everything inside is scaled about
        the origin and then shifted. Tone functions still see the original coordinates."""
        prev = self._xf
        self._xf = (scale, dx, dy)
        try:
            yield
        finally:
            self._xf = prev

    def _fwd(self, pts):
        if not self._xf:
            return pts
        k, dx, dy = self._xf
        return [(x * k + dx, y * k + dy) for x, y in pts]

    def _inv(self, q):
        if not self._xf:
            return q
        k, dx, dy = self._xf
        return ((q[0] - dx) / k, (q[1] - dy) / k)

    def _mark(self, layer, kind, length, **data):
        self.marks.append({"layer": layer, "kind": kind, "length": length, "seq": len(self.marks), **data})

    # strokes

    def _drift(self, pts, amp):
        ox = oy = 0.0
        out = []
        for x, y in pts:
            ox = ox * 0.82 + self.rng.gauss(0, amp) * 0.45
            oy = oy * 0.82 + self.rng.gauss(0, amp) * 0.45
            out.append((x + ox, y + oy))
        return out

    def contour(self, pts, closed=True, w=2.2, passes=2, amp=1.0, color=INK,
                opacity=0.92, layer="ink", dash=None, overshoot=0.0, ghosts=0):
        pts = self._fwd(pts)
        for _ in range(ghosts):
            dense = self._drift(_subdivide(pts, closed, 8), amp * 3.2)
            sh = (self.rng.uniform(-3, 3), self.rng.uniform(-3, 3))
            ghost = [(x + sh[0], y + sh[1]) for x, y in dense]
            self._mark("hatch", "stroke", _polylen(ghost), pts=ghost, color=color, w=0.7, opacity=0.28, dash=None)
        for p in range(passes):
            dense = _subdivide(pts, closed, 8)
            if closed:
                dense = dense + dense[: 2 + self.rng.randint(0, 2)]
            elif overshoot:
                (ax, ay), (bx, by) = dense[0], dense[1]
                L = math.dist((ax, ay), (bx, by)) or 1
                e = overshoot * self.rng.uniform(0.4, 1.0)
                dense.insert(0, (ax - (bx - ax) / L * e, ay - (by - ay) / L * e))
                (ax, ay), (bx, by) = dense[-1], dense[-2]
                L = math.dist((ax, ay), (bx, by)) or 1
                e = overshoot * self.rng.uniform(0.4, 1.0)
                dense.append((ax + (ax - bx) / L * e, ay + (ay - by) / L * e))
            shift = (self.rng.uniform(-0.7, 0.7), self.rng.uniform(-0.7, 0.7)) if p else (0, 0)
            dense = [(x + shift[0], y + shift[1]) for x, y in self._drift(dense, amp)]
            width = w if p == 0 else w * 0.5
            op = opacity if p == 0 else opacity * 0.75
            self._mark(layer, "stroke", _polylen(dense), pts=dense, color=color, w=width, opacity=op, dash=dash)

    def line(self, a, b, w=1.6, **kw):
        kw.setdefault("passes", 1)
        kw.setdefault("overshoot", 3)
        self.contour([a, b], closed=False, w=w, **kw)

    def chalk(self, pts, closed=True, w=1.1, opacity=0.6, **kw):
        kw.setdefault("passes", 1)
        self.contour(pts, closed=closed, w=w, color=CHALK, opacity=opacity, layer="chalk", **kw)

    def chalk_line(self, a, b, w=1.0, opacity=0.55, **kw):
        kw.setdefault("overshoot", 10)
        self.contour([a, b], closed=False, w=w, color=CHALK, opacity=opacity, layer="chalk", passes=1, **kw)

    def arrow_head(self, tip, frm, size=12, color=INK, w=1.4, layer="ink", opacity=0.85):
        ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
        for da in (2.7, -2.7):
            end = (tip[0] + size * math.cos(ang + da), tip[1] + size * math.sin(ang + da))
            self.contour([tip, end], closed=False, w=w, passes=1, color=color, layer=layer, opacity=opacity)

    def hatch(self, polys, angle=45.0, spacing=6.0, w=0.9, color=INK, opacity=0.8,
              tone=None, trim=0.08, layer="hatch", bend=1.0, max_len=38.0):
        """Parallel strokes filling `polys` (even-odd, so inner polys become holes).

        `tone(p) -> 0..1` controls density: each stroke gets a random
        threshold and is only drawn where the tone exceeds it, so shading
        fades out gradually instead of ending in a hard band.
        """
        if polys and isinstance(polys[0][0], (int, float)):
            polys = [polys]
        polys = [self._fwd(poly) for poly in polys]
        if tone and self._xf:
            local_tone, inv = tone, self._inv
            tone = lambda q: local_tone(inv(q))  # noqa: E731
        a = math.radians(angle)
        ca, sa = math.cos(a), math.sin(a)

        def fwd(p):
            return (p[0] * ca + p[1] * sa, -p[0] * sa + p[1] * ca)

        def back(u, v):
            return (u * ca - v * sa, u * sa + v * ca)

        rp = [[fwd(p) for p in poly] for poly in polys]
        vs = [p[1] for poly in rp for p in poly]
        v = min(vs) + spacing * self.rng.uniform(0.2, 0.8)
        vmax = max(vs)
        d = []
        total = 0.0
        while v < vmax:
            xs = []
            for poly in rp:
                n = len(poly)
                for i in range(n):
                    (u0, v0), (u1, v1) = poly[i], poly[(i + 1) % n]
                    if (v0 <= v < v1) or (v1 <= v < v0):
                        xs.append(u0 + (v - v0) * (u1 - u0) / (v1 - v0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                s0, s1 = xs[k], xs[k + 1]
                if s1 - s0 < 2:
                    continue
                runs = [(s0, s1)]
                if tone:
                    thr = self.rng.uniform(0.04, 0.96)
                    m = max(4, int((s1 - s0) / 5))
                    runs, start = [], None
                    for j in range(m + 1):
                        u = s0 + (s1 - s0) * j / m
                        on = tone(back(u, v)) >= thr
                        if on and start is None:
                            start = u
                        if (not on or j == m) and start is not None:
                            runs.append((start, u))
                            start = None
                for r0, r1 in runs:
                    L = r1 - r0
                    if L < 3:
                        continue
                    r0 += L * self.rng.uniform(0, trim)
                    r1 -= L * self.rng.uniform(0, trim)
                    # Break long runs into short pen strokes with small gaps.
                    a_ = r0
                    while a_ < r1 - 2:
                        b_ = min(r1, a_ + self.rng.uniform(max_len * 0.55, max_len))
                        if r1 - b_ < 6:
                            b_ = r1
                        vv = v + self.rng.uniform(-0.8, 0.8)
                        p0 = back(a_, vv)
                        p1 = back(b_, vv + self.rng.uniform(-1.2, 1.2))
                        pm = back((a_ + b_) / 2, vv + self.rng.uniform(-bend, bend))
                        d.append(f"M{_f(p0[0])} {_f(p0[1])}Q{_f(pm[0])} {_f(pm[1])} {_f(p1[0])} {_f(p1[1])}")
                        total += b_ - a_
                        a_ = b_ + self.rng.uniform(1.5, 5.0)
            v += spacing * self.rng.uniform(0.8, 1.2)
        if d:
            self._mark(layer, "hatch", total, subs=d, color=color, w=w, opacity=opacity)

    def shade(self, polys, tone, spacing=3.8, w=0.72):
        """Three passes of hatching at slightly different angles, each only
        reaching into darker tones, so shadows build up the way they do with
        a pen instead of as one flat grey."""
        self.hatch(polys, 45, spacing, w=w, opacity=0.85, tone=tone)
        self.hatch(polys, 28, spacing * 1.15, w=w * 0.85, opacity=0.7, tone=lambda p: tone(p) ** 2.2)
        self.hatch(polys, 63, spacing * 1.3, w=w * 0.8, opacity=0.6, tone=lambda p: tone(p) ** 4.0)

    # writing (mirrored, as Leonardo wrote)

    def _mirror_text(self, s, x_right, y, size, opacity, rot=0.0, title=False):
        (x_right, y), = self._fwd([(x_right, y)])
        self._mark("text", "text", len(s) * size * 0.5, s=s, x=x_right, y=y, size=size,
                   opacity=opacity, rot=rot, title=title)

    def note(self, lines, x_right, y_top, size=17, lh=1.42, opacity=0.82):
        rot = self.rng.uniform(-1.6, 1.2)
        for i, s in enumerate(lines):
            y = y_top + size + i * size * lh
            self._mirror_text(s, x_right + self.rng.uniform(-5, 5), y, size, opacity, rot)

    def title(self, s, x_right, y, size=34):
        self._mirror_text(s, x_right, y, size, 0.9, self.rng.uniform(-1.2, 0.6), title=True)

    def label(self, letter, x, y, size=21):
        self._mirror_text(letter, x, y, size, 0.85)

    # output

    def _render(self, m, prog) -> str:
        if prog <= 0:
            return ""
        if m["kind"] == "stroke":
            pts = m["pts"]
            if prog < 1:
                k = prog * (len(pts) - 1)
                i = int(k)
                if i + 1 < len(pts):
                    f = k - i
                    (ax, ay), (bx, by) = pts[i], pts[i + 1]
                    pts = pts[: i + 1] + [(ax + (bx - ax) * f, ay + (by - ay) * f)]
                if len(pts) < 2:
                    return ""
            dash = f' stroke-dasharray="{m["dash"]}"' if m["dash"] else ""
            return (f'<path d="{_catmull(pts)}" fill="none" stroke="{m["color"]}" stroke-width="{_f(m["w"])}" '
                    f'stroke-linecap="round" stroke-linejoin="round" opacity="{m["opacity"]:.2f}"{dash}/>')
        if m["kind"] == "hatch":
            subs = m["subs"][: max(1, round(prog * len(m["subs"])))]
            return (f'<path d="{"".join(subs)}" fill="none" stroke="{m["color"]}" stroke-width="{_f(m["w"])}" '
                    f'stroke-linecap="round" opacity="{m["opacity"]:.2f}"/>')
        # Mirrored text is revealed from right to left, the direction Leonardo wrote.
        x, y, size, rot = m["x"], m["y"], m["size"], m["rot"]
        clip = ""
        if prog < 1:
            width = len(m["s"]) * size * 0.56 + 24
            cid = f"w{m['seq']}"
            reveal = width * prog
            clip = (f'<clipPath id="{cid}"><rect x="{_f(x + 12 - reveal)}" y="{_f(y - size * 1.3)}" '
                    f'width="{_f(reveal)}" height="{_f(size * 1.9)}" transform="rotate({rot:.2f} {_f(x)} {_f(y)})"/></clipPath>')
            # The clip goes on an untransformed wrapper so its rect is in page coordinates.
            wrap = (f'<g clip-path="url(#{cid})">', "</g>")
        else:
            wrap = ("", "")
        return (f'{clip}{wrap[0]}<text transform="translate({_f(x)} {_f(y)}) rotate({rot:.2f}) scale(-1 1)" '
                f'font-family="{FONT}" font-size="{size}" fill="{INK}" opacity="{m["opacity"]:.2f}">'
                f'{escape(m["s"])}</text>{wrap[1]}')

    def svg(self, progress: dict[int, float] | None = None) -> str:
        """The page as SVG. `progress` maps a mark's seq to how much of it
        is drawn (0..1); marks missing from it are not drawn yet. None draws
        the finished page."""
        def layer(name):
            return "".join(self._render(m, 1.0 if progress is None else progress.get(m["seq"], 0.0))
                           for m in self.marks if m["layer"] == name)

        r = random.Random(self.seed * 7919)
        s = self.seed
        foxing = []
        for _ in range(34):
            x, y = r.uniform(30, W - 30), r.uniform(30, H - 30)
            foxing.append(
                f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r.uniform(1.5, 11))}" fill="#7d4d22" '
                f'opacity="{r.uniform(0.05, 0.22):.2f}" filter="url(#soft)"/>'
            )
        sx, sy = r.choice([(r.uniform(150, 400), r.uniform(150, 350)), (r.uniform(1200, 1450), r.uniform(850, 1050))])
        stain = (
            f'<ellipse cx="{_f(sx)}" cy="{_f(sy)}" rx="{_f(r.uniform(70, 110))}" ry="{_f(r.uniform(60, 95))}" '
            f'fill="none" stroke="#8a5a2b" stroke-width="4" opacity="0.10" filter="url(#soft)" '
            f'transform="rotate({r.uniform(-30, 30):.1f} {_f(sx)} {_f(sy)})"/>'
        )
        region = f'filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"'
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<filter id="fibers" {region}><feTurbulence type="fractalNoise" baseFrequency="0.85 0.55" numOctaves="3" seed="{s}"/>
<feColorMatrix type="matrix" values="0 0 0 0 0.33  0 0 0 0 0.22  0 0 0 0 0.10  0.55 0 0 0 -0.2"/></filter>
<filter id="blotch" {region}><feTurbulence type="fractalNoise" baseFrequency="0.0032" numOctaves="4" seed="{s + 7}"/>
<feColorMatrix type="matrix" values="0 0 0 0 0.52  0 0 0 0 0.35  0 0 0 0 0.16  1.2 0 0 0 -0.5"/></filter>
<filter id="wob" {region}><feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="2" seed="{s + 3}" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="3.6" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feGaussianBlur in="d" stdDeviation="0.35"/></filter>
<filter id="wobtext" {region}><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="1" seed="{s + 5}" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>
<radialGradient id="vignette" cx="50%" cy="48%" r="72%">
<stop offset="0.55" stop-color="#6b4423" stop-opacity="0"/><stop offset="1" stop-color="#5a3518" stop-opacity="0.5"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="#e8d6ae"/>
<rect width="{W}" height="{H}" filter="url(#blotch)"/>
<rect width="{W}" height="{H}" filter="url(#fibers)"/>
{"".join(foxing)}
{stain}
<rect width="{W}" height="{H}" fill="url(#vignette)"/>
<g filter="url(#wob)" style="mix-blend-mode:multiply">
<g>{layer("chalk")}</g>
<g>{layer("hatch")}</g>
<g>{layer("ink")}</g>
</g>
<g filter="url(#wobtext)" style="mix-blend-mode:multiply">{layer("text")}</g>
<text x="{W - 70}" y="{H - 38}" text-anchor="end" font-family="{FONT}" font-size="19" fill="#5e4a38" opacity="0.62">Codice Moderno · {escape(self.folio)}</text>
</svg>"""
