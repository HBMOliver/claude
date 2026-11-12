#!/usr/bin/env python3
"""Screenshot and/or print an HTML page with headless Chrome, waiting for web fonts.
Usage: render_page.py page.html --png out.png --size 794x1123 [--scale 2] [--pdf out.pdf]"""
import argparse, os, subprocess, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ap = argparse.ArgumentParser()
ap.add_argument("page"); ap.add_argument("--png"); ap.add_argument("--pdf")
ap.add_argument("--size", default="794x1123"); ap.add_argument("--scale", type=float, default=1.0)
a = ap.parse_args()
url = "file://" + os.path.abspath(a.page)
prof = tempfile.mkdtemp(prefix="page-")
base = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars",
        f"--user-data-dir={prof}", "--virtual-time-budget=15000"]
w, h = a.size.split("x")
if a.png:
    subprocess.run(base + [f"--window-size={w},{h}", f"--force-device-scale-factor={a.scale}", f"--screenshot={os.path.abspath(a.png)}", url],
                   capture_output=True, timeout=180)
    print("wrote", a.png)
if a.pdf:
    subprocess.run(base + ["--no-pdf-header-footer", f"--print-to-pdf={os.path.abspath(a.pdf)}", url], capture_output=True, timeout=180)
    print("wrote", a.pdf)
