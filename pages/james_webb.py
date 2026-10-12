"""f. 11r — the James Webb Space Telescope (2021): eighteen gold hexagons, a five-layer sunshield."""

from __future__ import annotations

import math

from codex import CHALK, Page, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import draw_visible, not_in, smooth_closed

LIGHT = (-1.0, -1.2)
MC = (480, 560)   # centre of the primary mirror
HR = 70           # hexagon circumradius


def _hex(c, r, rot=30):
    return [(c[0] + r * math.cos(math.radians(rot + k * 60)), c[1] + r * math.sin(math.radians(rot + k * 60))) for k in range(6)]


def _segments():
    cells = []
    for q in range(-2, 3):
        for r in range(-2, 3):
            s = -q - r
            ring = max(abs(q), abs(r), abs(s))
            if 1 <= ring <= 2:
                x = MC[0] + HR * math.sqrt(3) * (q + r / 2)
                y = MC[1] + HR * 1.5 * r
                cells.append((x, y))
    return cells


def _primary(p: Page):
    rng = p.rng
    cells = _segments()
    sec = ellipse_pts(MC[0], MC[1] - 6, 30, 30)
    struts = []
    for end in ((MC[0], MC[1] - 300), (MC[0] - 262, MC[1] + 214), (MC[0] + 262, MC[1] + 214)):
        dx, dy = end[0] - MC[0], end[1] - MC[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * 4, dx / L * 4
        struts.append([(MC[0] + nx, MC[1] + ny), (end[0] + nx, end[1] + ny), (end[0] - nx, end[1] - ny), (MC[0] - nx, MC[1] - ny)])
    front = [sec] + struts
    for c in cells:
        h = _hex(c, HR * 0.95, rot=90)
        draw_visible(p, h, front, w=1.6)
        base = rng.uniform(0.0, 0.3)
        glint = rng.uniform(-40, 40)
        tone = lambda q, c=c, base=base, glint=glint: (0.0 if -14 < (q[0] - c[0]) - (q[1] - c[1]) * 0.7 + glint < 16
                                                     else base + 0.5 * lin_tone((c[0] - 60, c[1] - 60), (c[0] + 60, c[1] + 60))(q))
        p.shade(h, lambda q, t=tone: t(q) * not_in(front)(q), spacing=3.2)
        p.contour(_hex(c, HR * 0.86, rot=90), w=0.6, passes=1, opacity=0.35)
    hole = _hex(MC, HR * 0.95, rot=90)
    draw_visible(p, hole, front, w=1.0, dash="4 4")
    for s in struts:
        p.contour(s, w=1.2, passes=1)
        p.hatch(s, 45, 2.0, w=0.6, opacity=0.7)
    p.contour(sec, w=1.8)
    p.shade(sec, form_tone(sec, LIGHT, rim=10, base=0.25), spacing=2.6)
    p.contour(ellipse_pts(MC[0], MC[1] - 6, 12, 12), w=1.0, passes=1)
    p.label("d", MC[0] + 70, MC[1] - 64)
    p.chalk(ellipse_pts(*MC, 330, 330), dash="3 7", opacity=0.45)
    p.chalk_line((MC[0] - 360, MC[1]), (MC[0] + 360, MC[1]), dash="6 6", opacity=0.4)


def _side_view(p: Page):
    """The whole observatory from the side, with the sun below and to the left."""
    layers = []
    for k in range(5):
        y = 450 + k * 9
        spread = k * 5
        layer = smooth_closed([(1010 - spread, y + 6), (1260, y - 4), (1500 + spread, y + 6), (1260, y + 3)], n=6)
        layers.append(layer)
        p.contour(layer, w=1.2 if k else 1.5, passes=1)
    p.hatch(layers[-1], 45, 2.4, w=0.6, opacity=0.7)
    bus = rrect_pts(1222, 500, 70, 46, 3)
    p.contour(bus, w=1.6)
    p.shade(bus, form_tone(bus, LIGHT, rim=8, base=0.2), spacing=2.6)
    panel = [(1222, 520), (1150, 560), (1156, 572), (1228, 532)]
    p.contour(panel, w=1.2, passes=1)
    p.hatch(panel, 0, 3.0, w=0.6, opacity=0.8)
    p.contour(ellipse_pts(1300, 556, 14, 6, 30), w=1.0, passes=1)
    mirror = [(x, y + 40) for x, y in ellipse_pts(1250, 250, 150, 40, 0, 20, 160)]
    p.contour(mirror, closed=False, w=2.2)
    p.contour([(x, y + 6) for x, y in mirror], closed=False, w=1.0, passes=1)
    p.contour([(1250, 440), (1250, 330)], closed=False, w=1.6, passes=1)
    for sx in (-1, 1):
        p.contour([(1250 + sx * 110, 300), (1250, 196)], closed=False, w=0.9, passes=1)
    p.contour([(1250 - 20, 194), (1250 + 20, 194)], closed=False, w=2.4, passes=1)
    for x in (1180, 1250, 1320):
        top = (x, 120)
        hit = (x, 286 + 0.002 * (x - 1250) ** 2)
        p.contour([top, hit, (1250, 198)], closed=False, w=0.6, passes=1, opacity=0.55)
    p.arrow_head((1250, 160), (1250, 140), size=8, w=0.9)
    sun = (1040, 660)
    p.contour(ellipse_pts(*sun, 20, 20), w=1.6, passes=1)
    for k in range(12):
        a = math.radians(k * 30)
        p.contour([(sun[0] + 26 * math.cos(a), sun[1] + 26 * math.sin(a)), (sun[0] + 40 * math.cos(a), sun[1] + 40 * math.sin(a))],
                  closed=False, w=1.0, passes=1)
    for x0 in (1080, 1140, 1200, 1260):
        p.chalk_line((sun[0] + 30, sun[1] - 20), (x0 + 20, 494), dash="5 5", opacity=0.55, overshoot=0)
    p.label("a", 1530, 476)


def _unfolding(p: Page):
    """b. folded to fit the rocket; c. opened like a flower."""
    y0, h = 820, 120
    for k, ang in enumerate((88, 45, 0)):
        cx = 1090 + k * 175
        core = rrect_pts(cx - 40, y0, 80, h, 2)
        p.contour(core, w=1.5)
        for sx in (-1, 1):
            w = 42 * math.cos(math.radians(ang))
            skew = 18 * math.sin(math.radians(ang))
            x_edge = cx + sx * 40
            wing = [(x_edge, y0), (x_edge + sx * w, y0 - skew), (x_edge + sx * w, y0 + h - skew), (x_edge, y0 + h)]
            p.contour(wing, w=1.3, passes=1)
            p.hatch(wing, 45, 2.6, w=0.6, opacity=0.6 + 0.2 * (ang > 0))
        for r in range(3):
            for col in (-1, 0, 1):
                p.contour(_hex((cx + col * 25, y0 + 22 + r * 38), 13, rot=90), w=0.7, passes=1, opacity=0.7)
        if k < 2:
            p.arrow_head((cx + 118, y0 + h / 2), (cx + 96, y0 + h / 2), size=9, w=1.1)
            p.contour([(cx + 78, y0 + h / 2), (cx + 118, y0 + h / 2)], closed=False, w=1.0, passes=1)
    p.label("b", 1100, y0 - 30)
    p.label("c", 1446, y0 - 30)


def folio_james_webb() -> Page:
    p = Page(seed=1111, folio="")
    _primary(p)
    _side_view(p)
    _unfolding(p)

    p.title("Dello specchio d'oro che guarda il principio", 940, 110)
    p.note([
        "diciotto specchi d'oro fanno uno occhio",
        "che vede la luce partita",
        "quando il mondo era giovane",
        "d. lo specchio piccolo su tre gambe",
    ], 780, 930)
    p.note([
        "a. cinque veli tra il sole e l'occhio",
        "dalla parte del sole arde",
        "dall'altra parte gela",
    ], 1530, 600)
    p.note([
        "b. si piegò per entrare nel razzo",
        "c. e si aperse come uno fiore",
    ], 1530, 980)
    return p


NOTES = {
    "Dello specchio d'oro che guarda il principio": "Of the golden mirror that looks back to the beginning",
    "diciotto specchi d'oro fanno uno occhio": "eighteen golden mirrors make one eye",
    "che vede la luce partita": "that sees light which set out",
    "quando il mondo era giovane": "when the world was young",
    "d. lo specchio piccolo su tre gambe": "d. the small mirror on three legs",
    "a. cinque veli tra il sole e l'occhio": "a. five veils between the sun and the eye",
    "dalla parte del sole arde": "on the sun's side it burns",
    "dall'altra parte gela": "on the other side it freezes",
    "b. si piegò per entrare nel razzo": "b. it folded itself to fit inside the rocket",
    "c. e si aperse come uno fiore": "c. and opened like a flower",
}
