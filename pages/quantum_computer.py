"""f. 8r — the quantum computer (Google Sycamore, 2019): the cold chandelier and its 54-qubit chip."""

from __future__ import annotations

import math

from codex import Page, ellipse_pts, form_tone, lin_tone, rrect_pts

LIGHT = (-1.0, -1.2)
CX = 560
PLATES = [(230, 262), (380, 226), (520, 192), (650, 158), (770, 124), (880, 92)]  # (y, radius)
TILT = 0.2   # how flat the plates look: ry = TILT * rx
THICK = 13


def _plate(p: Page, y, r):
    top = ellipse_pts(CX, y, r, r * TILT)
    front = ellipse_pts(CX, y, r, r * TILT, 0, 0, 180)
    band = ellipse_pts(CX, y, r, r * TILT, 0, 0, 180) + \
        [(x, yy + THICK) for x, yy in ellipse_pts(CX, y, r, r * TILT, 0, 0, 180)][::-1]
    p.contour(top, w=1.9, ghosts=1)
    p.contour([(x, yy + THICK) for x, yy in front], closed=False, w=1.6)
    p.contour([(CX - r, y), (CX - r, y + THICK)], closed=False, w=1.3, passes=1)
    p.contour([(CX + r, y), (CX + r, y + THICK)], closed=False, w=1.3, passes=1)
    p.shade(band, lin_tone((CX - r, 0), (CX + r, 0), gamma=1.3, lo=0.35), spacing=2.6)
    p.hatch(top, 45, 4.0, w=0.55, opacity=0.4, tone=lambda q: 0.0 if abs(q[0] - CX + r * 0.25) < r * 0.18 else 0.35)
    for k in range(10):
        a = math.radians(200 + k * 14)
        hx, hy = CX + r * 0.72 * math.cos(a), y + r * TILT * 0.72 * math.sin(a)
        p.contour(ellipse_pts(hx, hy, 4.5, 1.6), w=0.8, passes=1, opacity=0.8)
    return top, band


def _cables(p: Page, rng):
    for i in range(len(PLATES) - 1):
        (y0, r0), (y1, r1) = PLATES[i], PLATES[i + 1]
        for k in range(9):
            f = (k - 4) / 4.6
            x0 = CX + f * r1 * 0.78
            ys = y0 + THICK + r0 * TILT * 0.55
            ye = y1 + r1 * TILT * 0.55 * math.sqrt(max(0.0, 1 - (f * 0.78) ** 2))
            pts = []
            loop = rng.random() < 0.35 and ye - ys > 90
            for j in range(26):
                t = j / 25
                y = ys + (ye - ys) * t
                x = x0 + math.sin(t * math.pi * 2 + k) * 4
                pts.append((x, y))
            if loop:
                mid = len(pts) // 2
                cx_, cy_ = pts[mid]
                coil = []
                for j in range(40):
                    a = 2 * math.pi * 2.2 * j / 39
                    coil.append((cx_ + 11 * math.sin(a), cy_ - 18 + 36 * j / 39 + 6 * math.cos(a)))
                pts = pts[:mid - 4] + coil + pts[mid + 4:]
            p.contour(pts, closed=False, w=0.8, passes=1, opacity=0.75)
        for f in (-0.86, 0.86):
            xa = CX + f * r1
            p.contour([(xa, y0 + THICK + 6), (xa, y1 + r1 * TILT * 0.4)], closed=False, w=2.6, passes=1, opacity=0.9)
            p.contour([(xa + 5 * (1 if f > 0 else -1), y0 + THICK + 6), (xa + 5 * (1 if f > 0 else -1), y1 + r1 * TILT * 0.4)],
                      closed=False, w=0.8, passes=1, opacity=0.6)


def _chandelier(p: Page):
    _cables(p, p.rng)
    for y, r in PLATES:
        _plate(p, y, r)
    y, r = PLATES[-1]
    pkg = rrect_pts(CX - 34, y + THICK + 6, 68, 90, 6)
    p.contour(pkg, w=1.8)
    p.shade(pkg, form_tone(pkg, LIGHT, rim=12, base=0.15), spacing=2.8)
    p.contour([(CX - 30, y + THICK + 60), (CX + 30, y + THICK + 60)], closed=False, w=0.9, passes=1)
    for x in range(-24, 25, 8):
        p.contour([(CX + x, y + THICK + 96), (CX + x, y + THICK + 104)], closed=False, w=0.9, passes=1)
    p.contour([(CX - 300, 216), (CX + 300, 216)], closed=False, w=1.0, passes=1, opacity=0.5)
    for x in (CX - 220, CX + 220):
        p.contour([(x, 160), (x, 216)], closed=False, w=2.4, passes=1)
    # a scale of cold down the side, one mark per plate
    p.chalk_line((210, 220), (210, 900), overshoot=0, opacity=0.6)
    for y, _ in PLATES:
        p.chalk_line((200, y + 6), (220, y + 6), overshoot=0, opacity=0.7)
    p.chalk(ellipse_pts(210, 925, 12, 12), opacity=0.7)
    p.label("a", CX - PLATES[1][1] - 22, PLATES[1][0] + 14)
    p.label("b", CX + 120, 455)
    p.label("e", CX - PLATES[-1][1] - 24, PLATES[-1][0] + 14)


def _chip(p: Page, x0=1110, y0=230, size=300):
    die = rrect_pts(x0, y0, size, size, 4)
    p.contour(die, w=2.0, ghosts=1)
    inner = rrect_pts(x0 + 26, y0 + 26, size - 52, size - 52, 2)
    p.contour(inner, w=0.9, passes=1, opacity=0.7)
    for k in range(10):
        tx = x0 + 34 + k * (size - 68) / 9
        ty = y0 + 34 + k * (size - 68) / 9
        for pad in (rrect_pts(tx - 5, y0 + 6, 10, 12, 1), rrect_pts(tx - 5, y0 + size - 18, 10, 12, 1),
                    rrect_pts(x0 + 6, ty - 5, 12, 10, 1), rrect_pts(x0 + size - 18, ty - 5, 12, 10, 1)):
            p.contour(pad, w=0.8, passes=1)
            p.hatch(pad, 45, 2.0, w=0.6, opacity=0.8)
    p.hatch([die, inner], 45, 3.0, w=0.55, opacity=0.5)
    cx, cy = x0 + size / 2, y0 + size / 2
    qubits = []
    for j in range(6):
        for i in range(9):
            u, v = (i - 4) * 26, (j - 2.5) * 38 + (13 if i % 2 else -6)
            qubits.append((cx + u * 0.98, cy + v * 0.9))
    for k, (qx, qy) in enumerate(qubits):
        for (ax, ay), (bx, by) in (((qx - 9, qy), (qx + 9, qy)), ((qx, qy - 9), (qx, qy + 9))):
            p.contour([(ax, ay), (bx, by)], closed=False, w=2.6, passes=1, opacity=0.9)
        if k + 9 < len(qubits):
            nx, ny = qubits[k + 9]
            p.contour([(qx, qy + 10), (nx, ny - 10)], closed=False, w=0.6, passes=1, opacity=0.6)
        if (k + 1) % 9 and k + 1 < len(qubits):
            nx, ny = qubits[k + 1]
            p.contour([(qx + 10, qy), (nx - 10, ny)], closed=False, w=0.6, passes=1, opacity=0.6)
    dead = qubits[4]
    p.contour(ellipse_pts(*dead, 15, 15), w=1.2, passes=1)
    for d in ((-1, -1), (1, -1)):
        p.contour([(dead[0] - 14 * d[0], dead[1] - 14), (dead[0] + 14 * d[0], dead[1] + 14)], closed=False, w=1.0, passes=1)
    p.label("d", dead[0] + 8, y0 - 14)
    p.label("c", x0 + size + 34, y0 + size / 2)
    # magnified from the package at the bottom of the chandelier
    y, _ = PLATES[-1]
    for (ax, ay), (bx, by) in (((CX + 34, y + 30), (x0, y0)), ((CX + 34, y + 110), (x0, y0 + size))):
        p.chalk_line((ax, ay), (bx, by), dash="5 6", opacity=0.5, overshoot=0)


def folio_quantum_computer() -> Page:
    p = Page(seed=808, folio="")
    _chandelier(p)
    _chip(p)

    p.title("Della lumiera fredda che pensa", 760, 110)
    p.note([
        "questa lumiera non fa lume",
        "ma pensa nel freddo",
        "più freddo che lo spazio tra le stelle",
    ], 1530, 620)
    p.note([
        "a. ogni piatto è più freddo di quello di sopra",
        "b. li fili d'oro portano le voci",
        "c. la pietra che pensa con cinquantatré spiriti",
        "d. uno de' cinquantaquattro è morto",
        "e. qui è più freddo che la notte del cielo",
    ], 1530, 800)
    return p


NOTES = {
    "Della lumiera fredda che pensa": "Of the cold chandelier that thinks",
    "questa lumiera non fa lume": "this chandelier gives no light",
    "ma pensa nel freddo": "but thinks in the cold",
    "più freddo che lo spazio tra le stelle": "colder than the space between the stars",
    "a. ogni piatto è più freddo di quello di sopra": "a. each plate is colder than the one above",
    "b. li fili d'oro portano le voci": "b. the golden threads carry the voices",
    "c. la pietra che pensa con cinquantatré spiriti": "c. the stone that thinks with fifty-three spirits",
    "d. uno de' cinquantaquattro è morto": "d. one of the fifty-four is dead",
    "e. qui è più freddo che la notte del cielo": "e. here it is colder than the night of the sky",
}
