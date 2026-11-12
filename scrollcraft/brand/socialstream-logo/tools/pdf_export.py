#!/usr/bin/env python3
"""Print SVG masters to vector PDFs with headless Chrome (RGB; convert or assign CMYK at the printer).
Usage: pdf_export.py out-dir width_mm file.svg [file.svg ...]"""
import os, re, subprocess, sys, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main():
    out, width_mm, files = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="pdf-")
    for f in files:
        svg = open(f).read()
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
        h_mm = width_mm * vb[3] / vb[2]
        svg = re.sub(r'\swidth="[^"]*"', "", svg, count=1)
        svg = re.sub(r'\sheight="[^"]*"', "", svg, count=1)
        html = (f"<!doctype html><html><head><meta charset='utf-8'><style>@page{{size:{width_mm}mm {h_mm}mm;margin:0}}"
                f"html,body{{margin:0;padding:0}}svg{{display:block;width:{width_mm}mm;height:{h_mm}mm}}</style></head>"
                f"<body>{svg}</body></html>")
        page = os.path.join(tmp, "page.html")
        open(page, "w").write(html)
        pdf = os.path.join(out, os.path.splitext(os.path.basename(f))[0] + ".pdf")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                        f"--user-data-dir={os.path.join(tmp, 'profile')}", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", "file://" + page], capture_output=True, timeout=120)
        print("wrote", pdf, f"({width_mm:g} x {h_mm:.1f} mm)")


if __name__ == "__main__":
    main()
