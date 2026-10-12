"""f. 1r — the iPhone (2007), drawn from the original's proportions: 115 x 61 x 11.6 mm."""

from __future__ import annotations

import math

from codex import CHALK, Page, _inside, ellipse_pts, form_tone, lin_tone, radial_tone, rrect_pts
from folios import outside_runs

MM = 5.2  # px per mm for the main views


def _visible(pts, occluders, closed=True):
    """Runs of `pts` not hidden behind any of the occluding shapes."""
    if not occluders:
        return [pts]
    flags = [not any(_inside(q, o) for o in occluders) for q in pts]
    if all(flags):
        return [pts]
    if closed and not all(not f for f in flags):
        k = flags.index(False)
        pts, flags = pts[k:] + pts[:k], flags[k:] + flags[:k]
    runs, cur = [], []
    for q, ok in zip(pts, flags):
        if ok:
            cur.append(q)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


# ---------- the sixteen icons of the first home screen ----------

def _glyph(p: Page, kind: str, cx: float, cy: float):
    w = 1.0
    c = lambda pts, closed=True: p.contour(pts, closed=closed, w=w, passes=1, opacity=0.85)  # noqa: E731
    if kind == "phone":
        c(ellipse_pts(cx, cy, 11, 11, 0, 120, 330), closed=False)
        c(ellipse_pts(cx - 8, cy + 7, 4, 3, 45))
        c(ellipse_pts(cx + 7, cy - 8, 4, 3, 45))
    elif kind == "mail":
        c(rrect_pts(cx - 12, cy - 8, 24, 16, 1))
        c([(cx - 12, cy - 8), (cx, cy + 2), (cx + 12, cy - 8)], closed=False)
    elif kind == "globe":
        c(ellipse_pts(cx, cy, 12, 12))
        c(ellipse_pts(cx, cy, 5, 12))
        c([(cx - 12, cy), (cx + 12, cy)], closed=False)
    elif kind == "music":
        c(ellipse_pts(cx - 4, cy + 7, 5, 3.5, -20))
        c([(cx + 1, cy + 6), (cx + 1, cy - 11), (cx + 9, cy - 7)], closed=False)
    elif kind == "message":
        c(ellipse_pts(cx, cy - 2, 12, 8))
        c([(cx - 6, cy + 5), (cx - 10, cy + 11), (cx - 1, cy + 6)], closed=False)
    elif kind == "calendar":
        c(rrect_pts(cx - 11, cy - 11, 22, 22, 2))
        c([(cx - 11, cy - 5), (cx + 11, cy - 5)], closed=False)
        for i in range(3):
            for j in range(2):
                c(ellipse_pts(cx - 6 + i * 6, cy + 1 + j * 6, 1.2, 1.2))
    elif kind == "photos":
        for k in range(5):
            a = math.radians(k * 72)
            c(ellipse_pts(cx + 6 * math.cos(a), cy + 6 * math.sin(a), 4.5, 4.5))
    elif kind == "camera":
        c(rrect_pts(cx - 12, cy - 7, 24, 16, 2))
        c(ellipse_pts(cx, cy + 1, 5, 5))
        c([(cx - 5, cy - 7), (cx - 3, cy - 10), (cx + 3, cy - 10), (cx + 5, cy - 7)], closed=False)
    elif kind == "video":
        c(rrect_pts(cx - 12, cy - 9, 24, 16, 3))
        c([(cx - 3, cy - 5), (cx + 4, cy - 1), (cx - 3, cy + 3)])
        c([(cx - 5, cy + 11), (cx + 5, cy + 11)], closed=False)
    elif kind == "stocks":
        c([(cx - 12, cy + 8), (cx - 5, cy), (cx, cy + 4), (cx + 6, cy - 6), (cx + 12, cy - 9)], closed=False)
        c([(cx - 12, cy + 11), (cx + 12, cy + 11)], closed=False)
    elif kind == "maps":
        c([(cx - 12, cy - 8), (cx - 4, cy - 11), (cx + 4, cy - 8), (cx + 12, cy - 11),
           (cx + 12, cy + 8), (cx + 4, cy + 11), (cx - 4, cy + 8), (cx - 12, cy + 11)])
        c([(cx - 4, cy - 11), (cx - 4, cy + 8)], closed=False)
        c([(cx + 4, cy - 8), (cx + 4, cy + 11)], closed=False)
    elif kind == "weather":
        c(ellipse_pts(cx, cy, 5.5, 5.5))
        for k in range(8):
            a = math.radians(k * 45)
            c([(cx + 8 * math.cos(a), cy + 8 * math.sin(a)), (cx + 12 * math.cos(a), cy + 12 * math.sin(a))], closed=False)
    elif kind == "clock":
        c(ellipse_pts(cx, cy, 12, 12))
        c([(cx, cy - 8), (cx, cy), (cx + 6, cy + 3)], closed=False)
    elif kind == "calculator":
        c(rrect_pts(cx - 9, cy - 12, 18, 24, 2))
        for i in range(3):
            for j in range(3):
                c(ellipse_pts(cx - 5 + i * 5, cy - 3 + j * 5, 1.2, 1.2))
        c([(cx - 6, cy - 8), (cx + 6, cy - 8)], closed=False)
    elif kind == "notes":
        c(rrect_pts(cx - 10, cy - 12, 20, 24, 1))
        for k in range(4):
            c([(cx - 6, cy - 6 + k * 5), (cx + 6, cy - 6 + k * 5)], closed=False)
    elif kind == "settings":
        c(ellipse_pts(cx, cy, 7, 7))
        c(ellipse_pts(cx, cy, 2.5, 2.5))
        for k in range(8):
            a = math.radians(k * 45 + 22)
            c([(cx + 8 * math.cos(a), cy + 8 * math.sin(a)), (cx + 12 * math.cos(a), cy + 12 * math.sin(a))], closed=False)


GRID = ["message", "calendar", "photos", "camera",
        "video", "stocks", "maps", "weather",
        "clock", "calculator", "notes", "settings"]
DOCK = ["phone", "mail", "globe", "music"]


def _icon(p: Page, kind, cx, cy, label=True):
    box = rrect_pts(cx - 22, cy - 22, 44, 44, 10)
    p.contour(box, w=1.2, passes=1, opacity=0.9)
    p.hatch(box, 45, 3.0, w=0.55, opacity=0.55, tone=form_tone(box, rim=9, base=-0.05))
    _glyph(p, kind, cx, cy)
    if label:
        n = p.rng.randint(4, 7)
        pts = [(cx - n * 2.4 + k * 4.8, cy + 32 + (1.2 if k % 2 else -1.2)) for k in range(n)]
        p.contour(pts, closed=False, w=0.8, passes=1, opacity=0.55)


# ---------- the views ----------

def _front(p: Page, x0, y0):
    W, H, R = 61 * MM, 115 * MM, 9 * MM
    outer = rrect_pts(x0, y0, W, H, R)
    bezel = rrect_pts(x0 + 5, y0 + 5, W - 10, H - 10, R - 5)
    sx, sy, sw, sh = x0 + (61 - 49.3) / 2 * MM, y0 + 20.5 * MM, 49.3 * MM, 74 * MM
    screen = rrect_pts(sx, sy, sw, sh, 2)
    home_c = (x0 + W / 2, y0 + H - 10.5 * MM)
    home = ellipse_pts(*home_c, 5.5 * MM, 5.5 * MM)
    ear = rrect_pts(x0 + W / 2 - 30, y0 + 10 * MM - 4, 60, 8, 4)

    p.contour(outer, w=2.1, ghosts=1)
    p.contour(bezel, w=1.0, passes=1, opacity=0.7)
    p.contour(screen, w=1.4)
    p.contour(home, w=1.5)
    p.contour(rrect_pts(home_c[0] - 7, home_c[1] - 7, 14, 14, 3), w=1.0, passes=1)
    p.contour(ear, w=1.1, passes=1)
    p.hatch(ear, 45, 2.0, w=0.7)

    glass = lin_tone((x0, y0), (x0 + W, y0 + H), gamma=1.0, lo=0.5)
    p.shade([bezel, screen, home], lambda q: glass(q) * 0.85, spacing=3.4)
    p.hatch(home, 45, 3.0, w=0.6, opacity=0.6, tone=radial_tone(home_c, 5.5 * MM, 0, gamma=1.5))
    p.hatch([outer, bezel], 45, 3.2, w=0.6, opacity=0.5, tone=lin_tone((x0, y0), (x0 + W, y0 + H), lo=0.1))

    # the screen, lit, with a glint across it
    p.contour([(sx + 6, sy + 13), (sx + sw - 6, sy + 13)], closed=False, w=0.7, passes=1, opacity=0.6)
    m = (sw - 4 * 44) / 5
    for k, kind in enumerate(GRID):
        col, row = k % 4, k // 4
        _icon(p, kind, sx + m + 22 + col * (44 + m), sy + 48 + row * 76)
    dock = [(sx, sy + sh - 78), (sx + sw, sy + sh - 78), (sx + sw, sy + sh), (sx, sy + sh)]
    p.contour([dock[0], dock[1]], closed=False, w=0.9, passes=1, opacity=0.7)
    p.hatch(dock, 45, 4.2, w=0.6, opacity=0.5, tone=lambda q: 0.0 if 20 < (q[0] - sx) - (q[1] - sy) * 0.6 + 120 < 60 else 0.45)
    for k, kind in enumerate(DOCK):
        _icon(p, kind, sx + m + 22 + k * (44 + m), sy + sh - 43, label=False)
    p.hatch(screen, 45, 6.0, w=0.5, opacity=0.35,
            tone=lambda q: 0.0 if -60 < (q[0] - sx) - (q[1] - sy) * 0.6 < 30 or (q[1] > sy + sh - 78) else 0.25)

    # red chalk: centre line and a scale of centimetres down the side
    p.chalk_line((x0 + W / 2, y0 - 25), (x0 + W / 2, y0 + H + 25), dash="6 5")
    p.chalk_line((x0 - 34, y0), (x0 - 34, y0 + H), overshoot=0, opacity=0.6)
    for k in range(12):
        y = y0 + k * 10 * MM
        if y <= y0 + H:
            p.chalk_line((x0 - 34, y), (x0 - 26 if k % 5 else x0 - 20, y), overshoot=0, opacity=0.6)
    return home_c


def _side(p: Page, x0, y0):
    W, H = 11.6 * MM, 115 * MM
    body = rrect_pts(x0, y0, W, H, 26)
    p.contour(body, w=2.0, ghosts=1)
    p.contour([(x0 + 7, y0 + 18), (x0 + 7, y0 + H - 18)], closed=False, w=0.9, passes=1, opacity=0.7)
    switch = rrect_pts(x0 + W / 2 - 7, y0 + 72, 14, 24, 4)
    rocker = rrect_pts(x0 + W / 2 - 8, y0 + 122, 16, 84, 8)
    for part in (switch, rocker):
        p.contour(part, w=1.3, passes=1)
        p.shade(part, form_tone(part, rim=5, base=0.1), spacing=2.4)
    p.contour([(x0 + W / 2 - 6, y0 + 164), (x0 + W / 2 + 6, y0 + 164)], closed=False, w=0.8, passes=1)
    p.shade(body, lin_tone((x0, 0), (x0 + W, 0), gamma=1.6, lo=0.05), spacing=3.2)


def _back(p: Page, x0, y0, s=2.6):
    W, H, R = 61 * s, 115 * s, 9 * s
    shell = rrect_pts(x0, y0, W, H, R)
    strip = [(x0, y0 + 95 * s), (x0 + W, y0 + 95 * s)] + [q for q in shell if q[1] > y0 + 95 * s]
    lens = ellipse_pts(x0 + 9 * s, y0 + 9 * s, 3.2 * s, 3.2 * s)
    p.contour(shell, w=1.8, ghosts=1)
    p.contour([(x0, y0 + 95 * s), (x0 + W, y0 + 95 * s)], closed=False, w=1.2, passes=1)
    p.contour(lens, w=1.3)
    p.contour(ellipse_pts(x0 + 9 * s, y0 + 9 * s, 1.4 * s, 1.4 * s), w=0.9, passes=1)
    p.hatch(lens, 45, 2.2, w=0.6, opacity=0.8)
    p.hatch(shell, 0, 5.5, w=0.5, opacity=0.35, tone=lambda q: 0.0 if q[1] > y0 + 95 * s else 0.5)
    p.shade(shell, form_tone(shell, rim=18, base=0.0), spacing=3.4)
    p.shade(strip, lambda q: 0.85, spacing=2.6)


def _exploded(p: Page):
    s, OX, gap = 2.6, 1290, 112
    W, H, R = 61 * s, 115 * s, 9 * s

    def iso(pts, oy):
        return [(OX + (x - y) * 0.866, oy + (x + y) * 0.5) for x, y in pts]

    layers = [
        ("glass", 4), ("display", 6), ("board", 6), ("battery", 10), ("back", 12),
    ]
    tops, occluders = [], []
    label_pts = []
    for k, (name, t) in enumerate(layers):
        oy = 330 + k * gap
        if name == "glass":
            plan = rrect_pts(0, 0, W, H, R)
        elif name == "display":
            plan = rrect_pts(4.5 * s, 18 * s, 52 * s, 79 * s, 3)
        elif name == "board":
            plan = rrect_pts(2 * s, 2 * s, 57 * s, 111 * s, R - 2)
        elif name == "battery":
            plan = rrect_pts(6 * s, 52 * s, 49 * s, 56 * s, 6)
        else:
            plan = rrect_pts(0, 0, W, H, R)
        top = iso(plan, oy)
        side = [(x, y + t) for x, y in top]
        slab_edge = _visible(side, [top] + occluders)
        for run in _visible(top, occluders):
            p.contour(run, closed=False, w=1.7, overshoot=1)
        for run in slab_edge:
            p.contour(run, closed=False, w=1.2, passes=1, opacity=0.85)
        p.hatch(side, 45, 2.4, w=0.7, opacity=0.8,
                tone=lambda q, top=top, occ=list(occluders): 0.0 if _inside(q, top) or any(_inside(q, o) for o in occ) else 0.9)

        hidden = list(occluders)
        vis = lambda q, hidden=hidden: not any(_inside(q, o) for o in hidden)  # noqa: E731

        def draw_detail(plan_pts, closed=True, w=1.0, oy=oy, hidden=hidden):
            for run in _visible(iso(plan_pts, oy), hidden, closed):
                p.contour(run, closed=False, w=w, passes=1, opacity=0.85)

        if name == "glass":
            draw_detail(rrect_pts(5.8 * s, 20.5 * s, 49.3 * s, 74 * s, 2))
            draw_detail(ellipse_pts(W / 2, H - 10.5 * s, 5.5 * s, 5.5 * s))
            p.hatch(top, 45, 7.0, w=0.5, opacity=0.4,
                    tone=lambda q, top=top: 0.0 if 30 < (q[0] - OX) - (q[1] - 330) * 0.3 < 90 else 0.3 * vis(q))
        elif name == "display":
            p.shade([top], lambda q: 0.6 * vis(q), spacing=3.4)
            draw_detail([(26 * s, 97 * s), (26 * s, 104 * s), (35 * s, 104 * s), (35 * s, 97 * s)], closed=False)
        elif name == "board":
            draw_detail(rrect_pts(5 * s, 6 * s, 51 * s, 44 * s, 3))
            for (cx, cy, w_, h_) in ((16, 16, 14, 12), (36, 14, 16, 16), (49, 32, 8, 12), (22, 38, 18, 8), (42, 40, 10, 6), (30, 88, 22, 10)):
                chip = rrect_pts((cx - w_ / 2) * s, (cy - h_ / 2) * s, w_ * s, h_ * s, 1)
                draw_detail(chip)
                ch = iso(chip, oy)
                p.hatch(ch, 45, 2.0, w=0.6, opacity=0.75, tone=lambda q: 0.8 * vis(q))
            draw_detail(ellipse_pts(9 * s, 9 * s, 3 * s, 3 * s))
            p.shade([top], lambda q: 0.25 * vis(q), spacing=4.0)
        elif name == "battery":
            draw_detail([(12 * s, 62 * s), (49 * s, 62 * s)], closed=False)
            draw_detail([(12 * s, 66 * s), (40 * s, 66 * s)], closed=False)
            p.shade([top], lambda q: 0.45 * vis(q), spacing=3.4)
        else:
            draw_detail(ellipse_pts(W - 9 * s, 9 * s, 3.2 * s, 3.2 * s))
            band = iso([(0, 95 * s), (W, 95 * s), (W, H), (0, H)], oy)
            p.shade([band], lambda q, top=top: 0.85 * vis(q) * _inside(q, top), spacing=2.6)
            p.shade([top], lambda q: 0.3 * vis(q), spacing=3.8)

        tops.append(top)
        occluders = occluders + [top, side]
        right = max(top, key=lambda q: q[0])
        label_pts.append((1488, oy + W * 0.5 + 8))

    corners = [(0, 0), (W, 0), (W, H), (0, H)]
    for cx, cy in corners:
        x = OX + (cx - cy) * 0.866
        y0 = 330 + (cx + cy) * 0.5
        p.chalk_line((x, y0 - 20), (x, y0 + gap * (len(layers) - 1) + 30), dash="5 6", opacity=0.45)
    for letter, (x, y) in zip("abcde", label_pts):
        p.label(letter, x, y)


def _pinch(p: Page):
    frame = rrect_pts(150, 900, 330, 200, 6)
    p.contour(frame, w=1.4, passes=1)
    for k in range(1, 6):
        p.contour([(150 + k * 55, 902), (150 + k * 55, 1098)], closed=False, w=0.6, passes=1, opacity=0.4)
    for k in range(1, 4):
        p.contour([(152, 900 + k * 50), (478, 900 + k * 50)], closed=False, w=0.6, passes=1, opacity=0.4)
    p.contour([(160, 1080), (230, 1010), (300, 1030), (390, 950), (470, 935)], closed=False, w=1.6, passes=1)
    for (cx, cy), (sx, sy), ang in (((262, 1032), (292, 1012), 30), ((370, 966), (338, 986), 30)):
        for k, r in enumerate((24, 19, 14, 9, 4.5)):
            p.contour(ellipse_pts(cx, cy, r, r * 1.3, ang), w=1.2 if k == 0 else 0.7, passes=1, opacity=0.9 if k == 0 else 0.6)
        p.chalk(ellipse_pts(sx, sy, 22, 28, ang), dash="4 4", opacity=0.55)
        dx, dy = cx - sx, cy - sy
        L = math.hypot(dx, dy)
        tip = (cx + dx / L * 40, cy + dy / L * 40)
        frm = (cx + dx / L * 30, cy + dy / L * 30)
        p.contour([frm, tip], closed=False, w=1.3, passes=1)
        p.arrow_head(tip, frm, size=10, w=1.3)


def folio_iphone() -> Page:
    p = Page(seed=101, folio="")
    home_c = _front(p, 130, 215)
    p.label("g", home_c[0] + 74, home_c[1] + 8)
    p.line((home_c[0] + 34, home_c[1]), (home_c[0] + 52, home_c[1]), w=0.8, opacity=0.6)
    _side(p, 505, 215)
    _back(p, 655, 420)
    _exploded(p)
    _pinch(p)

    p.title("Della tavoletta che parla", 600, 110)
    p.note([
        "in questa tavoletta di vetro",
        "sta il telefono e la musica",
        "e tutte le lettere del mondo",
        "si comanda col dito sanza tasti",
    ], 965, 228)
    p.note([
        "a. il vetro che sente il tocco",
        "b. la finestra della luce",
        "c. il cervello di rame",
        "d. il serbatoio della forza",
        "e. la schiena di metallo",
    ], 1530, 105)
    p.note([
        "due dita che s'allargano",
        "fanno la figura più grande",
        "g. il bottone che riporta a casa",
    ], 960, 930)
    return p
