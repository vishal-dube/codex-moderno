"""Render folios to SVG, then to a 2x PNG and a postable JPEG via headless Chrome.

Usage: python3 render.py [name ...]   (no names = all folios)
"""

import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from codex import W, H
from catalog import by_slug, drawn, make_page
from folios import FOLIOS

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = Path(__file__).resolve().parent / "out"


def page_for(name: str):
    """Catalog folios get their numbered label; extras (like the skateboard) render as drawn."""
    try:
        by_slug(name)
    except KeyError:
        return FOLIOS[name]()
    return make_page(name)


def chrome_screenshot(svg_path: Path, png_path: Path, profile: str, scale: int = 2) -> bool:
    """Screenshot an SVG with headless Chrome. Chrome sometimes lingers after writing
    the file, so stop it as soon as the PNG stops growing."""
    if png_path.exists():
        png_path.unlink()
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
        "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--disable-background-networking",
        "--disable-component-update", "--disable-sync",
        f"--force-device-scale-factor={scale}", f"--window-size={W},{H}", f"--screenshot={png_path}", svg_path.as_uri(),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size, deadline = -1, time.time() + 90
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        if png_path.exists():
            cur = png_path.stat().st_size
            if cur > 0 and cur == size:
                break
            size = cur
        time.sleep(0.25)
    if proc.poll() is None:
        proc.kill()
        proc.wait()
    return png_path.exists() and png_path.stat().st_size > 0


def render(name: str) -> Path:
    OUT.mkdir(exist_ok=True)
    svg = OUT / f"{name}.svg"
    png = OUT / f"{name}.png"
    jpg = OUT / f"{name}.jpg"
    svg.write_text(page_for(name).svg())
    profile = tempfile.mkdtemp(prefix="codex-chrome-")
    try:
        if not any(chrome_screenshot(svg, png, profile, scale=2) for _ in range(3)):
            raise RuntimeError(f"Chrome produced no image for {name}")
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "88", str(png), "--out", str(jpg)],
                   check=True, capture_output=True)
    return jpg


if __name__ == "__main__":
    for n in sys.argv[1:] or drawn():
        print(render(n))
