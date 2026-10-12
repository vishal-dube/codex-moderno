"""A long-lived headless Chrome driven over the DevTools protocol.

Launching Chrome once per frame costs seconds and occasionally stalls; one
browser that navigates to each frame and screenshots it is much faster.
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class Chrome:
    def __init__(self, width: int, height: int, scale: float = 1):
        self.w, self.h, self.scale = width, height, scale
        self.profile = tempfile.mkdtemp(prefix="codex-cdp-")
        self.proc = subprocess.Popen([
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--remote-debugging-port=0",
            f"--user-data-dir={self.profile}", "--no-first-run", "--no-default-browser-check",
            "--disable-extensions", "--disable-background-networking", "--disable-component-update",
            "--disable-sync", "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port_file = Path(self.profile) / "DevToolsActivePort"
        deadline = time.time() + 30
        while not (port_file.exists() and port_file.read_text().strip()):
            if time.time() > deadline:
                self.close()
                raise RuntimeError("headless Chrome did not start")
            time.sleep(0.1)
        port = int(port_file.read_text().splitlines()[0])
        targets = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list").read())
        page = next(t for t in targets if t["type"] == "page")
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=90, suppress_origin=True)
        self._id = 0
        self._loaded = False
        self.call("Page.enable")
        self.call("Emulation.setDeviceMetricsOverride", width=width, height=height,
                  deviceScaleFactor=scale, mobile=False)

    def _handle(self, msg):
        if msg.get("method") == "Page.loadEventFired":
            self._loaded = True

    def call(self, method, **params):
        self._id += 1
        self.ws.send(json.dumps({"id": self._id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self._id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
            self._handle(msg)

    def screenshot(self, url: str, png_path: Path):
        self._loaded = False
        self.call("Page.navigate", url=url)
        while not self._loaded:
            self._handle(json.loads(self.ws.recv()))
        result = self.call("Page.captureScreenshot", format="png",
                           clip={"x": 0, "y": 0, "width": self.w, "height": self.h, "scale": 1})
        png_path.write_bytes(base64.b64decode(result["data"]))

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        shutil.rmtree(self.profile, ignore_errors=True)
