"""f. 5r — the humanoid robot (Atlas, 2013; all-electric, 2024), measured as the Vitruvian Man."""

from __future__ import annotations

import math

from codex import CHALK, Page, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import draw_visible, gear, not_in, place, smooth_closed

LIGHT = (-1.0, -1.2)
CX, FEET, HEIGHT = 560, 1000, 700


def _limb(a, b, w0, w1):
    """A tapered rod from a to b, rounded at both ends."""
    L = math.dist(a, b)
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) - 90
    local = smooth_closed([(-w0 / 2, 0), (-w0 / 2 * 0.95, L * 0.15), (-w1 / 2, L * 0.85), (-w1 / 2, L),
                           (w1 / 2, L), (w1 / 2, L * 0.85), (w0 / 2 * 0.95, L * 0.15), (w0 / 2, 0)], n=5)
    return place(local, ang, a)


def _joint(p: Page, c, r, front=True):
    disc = ellipse_pts(*c, r, r)
    p.contour(disc, w=1.6)
    p.contour(ellipse_pts(*c, r * 0.55, r * 0.55), w=0.9, passes=1)
    for k in range(6):
        a = math.radians(k * 60 + 15)
        p.contour(ellipse_pts(c[0] + r * 0.78 * math.cos(a), c[1] + r * 0.78 * math.sin(a), 1.6, 1.6), w=0.7, passes=1)
    p.shade(disc, form_tone(disc, LIGHT, rim=r * 0.5, base=0.1), spacing=2.8)
    return disc


def _figure(p: Page, arms_up=0.0, legs_out=0.0, ghost=False):
    top = FEET - HEIGHT
    shoulder_y = top + 118
    hips = [(CX - 30, top + 350), (CX + 30, top + 350)]
    shoulders = [(CX - 98, shoulder_y), (CX + 98, shoulder_y)]
    reach = HEIGHT / 2 - 98
    limbs, joints = [], []
    for side, sh in zip((-1, 1), shoulders):
        a = math.radians(arms_up)
        elbow = (sh[0] + side * reach * 0.52 * math.cos(a), sh[1] - reach * 0.52 * math.sin(a))
        wrist = (sh[0] + side * reach * 0.94 * math.cos(a), sh[1] - reach * 0.94 * math.sin(a))
        limbs += [(sh, elbow, 40, 34), (elbow, wrist, 32, 28)]
        joints += [(sh, 26), (elbow, 19), (wrist, 12)]
    for side, hp in zip((-1, 1), hips):
        a = math.radians(legs_out)
        knee = (hp[0] + side * 170 * math.sin(a), hp[1] + 170 * math.cos(a))
        ankle = (hp[0] + side * 328 * math.sin(a), hp[1] + 328 * math.cos(a))
        limbs += [(hp, knee, 50, 42), (knee, ankle, 42, 32)]
        joints += [(hp, 24), (knee, 22), (ankle, 14)]
    head = ellipse_pts(CX, top + 44, 40, 42)
    torso = smooth_closed([(CX - 106, top + 100), (CX + 106, top + 100), (CX + 94, top + 176),
                           (CX + 50, top + 296), (CX - 50, top + 296), (CX - 94, top + 176)], n=6)
    pelvis = rrect_pts(CX - 56, top + 300, 112, 62, 14)

    if ghost:
        for a, b, w0, w1 in limbs:
            p.chalk(_limb(a, b, w0, w1), dash="5 5", opacity=0.5)
        return
    shapes = [_limb(a, b, w0, w1) for a, b, w0, w1 in limbs]
    discs = [ellipse_pts(*c, r, r) for c, r in joints]
    for shape in shapes:
        draw_visible(p, shape, discs + [torso, pelvis], w=1.8)
        p.shade(shape, lambda q, s=shape: form_tone(s, LIGHT, rim=14)(q) * not_in(discs + [torso, pelvis])(q), spacing=3.2)
    draw_visible(p, pelvis, [torso] + discs, w=1.9)
    p.shade(pelvis, lambda q: form_tone(pelvis, LIGHT, rim=14, base=0.15)(q) * not_in([torso] + discs)(q), spacing=3.0)
    p.contour(torso, w=2.1, ghosts=1)
    p.shade(torso, lambda q: form_tone(torso, LIGHT, rim=30)(q) * not_in(discs)(q), spacing=3.4)
    p.contour([(CX, top + 104), (CX, top + 296)], closed=False, w=0.8, passes=1, opacity=0.6)
    p.contour(smooth_closed([(CX - 74, top + 134), (CX + 74, top + 134), (CX + 56, top + 210), (CX - 56, top + 210)], n=4),
              w=1.0, passes=1, opacity=0.7)
    for k in range(4):
        y = top + 232 + k * 14
        half = 44 - k * 4
        p.contour([(CX - half, y), (CX + half, y)], closed=False, w=0.8, passes=1, opacity=0.6)
    # actuator pistons along the thighs and shins
    for a, b, *_ in limbs[4:]:
        d = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        for off in (-1,):
            nx, ny = -uy * 30 * off, ux * 30 * off
            s0 = (a[0] + ux * 26 + nx * 0.62, a[1] + uy * 26 + ny * 0.62)
            s1 = (a[0] + ux * (d * 0.62) + nx * 0.62, a[1] + uy * (d * 0.62) + ny * 0.62)
            s2 = (a[0] + ux * (d - 26) + nx * 0.5, a[1] + uy * (d - 26) + ny * 0.5)
            p.contour([s0, s1], closed=False, w=3.2, passes=1, opacity=0.85)
            p.contour([s1, s2], closed=False, w=1.4, passes=1, opacity=0.85)
    p.contour(rrect_pts(CX - 16, top + 82, 32, 20, 4), w=1.3, passes=1)
    p.contour(head, w=2.0, ghosts=1)
    p.shade(head, form_tone(head, LIGHT, rim=14, base=0.05), spacing=3.0)
    ring = ellipse_pts(CX, top + 44, 25, 25)
    p.contour(ring, w=1.5)
    p.hatch([ring, ellipse_pts(CX, top + 44, 16, 16)], 45, 2.2, w=0.7, opacity=0.8)
    for c, r in joints:
        _joint(p, c, r)
    for side in (-1, 1):
        wrist = joints[2][0] if side == -1 else joints[5][0]
        for k, da in enumerate((-28, 0, 28)):
            a = math.radians(da) if side == 1 else math.radians(180 - da)
            tip = (wrist[0] + 30 * math.cos(a), wrist[1] + 30 * math.sin(a))
            p.contour([(wrist[0] + 10 * math.cos(a), wrist[1] + 10 * math.sin(a)), tip], closed=False, w=1.6, passes=1)
    for side in (-1, 1):
        ankle = joints[8][0] if side == -1 else joints[11][0]
        foot = rrect_pts(ankle[0] - 30 + side * 6, ankle[1] + 8, 60, 22, 6)
        p.contour(foot, w=1.7)
        p.shade(foot, form_tone(foot, LIGHT, rim=8, base=0.2), spacing=2.8)


def _vitruvian(p: Page):
    side = HEIGHT
    sq = rrect_pts(CX - side / 2, FEET - side, side, side, 0)
    navel_y = FEET - 0.6 * HEIGHT
    p.chalk(sq, opacity=0.65)
    p.contour(sq, w=1.1, passes=1, opacity=0.55)
    circle = ellipse_pts(CX, navel_y, 0.6 * HEIGHT, 0.6 * HEIGHT)
    p.contour(circle, w=1.1, passes=1, opacity=0.6)
    p.chalk_line((CX, FEET - side - 20), (CX, FEET + 20), dash="6 5", opacity=0.5)
    for k in range(1, 8):
        y = FEET - side + k * side / 8
        p.chalk_line((CX - side / 2 - 12, y), (CX - side / 2 + 4, y), overshoot=0, opacity=0.6)
        p.chalk_line((CX + side / 2 - 4, y), (CX + side / 2 + 12, y), overshoot=0, opacity=0.6)
    p.chalk_line((CX - side / 2, FEET - side + 118), (CX + side / 2, FEET - side + 118), dash="6 5", opacity=0.45)
    _figure(p, arms_up=24, legs_out=17, ghost=True)
    _figure(p)


def _harmonic_drive(p: Page, c=(1290, 380)):
    ring_out = ellipse_pts(*c, 128, 128)
    ring_in = gear(*c, 96, 44, depth=-8)
    p.contour(ring_out, w=2.0, ghosts=1)
    p.contour(ring_in, w=1.1, passes=1)
    p.shade([ring_out, ring_in], form_tone(ring_out, LIGHT, rim=40, base=0.25), spacing=3.0)
    for k in range(8):
        a = math.radians(k * 45 + 22)
        p.contour(ellipse_pts(c[0] + 114 * math.cos(a), c[1] + 114 * math.sin(a), 4, 4), w=0.9, passes=1)
    flex = [(c[0] + (x - c[0]) * 1.06, c[1] + (y - c[1]) * 0.9) for x, y in gear(*c, 80, 42, depth=6)]
    p.contour(flex, w=1.3, passes=1)
    flex_in = ellipse_pts(*c, 80, 68)
    p.contour(flex_in, w=0.9, passes=1)
    p.hatch([flex, flex_in], 45, 2.6, w=0.6, opacity=0.6)
    gen = ellipse_pts(*c, 62, 48)
    p.contour(gen, w=1.7)
    for k in range(18):
        a = 2 * math.pi * k / 18
        p.contour(ellipse_pts(c[0] + 71 * math.cos(a), c[1] + 58 * math.sin(a), 4.5, 4.5), w=0.8, passes=1)
    hub = ellipse_pts(*c, 15, 15)
    p.contour(hub, w=1.4)
    p.shade([gen, hub], form_tone(gen, LIGHT, rim=14, base=0.0), spacing=3.0)
    p.chalk_line((c[0] - 150, c[1]), (c[0] + 150, c[1]), dash="6 5", opacity=0.45)
    p.chalk_line((c[0], c[1] - 150), (c[0], c[1] + 150), dash="6 5", opacity=0.45)
    p.label("a", c[0] + 162, c[1] - 92)
    p.label("b", c[0] + 132, c[1] + 104)
    p.label("c", c[0] - 18, c[1] + 26)


def _stick(p: Page, pos, rot, tuck):
    leg = 34 if not tuck else 22
    pts = {
        "head": (0, -72), "neck": (0, -62), "hip": (0, -32),
        "hand_l": (-22, -58 + (14 if tuck else 30)), "hand_r": (22, -58 + (14 if tuck else 30)),
        "knee": (10 if tuck else 0, -32 + leg * 0.6), "foot": (0 if tuck else 0, -32 + leg),
    }
    q = {k: place([v], rot, pos)[0] for k, v in pts.items()}
    p.contour(ellipse_pts(*q["head"], 8, 8), w=1.2, passes=1)
    p.contour([q["neck"], q["hip"]], closed=False, w=1.8, passes=1)
    p.contour([q["hand_l"], q["neck"], q["hand_r"]], closed=False, w=1.2, passes=1)
    p.contour([q["hip"], q["knee"], q["foot"]], closed=False, w=1.5, passes=1)


def _backflip(p: Page):
    ground = 1000
    path = [(1100 + 340 * t, ground - 230 * 4 * t * (1 - t) - 4) for t in (k / 40 for k in range(41))]
    p.chalk(path, closed=False, dash="6 5", opacity=0.65)
    p.arrow_head(path[22], path[19], color=CHALK, layer="chalk", w=1.1)
    for k in range(5):
        t = k / 4
        x = 1100 + 340 * t
        y = ground - 230 * 4 * t * (1 - t)
        _stick(p, (x, y), -360 * t, tuck=0 < k < 4)
    p.line((1060, ground), (1500, ground), w=1.1, overshoot=6)
    p.label("d", 1290, 720)


def folio_humanoid_robot() -> Page:
    p = Page(seed=505, folio="")
    _vitruvian(p)
    _harmonic_drive(p)
    _backflip(p)

    p.title("Dell'omo meccanico", 700, 110)
    p.note([
        "come l'omo di Vitruvio",
        "così è misurato questo omo di ferro",
        "le braccia aperte quanto la sua altezza",
        "io feci uno cavaliere che si moveva",
        "ora l'omo di ferro corre e salta",
    ], 1530, 548)
    p.note([
        "a. l'anello dentato",
        "b. la ruota molle che si piega",
        "c. l'ovato che la spinge",
    ], 1530, 98)
    p.note(["d. salta e si volta nell'aria come il gatto"], 1530, 1040)
    return p


NOTES = {
    "Dell'omo meccanico": "Of the mechanical man",
    "come l'omo di Vitruvio": "like the man of Vitruvius",
    "così è misurato questo omo di ferro": "so this iron man is measured",
    "le braccia aperte quanto la sua altezza": "his open arms as wide as he is tall",
    "io feci uno cavaliere che si moveva": "I once made a knight that moved",
    "ora l'omo di ferro corre e salta": "now the iron man runs and leaps",
    "a. l'anello dentato": "a. the toothed ring",
    "b. la ruota molle che si piega": "b. the supple wheel that bends",
    "c. l'ovato che la spinge": "c. the oval that drives it",
    "d. salta e si volta nell'aria come il gatto": "d. it leaps and turns in the air like a cat",
}
