"""f. 13r — Apple Vision Pro (2024): a headset studied as Leonardo studied the eye."""

from __future__ import annotations

import math

from codex import Page, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import draw_visible, not_in, smooth_closed

LIGHT = (-1.0, -1.2)


def _mirror_x(pts, cx):
    return [(2 * cx - x, y) for x, y in pts]


def _headset(p: Page, cx=455):
    right = [(cx, 232), (600, 238), (700, 262), (742, 320), (735, 395), (690, 446), (590, 462), (520, 446), (480, 412), (cx, 404)]
    left = _mirror_x(right[1:-1], cx)[::-1]
    glass = smooth_closed(right + left, n=6)
    frame = [(cx + (x - cx) * 1.035, 340 + (y - 340) * 1.07) for x, y in glass]
    p.contour(frame, w=2.2, ghosts=1)
    p.contour(glass, w=1.6)
    p.hatch([frame, glass], 45, 2.4, w=0.6, opacity=0.6, tone=lin_tone((150, 0), (760, 0), lo=0.4))
    # the eyes shown on the outside of the glass
    eyes = []
    for ex in (cx - 100, cx + 100):
        lid = smooth_closed([(ex - 50, 340), (ex, 318), (ex + 50, 340), (ex, 356)], n=8)
        iris = ellipse_pts(ex + 2, 338, 15, 15)
        eyes.append(lid)
        p.contour(lid, w=1.1, passes=1, opacity=0.6)
        p.contour(iris, w=1.0, passes=1, opacity=0.6)
        p.hatch(ellipse_pts(ex + 2, 338, 6, 6), 45, 1.6, w=0.6, opacity=0.8)
        p.hatch(iris, 45, 2.4, w=0.5, opacity=0.5)
    p.shade(glass, lambda q: (0.0 if -40 < (q[0] - cx) - (q[1] - 340) * 1.2 < 30 else 0.35) * not_in(eyes)(q), spacing=3.6)
    for x in (cx - 190, cx - 150, cx + 150, cx + 190):
        p.contour(ellipse_pts(x, 420 if abs(x - cx) > 160 else 300, 6, 6), w=0.8, passes=1, opacity=0.55)
    crown = rrect_pts(632, 210, 30, 18, 4)
    p.contour(crown, w=1.4)
    for k in range(6):
        p.contour([(636 + k * 4.5, 212), (636 + k * 4.5, 226)], closed=False, w=0.6, passes=1)
    button = rrect_pts(262, 220, 46, 12, 6)
    p.contour(button, w=1.2, passes=1)
    p.hatch(button, 45, 2.0, w=0.6)
    for sx in (-1, 1):
        x0 = cx + sx * 300
        p.contour([(x0, 300), (x0 + sx * 60, 290), (x0 + sx * 90, 300)], closed=False, w=1.4, passes=1, opacity=0.7)
        p.contour([(x0, 380), (x0 + sx * 60, 392), (x0 + sx * 90, 384)], closed=False, w=1.4, passes=1, opacity=0.7)
    p.label("a", cx + 40, 296)


def _section(p: Page):
    """Display, lens and eye, cut through from the side."""
    y = 740
    display = rrect_pts(196, y - 92, 14, 184, 2)
    p.contour(display, w=1.6)
    p.shade(display, lambda q: 0.85, spacing=2.0)
    lens = smooth_closed([(330, y - 92), (350, y - 40), (352, y), (350, y + 40), (330, y + 92),
                          (310, y + 40), (308, y), (310, y - 40)], n=6)
    p.contour(lens, w=1.7)
    p.shade(lens, form_tone(lens, LIGHT, rim=12, base=-0.05), spacing=2.6)
    for dy in (-96, 96):
        p.contour(ellipse_pts(330, y + dy, 4, 4), w=0.9, passes=1)

    eye_c, R = (640, y), 92
    sclera = ellipse_pts(*eye_c, R, R)
    cornea = ellipse_pts(eye_c[0] - R + 6, y, 26, 44, 0, 90, 270)
    draw_visible(p, sclera, [], w=1.9, ghosts=1)
    p.contour(cornea, closed=False, w=1.5)
    retina = ellipse_pts(*eye_c, R - 7, R - 7, 0, -70, 70)
    p.contour(retina, closed=False, w=2.2, passes=1)
    crystal = ellipse_pts(eye_c[0] - R + 34, y, 12, 34)
    p.contour(crystal, w=1.4)
    p.hatch(crystal, 45, 2.0, w=0.5, opacity=0.6)
    for dy in (-1, 1):
        p.contour([(eye_c[0] - R + 26, y + dy * 36), (eye_c[0] - R + 22, y + dy * 54)], closed=False, w=1.6, passes=1)
    nerve = [(eye_c[0] + R - 4, y - 14), (eye_c[0] + R + 70, y - 22), (eye_c[0] + R + 70, y + 6), (eye_c[0] + R - 4, y + 14)]
    p.contour(nerve, w=1.5)
    p.shade(nerve, lambda q: 0.5, spacing=2.6)
    p.shade(sclera, lambda q: form_tone(sclera, LIGHT, rim=26, base=-0.1)(q) * not_in([crystal])(q), spacing=3.4)

    focus = (eye_c[0] + R - 9, y + 6)
    for sy in (-70, 0, 70):
        src = (212, y + sy)
        for spread in (-26, 0, 26):
            hit = (330, y + sy * 0.55 + spread)
            pupil = (eye_c[0] - R + 34, y + spread * 0.35)
            p.contour([src, hit, pupil, (focus[0], focus[1] - sy * 0.3)], closed=False, w=0.6, passes=1, opacity=0.5)
    for dy in (-96, 96):
        p.chalk_line((334, y + dy), (eye_c[0] - R - 10, y + dy * 0.3), dash="4 5", opacity=0.55, overshoot=0)
    p.chalk_line((150, y), (eye_c[0] + R + 100, y), dash="6 6", opacity=0.4)
    p.label("b", 220, y - 110)
    p.label("c", 346, y - 110)
    p.label("d", eye_c[0] + 30, y - R - 18)


def _pixels(p: Page, c=(1250, 320), r=130):
    lens = ellipse_pts(*c, r, r)
    p.contour(lens, w=2.0, ghosts=1)
    p.contour(ellipse_pts(*c, r + 10, r + 10), w=1.0, passes=1)
    cell = 30
    for i in range(-5, 6):
        for j in range(-5, 6):
            x0, y0 = c[0] + i * cell - cell / 2, c[1] + j * cell - cell / 2
            if math.dist((x0 + cell / 2, y0 + cell / 2), c) > r - 18:
                continue
            for k, dens in enumerate((2.2, 3.2, 4.6)):
                stripe = rrect_pts(x0 + 3 + k * 8.5, y0 + 4, 7, cell - 8, 1)
                p.contour(stripe, w=0.6, passes=1, opacity=0.7)
                p.hatch(stripe, 45, dens, w=0.5, opacity=0.75)
    handle = [(c[0] + r * 0.72, c[1] + r * 0.72), (c[0] + r * 1.05, c[1] + r * 1.05)]
    p.contour(handle, closed=False, w=5, passes=1)
    p.label("e", c[0] + r + 40, c[1] - r + 20)


def _tracker(p: Page, c=(1250, 760)):
    rim = ellipse_pts(*c, 96, 96)
    glass = ellipse_pts(*c, 74, 74)
    p.contour(rim, w=2.0, ghosts=1)
    p.contour(glass, w=1.3)
    p.hatch([rim, glass], 45, 2.6, w=0.6, opacity=0.7)
    p.shade(glass, lambda q: 0.0 if -20 < (q[0] - c[0]) - (q[1] - c[1]) < 14 else 0.25, spacing=3.6)
    for k in range(10):
        a = math.radians(k * 36 + 18)
        led = (c[0] + 85 * math.cos(a), c[1] + 85 * math.sin(a))
        p.contour(ellipse_pts(*led, 4, 4), w=1.0, passes=1)
        p.chalk_line(led, (c[0] + 20 * math.cos(a), c[1] + 20 * math.sin(a)), dash="3 4", opacity=0.5, overshoot=0)
    for a in (200, 340):
        cam = (c[0] + 85 * math.cos(math.radians(a)), c[1] + 85 * math.sin(math.radians(a)) + 4)
        box = rrect_pts(cam[0] - 7, cam[1] - 6, 14, 12, 2)
        p.contour(box, w=1.0, passes=1)
        p.hatch(box, 45, 1.6, w=0.6)
    p.label("f", c[0] + 140, c[1] - 40)


def folio_vision_pro() -> Page:
    p = Page(seed=1313, folio="")
    _headset(p)
    _section(p)
    _pixels(p)
    _tracker(p)

    p.title("Dell'occhio che vede due mondi", 820, 110)
    p.note([
        "questo velo si mette dinanzi agli occhi",
        "e mostra uno mondo dentro al mondo",
        "guarda dove tu guardi",
        "e obbedisce al tocco delle dita",
    ], 1530, 500)
    p.note([
        "a. gli occhi mostrati di fuori",
        "b. la vetrina della luce",
        "c. la lente che piega i raggi",
        "d. l'occhio come io lo disegnai",
        "e. ventitré milioni di punti di luce",
        "f. lumi che non si vedono guardano l'occhio",
    ], 1530, 920)
    return p


NOTES = {
    "Dell'occhio che vede due mondi": "Of the eye that sees two worlds",
    "questo velo si mette dinanzi agli occhi": "this veil is set before the eyes",
    "e mostra uno mondo dentro al mondo": "and shows a world within the world",
    "guarda dove tu guardi": "it looks where you look",
    "e obbedisce al tocco delle dita": "and obeys the touch of the fingers",
    "a. gli occhi mostrati di fuori": "a. the eyes shown on the outside",
    "b. la vetrina della luce": "b. the little window of light",
    "c. la lente che piega i raggi": "c. the lens that bends the rays",
    "d. l'occhio come io lo disegnai": "d. the eye, as I drew it",
    "e. ventitré milioni di punti di luce": "e. twenty-three million points of light",
    "f. lumi che non si vedono guardano l'occhio": "f. unseen lights watch the eye",
}
