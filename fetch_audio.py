"""Fetch the codex's recordings from Wikimedia Commons, checking each license first.

Every source is public domain, CC0, or CC BY (attribution only). Nothing
share-alike: syncing music to video counts as an adaptation, and share-alike
would force the videos themselves under that license.

Usage: .venv/bin/python fetch_audio.py      writes audio/<slug>.<ext> and audio/credits.json
"""

from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = "codex-moderno/1.0 (personal art project)"
AUDIO = Path(__file__).resolve().parent / "audio"
ALLOWED = re.compile(r"^(public domain|pdm-owner|cc0|cc by [0-9.]+)$", re.I)

SOURCES = {
    "iphone": ("Kimiko Ishizaka - Bach - Well-Tempered Clavier, Book 1 - 01 Prelude No. 1 in C major, BWV 846.ogg",
               "J. S. Bach, Prelude No. 1 in C major, BWV 846", "Kimiko Ishizaka, piano"),
    "bionic-hand": ("Aaron Dunn - Minuet - Notebook for Anna Magdalena.ogg",
                    "Christian Petzold, Minuet in G major, BWV Anh. 114", "Aaron Dunn, piano (Musopen)"),
    "atlas-detector": ("Bach, Toccata und Fuge d-moll BWV 565, Norbert Schenk.mp3",
                       "J. S. Bach (attr.), Toccata in D minor, BWV 565", "Norbert Schenk, organ"),
    "sky-crane": ("Ludwig van Beethoven - symphony no. 5 in c minor, op. 67 - i. allegro con brio.ogg",
                  "Beethoven, Symphony No. 5, I. Allegro con brio", "Musopen"),
    "humanoid-robot": ("Kimiko Ishizaka - Bach - Well-Tempered Clavier, Book 1 - 03 Prelude No. 2 in C minor, BWV 847.ogg",
                       "J. S. Bach, Prelude No. 2 in C minor, BWV 847", "Kimiko Ishizaka, piano"),
    "airpods": ("Kevin MacLeod - Canon in D Major.ogg", "Johann Pachelbel, Canon in D", "Kevin MacLeod"),
    "cybertruck": ("FurElise.ogg", "Beethoven, Für Elise", "V. Gao, piano"),
    "quantum-computer": ("Erik Satie - gymnopedies - la 1 ere. lent et douloureux.ogg",
                         "Erik Satie, Gymnopédie No. 1", "Robin Alciatore, piano (Musopen)"),
    "euv-machine": ("Bach, BWV 147, 10. Jesus bleibet meine Freude.ogg",
                    "J. S. Bach, Jesu, Joy of Man's Desiring, BWV 147", "Orchestra Gli Armonici"),
    "ingenuity": ("Mozart - 12 Variations K. 265 - Stefano Ligoratti.mp3",
                  "Mozart, Twelve Variations on 'Ah vous dirai-je, maman', K. 265", "Stefano Ligoratti, piano"),
    "james-webb": ("Ludwig van Beethoven - sonata no. 14 in c sharp minor 'moonlight', op. 27 no. 2 - i. adagio sostenuto.ogg",
                   "Beethoven, 'Moonlight' Sonata, I. Adagio sostenuto", "Paul Pitman, piano (Musopen)"),
    "neuralink": ("Bach Cello Suite 1 Prelude (BWV 1007) Played by Chris.ogg",
                  "J. S. Bach, Cello Suite No. 1, Prelude, BWV 1007", "Chris, cello"),
    "vision-pro": ("Greensleeves. La Juglaresa.opus", "Greensleeves (anonymous, 16th century)",
                   "La Juglaresa / Emilio Villalba"),
    "starship-catch": ("Anthem of Europe (US Navy instrumental long version).ogg",
                       "Beethoven, 'Ode to Joy' (Anthem of Europe)", "United States Navy Band"),
}


def _curl(args):
    return subprocess.run(["curl", "-s", "--max-time", "300", "-H", f"User-Agent: {UA}", *args], capture_output=True)


def _api(params):
    for _ in range(6):
        time.sleep(2.5)
        out = _curl([API + "?" + urllib.parse.urlencode({**params, "format": "json"})]).stdout
        try:
            return json.loads(out)
        except ValueError:
            time.sleep(30)  # rate limited: wait, then retry
    raise RuntimeError("Wikimedia Commons kept refusing requests")


def clean(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", html)).strip()


def main():
    AUDIO.mkdir(exist_ok=True)
    titles = {slug: "File:" + src[0] for slug, src in SOURCES.items()}
    info = {}
    names = list(titles.values())
    for i in range(0, len(names), 5):
        r = _api({"action": "query", "prop": "imageinfo", "iiprop": "url|size|extmetadata", "titles": "|".join(names[i:i + 5])})
        for page in r["query"]["pages"].values():
            if "imageinfo" not in page:
                raise SystemExit(f"not found on Commons: {page['title']}")
            info[page["title"]] = page["imageinfo"][0]
    credits = {}
    for slug, title in titles.items():
        ii = info[title]
        meta = ii["extmetadata"]
        lic = clean(meta.get("LicenseShortName", {}).get("value", ""))
        if not ALLOWED.match(lic):
            raise SystemExit(f"{slug}: license {lic!r} is not public domain, CC0 or CC BY; refusing")
        ext = Path(urllib.parse.urlparse(ii["url"]).path).suffix
        dest = AUDIO / f"{slug}{ext}"
        for attempt in range(4):
            if dest.exists() and dest.stat().st_size == ii["size"]:
                break
            time.sleep(12 if attempt == 0 else 60)
            _curl(["-L", "-o", str(dest), ii["url"]])
        else:
            raise SystemExit(f"{slug}: download failed or incomplete")
        _, piece, performer = SOURCES[slug]
        credits[slug] = {"file": dest.name, "piece": piece, "performer": performer, "license": lic,
                         "license_url": meta.get("LicenseUrl", {}).get("value", ""),
                         "source": ii.get("descriptionurl") or f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title)}"}
        print(f"  {slug:16} {lic:14} {dest.stat().st_size / 1e6:5.1f} MB  {dest.name}")
    (AUDIO / "credits.json").write_text(json.dumps(credits, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
