"""Publish the built site/ to the gh-pages branch, which GitHub Pages serves.

The site can only be built on a Mac with Chrome (see build.py), so it is
built locally and pushed as a single fresh commit; each publish replaces
the previous one rather than growing the branch's history.

Usage: .venv/bin/python build.py && .venv/bin/python publish.py
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True)


def main():
    if not (SITE / "index.html").exists():
        raise SystemExit("site/ is empty: run build.py first")
    remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, check=True,
                            capture_output=True, text=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="codex-publish-") as tmp:
        dest = Path(tmp) / "site"
        shutil.copytree(SITE, dest)
        (dest / ".nojekyll").touch()  # serve files as-is, no Jekyll processing
        git("init", "-q", "-b", "gh-pages", cwd=dest)
        git("add", "-A", cwd=dest)
        git("commit", "-q", "-m", "Publish site", cwd=dest)
        git("push", "-q", "--force", remote, "gh-pages", cwd=dest)
    print("published to gh-pages")


if __name__ == "__main__":
    main()
