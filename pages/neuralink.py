"""f. 12r — the Neuralink implant (2024): a coin in the skull, sixty-four threads into the brain."""

from __future__ import annotations

import math

from codex import Page, _inside, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import draw_visible, smooth_closed, visible

LIGHT = (-1.0, -1.2)
IMPLANT = (540, 336)


def _skull_and_brain(p: Page):
    skull = smooth_closed([(222, 620), (244, 478), (330, 372), (470, 322), (622, 338), (734, 414), (776, 528),
                           (764, 640), (704, 704), (566, 762), (420, 792), (296, 758)], n=10)
    brain = smooth_closed([(262, 616), (280, 494), (352, 404), (474, 358), (612, 372), (708, 438), (742, 532),
                           (726, 626), (650, 676), (520, 690), (420, 716), (318, 690)], n=10)
    cerebellum = smooth_closed([(326, 668), (362, 650), (432, 662), (446, 704), (400, 730), (342, 718)], n=6)
    hole = ellipse_pts(*IMPLANT, 30, 12)
    foramen = rrect_pts(436, 700, 48, 120, 4)
    for run in visible(skull, [hole, foramen]):
        p.contour(run, closed=False, w=2.2, overshoot=1)
    inner = [(x * 0.965 + 500 * 0.035, y * 0.965 + 560 * 0.035) for x, y in skull]
    draw_visible(p, inner, [hole, foramen], w=1.0, passes=1, opacity=0.7)
    p.hatch([skull, inner], 45, 2.6, w=0.6, opacity=0.7,
            tone=lambda q: 0.0 if _inside(q, hole) or _inside(q, foramen) else 0.75)

    draw_visible(p, brain, [cerebellum], w=1.7, ghosts=1)
    p.shade(brain, form_tone(brain, LIGHT, rim=40, base=-0.1), spacing=3.6)
    rng = p.rng
    for _ in range(150):
        x, y = rng.uniform(280, 730), rng.uniform(380, 680)
        if not _inside((x, y), brain) or _inside((x, y), cerebellum):
            continue
        heading = rng.uniform(0, 2 * math.pi)
        turn = rng.choice((-1, 1))
        pts = [(x, y)]
        for _ in range(rng.randint(10, 26)):
            heading += turn * abs(rng.gauss(0.35, 0.3))
            if rng.random() < 0.18:
                turn = -turn
            x, y = x + 4.5 * math.cos(heading), y + 4.5 * math.sin(heading)
            if not _inside((x, y), brain) or _inside((x, y), cerebellum):
                break
            pts.append((x, y))
        if len(pts) > 4:
            p.contour(pts, closed=False, w=0.9, passes=1, opacity=0.62)
    p.contour([(650, 640), (590, 600), (520, 590), (452, 560)], closed=False, w=1.5, passes=1)
    p.contour([(520, 364), (512, 440), (494, 500), (474, 560)], closed=False, w=1.4, passes=1)
    p.contour(cerebellum, w=1.5)
    for k in range(7):
        p.contour(ellipse_pts(380, 704, 56 - k * 7, 32 - k * 4, -8, 190, 350), closed=False, w=0.7, passes=1, opacity=0.6)
    stem = [(440, 700), (476, 700), (490, 900), (456, 900)]
    p.contour(stem, w=1.5)
    p.shade(stem, form_tone(stem, LIGHT, rim=10, base=0.2), spacing=2.8)

    # the coin, flush with the bone, and its threads sinking into the cortex
    coin = rrect_pts(IMPLANT[0] - 28, IMPLANT[1] - 7, 56, 12, 3)
    p.contour(coin, w=1.8)
    p.shade(coin, lambda q: 0.7, spacing=2.0)
    for k in range(9):
        dx = (k - 4) * 9
        pts = [(IMPLANT[0] + dx * 0.3, IMPLANT[1] + 6), (IMPLANT[0] + dx, IMPLANT[1] + 30), (IMPLANT[0] + dx * 1.4, IMPLANT[1] + 62)]
        p.contour(pts, closed=False, w=0.6, passes=1, opacity=0.85)
    p.label("a", IMPLANT[0] - 40, IMPLANT[1] - 24)
    p.label("b", IMPLANT[0] + 68, IMPLANT[1] + 70)
    p.chalk(ellipse_pts(IMPLANT[0], IMPLANT[1] + 20, 78, 62), dash="4 5", opacity=0.6)


def _coin_top(p: Page, c=(1170, 330)):
    p.chalk_line((IMPLANT[0] + 70, IMPLANT[1] - 20), (c[0] - 120, c[1] - 30), dash="4 6", opacity=0.5, overshoot=0)
    p.chalk_line((IMPLANT[0] + 74, IMPLANT[1] + 50), (c[0] - 110, c[1] + 70), dash="4 6", opacity=0.5, overshoot=0)
    body = ellipse_pts(*c, 76, 76)
    p.contour(body, w=2.0, ghosts=1)
    p.contour(ellipse_pts(*c, 62, 62), w=1.0, passes=1)
    p.shade([body], form_tone(body, LIGHT, rim=22, base=0.15), spacing=2.8)
    for k in range(8):
        a = math.radians(k * 45)
        p.contour(ellipse_pts(c[0] + 34 * math.cos(a), c[1] + 34 * math.sin(a), 4, 4), w=0.8, passes=1)
    rng = p.rng
    for k in range(64):
        a0 = math.radians(150 + k * 60 / 63)
        start = (c[0] + 76 * math.cos(a0), c[1] + 76 * math.sin(a0))
        length = rng.uniform(70, 150)
        bend = rng.uniform(-0.4, 0.4)
        pts = []
        for j in range(12):
            t = j / 11
            a = a0 + bend * t
            pts.append((start[0] + length * t * math.cos(a), start[1] + length * t * math.sin(a) + 30 * t * t))
        p.contour(pts, closed=False, w=0.4, passes=1, opacity=0.55)


def _thread(p: Page):
    y = 600
    pts = [(1010 + k * 23, y + 6 * math.sin(k * 0.6)) for k in range(21)]
    p.contour(pts, closed=False, w=2.2, passes=1)
    p.contour([(x, yy + 3) for x, yy in pts], closed=False, w=0.8, passes=1, opacity=0.6)
    for k in range(16):
        x, yy = pts[2 + k]
        p.contour(ellipse_pts(x, yy, 3.2, 3.2), w=1.0, passes=1)
        p.hatch(ellipse_pts(x, yy, 3.2, 3.2), 45, 1.4, w=0.6)
    loop = ellipse_pts(pts[-1][0] + 14, pts[-1][1], 12, 8)
    p.contour(loop, w=1.2, passes=1)
    needle = [(1468, 470), (1476, 470), (1476, 596), (1470, 612), (1462, 598), (1462, 470)]
    p.contour(needle, w=1.4, passes=1)
    p.shade(needle, lin_tone((1462, 0), (1476, 0), lo=0.2), spacing=2.0)
    p.contour([(1470, 612), (1478, 604), (1476, 596)], closed=False, w=1.0, passes=1)
    p.contour(rrect_pts(1450, 430, 46, 40, 4), w=1.5)
    p.contour(ellipse_pts(1473, 450, 9, 9), w=1.0, passes=1)
    p.hatch(rrect_pts(1450, 430, 46, 40, 4), 45, 2.6, w=0.6, opacity=0.6)
    p.arrow_head((1500, 620), (1500, 560), size=10, w=1.1)
    p.contour([(1500, 540), (1500, 620)], closed=False, w=1.0, passes=1)
    p.label("c", 1220, 660)
    p.label("d", 1530, 450)


def _screen(p: Page):
    scr = rrect_pts(1080, 860, 360, 210, 8)
    p.contour(scr, w=1.9, ghosts=1)
    inner = rrect_pts(1094, 874, 332, 182, 3)
    p.contour(inner, w=1.0, passes=1)
    p.hatch([scr, inner], 45, 2.6, w=0.6, opacity=0.7)
    path = [(1130, 1020), (1180, 990), (1230, 1000), (1290, 940), (1350, 930), (1380, 905)]
    p.chalk(path, closed=False, dash="4 5", opacity=0.8)
    tip = (1386, 900)
    arrow = [tip, (tip[0], tip[1] + 30), (tip[0] + 8, tip[1] + 22), (tip[0] + 14, tip[1] + 34),
             (tip[0] + 19, tip[1] + 31), (tip[0] + 13, tip[1] + 20), (tip[0] + 24, tip[1] + 20)]
    p.contour(arrow, w=1.4, passes=1)
    p.hatch(arrow, 45, 1.8, w=0.6)
    for k in range(4):
        p.contour(rrect_pts(1112 + k * 30, 890, 20, 20, 4), w=0.8, passes=1, opacity=0.6)
    p.contour([(1240, 1070), (1280, 1070), (1290, 1100), (1230, 1100)], w=1.4)
    p.label("e", 1470, 900)


def folio_neuralink() -> Page:
    p = Page(seed=1212, folio="")
    _skull_and_brain(p)
    _coin_top(p)
    _thread(p)
    _screen(p)

    p.title("Del pensiero che move la freccia", 820, 110)
    p.note([
        "una moneta posta nel capo",
        "con sessantaquattro fili più sottili che li capelli",
        "ascolta le voci del cervello",
        "e l'omo che non move le mani",
        "move la freccia col pensiero",
    ], 940, 900)
    p.note([
        "a. la moneta",
        "b. li fili nella carne del cervello",
        "c. sedici orecchi per ogni filo",
        "d. l'ago che cuce come una sarta",
        "e. la freccia mossa dal pensiero",
    ], 1530, 105)
    return p


NOTES = {
    "Del pensiero che move la freccia": "Of the thought that moves the arrow",
    "una moneta posta nel capo": "a coin set into the head",
    "con sessantaquattro fili più sottili che li capelli": "with sixty-four threads finer than hairs",
    "ascolta le voci del cervello": "listens to the voices of the brain",
    "e l'omo che non move le mani": "and the man who cannot move his hands",
    "move la freccia col pensiero": "moves the arrow with his thought",
    "a. la moneta": "a. the coin",
    "b. li fili nella carne del cervello": "b. the threads in the flesh of the brain",
    "c. sedici orecchi per ogni filo": "c. sixteen ears on every thread",
    "d. l'ago che cuce come una sarta": "d. the needle that sews like a seamstress",
    "e. la freccia mossa dal pensiero": "e. the arrow moved by thought",
}
