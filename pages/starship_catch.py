"""f. 14r — the Starship booster catch (13 October 2024): a 70 m booster caught by the tower's arms."""

from __future__ import annotations

import math

from codex import CHALK, Page, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import draw_visible, not_in, place, smooth_closed

LIGHT = (-1.0, -1.2)
GROUND = 1080
TX0, TX1, TTOP = 440, 530, 210    # the tower
BX, BTOP, BLEN, BW = 700, 318, 440, 58   # the booster


def _tower(p: Page):
    legs = [(TX0, TTOP), (TX0, GROUND)], [(TX1, TTOP), (TX1, GROUND)]
    for a, b in legs:
        p.contour([a, b], closed=False, w=2.4, passes=2)
    y = TTOP
    while y < GROUND - 10:
        y1 = min(GROUND, y + 62)
        p.contour([(TX0, y), (TX1, y)], closed=False, w=1.1, passes=1)
        p.contour([(TX0, y), (TX1, y1)], closed=False, w=0.8, passes=1, opacity=0.8)
        p.contour([(TX1, y), (TX0, y1)], closed=False, w=0.8, passes=1, opacity=0.8)
        y = y1
    p.contour([(TX0 + 45, TTOP), (TX0 + 45, TTOP - 50)], closed=False, w=1.4, passes=1)
    p.hatch([(TX1 - 10, TTOP), (TX1, TTOP), (TX1, GROUND), (TX1 - 10, GROUND)], 45, 2.6, w=0.6, opacity=0.6)
    p.label("a", TX0 - 16, 620)


def _arms(p: Page):
    carriage = rrect_pts(TX0 - 12, 336, TX1 - TX0 + 24, 58, 3)
    p.contour(carriage, w=1.9)
    p.shade(carriage, form_tone(carriage, LIGHT, rim=10, base=0.3), spacing=2.6)
    top, bot = 346, 384
    tip = BX + BW / 2 + 40
    p.contour([(TX1 + 12, top), (tip, top + 4)], closed=False, w=2.0, passes=1)
    p.contour([(TX1 + 12, bot), (tip, bot - 6)], closed=False, w=2.0, passes=1)
    p.contour([(tip, top + 4), (tip + 10, top + 14), (tip, bot - 6)], closed=False, w=1.6, passes=1)
    x = TX1 + 12
    k = 0
    while x < tip - 10:
        x1 = min(tip, x + 34)
        y_top0, y_top1 = top + 4 * (x - TX1) / (tip - TX1), top + 4 * (x1 - TX1) / (tip - TX1)
        y_bot0, y_bot1 = bot - 6 * (x - TX1) / (tip - TX1), bot - 6 * (x1 - TX1) / (tip - TX1)
        p.contour([(x, y_top0), (x1, y_bot1)] if k % 2 else [(x, y_bot0), (x1, y_top1)], closed=False, w=0.8, passes=1)
        x, k = x1, k + 1
    for x in (BX - BW / 2 - 6, BX + BW / 2 + 6):
        p.contour(rrect_pts(x - 5, top - 8, 10, 10, 2), w=1.0, passes=1)
    p.label("b", tip + 34, 336)


def _booster(p: Page, cx, top, s=1.0, rot=0.0, flame=0.0, detail=True):
    L, W = BLEN * s, BW * s
    body_l = [(-W / 2, 0), (W / 2, 0), (W / 2, L - 26 * s), (W / 2 + 6 * s, L), (-W / 2 - 6 * s, L), (-W / 2, L - 26 * s)]
    body = place(body_l, rot, (cx, top))
    fins = []
    for side in (-1, 1):
        fin_l = rrect_pts(side * W / 2 + (0 if side > 0 else -24 * s), 18 * s, 24 * s, 26 * s, 1)
        fins.append(place(fin_l, rot, (cx, top)))
    p.contour(body, w=2.0 * s ** 0.4, ghosts=1 if detail else 0)
    p.shade(body, lambda q: lin_tone(place([(-W / 2, 0)], rot, (cx, top))[0], place([(W / 2, 0)], rot, (cx, top))[0],
                                     gamma=1.6, lo=0.05)(q) * not_in(fins)(q), spacing=3.0 if detail else 2.6)
    for fin in fins:
        p.contour(fin, w=1.3 * s ** 0.4, passes=1)
        p.hatch(fin, 45, 3.0 * max(s, 0.5), w=0.6, opacity=0.8, max_len=200, trim=0)
        p.hatch(fin, -45, 3.0 * max(s, 0.5), w=0.6, opacity=0.8, max_len=200, trim=0)
    if detail:
        for k in range(1, 9):
            y = k * L / 9
            p.contour(place([(-W / 2, y), (W / 2, y)], rot, (cx, top)), closed=False, w=0.6, passes=1, opacity=0.45)
        for k in range(5):
            bell = place([(-22 + k * 11 - 4, L), (-22 + k * 11 + 4, L), (-22 + k * 11 + 6, L + 10), (-22 + k * 11 - 6, L + 10)], rot, (cx, top))
            p.contour(bell, w=0.9, passes=1)
    if flame:
        base = place([(0, L + 10 * s)], rot, (cx, top))[0]
        for k in range(7):
            sp = (k - 3) * 4 * s
            pts = []
            for j in range(14):
                t = j / 13
                d = flame * t
                pts.append(place([(sp * (1 + t * 0.8) + math.sin(t * 6 + k) * 3 * s, 10 * s + L + d)], rot, (cx, top))[0])
            p.contour(pts, closed=False, w=0.8, passes=1, opacity=0.6)
    return body


def _mount_and_ground(p: Page):
    table = [(640, 980), (780, 980), (780, 996), (640, 996)]
    p.contour(table, w=1.7)
    p.shade(table, lambda q: 0.5, spacing=2.4)
    for x in (650, 700, 720, 770):
        p.contour([(x, 996), (x + (6 if x > 710 else -6), GROUND)], closed=False, w=1.6, passes=1)
    p.contour(ellipse_pts(710, 980, 40, 6), w=1.2, passes=1)
    p.line((150, GROUND), (1010, GROUND), w=1.3, overshoot=10)
    p.hatch([(170, GROUND), (990, GROUND), (970, GROUND + 14), (190, GROUND + 14)], 45, 2.6, w=0.8, opacity=0.7)
    x, h = 900, 1.8 * 6.2 * 1.6
    p.contour(ellipse_pts(x, GROUND - h + 2, 2.2, 2.4), w=0.8, passes=1)
    p.contour([(x, GROUND - h + 4), (x, GROUND - h * 0.45)], closed=False, w=1.0, passes=1)
    p.contour([(x - 3, GROUND), (x, GROUND - h * 0.45), (x + 3, GROUND)], closed=False, w=0.9, passes=1)
    p.label("f", 930, GROUND - 40)


def _return(p: Page):
    """The booster coming home: it flips, falls, lights, and is caught."""
    path = [(1460 - 300 * t, 210 + 690 * (t ** 1.3)) for t in (k / 30 for k in range(31))]
    p.chalk(path, closed=False, dash="6 5", opacity=0.6)
    p.arrow_head(path[16], path[13], color=CHALK, layer="chalk", w=1.1)
    for k, (t, rot, fl) in enumerate(((0.0, 105, 0), (0.25, 60, 0), (0.5, 20, 0), (0.75, 4, 60), (1.0, 0, 30))):
        x, y = 1460 - 300 * t, 210 + 690 * (t ** 1.3)
        s = 0.24
        _booster(p, x, y - BLEN * s / 2, s=s, rot=rot, flame=fl, detail=False)
    x, y = path[-1]
    p.contour([(x - 40, y - 52), (x - 8, y - 50)], closed=False, w=1.4, passes=1)
    p.contour([(x + 40, y - 52), (x + 8, y - 50)], closed=False, w=1.4, passes=1)
    p.label("e", 1500, 300)


def _grid_fin(p: Page, x0=150, y0=250):
    frame = rrect_pts(x0, y0, 170, 128, 4)
    inner = rrect_pts(x0 + 11, y0 + 11, 148, 106, 2)
    p.contour(frame, w=2.0, ghosts=1)
    p.contour(inner, w=1.0, passes=1)
    p.hatch([frame, inner], 45, 2.6, w=0.6, opacity=0.7)
    p.hatch(inner, 45, 14, w=1.1, opacity=0.9, max_len=400, trim=0)
    p.hatch(inner, -45, 14, w=1.1, opacity=0.9, max_len=400, trim=0)
    p.contour([(x0 + 170, y0 + 50), (x0 + 200, y0 + 50)], closed=False, w=2.4, passes=1)
    p.contour([(x0 + 170, y0 + 78), (x0 + 200, y0 + 78)], closed=False, w=2.4, passes=1)
    p.contour(ellipse_pts(x0 + 207, y0 + 64, 10, 21), w=1.3)
    p.label("c", x0 + 100, y0 - 14)
    p.chalk_line((x0 + 222, y0 + 64), (BX - BW / 2 - 24, BTOP + 30), dash="4 6", opacity=0.5, overshoot=0)


def folio_starship_catch() -> Page:
    p = Page(seed=1414, folio="")
    _tower(p)
    _booster(p, BX, BTOP, flame=90)
    _arms(p)
    _mount_and_ground(p)
    _return(p)
    _grid_fin(p)
    p.label("d", BX + 60, BTOP + BLEN + 40)

    p.title("Del gigante preso con le bacchette", 960, 110)
    p.note([
        "questo vaso di fuoco alto come una torre",
        "torna dal cielo",
        "e la torre lo prende con due braccia",
        "come le mani prendono uno uccello",
    ], 1530, 980)
    p.note([
        "a. la torre di ferro",
        "b. le braccia che si chiudono",
        "c. le ali a graticola che lo guidano",
        "d. trentatré fuochi di sotto",
        "e. torna voltandosi nell'aria",
        "f. l'omo per misura",
    ], 420, 880)
    return p


NOTES = {
    "Del gigante preso con le bacchette": "Of the giant caught with chopsticks",
    "questo vaso di fuoco alto come una torre": "this vessel of fire, as tall as a tower",
    "torna dal cielo": "comes back from the sky",
    "e la torre lo prende con due braccia": "and the tower takes it in two arms",
    "come le mani prendono uno uccello": "as hands catch a bird",
    "a. la torre di ferro": "a. the iron tower",
    "b. le braccia che si chiudono": "b. the arms that close",
    "c. le ali a graticola che lo guidano": "c. the gridiron wings that steer it",
    "d. trentatré fuochi di sotto": "d. thirty-three fires beneath",
    "e. torna voltandosi nell'aria": "e. it returns, turning in the air",
    "f. l'omo per misura": "f. the man, for measure",
}
