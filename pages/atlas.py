"""f. 3r — the ATLAS detector at CERN (2008), end-on, at its true proportions: 25 m high."""

from __future__ import annotations

import math

from codex import Page, ellipse_pts, form_tone, lin_tone, radial_tone, rrect_pts
from pages.common import place

LIGHT = (-1.0, -1.2)
C = (560, 620)
R = 400            # 12.5 m
PX_M = R / 12.5


def _ring(r0, r1, a0=0, a1=360):
    outer = ellipse_pts(*C, r1, r1, 0, a0, a1)
    inner = ellipse_pts(*C, r0, r0, 0, a0, a1)
    return outer, inner


def _polar(r, deg):
    a = math.radians(deg)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


def _end_view(p: Page):
    # muon chambers: three stations between the coils and one outer ring
    coils = []
    for k in range(8):
        ang = 22.5 + k * 45
        coil = place(rrect_pts(150, -21, 172, 42, 18), ang, C)
        coils.append(coil)
    chambers = []
    for k in range(8):
        for r, depth in ((168, 18), (238, 20), (340, 22)):
            ang = k * 45
            if ang in (45, 90, 135) and r > 300:
                continue
            half = r * math.tan(math.radians(22.5)) * 0.66
            chambers.append(place(rrect_pts(r, -half, depth, half * 2, 2), ang, C))

    for ch in chambers:
        p.contour(ch, w=1.3, passes=1)
        p.hatch(ch, 45, 3.0, w=0.6, opacity=0.6, tone=form_tone(ch, LIGHT, rim=8, base=0.15))
        if p.rng.random() < 0.6:
            mid = sum(q[0] for q in ch) / len(ch), sum(q[1] for q in ch) / len(ch)
            d = math.dist(mid, C)
            ux, uy = (mid[0] - C[0]) / d, (mid[1] - C[1]) / d
            p.contour([(mid[0] - uy * 12, mid[1] + ux * 12), (mid[0] + uy * 12, mid[1] - ux * 12)],
                      closed=False, w=0.7, passes=1, opacity=0.6)
    for coil in coils:
        p.contour(coil, w=1.9, ghosts=1)
        p.shade(coil, form_tone(coil, LIGHT, rim=14, base=0.1), spacing=3.0)

    # the tile calorimeter: a thick ring cut into 64 wedges
    outer, inner = _ring(64, 136)
    p.contour(outer, w=2.0, ghosts=1)
    p.contour(inner, w=1.5)
    for k in range(64):
        a = k * 360 / 64
        p.contour([_polar(66, a), _polar(134, a)], closed=False, w=0.6, passes=1, opacity=0.55)
    p.shade([outer, inner], lambda q: 0.12 + 0.4 * lin_tone((C[0] - 136, C[1] - 136), (C[0] + 136, C[1] + 136))(q), spacing=3.2)
    p.contour(ellipse_pts(*C, 100, 100), w=0.8, passes=1, opacity=0.6)

    # the liquid-argon calorimeter, folded like an accordion
    acc = []
    n = 96
    for k in range(n):
        a = k * 360 / n
        acc.append(_polar(42 if k % 2 else 60, a))
    p.contour(acc, w=0.8, passes=1, opacity=0.8)
    p.contour(ellipse_pts(*C, 38, 38), w=1.2, passes=1)

    # the inner tracker: thin circles round the beam
    for r in (9, 16, 23, 30):
        p.contour(ellipse_pts(*C, r, r), w=0.8, passes=1, opacity=0.75)
    p.contour(ellipse_pts(*C, 3, 3), w=1.4, passes=1)

    # the feet it stands on, and the cavern floor
    floor = C[1] + R
    for sx in (-1, 1):
        foot = [(C[0] + sx * 120, floor), (C[0] + sx * 240, floor), (C[0] + sx * 214, floor - 96), (C[0] + sx * 146, floor - 96)]
        p.contour(foot, w=1.8)
        p.shade(foot, form_tone(foot, LIGHT, rim=14, base=0.2), spacing=3.0)
    p.line((140, floor), (1080, floor), w=1.3, overshoot=10)
    p.hatch([(160, floor), (1060, floor), (1040, floor + 14), (180, floor + 14)], 45, 2.6, w=0.8, opacity=0.7)


def _tracks(p: Page):
    """The collision: curling tracks like water in a whirlpool, and four straight muons."""
    rng = p.rng
    for k in range(13):
        ang = rng.uniform(0, 360)
        radius = rng.uniform(40, 240)
        side = rng.choice((-1, 1))
        length = rng.uniform(55, 130)
        pts = []
        for j in range(30):
            s = length * j / 29
            th = s / radius
            x = radius * math.sin(th)
            y = side * radius * (1 - math.cos(th))
            a = math.radians(ang)
            pts.append((C[0] + x * math.cos(a) - y * math.sin(a), C[1] + x * math.sin(a) + y * math.cos(a)))
        p.contour(pts, closed=False, w=0.9, passes=1, opacity=0.8)
        end = pts[-1]
        if math.dist(end, C) > 62:
            blob = ellipse_pts(*end, 7, 4, ang)
            p.hatch(blob, 45, 1.6, w=0.7, opacity=0.8)
    for k in range(3):
        a0 = rng.uniform(0, 360)
        pts = []
        for j in range(60):
            t = j / 59
            r = 4 + 26 * t
            a = math.radians(a0 + 760 * t)
            pts.append((C[0] + r * math.cos(a), C[1] + r * math.sin(a)))
        p.contour(pts, closed=False, w=0.7, passes=1, opacity=0.65)
    for ang in (38, 151, 214, 302):
        far = _polar(398, ang)
        p.contour([C, _polar(200, ang + 1.5), far], closed=False, w=1.3, passes=1)
        p.arrow_head(far, _polar(380, ang + 0.2), size=10, w=1.2)


def _man(p: Page, x, floor, h):
    """A small figure for scale."""
    head = ellipse_pts(x, floor - h + h * 0.07, h * 0.07, h * 0.08)
    p.contour(head, w=1.2, passes=1)
    neck, hip = (x, floor - h * 0.84), (x, floor - h * 0.47)
    p.contour([neck, hip], closed=False, w=1.4, passes=1)
    p.contour([(x - h * 0.13, floor - h * 0.55), (x - h * 0.1, floor - h * 0.8), neck,
               (x + h * 0.1, floor - h * 0.8), (x + h * 0.15, floor - h * 0.56)], closed=False, w=1.2, passes=1)
    p.contour([(x - h * 0.1, floor), hip, (x + h * 0.11, floor)], closed=False, w=1.3, passes=1)


def _side_view(p: Page):
    x0, x1, yc = 1080, 1500, 420
    s = (x1 - x0) / 44.0
    half = 12.5 * s
    wheels = [(x0, x0 + 22), (x1 - 22, x1)]
    for a, b in wheels:
        w = rrect_pts(a, yc - half, b - a, half * 2, 4)
        p.contour(w, w=1.6)
        p.shade(w, form_tone(w, LIGHT, rim=8, base=0.35), spacing=2.8)
    barrel = rrect_pts(x0 + 50, yc - 10 * s, x1 - x0 - 100, 20 * s, 6)
    p.contour(barrel, w=1.8, ghosts=1)
    for k in range(-3, 4):
        y = yc + k * 10 * s / 3.4
        p.contour([(x0 + 54, y), (x1 - 54, y)], closed=False, w=0.7, passes=1, opacity=0.55)
    calo = rrect_pts(x0 + 130, yc - 4.25 * s, x1 - x0 - 260, 8.5 * s, 4)
    p.contour(calo, w=1.5)
    p.shade([barrel, calo], lambda q: 0.35, spacing=3.6)
    p.shade(calo, lin_tone((0, yc - 4.25 * s), (0, yc + 4.25 * s), lo=0.2), spacing=3.0)
    tracker = rrect_pts(x0 + 175, yc - 1.15 * s, x1 - x0 - 350, 2.3 * s, 2)
    p.contour(tracker, w=1.1, passes=1)
    p.chalk_line((x0 - 50, yc), (x1 + 40, yc), dash="8 5", opacity=0.6)
    p.arrow_head((x0 + 160, yc), (x0 + 120, yc), color="#a5462b", layer="chalk", w=1.1)
    p.arrow_head((x1 - 160, yc), (x1 - 120, yc), color="#a5462b", layer="chalk", w=1.1)
    floor = yc + half
    p.line((x0 - 30, floor), (x1 + 30, floor), w=1.0, overshoot=6)
    _man(p, x1 + 18, floor, 1.8 * s)


def folio_atlas() -> Page:
    p = Page(seed=303, folio="")
    p.chalk(ellipse_pts(*C, R + 14, R + 14), dash="3 7", opacity=0.45)
    for k in range(8):
        a = 22.5 + k * 45
        p.chalk_line(_polar(140, a), _polar(R + 10, a), dash="6 6", opacity=0.35, overshoot=0)
    _end_view(p)
    _tracks(p)
    _man(p, 1010, C[1] + R, 1.8 * PX_M)
    _side_view(p)

    p.label("a", C[0] + 22, C[1] - 6)
    p.label("b", *_polar(100, 200))
    p.label("c", *_polar(255, 22.5 + 45 * 5))
    p.label("d", *_polar(250, 92))
    p.label("e", 1036, C[1] + R - 70)

    p.title("Dell'occhio che vede il più piccolo", 900, 110)
    p.note([
        "questo è uno occhio grande come una chiesa",
        "per vedere cose più piccole d'ogni cosa",
        "due correnti di materia si scontrano nel mezzo",
        "e le schegge volano come nel diluvio",
    ], 1530, 640)
    p.note(["dal fianco  lungo come una nave"], 1500, 560)
    p.note([
        "a. il cuore dove nasce l'urto",
        "b. le fette che pesano la forza",
        "c. otto calamite grandi come case",
        "d. le camere che seguono le schegge",
        "e. l'omo per misura",
    ], 1530, 900)
    return p


NOTES = {
    "Dell'occhio che vede il più piccolo": "Of the eye that sees the smallest",
    "questo è uno occhio grande come una chiesa": "this is an eye as large as a church",
    "per vedere cose più piccole d'ogni cosa": "for seeing things smaller than anything",
    "due correnti di materia si scontrano nel mezzo": "two streams of matter collide in the middle",
    "e le schegge volano come nel diluvio": "and the splinters fly as in the deluge",
    "dal fianco  lungo come una nave": "from the side, long as a ship",
    "a. il cuore dove nasce l'urto": "a. the heart where the collision is born",
    "b. le fette che pesano la forza": "b. the slices that weigh the force",
    "c. otto calamite grandi come case": "c. eight magnets as large as houses",
    "d. le camere che seguono le schegge": "d. the chambers that follow the splinters",
    "e. l'omo per misura": "e. the man, for measure",
}
