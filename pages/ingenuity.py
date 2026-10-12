"""f. 10r — Ingenuity (2021), the first powered flight on another planet, beside Leonardo's own aerial screw."""

from __future__ import annotations

import math

from codex import CHALK, Page, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import draw_visible, not_in, smooth_closed

LIGHT = (-1.0, -1.2)
CX = 520


def _blade(hub, tip_dx, y, root_w=13, tip_w=7, droop=6):
    """One rotor blade seen from the side: a long, thin, slightly cambered leaf."""
    x0, x1 = hub[0], hub[0] + tip_dx
    sgn = 1 if tip_dx > 0 else -1
    top = [(x0 + sgn * 18, y - root_w / 2), (x0 + tip_dx * 0.5, y - root_w * 0.55 + droop * 0.3), (x1, y - tip_w / 2 + droop)]
    bot = [(x1 + sgn * 4, y + droop), (x0 + tip_dx * 0.5, y + root_w * 0.45 + droop * 0.3), (x0 + sgn * 18, y + root_w / 2)]
    return smooth_closed(top + bot, n=6)


def _rotor(p: Page, y, left, right, spin):
    hub = (CX, y)
    blades = [_blade(hub, -left, y), _blade(hub, right, y)]
    disc = ellipse_pts(*hub, 20, 9)
    for b in blades:
        draw_visible(p, b, [disc], w=1.6)
        p.shade(b, lambda q, b=b: lin_tone((0, y - 8), (0, y + 8), lo=0.15)(q) * not_in([disc])(q), spacing=2.4)
    p.contour(disc, w=1.6)
    p.shade(disc, form_tone(disc, LIGHT, rim=6, base=0.2), spacing=2.4)
    sweep = ellipse_pts(CX, y + 2, 336, 36, 0, 20, 160) if spin > 0 else ellipse_pts(CX, y + 2, 336, 36, 0, 160, 20)
    p.chalk(sweep, closed=False, dash="6 5", opacity=0.6)
    p.arrow_head(sweep[-1], sweep[-3], color=CHALK, layer="chalk", w=1.1)


def _ingenuity(p: Page):
    ground = 905
    body = rrect_pts(CX - 38, 742, 76, 74, 5)
    legs = [((CX - 34, 812), (CX - 150, ground - 4)), ((CX + 34, 812), (CX + 150, ground - 4)),
            ((CX - 24, 814), (CX - 80, ground - 14)), ((CX + 24, 814), (CX + 80, ground - 14))]
    for k, (a, b) in enumerate(legs):
        p.contour([a, b], closed=False, w=2.0 if k < 2 else 1.3, passes=1, opacity=1.0 if k < 2 else 0.6)
        pad = ellipse_pts(b[0], b[1] + 3, 12, 4)
        p.contour(pad, w=1.2, passes=1, opacity=1.0 if k < 2 else 0.6)
    p.hatch(ellipse_pts(CX + 20, ground + 8, 200, 12), 45, 3.0, w=0.8, opacity=0.6,
            tone=lambda q: 1 - min(1, abs(q[0] - CX - 20) / 200))
    p.contour(body, w=2.0, ghosts=1)
    p.shade(body, form_tone(body, LIGHT, rim=14, base=0.15), spacing=2.8)
    p.contour([(CX - 30, 760), (CX + 30, 760)], closed=False, w=0.8, passes=1, opacity=0.6)
    p.contour(ellipse_pts(CX - 18, 796, 5, 5), w=1.0, passes=1)

    for x in (CX - 4, CX + 4):
        p.contour([(x, 742), (x, 600)], closed=False, w=1.6, passes=1)
    _rotor(p, 704, 300, 318, spin=1)
    _rotor(p, 660, 262, 300, spin=-1)
    panel = rrect_pts(CX - 84, 586, 168, 13, 2)
    p.contour(panel, w=1.7)
    for k in range(1, 8):
        x = CX - 84 + k * 21
        p.contour([(x, 588), (x, 597)], closed=False, w=0.7, passes=1)
    p.shade(panel, lambda q: 0.6, spacing=2.4)
    swatch = rrect_pts(CX + 10, 606, 22, 14, 1)
    p.contour([(CX + 21, 599), (CX + 21, 606)], closed=False, w=0.8, passes=1)
    p.contour(swatch, w=1.0, passes=1)
    p.hatch(swatch, 45, 2.2, w=0.6)
    p.hatch(swatch, -45, 2.2, w=0.6)
    p.label("g", CX + 64, 622)

    p.line((230, ground), (840, ground), w=1.3, overshoot=10)
    for k in range(18):
        x = 240 + k * 34 + p.rng.uniform(-10, 10)
        if abs(x - CX) < 170:
            continue
        rock = smooth_closed([(x - 9, ground), (x - 6, ground - 7), (x + 3, ground - 9), (x + 10, ground)], n=3)
        p.contour(rock, w=0.9, passes=1)
        p.hatch(rock, 45, 2.0, w=0.6, opacity=0.7)
    # a man's height, for scale: the whole machine is shorter than a knee
    p.chalk_line((CX + 300, 586), (CX + 300, ground), overshoot=0, opacity=0.6)
    for y in (586, ground):
        p.chalk_line((CX + 290, y), (CX + 310, y), overshoot=0, opacity=0.6)


def _aerial_screw(p: Page, c=(1250, 520)):
    """Leonardo's helicopter, c. 1489: a linen screw on a mast, turned by men on a platform."""
    plat_top = ellipse_pts(c[0], c[1], 150, 30)
    p.contour(plat_top, w=1.6)
    p.contour([(x, y + 14) for x, y in ellipse_pts(c[0], c[1], 150, 30, 0, 0, 180)], closed=False, w=1.4)
    p.contour([(c[0] - 150, c[1]), (c[0] - 150, c[1] + 14)], closed=False, w=1.2, passes=1)
    p.contour([(c[0] + 150, c[1]), (c[0] + 150, c[1] + 14)], closed=False, w=1.2, passes=1)
    p.shade([x for x in ellipse_pts(c[0], c[1], 150, 30, 0, 0, 180)] + [(x, y + 14) for x, y in ellipse_pts(c[0], c[1], 150, 30, 0, 0, 180)][::-1],
            lambda q: 0.6, spacing=2.6)
    for x in (c[0] - 4, c[0] + 4):
        p.contour([(x, c[1]), (x, 270)], closed=False, w=1.5, passes=1)
    rim = []
    turns, y_top, y_bot, R = 1.25, 300, 470, 145

    def helix(k, r=R):
        t = k / 120 * turns * 2 * math.pi
        y = y_top + (y_bot - y_top) * k / 120
        return (c[0] + r * math.cos(t), y + r * 0.2 * math.sin(t)), math.sin(t)

    for k in range(121):
        rim.append(helix(k)[0])
    p.contour(rim, closed=False, w=1.7)
    for k in range(0, 121, 8):
        (x, y), _ = helix(k)
        p.contour([(c[0], y), (x, y)], closed=False, w=0.8, passes=1, opacity=0.7)
    # the linen sail: shade the parts turned away from us
    for k in range(120):
        (x0, y0), sn = helix(k)
        if sn < 0.2:
            continue
        (x1, y1), _ = helix(k + 1)
        drop = 26
        p.hatch([(c[0], y0), (x0, y0), (x1, y1), (c[0], y1 + drop * 0.1)], 45, 3.0, w=0.5, opacity=0.35 + 0.3 * sn)
    for k in range(4):
        a = math.radians(30 + k * 90)
        hx, hy = c[0] + 70 * math.cos(a), c[1] + 14 * math.sin(a)
        p.contour([(c[0], c[1] - 40), (hx, hy - 4)], closed=False, w=1.0, passes=1, opacity=0.8)
    p.chalk_line((c[0], 240), (c[0], c[1] + 40), dash="6 5", opacity=0.45)
    p.label("f", c[0] + 196, 360)


def _first_flight(p: Page):
    ground = 960
    p.line((1020, ground), (1500, ground), w=1.1, overshoot=6)
    path = [(1050, ground - 4), (1110, 840), (1380, 840), (1450, ground - 4)]
    p.chalk(path, closed=False, dash="6 5", opacity=0.7)
    for a, b in ((path[0], path[1]), (path[2], path[3])):
        p.arrow_head(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), a, color=CHALK, layer="chalk", w=1.1, size=9)
    hx = 1245
    p.contour([(hx - 46, 826), (hx + 46, 826)], closed=False, w=1.6, passes=1)
    p.contour([(hx - 40, 816), (hx + 40, 816)], closed=False, w=1.6, passes=1)
    p.contour([(hx, 812), (hx, 846)], closed=False, w=1.3, passes=1)
    box = rrect_pts(hx - 9, 840, 18, 16, 2)
    p.contour(box, w=1.2, passes=1)
    p.hatch(box, 45, 2.0, w=0.6)
    for sx in (-1, 1):
        p.contour([(hx + sx * 6, 856), (hx + sx * 22, 872)], closed=False, w=1.0, passes=1)


def _blade_study(p: Page):
    """One blade from above, and cut through, with the air parting round it."""
    planform = smooth_closed([(150, 466), (190, 454), (430, 452), (600, 458), (628, 466),
                              (600, 474), (430, 480), (190, 478)], n=5)
    p.contour(planform, w=1.6, ghosts=1)
    p.shade(planform, lin_tone((0, 454), (0, 480), lo=0.15), spacing=2.4)
    p.contour(ellipse_pts(160, 466, 9, 9), w=1.2, passes=1)
    p.chalk_line((392, 430), (392, 504), dash="5 5", opacity=0.65)
    p.label("h", 380, 430)

    c = (330, 320)
    foil = smooth_closed([(c[0] - 110, c[1] + 4), (c[0] - 96, c[1] - 12), (c[0] - 40, c[1] - 24), (c[0] + 40, c[1] - 18),
                          (c[0] + 112, c[1] - 2), (c[0] + 40, c[1] + 4), (c[0] - 40, c[1] + 8), (c[0] - 96, c[1] + 14)], n=6)
    p.contour(foil, w=1.8)
    p.shade(foil, form_tone(foil, LIGHT, rim=10, base=0.2), spacing=2.4)
    for k, off in enumerate((-78, -52, -30, 28, 50)):
        pts = []
        for j in range(41):
            x = c[0] - 220 + 440 * j / 40
            u = (x - c[0]) / 115
            bump = max(0.0, 1 - u * u)
            y = c[1] + off + (-(44 if off < 0 else -16) * bump ** 1.5 * (1 - abs(off) / 120))
            pts.append((x, y))
        p.contour(pts, closed=False, w=0.8, passes=1, opacity=0.6)
        p.arrow_head(pts[-1], pts[-3], size=8, w=0.9)
    p.chalk_line((c[0] - 230, c[1] + 60), (c[0] + 230, c[1] - 30), dash="6 5", opacity=0.4)


def folio_ingenuity() -> Page:
    p = Page(seed=1010, folio="")
    with p.transformed(1.3, 520 - 520 * 1.3, 980 - 905 * 1.3):
        _ingenuity(p)
    _aerial_screw(p)
    _first_flight(p)
    _blade_study(p)

    p.title("Dell'uccello che vola in un altro cielo", 900, 110)
    p.note([
        "l'aria di là è cento volte più sottile",
        "però le ali girano quaranta volte",
        "in uno battito di cuore",
        "due ali di sopra e due di sotto",
        "che girano l'una contro l'altra",
    ], 960, 175)
    p.note([
        "f. la vite d'aria che io disegnai",
        "ora vola in un altro mondo",
    ], 1530, 600)
    p.note(["h. la penna dell'ala tagliata"], 900, 445)
    p.note([
        "il primo volo durò trentanove battiti",
        "g. porta un pezzo della tela del primo volo",
    ], 1530, 1000)
    return p


NOTES = {
    "Dell'uccello che vola in un altro cielo": "Of the bird that flies in another sky",
    "l'aria di là è cento volte più sottile": "the air there is a hundred times thinner",
    "però le ali girano quaranta volte": "so the wings turn forty times",
    "in uno battito di cuore": "in a single heartbeat",
    "due ali di sopra e due di sotto": "two wings above and two below",
    "che girano l'una contro l'altra": "turning against each other",
    "f. la vite d'aria che io disegnai": "f. the air screw that I designed",
    "ora vola in un altro mondo": "now flies in another world",
    "h. la penna dell'ala tagliata": "h. the wing's feather, cut through",
    "il primo volo durò trentanove battiti": "the first flight lasted thirty-nine beats",
    "g. porta un pezzo della tela del primo volo": "g. it carries a piece of the cloth of the first flight",
}
