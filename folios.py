"""The pages of the Codice Moderno: one function per modern object."""

from __future__ import annotations

import math

from codex import (
    Page, CHALK, _inside, ellipse_pts, rrect_pts, rotate_pts, transform,
    lin_tone, radial_tone, form_tone, union_outline,
)


def outside_runs(pts, poly, closed=True):
    """Split a path into the runs that lie outside `poly`, so overlapping
    shapes read as one solid object instead of two see-through outlines."""
    flags = [not _inside(p, poly) for p in pts]
    if all(flags):
        return [pts]
    if closed:
        k = flags.index(False)
        pts, flags = pts[k:] + pts[:k], flags[k:] + flags[:k]
    runs, cur = [], []
    for p, ok in zip(pts, flags):
        if ok:
            cur.append(p)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def capsule(S0, S1, w0, w1, flat=0.6, n=30):
    """A tapered rod from S0 to S1 with a rounded end at S1 (open at S0)."""
    L = math.dist(S0, S1)
    u = ((S1[0] - S0[0]) / L, (S1[1] - S0[1]) / L)
    nr = (u[1], -u[0])
    deg = math.degrees(math.atan2(u[1], u[0]))

    def at(s, off=0.0):
        return (S0[0] + u[0] * s + nr[0] * off, S0[1] + u[1] * s + nr[1] * off)

    def wid(s):
        return w0 + (w1 - w0) * s / L

    ss = [L * i / n for i in range(n + 1)]
    left = [at(s, -wid(s)) for s in ss]
    cap = ellipse_pts(S1[0], S1[1], w1 * flat, w1, deg, 90, -90)
    right = [at(s, wid(s)) for s in reversed(ss)]
    return left + cap + right, at, wid, L, deg


# ---------------------------------------------------------------- f. 1r

def _earbud(p: Page, scale, rot, dx, dy, mirror=False, detail=True):
    T = lambda pts: transform(pts, scale, rot, dx, dy, mirror)  # noqa: E731
    light = (-1.0, -1.2)

    head_l = ellipse_pts(0, 0, 105, 88, -20)
    nozzle_l = ellipse_pts(-80, 40, 46, 57, -40)
    body_l = union_outline(head_l, nozzle_l)
    grille_l = ellipse_pts(-92, 47, 29, 40, -40)
    stem_l, at, wid, L, deg = capsule((50, 40), (50 + 250 * math.cos(math.radians(77)),
                                                 40 + 250 * math.sin(math.radians(77))), 31, 26)

    body, grille, stem = T(body_l), T(grille_l), T(stem_l)
    w = 2.1 * scale ** 0.4

    for run in outside_runs(body, stem):
        p.contour(run, closed=False, w=w, overshoot=2, ghosts=1 if detail else 0)
    for run in outside_runs(stem, body, closed=False):
        p.contour(run, closed=False, w=w, overshoot=2, ghosts=1 if detail else 0)
    p.contour(grille, w=w * 0.75)

    sp = 3.7 * scale ** 0.35
    p.shade([body, grille], form_tone(body, light, rim=34 * scale), spacing=sp)
    p.shade(stem, form_tone(stem, light, rim=26 * scale, base=0.05), spacing=sp)
    p.hatch(grille, 45, 3.0, w=0.6, opacity=0.7)
    p.hatch(grille, -45, 3.0, w=0.6, opacity=0.7)
    p.hatch(grille, 45, 3.0, w=0.7, opacity=0.6, tone=form_tone(grille, light, rim=12, base=0.2))

    sensor = T(ellipse_pts(30, -42, 11, 7, -20))
    p.contour(sensor, w=w * 0.5, passes=1)
    p.hatch(sensor, 45, 2.0, w=0.7)
    p.contour(T(ellipse_pts(*at(105, -6), 34, 7, deg)), w=w * 0.42, passes=1)
    p.contour(T([at(L - 26, -wid(L - 26)), at(L - 24, 0), at(L - 26, wid(L - 26))]), closed=False, w=w * 0.5, passes=1)
    p.contour(T(ellipse_pts(*at(L + 6), 6, 2.5, deg + 90)), w=w * 0.45, passes=1)

    out = {"grille": T([(-92, 47)])[0]}
    if detail:
        for r in (31, 21, 8):
            p.chalk(T(ellipse_pts(-70, 28, r, r * 0.85, -40)))
        c = at(42)
        chip = rotate_pts(rrect_pts(-11, -15, 22, 30, 3), deg - 90, (0, 0))
        p.chalk(T([(x + c[0], y + c[1]) for x, y in chip]))
        b0, b1 = 82, L - 34
        mid = at((b0 + b1) / 2)
        batt = rotate_pts(rrect_pts(-16, -(b1 - b0) / 2, 32, b1 - b0, 15), deg - 90, (0, 0))
        p.chalk(T([(x + mid[0], y + mid[1]) for x, y in batt]))
        p.chalk(T([at(26), (-50, 40)]), closed=False, dash="5 4")
        p.chalk(T([at(58), at(b0)]), closed=False, dash="5 4")
        p.chalk(T(ellipse_pts(0, 0, 122, 122)), dash="3 7", opacity=0.45)
        p.chalk(T([at(-150), at(L + 40)]), closed=False, dash="8 6", opacity=0.45)
        for s in range(0, int(L) + 1, 25):
            p.chalk(T([at(s, 52), at(s, 60 if s % 50 else 66)]), closed=False, w=0.9)
        p.chalk(T([at(0, 56), at(L, 56)]), closed=False, w=0.9)
        out.update({"driver": T([(-70, 28)])[0], "battery": T([mid])[0], "chip": T([c])[0]})
    return out


def folio_airpods() -> Page:
    p = Page(seed=11, folio="f. 1r")

    bud = _earbud(p, 1.3, 0, 420, 365)
    g = bud["grille"]
    for i, r in enumerate(range(70, 240, 28)):
        p.contour(ellipse_pts(g[0] - 6, g[1], r, r * 1.08, 0, 148, 214), closed=False,
                  w=1.1 - i * 0.08, passes=1, opacity=0.6 - i * 0.05)
    dx, dy = bud["driver"]
    p.label("c", dx + 52, dy - 96)
    p.line((dx + 4, dy - 14), (dx + 36, dy - 88), w=0.8, opacity=0.55)
    bx, by = bud["battery"]
    p.label("d", bx - 72, by + 8)
    p.line((bx - 10, by), (bx - 64, by), w=0.8, opacity=0.55)

    _earbud(p, 0.62, 14, 815, 545, mirror=True, detail=False)

    # case, front view
    case = rrect_pts(1060, 175, 300, 225, 66)
    p.contour(case, w=2.0, ghosts=1)
    p.contour([(1062, 248), (1210, 252), (1358, 248)], closed=False, w=1.8, passes=1)
    p.contour(ellipse_pts(1210, 335, 4.5, 4.5), w=1.4, passes=1)
    p.shade(case, form_tone(case, rim=40, base=0.02), spacing=4.0)
    shadow = ellipse_pts(1225, 410, 178, 12)
    p.hatch(shadow, 45, 3.0, w=0.8, opacity=0.75, tone=radial_tone((1245, 410), 178, 0, gamma=0.6))
    p.chalk_line((1210, 145), (1210, 435), dash="6 5")
    p.chalk_line((1030, 287), (1390, 287), dash="6 5")

    # case, side view with the lid swung open about its hinge
    hinge = (1235, 700)
    base = rrect_pts(1125, 700, 110, 150, (0, 0, 42, 42))
    lid_closed = rrect_pts(1125, 627, 110, 73, (40, 40, 0, 0))
    lid_open = rotate_pts(lid_closed, 112, hinge)
    bud_top = ellipse_pts(1172, 700, 31, 20, 0, 180, 360)
    p.contour(base, w=2.0, ghosts=1)
    p.contour(lid_open, w=2.0)
    p.contour(bud_top, closed=False, w=1.9)
    p.chalk(lid_closed, dash="7 5")
    p.chalk(rrect_pts(1156, 712, 32, 118, 15), dash="5 4")
    p.shade(base, form_tone(base, rim=30, base=0.04), spacing=3.8)
    p.shade(lid_open, form_tone(lid_open, rim=26, base=0.1), spacing=3.8)
    p.shade(bud_top + [(1141, 700)], form_tone(bud_top + [(1141, 700)], rim=10), spacing=3.0)
    r_arc = math.dist(hinge, (1125, 640))
    a0 = math.degrees(math.atan2(640 - hinge[1], 1125 - hinge[0]))
    arc = ellipse_pts(hinge[0], hinge[1], r_arc + 18, r_arc + 18, 0, a0, a0 + 106)
    p.chalk(arc, closed=False, w=1.3, opacity=0.75)
    p.arrow_head(arc[-1], arc[-4], color=CHALK, layer="chalk", w=1.3)
    p.contour(ellipse_pts(*hinge, 5, 5), w=1.4, passes=1)
    p.label("a", hinge[0] + 42, hinge[1] + 24)
    tip = rotate_pts([(1145, 640)], 112, hinge)[0]
    p.label("b", tip[0] + 36, tip[1] - 4)
    floor = ellipse_pts(1182, 862, 98, 9)
    p.hatch(floor, 45, 3.0, w=0.8, opacity=0.65, tone=radial_tone((1192, 862), 98, 0, gamma=0.6))

    # two sources, two ears: interfering rings like stones dropped in water
    for cx in (225, 365):
        for i, r in enumerate(range(16, 132, 15)):
            p.contour(ellipse_pts(cx, 1010, r, r * 0.97), w=1.0, passes=1, opacity=0.62 - i * 0.04, amp=0.6)
        p.contour(ellipse_pts(cx, 1010, 3.5, 3.5), w=2.4, passes=1)
    p.label("e", 232, 866)
    p.label("f", 372, 866)

    p.title("Delli orecchini che cantano", 650, 108)
    p.note([
        "questo strumento si mette nell'orecchio",
        "e porta la musica sanza alcuno filo",
        "per virtù d'una forza invisibile",
        "che passa per l'aria come la luce",
        "la sua virtù sta nel gambo",
        "dove si nasconde lo spirito suo",
    ], 1010, 150)
    p.note([
        "c. la membrana che trema e fa la voce",
        "d. il serbatoio della forza",
        "le onde dell'aria si movono",
        "come quelle dell'acqua quando",
        "vi si getta una pietra",
        "e. f. due fonti per due orecchie",
    ], 1000, 890)
    p.note([
        "la scatola bianca li nutrisce",
        "come la madre nutrisce li figlioli",
        "a. il perno ove si volge il coperchio",
        "b. il coperchio aperto",
    ], 1530, 925)
    return p


# ---------------------------------------------------------------- f. 2r

def _wheel(p: Page, c, r, detail=1.0):
    tire = ellipse_pts(*c, r, r)
    rim = ellipse_pts(*c, r * 0.67, r * 0.67)
    p.contour(tire, w=2.0, ghosts=1)
    p.contour(rim, w=1.6)
    p.contour(ellipse_pts(*c, r * 0.18, r * 0.18), w=1.4, passes=1)
    p.shade([tire, rim], lambda q: 0.55 + 0.45 * min(1, max(0, (q[0] - c[0] + q[1] - c[1]) / (2 * r) + 0.5)), spacing=3.2)
    for k in range(6):
        a = math.radians(k * 60 + 15)
        a2 = math.radians(k * 60 + 38)
        r0, r1 = r * 0.26, r * 0.6
        slot = [(c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a)), (c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a)),
                (c[0] + r1 * math.cos(a2), c[1] + r1 * math.sin(a2)), (c[0] + r0 * math.cos(a2), c[1] + r0 * math.sin(a2))]
        p.contour(slot, w=1.1, passes=1, opacity=0.85)
        p.hatch(slot, 45, 2.6, w=0.7, opacity=0.8)
        if detail > 0.5:
            lug = (c[0] + r * 0.24 * math.cos(a - 0.5), c[1] + r * 0.24 * math.sin(a - 0.5))
            p.contour(ellipse_pts(*lug, r * 0.03 + 1, r * 0.03 + 1), w=1.0, passes=1)
    return tire


def folio_cybertruck() -> Page:
    p = Page(seed=23, folio="f. 2r")
    ground = 640
    fw, rw = (476, 562), (1146, 562)

    body = [(295, 505), (740, 325), (1300, 445), (1296, 585), (1256, 585), (1221, 470), (1071, 470),
            (1036, 585), (586, 585), (551, 470), (401, 470), (366, 585), (305, 585)]
    win1 = [(525, 428), (735, 343), (735, 428)]
    win2 = [(752, 346), (960, 388), (960, 428), (752, 428)]
    upper = [(295, 505), (740, 325), (1300, 445), (1277, 440), (456, 440)]
    lower = [(456, 440), (1277, 440), (1300, 445), (1296, 585), (1256, 585), (1221, 470), (1071, 470),
             (1036, 585), (586, 585), (551, 470), (401, 470), (366, 585), (305, 585), (295, 505)]

    # red chalk construction: the triangle the whole body is built on
    a, b, c = (295, 505), (740, 325), (1300, 445)
    p.chalk_line(a, b, overshoot=60)
    p.chalk_line(b, c, overshoot=60)
    p.chalk_line(a, c, overshoot=40, dash="8 6")
    p.chalk_line(b, (740, ground + 20), dash="6 5")
    p.chalk_line((380, 562), (1250, 562), dash="6 5")
    for wc in (fw, rw):
        p.chalk(ellipse_pts(*wc, 112, 112), dash="3 6", opacity=0.5)

    p.contour(body, w=2.2, ghosts=1)
    p.contour(win1, w=1.6)
    p.contour(win2, w=1.6)
    p.line((456, 440), (1277, 440), w=1.4)
    for x, y0 in ((600, 442), (743, 430), (975, 432)):
        p.line((x, y0), (x, 585), w=1.1, opacity=0.8)
    p.line((985, 382), (985, 438), w=1.1, opacity=0.8)
    mirror = [(498, 431), (536, 424), (541, 446), (503, 449)]
    p.contour(mirror, w=1.4)
    p.hatch(mirror, 45, 2.5, w=0.7)
    p.line((294, 500), (318, 492), w=3.0)

    p.shade([upper, win1, win2], lin_tone((500, 330), (1200, 450), gamma=2.2, lo=0.0), spacing=4.6)
    glint = lambda q, base=0.92: 0.0 if 30 < (q[0] - 600) - (q[1] - 400) * 1.4 < 70 else base  # noqa: E731
    p.shade([win1], glint, spacing=3.0)
    p.shade([win2], lambda q: glint((q[0] - 260, q[1])), spacing=3.0)
    p.shade(lower, lin_tone((0, 445), (0, 600), gamma=1.7, lo=0.04), spacing=4.2)
    for wc, arch in ((fw, [(366, 585), (401, 470), (551, 470), (586, 585)]),
                     (rw, [(1036, 585), (1071, 470), (1221, 470), (1256, 585)])):
        p.hatch(arch, 45, 2.6, w=0.8, opacity=0.9, tone=lambda q, wc=wc: 0 if math.dist(q, wc) < 80 else 1)
        p.hatch(arch, 15, 3.2, w=0.7, opacity=0.7, tone=lambda q, wc=wc: 0 if math.dist(q, wc) < 80 else 1)
        _wheel(p, wc, 78)

    p.line((215, ground), (1395, ground), w=1.3, overshoot=12)
    for x in range(240, 1380, 70):
        p.line((x, ground + 9 + (x % 3) * 3), (x + 34, ground + 9 + (x % 3) * 3), w=0.8, opacity=0.5)
    p.hatch([(380, ground), (1240, ground), (1215, ground + 14), (405, ground + 14)], 45, 2.6, w=0.8, opacity=0.8)

    p.label("a", 286, 494)
    p.label("b", 752, 300)
    p.label("c", 1340, 446)

    # front view
    fbody = [(265, 868), (395, 868), (450, 958), (448, 1030), (430, 1045), (230, 1045), (212, 1030), (210, 958)]
    fwin = [(272, 878), (388, 878), (425, 950), (235, 950)]
    p.chalk_line((330, 840), (330, 1095), dash="6 5")
    for x0 in (218, 406):
        tire = rrect_pts(x0, 1010, 36, 70, 8)
        for run in outside_runs(tire, fbody):
            p.contour(run, closed=False, w=1.8)
        p.shade(tire, lambda q: 0 if _inside(q, fbody) else 0.95, spacing=2.8)
    p.contour(fbody, w=2.1, ghosts=1)
    p.contour(fwin, w=1.5)
    p.line((213, 963), (447, 963), w=3.2)
    p.shade(fbody, lin_tone((200, 0), (460, 0), gamma=2.2, lo=0.0), spacing=4.4)
    p.shade(fwin, lambda q: 0.0 if 10 < (q[0] - 300) - (q[1] - 880) * 0.9 < 40 else 0.9, spacing=3.0)
    p.line((165, 1080), (505, 1080), w=1.2, overshoot=10)
    p.hatch([(215, 1080), (445, 1080), (435, 1092), (225, 1092)], 45, 2.6, w=0.8, opacity=0.8)

    # the force in little jars, the motor, and the wheel it turns
    jars = rrect_pts(680, 925, 110, 72, 6)
    p.contour(jars, w=1.8)
    for x in range(698, 790, 18):
        p.line((x, 929), (x, 993), w=0.9, opacity=0.8)
    p.shade(jars, form_tone(jars, rim=14, base=0.15), spacing=3.4)
    p.contour([(790, 945), (805, 930), (812, 952), (822, 938)], closed=False, w=1.3, passes=1)

    mx0, mx1, my, mr = 840, 1010, 960, 52
    motor = [(mx0, my - mr), (mx1, my - mr)] + ellipse_pts(mx1, my, 17, mr, 0, -90, 90)[1:-1] + \
            [(mx1, my + mr), (mx0, my + mr)] + ellipse_pts(mx0, my, 17, mr, 0, 90, 270)[1:-1]
    p.contour(motor, w=2.0, ghosts=1)
    p.contour(ellipse_pts(mx0, my, 17, mr), w=1.5, passes=1)
    for x in range(mx0 + 14, mx1 - 4, 10):
        p.contour(ellipse_pts(x, my, 7, mr, 0, -90, 90), closed=False, w=0.9, passes=1, opacity=0.75)
    p.shade(motor, lin_tone((0, my - mr), (0, my + mr), gamma=1.4, lo=0.1), spacing=3.4)
    p.line((mx1 + 14, my - 7), (1073, my - 7), w=1.5)
    p.line((mx1 + 14, my + 7), (1073, my + 7), w=1.5)
    _wheel(p, (1215, my), 140)
    p.chalk(ellipse_pts(1215, my, 158, 158), dash="3 6", opacity=0.5)
    for k in range(12):
        ang = math.radians(k * 30)
        p.chalk_line((1215 + 140 * math.cos(ang), my + 140 * math.sin(ang)),
                     (1215 + 165 * math.cos(ang), my + 165 * math.sin(ang)), overshoot=0, opacity=0.5)
    p.label("g", 760, 912)
    p.label("h", 945, 895)
    p.label("i", 1250, 795)

    p.title("Del carro di ferro sanza cavalli", 700, 110)
    p.note([
        "questo carro si move per sé medesimo",
        "sanza cavalli e sanza vento",
        "la forma sua è tutta di linee rette",
        "come uno triangolo posato in terra",
        "a. b. c. il triangolo del corpo",
        "il ferro non si piega",
    ], 1530, 105)
    p.note([
        "dinanzi. il lume è una sola linea",
        "le pietre non lo rompono  ma il vetro sì",
        "g. la forza chiusa in vasetti",
        "h. il motore che gira per virtù di calamita",
        "i. e la ruota seguita il motore",
    ], 1010, 680)
    return p


# ---------------------------------------------------------------- f. 3r

def _bez(p0, p1, p2, n=16):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]


def _deck_profile():
    """Side profile of a popsicle deck, flat middle with both kicks."""
    top = (_bez((530, 298), (600, 356), (690, 354)) + [(920, 354)] +
           _bez((1150, 354), (1240, 356), (1310, 296)))
    bottom = (_bez((1316, 307), (1244, 368), (1150, 366)) + [(920, 366)] +
              _bez((690, 366), (596, 368), (524, 309)))
    return top + [(1315, 300)] + bottom + [(521, 303)]


def _cylinder(p: Page, cx, top, bot, rx, ry=8.0, tone_base=0.1):
    shape = ellipse_pts(cx, top, rx, ry, 0, 180, 360) + ellipse_pts(cx, bot, rx, ry, 0, 0, 180)
    p.contour(shape, w=1.7)
    p.contour(ellipse_pts(cx, top, rx, ry, 0, 0, 180), closed=False, w=1.2, passes=1)
    p.shade(shape, form_tone(shape, rim=12, base=tone_base), spacing=3.0)
    return shape


def folio_skateboard() -> Page:
    p = Page(seed=37, folio="f. 3r")

    # top view of the deck
    deck = rrect_pts(150, 200, 200, 800, 100)
    p.chalk_line((250, 170), (250, 1030), dash="6 5")
    for y in (300, 900):
        p.chalk_line((120, y), (380, y), dash="6 5")
    for y in range(200, 1001, 25):
        p.chalk_line((112, y), (120 if y % 100 else 126, y), overshoot=0, opacity=0.6)
    p.chalk_line((116, 200), (116, 1000), overshoot=0, opacity=0.6)
    p.contour(deck, w=2.1, ghosts=1)
    for y in (258, 942):
        p.contour([(156, y), (250, y + (6 if y < 500 else -6)), (344, y)], closed=False, w=0.9, passes=1, opacity=0.6)
    for cy in (300, 900):
        for dx in (-20, 20):
            for dy in (-27, 27):
                hole = ellipse_pts(250 + dx, cy + dy, 4, 4)
                p.contour(hole, w=1.1, passes=1)
                p.hatch(hole, 45, 1.6, w=0.7)
    p.shade(deck, form_tone(deck, light=(-1.0, -0.2), rim=34, base=0.02), spacing=4.0)

    # side view
    prof = _deck_profile()
    ground = 462
    p.chalk_line((470, 360), (1370, 360), dash="6 5")
    p.chalk(ellipse_pts(690, 360, 70, 70, 0, 180, 205), closed=False, opacity=0.6)
    p.contour(prof, w=2.0, ghosts=1)
    for y in (358.5, 362):
        p.contour([(700, y), (1140, y)], closed=False, w=0.6, passes=1, opacity=0.55)
    p.hatch(prof, 45, 2.4, w=0.7, opacity=0.6)
    for tx, sgn in ((760, 1), (1080, -1)):
        base = [(tx - 32, 366), (tx + 32, 366), (tx + 26, 380), (tx - 26, 380)]
        hanger = [(tx - 16 * sgn, 380), (tx + 22 * sgn, 386), (tx + 14 * sgn, 424), (tx - 14 * sgn, 428), (tx - 24 * sgn, 404)]
        p.contour(base, w=1.6)
        p.contour(hanger, w=1.6)
        p.shade([base], form_tone(base, rim=6, base=0.2), spacing=2.6)
        p.shade([hanger], form_tone(hanger, rim=10, base=0.15), spacing=2.8)
        p.line((tx - 6 * sgn, 368), (tx - 16 * sgn, 412), w=1.3)
        wheel = ellipse_pts(tx, ground - 30, 30, 30)
        p.contour(wheel, w=1.9)
        p.contour(ellipse_pts(tx, ground - 30, 11, 11), w=1.2, passes=1)
        p.contour(ellipse_pts(tx, ground - 30, 3.5, 3.5), w=1.0, passes=1)
        p.shade([wheel, ellipse_pts(tx, ground - 30, 11, 11)], form_tone(wheel, rim=14, base=0.05), spacing=2.8)
    p.line((470, ground), (1370, ground), w=1.2, overshoot=10)
    p.hatch([(700, ground), (1140, ground), (1120, ground + 10), (720, ground + 10)], 45, 2.4, w=0.8, opacity=0.7)

    # the ollie: one board traced along the curve it flies
    pts, angles = [], []
    for i, ang in enumerate((-28, -14, 0, 6, 0)):
        t = i / 4
        pts.append((480 + 460 * t, 1060 - 300 * 4 * t * (1 - t)))
        angles.append(ang)
    curve = [(480 + 460 * t, 1060 - 300 * 4 * t * (1 - t)) for t in (i / 40 for i in range(41))]
    p.chalk(curve, closed=False, dash="7 6", opacity=0.7)
    p.arrow_head(curve[24], curve[21], color=CHALK, layer="chalk", w=1.2)
    centered = [(x - 920, y - 360) for x, y in prof]
    for (bx, by), ang in zip(pts, angles):
        board = transform(centered, 0.125, ang, bx, by)
        p.contour(board, w=1.5, passes=1)
        p.hatch(board, 45, 1.8, w=0.6, opacity=0.6)
        for off in (-21, 21):
            wc = transform([(off * 8, 82)], 0.125, ang, bx, by)[0]
            p.contour(ellipse_pts(*wc, 4.2, 4.2), w=1.2, passes=1)
    p.line((440, 1075), (990, 1075), w=1.1, overshoot=8)
    for k in range(3):
        a = math.radians(200 + k * 25)
        p.line((428 + 10 * math.cos(a), 1066 + 10 * math.sin(a)), (428 + 24 * math.cos(a), 1066 + 24 * math.sin(a)), w=1.0, passes=1)

    # the truck taken apart
    p.chalk_line((1150, 612), (1150, 1050), dash="6 5")
    plate = [(1075, 640), (1225, 640), (1210, 668), (1090, 668)]
    p.contour(plate, w=1.8, ghosts=1)
    p.shade([plate], form_tone(plate, rim=10, base=0.1), spacing=2.8)
    for hx in (1100, 1200):
        p.contour(ellipse_pts(hx, 654, 5, 3), w=1.0, passes=1)
    p.contour(ellipse_pts(1150, 700, 30, 8), w=1.4, passes=1)
    p.contour(ellipse_pts(1150, 700, 9, 3), w=1.0, passes=1)
    _cylinder(p, 1150, 720, 754, 28)
    hanger = [(1112, 792), (1188, 792), (1290, 856), (1290, 880), (1010, 880), (1010, 856)]
    axle = rrect_pts(975, 862, 350, 12, 5)
    for run in outside_runs(axle, hanger):
        p.contour(run, closed=False, w=1.4)
    p.contour(hanger, w=2.0, ghosts=1)
    p.contour(ellipse_pts(1150, 806, 10, 6), w=1.2, passes=1)
    p.shade([hanger], form_tone(hanger, rim=18, base=0.1), spacing=3.2)
    _cylinder(p, 1150, 918, 952, 28)
    p.contour(ellipse_pts(1150, 975, 30, 8), w=1.4, passes=1)
    nut = rrect_pts(1132, 994, 36, 24, 2)
    p.contour(nut, w=1.5)
    for x in (1144, 1156):
        p.line((x, 996), (x, 1016), w=0.9, overshoot=0)
    p.hatch(nut, 45, 2.4, w=0.7, opacity=0.7)
    for wx in (935, 1365):
        wheel = ellipse_pts(wx, 868, 22, 36)
        p.contour(wheel, w=1.8)
        p.contour(ellipse_pts(wx, 868, 8, 13), w=1.1, passes=1)
        p.shade([wheel, ellipse_pts(wx, 868, 8, 13)], form_tone(wheel, rim=10, base=0.08), spacing=2.6)
    head = rrect_pts(1404, 640, 32, 18, 2)
    p.contour(head, w=1.6)
    p.hatch(head, 45, 2.4, w=0.7, opacity=0.7)
    p.line((1414, 658), (1414, 1010), w=1.4, overshoot=0)
    p.line((1426, 658), (1426, 1010), w=1.4, overshoot=0)
    for y in range(950, 1006, 6):
        p.line((1414, y + 3), (1426, y), w=0.8, overshoot=0, opacity=0.8)

    p.label("d", 1470, 700)
    p.label("e", 1222, 742)
    p.label("e", 1222, 942)

    p.title("Della tavola che vola", 660, 110)
    p.note([
        "l'omo sta sopra la tavola",
        "e col piede la fa saltare",
        "e la tavola vola sanza ali",
        "la tavola è fatta di sette legni",
        "incollati l'uno sopra l'altro",
    ], 1530, 100)
    p.note([
        "la tavola segue la linea del moto",
        "la quale è una linea curva",
        "come il sasso gittato in aria",
    ], 1000, 505)
    p.note([
        "d. il perno maestro che lega il tutto",
        "e. le gomme che piegano e ritornano",
        "le quattro ruote girano sopra perni",
    ], 1530, 1035)
    return p


FOLIOS = {"airpods": folio_airpods, "cybertruck": folio_cybertruck, "skateboard": folio_skateboard}
