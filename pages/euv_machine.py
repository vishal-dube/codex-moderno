"""f. 9r — the EUV lithography machine (ASML, ~2019): tin, laser, mirrors, and light that prints chips."""

from __future__ import annotations

import math

from codex import CHALK, Page, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import draw_visible, not_in

LIGHT = (-1.0, -1.2)
F1 = (330, 650)      # where the tin becomes light
IF = (760, 520)      # the intermediate focus


def _unit(a, b):
    d = math.dist(a, b)
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def _mirror(p: Page, c, src, dst, size=80, depth=12):
    """A curved mirror at c, turned so light from src reflects toward dst."""
    din, dout = _unit(src, c), _unit(c, dst)
    nx, ny = dout[0] - din[0], dout[1] - din[1]
    L = math.hypot(nx, ny)
    nx, ny = nx / L, ny / L
    tx, ty = -ny, nx
    face, back = [], []
    for k in range(21):
        t = (k / 20 - 0.5) * size
        sag = (t / size) ** 2 * 10
        face.append((c[0] + tx * t + nx * sag, c[1] + ty * t + ny * sag))
        back.append((c[0] + tx * t + nx * (sag - depth), c[1] + ty * t + ny * (sag - depth)))
    body = face + back[::-1]
    p.contour(body, w=1.8)
    p.contour(face, closed=False, w=2.4, passes=1)
    p.shade(body, lambda q: 0.75, spacing=2.6)


def _beam(p: Page, a, b, wa, wb, opacity=0.8):
    ux, uy = _unit(a, b)
    nx, ny = -uy, ux
    for side in (-1, 1):
        p.contour([(a[0] + nx * wa * side, a[1] + ny * wa * side), (b[0] + nx * wb * side, b[1] + ny * wb * side)],
                  closed=False, w=0.9, passes=1, opacity=opacity)
    p.contour([a, b], closed=False, w=0.6, passes=1, opacity=opacity * 0.6)
    if wa > 1 or wb > 1:
        poly = [(a[0] + nx * wa, a[1] + ny * wa), (b[0] + nx * wb, b[1] + ny * wb),
                (b[0] - nx * wb, b[1] - ny * wb), (a[0] - nx * wa, a[1] - ny * wa)]
        p.hatch(poly, 45, 4.5, w=0.5, opacity=0.35)


def _star(p: Page, c, r_in, r_out, n=16, w=1.1):
    p.contour(ellipse_pts(*c, r_in, r_in), w=w + 0.4, passes=1)
    for k in range(n):
        a = math.radians(k * 360 / n + (8 if k % 2 else 0))
        r1 = r_out if k % 2 == 0 else r_out * 0.6
        p.contour([(c[0] + r_in * 1.3 * math.cos(a), c[1] + r_in * 1.3 * math.sin(a)),
                   (c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a))], closed=False, w=w, passes=1, opacity=0.85)


def _source(p: Page):
    # the collector: a great concave mirror behind the spark
    arc_out = ellipse_pts(*F1, 196, 196, 0, 120, 240)
    arc_in = ellipse_pts(*F1, 176, 176, 0, 120, 240)
    body = arc_out + arc_in[::-1]
    p.contour(body, w=2.0, ghosts=1)
    p.shade(body, lin_tone((F1[0] - 196, 0), (F1[0] - 176, 0), lo=0.4), spacing=2.6)
    hole = (F1[0] - 186, F1[1])
    p.contour([(hole[0] - 12, F1[1] - 10), (hole[0] + 12, F1[1] - 10)], closed=False, w=1.2, passes=1)
    p.contour([(hole[0] - 12, F1[1] + 10), (hole[0] + 12, F1[1] + 10)], closed=False, w=1.2, passes=1)

    # tin falling from the nozzle, past the spark, into the catcher
    nozzle = [(F1[0] - 16, 300), (F1[0] + 16, 300), (F1[0] + 6, 336), (F1[0] - 6, 336)]
    p.contour(nozzle, w=1.7)
    p.shade(nozzle, form_tone(nozzle, LIGHT, rim=6, base=0.3), spacing=2.4)
    p.contour(rrect_pts(F1[0] - 26, 268, 52, 32, 4), w=1.6)
    y = 352
    while y < 960:
        if abs(y - F1[1]) > 24:
            p.contour(ellipse_pts(F1[0], y, 3.6, 3.6), w=1.0, passes=1)
        y += 24
    catcher = [(F1[0] - 26, 968), (F1[0] + 26, 968), (F1[0] + 18, 1000), (F1[0] - 18, 1000)]
    p.contour(catcher, w=1.6)
    p.shade(catcher, lambda q: 0.6, spacing=2.6)

    # the laser, in red chalk, through the hole in the mirror
    for dy in (-6, 6):
        p.chalk_line((110, F1[1] + dy), (F1[0] - 14, F1[1] + dy * 0.3), w=1.6, opacity=0.85, overshoot=0)
    p.arrow_head((F1[0] - 16, F1[1]), (F1[0] - 40, F1[1]), color=CHALK, layer="chalk", w=1.4)
    _star(p, F1, 6, 28)

    # rays: from the spark to the mirror, and from the mirror to the focus
    for ang in (138, 156, 172, 188, 204, 222):
        a = math.radians(ang)
        m = (F1[0] + 176 * math.cos(a), F1[1] + 176 * math.sin(a))
        p.contour([F1, m], closed=False, w=0.6, passes=1, opacity=0.55)
        p.contour([m, IF], closed=False, w=0.8, passes=1, opacity=0.75)
    p.contour(ellipse_pts(*IF, 4, 4), w=1.4, passes=1)
    p.label("d", F1[0] - 200, F1[1] - 186)


def _optics(p: Page):
    m1, m2 = (1010, 780), (1180, 560)
    reticle_c = (1150, 230)
    p1, p2 = (1420, 470), (1140, 760)
    wafer_c = (1360, 1010)
    _beam(p, IF, m1, 0, 22)
    _beam(p, m1, m2, 22, 18)
    _beam(p, m2, reticle_c, 18, 30)
    _beam(p, reticle_c, p1, 30, 26)
    _beam(p, p1, p2, 26, 16)
    _beam(p, p2, wafer_c, 16, 2)
    _mirror(p, m1, IF, m2, size=96)
    _mirror(p, m2, m1, reticle_c, size=84)
    _mirror(p, p1, reticle_c, p2, size=96)
    _mirror(p, p2, p1, wafer_c, size=80)
    for a, b in ((IF, m1), (m2, reticle_c), (p2, wafer_c)):
        mid = ((a[0] * 0.45 + b[0] * 0.55), (a[1] * 0.45 + b[1] * 0.55))
        tip = ((a[0] * 0.38 + b[0] * 0.62), (a[1] * 0.38 + b[1] * 0.62))
        p.arrow_head(tip, mid, size=9, w=1.1)

    # the mask: the pattern the light copies
    mask = rrect_pts(reticle_c[0] - 130, reticle_c[1] - 26, 260, 18, 2)
    p.contour(mask, w=1.8)
    p.shade(mask, lambda q: 0.55, spacing=2.4)
    for k in range(18):
        x = reticle_c[0] - 120 + k * 14
        p.contour([(x, reticle_c[1] - 8), (x, reticle_c[1] - 2)], closed=False, w=1.2, passes=1)

    # the wafer on its stage, already ruled into chips
    wafer = ellipse_pts(*wafer_c, 132, 34)
    stage = [(wafer_c[0] - 160, wafer_c[1] + 30), (wafer_c[0] + 160, wafer_c[1] + 30),
             (wafer_c[0] + 150, wafer_c[1] + 78), (wafer_c[0] - 150, wafer_c[1] + 78)]
    draw_visible(p, stage, [wafer], w=1.7)
    p.shade(stage, lambda q: form_tone(stage, LIGHT, rim=12, base=0.3)(q) * not_in([wafer])(q), spacing=2.8)
    p.contour(wafer, w=1.8, ghosts=1)
    p.hatch(wafer, 0, 9, w=0.6, opacity=0.6, max_len=600, trim=0)
    p.hatch(wafer, 70, 18, w=0.6, opacity=0.6, max_len=600, trim=0)
    p.label("e", wafer_c[0] + 172, wafer_c[1] + 6)


def _drops(p: Page):
    """The drop, struck once and flattened, struck again and turned to a sun."""
    y = 1032
    xs = (640, 780, 920)
    p.contour(ellipse_pts(xs[0], y, 13, 13), w=1.6)
    p.shade(ellipse_pts(xs[0], y, 13, 13), form_tone(ellipse_pts(xs[0], y, 13, 13), LIGHT, rim=6), spacing=2.2)
    p.contour(ellipse_pts(xs[1], y, 30, 7), w=1.6)
    p.shade(ellipse_pts(xs[1], y, 30, 7), lambda q: 0.6, spacing=2.2)
    _star(p, (xs[2], y), 9, 40, n=20, w=1.0)
    for x in xs:
        for dy in (-4, 4):
            p.chalk_line((x - 70, y + dy), (x - 26, y + dy), w=1.3, opacity=0.75, overshoot=0)
        p.arrow_head((x - 24, y), (x - 40, y), color=CHALK, layer="chalk", w=1.2, size=8)
    for letter, x in zip("abc", xs):
        p.label(letter, x + 6, y - 46)
    p.chalk(ellipse_pts(780, y, 220, 78), dash="4 6", opacity=0.45)
    p.chalk_line((F1[0] + 30, F1[1] + 30), (590, 970), dash="4 6", opacity=0.4, overshoot=0)


def folio_euv_machine() -> Page:
    p = Page(seed=909, folio="")
    _source(p)
    _optics(p)
    _drops(p)

    p.title("Della luce che scrive le cose minime", 900, 110)
    p.note([
        "una goccia di stagno cade",
        "e il fuoco la percuote due volte",
        "cinquantamila volte in uno battito di cuore",
        "e nasce una luce che l'occhio non vede",
    ], 1010, 170)
    p.note([
        "a. la goccia",
        "b. il primo colpo la fa piatta",
        "c. il secondo la fa uno sole",
        "d. lo specchio che raccoglie la luce",
        "e. la carta dove la luce scrive",
    ], 560, 975)
    return p


NOTES = {
    "Della luce che scrive le cose minime": "Of the light that writes the smallest things",
    "una goccia di stagno cade": "a drop of tin falls",
    "e il fuoco la percuote due volte": "and fire strikes it twice",
    "cinquantamila volte in uno battito di cuore": "fifty thousand times in a heartbeat",
    "e nasce una luce che l'occhio non vede": "and a light is born that the eye cannot see",
    "a. la goccia": "a. the drop",
    "b. il primo colpo la fa piatta": "b. the first blow flattens it",
    "c. il secondo la fa uno sole": "c. the second makes it a sun",
    "d. lo specchio che raccoglie la luce": "d. the mirror that gathers the light",
    "e. la carta dove la luce scrive": "e. the leaf on which the light writes",
}
