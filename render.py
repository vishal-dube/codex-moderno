"""Render folios to SVG, then to a 2x PNG and a postable JPEG via headless Chrome.

Usage: python3 render.py [name ...]   (no names = all folios)
"""

import subprocess
import sys
from pathlib import Path

from codex import W, H
from folios import FOLIOS

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = Path(__file__).resolve().parent / "out"


def render(name: str) -> Path:
    OUT.mkdir(exist_ok=True)
    svg = OUT / f"{name}.svg"
    png = OUT / f"{name}.png"
    jpg = OUT / f"{name}.jpg"
    svg.write_text(FOLIOS[name]().svg())
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2", f"--window-size={W},{H}",
        f"--screenshot={png}", svg.as_uri(),
    ], check=True, capture_output=True)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "88", str(png), "--out", str(jpg)],
                   check=True, capture_output=True)
    return jpg


if __name__ == "__main__":
    for n in sys.argv[1:] or FOLIOS:
        print(render(n))
