"""Lay each folio's recording under its self-drawing video.

Takes the opening of the recording (skipping any leading silence), trims it
to the video's length, fades it in and out, normalises loudness for social
video (-16 LUFS), and writes out/<slug>-music.mp4. The silent video is kept.

Usage: .venv/bin/python soundtrack.py [slug ...]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
OUT, AUDIO = ROOT / "out", ROOT / "audio"
LENGTH, FADE_OUT = 28.13, 2.4


def credits() -> dict:
    path = AUDIO / "credits.json"
    return json.loads(path.read_text()) if path.exists() else {}


def score(slug: str, credit: dict) -> Path:
    video, audio = OUT / f"{slug}.mp4", AUDIO / credit["file"]
    dest = OUT / f"{slug}-music.mp4"
    chain = (f"[1:a]silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,"
             f"atrim=0:{LENGTH},asetpts=PTS-STARTPTS,"
             f"afade=t=in:d=0.3,afade=t=out:st={LENGTH - FADE_OUT}:d={FADE_OUT},"
             f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]")
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio),
                    "-filter_complex", chain, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(dest)], check=True)
    return dest


if __name__ == "__main__":
    table = credits()
    for slug in sys.argv[1:] or table:
        print(score(slug, table[slug]))
