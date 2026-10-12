"""f. 2r — the bionic hand (i-LIMB, 2007): a motor in every finger, driven by the muscles of the arm."""

from __future__ import annotations

import math

from codex import CHALK, Page, ellipse_pts, form_tone, lin_tone, rrect_pts
from pages.common import cylinder_h, draw_visible, gear, not_in, place, smooth_closed, zigzag

LIGHT = (-1.0, -1.2)


def _finger_parts(w, Lp, Ld):
    prox = rrect_pts(-w / 2, -(Lp - 4), w, Lp - 10, 7)
    dist = rrect_pts(-w / 2, -Ld, w, Ld - 4, (w / 2, w / 2, 6, 6))  # local to the joint
    return prox, dist


def _finger(p: Page, base, w, Lp, Ld, ang, bend=0.0, style="full", inner=True):
    """One finger: proximal segment from the knuckle, distal segment from the joint.
    style: full (inked and shaded), faint (light ink), chalk (dashed construction)."""
    prox_l, dist_l = _finger_parts(w, Lp, Ld)
    prox = place(prox_l, ang, base)
    joint_c = place([(0, -Lp)], ang, base)[0]
    dist = place(dist_l, ang + bend, joint_c)
    knuckle = place(ellipse_pts(0, 0, w * 0.5, w * 0.5), ang, base)
    joint = ellipse_pts(*joint_c, w * 0.42, w * 0.42)
    tip = place([(0, -Ld)], ang + bend, joint_c)[0]

    if style == "chalk":
        p.chalk(prox, dash="5 4", opacity=0.5)
        p.chalk(dist, dash="5 4", opacity=0.5)
        return tip, joint_c
    if style == "faint":
        for shape in (prox, dist, joint):
            p.contour(shape, w=1.0, passes=1, opacity=0.45)
        return tip, joint_c

    draw_visible(p, prox, [knuckle, joint], w=1.8)
    draw_visible(p, dist, [joint], w=1.8)
    p.contour(knuckle, w=1.6)
    p.contour(joint, w=1.5)
    p.contour(ellipse_pts(*joint_c, 4, 4), w=1.0, passes=1)
    pad = place([(-w / 2 + 4, -Ld + 30), (0, -Ld + 33), (w / 2 - 4, -Ld + 30)], ang + bend, joint_c)
    p.contour(pad, closed=False, w=0.9, passes=1, opacity=0.8)
    for shape, occ in ((prox, [knuckle, joint]), (dist, [joint])):
        t, m = form_tone(shape, LIGHT, rim=w * 0.42), not_in(occ)
        p.shade(shape, lambda q, t=t, m=m: t(q) * m(q), spacing=3.2)
    for shape in (knuckle, joint):
        t = form_tone(shape, LIGHT, rim=w * 0.3, base=0.05)
        p.shade(shape, t, spacing=3.0)

    if inner:
        motor = place(rrect_pts(-w * 0.2, -Lp * 0.78, w * 0.4, Lp * 0.5, 4), ang, base)
        p.chalk(motor, opacity=0.6)
        for k in range(5):
            s = Lp * 0.33 + k * Lp * 0.08
            p.chalk(place([(-w * 0.2, -s), (w * 0.2, -s - 3)], ang, base), closed=False, opacity=0.5)
        worm = [(w * 0.16 * (1 if k % 2 else -1), -Lp * 0.8 - k * 4) for k in range(5)]
        p.chalk(place(worm, ang, base), closed=False, opacity=0.6)
    return tip, joint_c


def _hand(p: Page):
    palm = smooth_closed([(352, 824), (488, 824), (526, 744), (540, 646), (522, 594),
                          (420, 584), (312, 594), (294, 650), (302, 744)])
    sock = [(322, 838), (518, 838), (546, 1132), (294, 1132)]

    # forearm socket, with the electrodes that listen to the muscles
    p.contour(sock[1:3], closed=False, w=2.0)
    p.contour([sock[3], sock[0]], closed=False, w=2.0)
    p.contour(ellipse_pts(420, 1132, 126, 16, 0, 0, 180), closed=False, w=1.8)
    p.chalk(ellipse_pts(420, 1132, 126, 16, 0, 180, 360), closed=False, dash="5 5", opacity=0.45)
    sock_shape = sock
    p.shade(sock_shape, lin_tone((300, 0), (546, 0), gamma=1.5, lo=0.05), spacing=3.4)
    for cx, cy in ((380, 1010), (466, 1040)):
        p.chalk(ellipse_pts(cx, cy, 13, 13), dash="3 3", opacity=0.7)
        p.chalk([(cx, cy - 13), (cx + 6, 920), (cx + 4, 846)], closed=False, dash="4 4", opacity=0.5)
    p.contour(ellipse_pts(420, 838, 100, 15, 0, 0, 180), closed=False, w=1.6)
    p.contour(ellipse_pts(420, 852, 103, 15, 0, 0, 180), closed=False, w=1.1, passes=1)

    # the fingers, then the thumb on its turning base
    occluders = []
    tips = []
    for x, w, Lp, Ld, ang in ((332, 44, 112, 96, -7), (384, 46, 122, 102, -2), (436, 44, 114, 96, 3), (486, 38, 92, 80, 8)):
        tip, _ = _finger(p, (x, 590), w, Lp, Ld, ang)
        tips.append(tip)
        prox_l, _ = _finger_parts(w, Lp, Ld)
        occluders += [place(prox_l, ang, (x, 590)), place(ellipse_pts(0, 0, w * 0.5, w * 0.5), ang, (x, 590))]
    thumb_base = (316, 712)
    disc = ellipse_pts(*thumb_base, 30, 30)
    _finger(p, thumb_base, 48, 96, 86, -58, bend=-6)
    prox_l, _ = _finger_parts(48, 96, 86)
    occluders += [place(prox_l, -58, thumb_base), disc]
    p.contour(disc, w=1.6)
    p.shade(disc, form_tone(disc, LIGHT, rim=10, base=0.1), spacing=3.0)
    p.contour(ellipse_pts(*thumb_base, 9, 9), w=1.0, passes=1)

    draw_visible(p, palm, occluders, w=2.1, ghosts=1)
    p.shade(palm, lambda q, t=form_tone(palm, LIGHT, rim=34), m=not_in(occluders): t(q) * m(q), spacing=3.6)
    for sx, sy in ((360, 640), (480, 640), (372, 790), (468, 790)):
        p.contour(ellipse_pts(sx, sy, 5, 5), w=1.0, passes=1)
        p.contour([(sx - 3, sy - 3), (sx + 3, sy + 3)], closed=False, w=0.8, passes=1)
    p.contour([(330, 700), (510, 700)], closed=False, w=0.8, passes=1, opacity=0.5)

    # the muscle's signal, as it would be written by a needle
    p.chalk_line((140, 1000), (290, 1000), overshoot=0, opacity=0.45)
    p.contour(zigzag(146, 284, 1000, 24, 6, p.rng), closed=False, w=1.0, passes=1, opacity=0.8)
    p.chalk([(290, 1000), (340, 1012), (366, 1010)], closed=False, dash="4 4", opacity=0.5)
    p.label("g", 222, 958)
    return tips


def _motion(p: Page):
    K, w, Lp, Ld = (1060, 560), 50, 150, 126
    block = rrect_pts(920, 586, 166, 96, 8)
    p.contour(block, w=1.8)
    p.shade(block, form_tone(block, LIGHT, rim=20, base=0.2), spacing=3.2)
    poses = [(0, 0, "chalk"), (38, 42, "faint"), (78, 96, "full")]
    tips = []
    for a1, a2, style in poses:
        tip, _ = _finger(p, K, w, Lp, Ld, a1, bend=a2, style=style, inner=(style == "full"))
        tips.append(tip)
    arc = []
    for k in range(21):
        t = k / 20
        prox_end = place([(0, -Lp)], 78 * t, K)[0]
        arc.append(place([(0, -Ld)], 78 * t + 96 * t, prox_end)[0])
    p.chalk(arc, closed=False, opacity=0.6)
    p.arrow_head(arc[-1], arc[-3], color=CHALK, layer="chalk", w=1.1)
    for letter, (x, y), (dx, dy) in zip("abc", tips, ((50, -6), (52, -2), (38, 30))):
        p.label(letter, x + dx, y + dy)


def _worm_gear(p: Page):
    gc, gr = (1250, 912), 92
    worm = cylinder_h(1120, 1384, 801, 17)
    motor = cylinder_h(986, 1098, 801, 32)
    wheel = gear(*gc, gr, 26, depth=10)
    draw_visible(p, wheel, [worm], w=1.7)
    p.contour(ellipse_pts(*gc, gr - 14, gr - 14), w=1.2, passes=1)
    p.contour(ellipse_pts(*gc, 16, 16), w=1.4)
    p.contour(ellipse_pts(*gc, 5, 5), w=1.0, passes=1)
    for k in range(4):
        a = math.radians(45 + k * 90)
        for off in (-5, 5):
            nx, ny = -math.sin(a) * off, math.cos(a) * off
            p.contour([(gc[0] + 16 * math.cos(a) + nx, gc[1] + 16 * math.sin(a) + ny),
                       (gc[0] + (gr - 14) * math.cos(a) + nx, gc[1] + (gr - 14) * math.sin(a) + ny)],
                      closed=False, w=1.0, passes=1)
    rim = [ellipse_pts(*gc, gr - 14, gr - 14)]
    p.shade([wheel] + rim, lambda q, t=form_tone(wheel, LIGHT, rim=16), m=not_in([worm]): t(q) * m(q), spacing=3.0)

    p.contour(worm, w=1.8)
    for x in range(1130, 1376, 13):
        p.contour([(x, 784), (x + 8, 801), (x + 2, 818)], closed=False, w=0.9, passes=1, opacity=0.85)
    p.shade(worm, lin_tone((0, 784), (0, 818), gamma=1.4, lo=0.1), spacing=2.6)
    p.contour(motor, w=1.9, ghosts=1)
    for x in range(1000, 1090, 9):
        p.contour(ellipse_pts(x, 801, 4, 32, 0, -90, 90), closed=False, w=0.8, passes=1, opacity=0.7)
    p.shade(motor, lin_tone((0, 769), (0, 833), gamma=1.3, lo=0.12), spacing=3.0)
    p.contour([(1098, 795), (1120, 795)], closed=False, w=1.2, passes=1)
    p.contour([(1098, 807), (1120, 807)], closed=False, w=1.2, passes=1)
    p.chalk_line((1250, 780), (1250, 1030), dash="6 5", opacity=0.45)
    p.chalk_line((960, 801), (1410, 801), dash="6 5", opacity=0.45)
    p.label("d", 1312, 768)
    p.label("e", 1374, 1000)
    p.label("f", 1052, 755)


def _bones(p: Page, base=(730, 566)):
    """A human index finger, bone by bone, beside its iron copy."""
    x, y = base
    for L, we, ww in ((128, 17, 10), (82, 15, 9), (54, 13, 8), (40, 12, 7)):
        bone = smooth_closed([(x - we, y), (x - ww, y - L * 0.3), (x - ww, y - L * 0.72), (x - we * 0.9, y - L),
                              (x + we * 0.9, y - L), (x + ww, y - L * 0.72), (x + ww, y - L * 0.3), (x + we, y)], n=6)
        p.contour(bone, w=1.6, ghosts=1)
        p.shade(bone, form_tone(bone, LIGHT, rim=9, base=0.05), spacing=2.8)
        y -= L + 7
    p.chalk([(x + 20, base[1] - 20), (x + 17, y + 60), (x + 6, y + 14)], closed=False, opacity=0.55)
    p.chalk([(x - 20, base[1] - 20), (x - 16, y + 60), (x - 5, y + 14)], closed=False, opacity=0.55)


def folio_bionic_hand() -> Page:
    p = Page(seed=202, folio="")
    _hand(p)
    _bones(p)
    _motion(p)
    _worm_gear(p)

    p.title("Della mano che obbedisce al pensiero", 760, 110)
    p.note([
        "ogni dito ha il suo motore",
        "come ogni dito ha il suo muscolo",
        "il muscolo del braccio parla piano",
        "e la mano l'ascolta",
    ], 905, 760)
    p.note([
        "a. il dito aperto",
        "b. il dito che si piega",
        "c. il dito chiuso",
    ], 1530, 380)
    p.note([
        "d. la vite sanza fine",
        "e. la rota che segue la vite",
        "f. il motore piccolo come un seme",
    ], 1530, 1032)
    p.note(["g. li segni del muscolo"], 300, 1050)
    p.note([
        "l'osso e il motore",
        "fanno uno medesimo officio",
    ], 905, 592)
    return p


NOTES = {
    "Della mano che obbedisce al pensiero": "Of the hand that obeys thought",
    "ogni dito ha il suo motore": "each finger has its own motor",
    "come ogni dito ha il suo muscolo": "as each finger has its own muscle",
    "il muscolo del braccio parla piano": "the muscle of the arm speaks softly",
    "e la mano l'ascolta": "and the hand listens",
    "a. il dito aperto": "a. the finger open",
    "b. il dito che si piega": "b. the finger bending",
    "c. il dito chiuso": "c. the finger closed",
    "d. la vite sanza fine": "d. the endless screw",
    "e. la rota che segue la vite": "e. the wheel that follows the screw",
    "f. il motore piccolo come un seme": "f. the motor, small as a seed",
    "g. li segni del muscolo": "g. the signals of the muscle",
    "l'osso e il motore": "the bone and the motor",
    "fanno uno medesimo officio": "do one and the same work",
}
