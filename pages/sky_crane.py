"""f. 4r — the Mars sky crane (Curiosity, August 2012): a rocket crane lowering a rover on cables."""

from __future__ import annotations

import math

from codex import CHALK, Page, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import draw_visible, not_in, place

LIGHT = (-1.0, -1.2)


def _T(cx, cy, s, rot=0.0):
    a = math.radians(rot)
    c, n = math.cos(a), math.sin(a)
    return lambda pts: [(cx + (x * c - y * n) * s, cy + (x * n + y * c) * s) for x, y in pts]


def _plume(p: Page, start, ang, length, s, wobble=6.0):
    """Rocket exhaust as Leonardo drew flame and falling water: wavering lines that spread."""
    for k in range(6):
        spread = (k - 2.5) * 3.2
        pts = []
        for j in range(18):
            t = j / 17
            a = math.radians(ang + spread * t)
            d = length * t
            sway = math.sin(t * 7 + k) * wobble * t * s
            pts.append((start[0] + d * math.sin(a) + sway, start[1] + d * math.cos(a)))
        p.contour(pts, closed=False, w=0.8, passes=1, opacity=0.55 - 0.02 * abs(k - 2.5))


def _stage(p: Page, cx, cy, s=1.0, fire=0.0, detail=True, rot=0.0):
    T = _T(cx, cy, s, rot)
    deck = T([(-160, -18), (160, -18), (150, 22), (-150, 22)])
    tanks = [T(ellipse_pts(x, y, 26, 26)) for x, y in ((-72, -42), (0, -48), (72, -42))]
    for t in tanks:
        draw_visible(p, t, [deck], w=1.6 * s ** 0.4)
        p.shade(t, lambda q, t=t: form_tone(t, LIGHT, rim=10 * s, base=0.05)(q) * not_in([deck])(q), spacing=3.0)
    p.contour(deck, w=2.0 * s ** 0.4, ghosts=1 if detail else 0)
    p.shade(deck, form_tone(deck, LIGHT, rim=14 * s, base=0.15), spacing=3.0)
    for x in (-110, -36, 36, 110):
        p.contour(T([(x, -18), (x * 0.65, -46)]), closed=False, w=1.0, passes=1, opacity=0.7)
    truss = [(-150 + k * 25, -14 if k % 2 else 18) for k in range(13)]
    p.contour(T(truss), closed=False, w=0.8, passes=1, opacity=0.6)
    exits = []
    for x, tilt in ((-140, 22), (-96, 10), (96, -10), (140, -22)):
        bell = T(place([(-6, 0), (6, 0), (12, 26), (-12, 26)], tilt, (x, 22)))
        p.contour(bell, w=1.3 * s ** 0.4, passes=1)
        p.hatch(bell, 45, 2.0, w=0.6, opacity=0.8)
        exits.append((T(place([(0, 26)], tilt, (x, 22)))[0], -tilt))
    if fire:
        for pos, ang in exits:
            _plume(p, pos, ang - rot, fire, s)
    return T([(-90, 22), (0, 22), (90, 22)])


def _rover(p: Page, cx, top, s=1.0, deployed=True, detail=True):
    T = _T(cx, top, s)
    body = T(rrect_pts(-100, 0, 200, 56, 6))
    rtg = T([(-100, 8), (-152, -26), (-164, -12), (-110, 22)])
    mast = T([(70, 0), (70, -106)])
    head = T(rrect_pts(52, -128, 40, 24, 3))
    p.contour(rtg, w=1.4 * s ** 0.4)
    for k in range(4):
        p.contour(T([(-112 - k * 11, -2 - k * 7), (-120 - k * 11, 4 - k * 7)]), closed=False, w=0.8, passes=1)
    p.shade(rtg, form_tone(rtg, LIGHT, rim=8, base=0.3), spacing=2.6)
    p.contour(body, w=1.9 * s ** 0.4, ghosts=1 if detail else 0)
    p.shade(body, form_tone(body, LIGHT, rim=14 * s, base=0.1), spacing=3.0)
    p.contour(mast, closed=False, w=1.6 * s ** 0.4, passes=1)
    p.contour(head, w=1.4 * s ** 0.4, passes=1)
    p.hatch(head, 45, 2.2, w=0.6, opacity=0.7)
    p.contour(T(ellipse_pts(84, -116, 5, 5)), w=0.9, passes=1)
    p.contour(T([(100, 20), (126, 34), (114, 52)]), closed=False, w=1.3 * s ** 0.4, passes=1)
    p.contour(T(ellipse_pts(114, 56, 8, 8)), w=1.1, passes=1)

    drop = 46 if deployed else 22
    wheels = [(85, 56 + drop), (0, 56 + drop), (-85, 56 + drop)]
    rocker, bogie = (12, 46), (-42, 56 + drop - 22)
    for a, b in ((rocker, wheels[0]), (rocker, bogie), (bogie, wheels[1]), (bogie, wheels[2])):
        p.contour(T([a, b]), closed=False, w=2.0 * s ** 0.4, passes=1)
    for c in (rocker, bogie):
        p.contour(T(ellipse_pts(*c, 5, 5)), w=1.0, passes=1)
    for wx, wy in wheels:
        tyre = T(ellipse_pts(wx, wy, 28, 28))
        hub = T(ellipse_pts(wx, wy, 8, 8))
        p.contour(tyre, w=1.8 * s ** 0.4)
        p.contour(hub, w=1.0, passes=1)
        if detail:
            for k in range(14):
                a = math.radians(k * 360 / 14)
                p.contour(T([(wx + 22 * math.cos(a), wy + 22 * math.sin(a)), (wx + 28 * math.cos(a), wy + 28 * math.sin(a))]),
                          closed=False, w=0.8, passes=1, opacity=0.8)
        p.shade([tyre, hub], form_tone(tyre, LIGHT, rim=10 * s, base=0.1), spacing=2.8)
    return T([(-90, 0), (0, 0), (90, 0)]), T([(0, 56 + drop + 28)])[0]


def _dust(p: Page, cx, cy, r):
    for turn in range(2):
        pts = []
        for j in range(60):
            t = j / 59
            a = math.radians(turn * 180 + 720 * t)
            rr = r * (0.15 + 0.85 * t)
            pts.append((cx + rr * math.cos(a), cy - abs(rr * math.sin(a)) * 0.55))
        p.contour(pts, closed=False, w=0.8, passes=1, opacity=0.55)


def _hero(p: Page):
    cx, ground = 520, 900
    hooks = _stage(p, cx, 290, 1.0, fire=0)
    tops, _ = _rover(p, cx, 640, 1.0, deployed=True)
    for a, b in zip(hooks, tops):
        p.contour([a, b], closed=False, w=1.0, passes=1, opacity=0.9)
    p.contour([hooks[1], (cx + 18, 470), (cx - 10, 560), tops[1]], closed=False, w=0.8, passes=1, opacity=0.6)
    for x, tilt in ((-140, -22), (-96, -10), (96, 10), (140, 22)):
        start = (cx + x + (8 if x > 0 else -8), 340)
        _plume(p, start, tilt * 0.9, 230, 1.0, wobble=7)
    p.line((150, ground), (900, ground), w=1.3, overshoot=10)
    for k in range(26):
        x = 170 + k * 28 + p.rng.uniform(-8, 8)
        p.contour(ellipse_pts(x, ground + 6 + p.rng.uniform(0, 10), p.rng.uniform(3, 7), p.rng.uniform(1.5, 3)), w=0.8, passes=1, opacity=0.6)
    for x in (300, 742):
        _dust(p, x, ground - 4, 60)
    p.chalk_line((cx, 210), (cx, ground + 20), dash="6 5", opacity=0.45)
    p.chalk_line((cx + 210, 312), (cx + 210, 640), overshoot=0, opacity=0.6)
    for y in (312, 640):
        p.chalk_line((cx + 200, y), (cx + 220, y), overshoot=0, opacity=0.6)
    p.label("b", cx + 210, 270)


def _descent(p: Page):
    cx, cy, s = 1190, 250, 0.42
    _stage(p, cx, cy, s, fire=70, detail=False)
    _rover(p, cx, cy + 30 * s, s, deployed=False, detail=False)
    p.label("a", cx + 92, cy - 30)


def _touchdown(p: Page):
    ground, s = 900, 0.42
    _rover(p, 1070, ground - (56 + 46 + 28) * s, s, deployed=True, detail=False)
    p.line((960, ground), (1520, ground), w=1.1, overshoot=6)
    start = (1100, 700)
    path = []
    for k in range(31):
        t = k / 30
        path.append((start[0] + 370 * t, start[1] - 120 * math.sin(math.pi * t * 0.8) + 260 * t * t))
    p.chalk(path, closed=False, dash="6 5", opacity=0.7)
    p.arrow_head(path[-1], path[-3], color=CHALK, layer="chalk", w=1.1)
    _stage(p, path[7][0], path[7][1] - 30, s, fire=45, detail=False, rot=-18)
    crash = path[-1]
    for k in range(3):
        _dust(p, crash[0] - 10 + k * 14, ground - 2, 26 + k * 8)
    p.label("c", 1150, 640)


def folio_sky_crane() -> Page:
    p = Page(seed=404, folio="")
    _hero(p)
    _descent(p)
    _touchdown(p)

    p.title("Del carro calato dal cielo", 760, 110)
    p.note([
        "questo carro fu mandato in un altro mondo",
        "e una gru di fuoco lo calò con funi",
        "poi la gru volò via e cadde lontano",
    ], 1530, 430)
    p.note([
        "a. discende con il carro in grembo",
        "b. cala il carro con tre funi",
        "c. tagliate le funi fugge e muore",
    ], 1530, 960)
    p.note(["la polvere si volge come l'acqua"], 760, 940)
    return p


NOTES = {
    "Del carro calato dal cielo": "Of the cart lowered from the sky",
    "questo carro fu mandato in un altro mondo": "this cart was sent to another world",
    "e una gru di fuoco lo calò con funi": "and a crane of fire lowered it on ropes",
    "poi la gru volò via e cadde lontano": "then the crane flew away and fell far off",
    "a. discende con il carro in grembo": "a. it descends with the cart in its lap",
    "b. cala il carro con tre funi": "b. it lowers the cart on three ropes",
    "c. tagliate le funi fugge e muore": "c. the ropes cut, it flees and dies",
    "la polvere si volge come l'acqua": "the dust turns like water",
}
