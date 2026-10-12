"""Build the Codice Moderno website into site/.

Usage: .venv/bin/python build.py [--render]
  --render   re-render every drawn folio's still first (otherwise reuses out/)
"""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
from pathlib import Path

from catalog import CATALOG, Folio, folio_label, make_page
from soundtrack import credits as music_credits
from render import OUT, render

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
WEB = ROOT / "web"
SITE_URL = "https://vishal-dube.github.io/codex-moderno"  # enables link previews on X

FONTS = ("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500"
         "&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def resize(src: Path, dst: Path, px: int, quality: int):
    subprocess.run(["sips", "-Z", str(px), "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
                    str(src), "--out", str(dst)], check=True, capture_output=True)


def page_lines(slug: str, notes: dict[str, str]) -> list[tuple[str, str]]:
    """Every mirrored Italian line on the page, in drawing order, with its translation."""
    page = make_page(slug)
    lines = [m["s"] for m in sorted(page.marks, key=lambda m: (not m.get("title"), m["seq"]))
             if m["kind"] == "text" and len(m["s"]) > 2]
    missing = [s for s in lines if s not in notes]
    if missing:
        raise SystemExit(f"{slug}: untranslated lines: {missing}")
    return [(s, notes[s]) for s in lines]


def head(title: str, description: str, depth: int, image: str | None = None) -> str:
    up = "../" * depth
    og = ""
    if SITE_URL and image:
        og = (f'<meta property="og:title" content="{esc(title)}">'
              f'<meta property="og:description" content="{esc(description)}">'
              f'<meta property="og:image" content="{SITE_URL}/{image}">'
              f'<meta name="twitter:card" content="summary_large_image">')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{og}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{up}style.css">
</head>
<body>"""


FOOT = """<footer class="foot">
<p>Every line in this codex is drawn by code with Claude. The mirror-written Italian is original,
composed in Leonardo's manner; each folio carries a translation.</p>
</footer>
</body>
</html>"""


def card(i: int, f: Folio, title_it: str | None) -> str:
    label = f"{folio_label(i)} · {f.year}"
    return f"""<li class="card">
<a href="{f.slug}/">
<img src="{f.slug}/thumb.jpg" alt="{esc(f.name)}, drawn as a page from Leonardo da Vinci's notebooks" loading="lazy" width="900" height="675">
<div class="cap"><p class="num">{label}</p><h2>{esc(f.name)}</h2><p class="it">{esc(title_it or "")}</p></div>
</a>
</li>"""


def music_credit(slug: str) -> str:
    c = music_credits().get(slug)
    if not c or not (OUT / f"{slug}-music.mp4").exists():
        return ""
    lic = esc(c["license"])
    if c.get("license_url"):
        lic = f'<a href="{esc(c["license_url"])}">{lic}</a>'
    return (f'<p class="music">Music: {esc(c["piece"])}, performed by {esc(c["performer"])}. '
            f'{lic}, <a href="{esc(c["source"])}">via Wikimedia Commons</a>.</p>')


def folio_page(i: int, f: Folio, lines: list[tuple[str, str]], has_video: bool,
               prev: tuple[int, Folio] | None, nxt: tuple[int, Folio] | None) -> str:
    title_it, title_en = lines[0]
    notes = "\n".join(f'<li><p class="it">{esc(it)}</p><p class="en">{esc(en)}</p></li>' for it, en in lines[1:])
    alt = f"{f.name}, drawn as a page from Leonardo da Vinci's notebooks"
    if has_video:
        media = (f'<video controls playsinline preload="none" poster="web.jpg" aria-label="{esc(alt)}, drawing itself">'
                 f'<source src="drawing.mp4" type="video/mp4"></video>')
        actions = '<p class="hint">Press play to watch the page draw itself, with sound.</p>'
    else:
        media = f'<img src="web.jpg" alt="{esc(alt)}" width="1800" height="1350">'
        actions = ""

    def link(n, rel):
        if not n:
            return "<span></span>"
        j, g = n
        arrow = "←" if rel == "prev" else "→"
        text = f"{arrow} {folio_label(j)} {esc(g.name)}" if rel == "prev" else f"{folio_label(j)} {esc(g.name)} {arrow}"
        return f'<a rel="{rel}" href="../{g.slug}/">{text}</a>'

    return f"""{head(f"{f.name} · Codice Moderno", f.summary, 1, f"{f.slug}/web.jpg")}
<nav class="top"><a href="../">Codice Moderno</a><span>{folio_label(i)} of {len(CATALOG)}</span></nav>
<main class="folio">
<header class="folio-head">
<p class="num">{folio_label(i)} · {f.year} · {esc(f.maker)}</p>
<h1>{esc(f.name)}</h1>
<p class="title-it"><span class="mirror" title="{esc(title_it)}">{esc(title_it)}</span><span class="en">{esc(title_en)}</span></p>
</header>
<figure class="plate">{media}
<figcaption>{actions}<a href="full.jpg">Open full resolution</a></figcaption>
</figure>
<section class="text">
<div class="about"><h2>The invention</h2><p>{esc(f.summary)}</p>{music_credit(f.slug)}</div>
<div class="notes"><h2>The notes, translated</h2><ol>{notes}</ol></div>
</section>
<nav class="pager">{link(prev, "prev")}{link(nxt, "next")}</nav>
</main>
{FOOT}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    args = ap.parse_args()

    shutil.rmtree(SITE, ignore_errors=True)
    SITE.mkdir()
    shutil.copy(WEB / "style.css", SITE / "style.css")

    drawn = [(i, f) for i, f in enumerate(CATALOG) if f.draw]
    titles = {}
    for k, (i, f) in enumerate(drawn):
        jpg = OUT / f"{f.slug}.jpg"
        if args.render or not jpg.exists():
            render(f.slug)
        lines = page_lines(f.slug, f.notes)
        titles[f.slug] = lines[0][0]
        d = SITE / f.slug
        d.mkdir()
        shutil.copy(jpg, d / "full.jpg")
        resize(jpg, d / "web.jpg", 1800, 82)
        resize(jpg, d / "thumb.jpg", 900, 78)
        mp4 = OUT / f"{f.slug}-music.mp4"
        if not mp4.exists():
            mp4 = OUT / f"{f.slug}.mp4"
        if mp4.exists():
            shutil.copy(mp4, d / "drawing.mp4")
        prev = drawn[k - 1] if k > 0 else None
        nxt = drawn[k + 1] if k + 1 < len(drawn) else None
        (d / "index.html").write_text(folio_page(i, f, lines, mp4.exists(), prev, nxt))
        print(f"  {folio_label(i)} {f.name}")

    cards = "\n".join(card(i, f, titles[f.slug]) for i, f in drawn)
    pending = "\n".join(f'<li><span class="num">{folio_label(i)}</span> {esc(f.name)} <span class="year">{f.year}</span></li>'
                        for i, f in enumerate(CATALOG) if not f.draw)
    forthcoming = (f'<section class="forthcoming"><h2>In preparazione</h2><p>Folios still being drawn.</p>'
                   f'<ul>{pending}</ul></section>') if pending else ""
    index = f"""{head("Codice Moderno", "The greatest inventions of the 21st century, drawn as pages from Leonardo da Vinci's notebooks.", 0, f"{drawn[0][1].slug}/web.jpg" if drawn else None)}
<header class="masthead">
<p class="eyebrow">A notebook of the twenty-first century</p>
<h1>Codice Moderno</h1>
<p class="lede">The greatest inventions of our century, drawn as Leonardo da Vinci might have drawn them:
iron-gall ink and red chalk, hatched shadows, and notes in mirror writing.</p>
<p class="count">{len(drawn)} of {len(CATALOG)} folios drawn</p>
</header>
<main><ol class="folios">
{cards}
</ol>
{forthcoming}</main>
{FOOT}"""
    (SITE / "index.html").write_text(index)
    print(f"built {SITE} ({len(drawn)} folios drawn)")


if __name__ == "__main__":
    main()
