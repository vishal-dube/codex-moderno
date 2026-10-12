"""Replay a folio stroke by stroke and encode it as an MP4.

Usage: .venv/bin/python animate.py airpods [--seconds 24] [--fps 30]
"""

import argparse
import queue
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import imageio_ffmpeg

from cdp import Chrome
from codex import H, W
from render import OUT, page_for

# px per second: the pen lingers on outlines and writing, and races through hatching.
SPEED = {"ink": 650, "chalk": 1300, "ghost": 2200, "hatch": 5200, "text": 240}
OVERLAP = 0.7      # next mark starts when the previous one is 70% done
LEAD, HOLD = 0.6, 3.5


def schedule(page, seconds):
    marks = sorted(page.marks, key=lambda m: (not m.get("title", False), m["seq"]))
    plan, t = [], 0.0
    for m in marks:
        if m["kind"] == "text":
            v = SPEED["text"]
        elif m["kind"] == "hatch":
            v = SPEED["hatch"]
        elif m["layer"] == "hatch":
            v = SPEED["ghost"]
        else:
            v = SPEED[m["layer"]]
        dur = max(0.04, m["length"] / v)
        plan.append([m["seq"], t, dur])
        t += dur * OVERLAP
    end = max(s + d for _, s, d in plan)
    k = seconds / end
    return [(seq, LEAD + s * k, d * k) for seq, s, d in plan]


def frame_progress(plan, t):
    prog = {}
    for seq, s, d in plan:
        if t >= s + d:
            prog[seq] = 1.0
        elif t > s:
            prog[seq] = (t - s) / d
    return prog


BROWSERS: "queue.Queue[Chrome]" = queue.Queue()


def shoot(args):
    """Screenshot one frame on whichever browser is free; restart it once if it fails."""
    svg_path, png_path = args
    browser = BROWSERS.get()
    try:
        try:
            browser.screenshot(svg_path.as_uri(), png_path)
        except Exception:
            browser.close()
            browser = Chrome(W, H)
            browser.screenshot(svg_path.as_uri(), png_path)
        svg_path.unlink()
    finally:
        BROWSERS.put(browser)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--seconds", type=float, default=24)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    page = page_for(args.name)
    plan = schedule(page, args.seconds)
    draw_frames = int((LEAD + args.seconds) * args.fps) + 1
    hold_frames = int(HOLD * args.fps)

    frames = OUT / f"frames_{args.name}"
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir(parents=True)
    for _ in range(args.workers):
        BROWSERS.put(Chrome(W, H))

    jobs = []
    last_key = None
    copies = []
    for i in range(draw_frames):
        prog = frame_progress(plan, i / args.fps)
        key = tuple(sorted((s, round(p, 3)) for s, p in prog.items()))
        png = frames / f"f_{i:05d}.png"
        if key == last_key:
            copies.append((frames / f"f_{i - 1:05d}.png", png))
            continue
        last_key = key
        svg = frames / f"f_{i:05d}.svg"
        svg.write_text(page.svg(prog))
        jobs.append((svg, png))

    print(f"{len(jobs)} frames to render ({len(copies)} repeated), {len(page.marks)} marks")
    with ThreadPoolExecutor(args.workers) as pool:
        for n, _ in enumerate(pool.map(shoot, jobs), 1):
            if n % 50 == 0:
                print(f"  {n}/{len(jobs)}", flush=True)
    for src, dst in copies:
        shutil.copy(src, dst)
    last = frames / f"f_{draw_frames - 1:05d}.png"
    for j in range(hold_frames):
        shutil.copy(last, frames / f"f_{draw_frames + j:05d}.png")
    while not BROWSERS.empty():
        BROWSERS.get().close()

    mp4 = OUT / f"{args.name}.mp4"
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", str(args.fps),
        "-i", str(frames / "f_%05d.png"), "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4),
    ], check=True)
    print(mp4)


if __name__ == "__main__":
    main()
