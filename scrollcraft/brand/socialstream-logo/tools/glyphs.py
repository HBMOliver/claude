#!/usr/bin/env python3
"""Turn text runs into SVG outline paths by printing them with headless Chrome and reading the PDF.

Chrome's PDF backend (Skia) writes variable fonts as Type 3 fonts whose glyph procedures are plain
path operators, so every glyph comes out as exact vector outlines of the instance Chrome rendered
(same weight / optical size / italic as on the web pages).

Usage: glyphs.py spec.json out.json
spec = {"runs": [{"id": "social", "text": "Social", "family": "Fraunces", "italic": false,
                  "axes": {"opsz": 144, "wght": 400}, "size": 1000}, ...],
        "css": "<extra @import / @font-face css>"}
Output: {"runs": {id: {"size":…, "baseline": y, "glyphs": [{"ch": "S", "x": …, "adv": …, "d": "M… Z"}]}}}
Coordinates are CSS px, y down, origin at the run's own start point (x = 0 at the first glyph origin,
y = 0 on the baseline).
"""
import json, os, re, subprocess, sys, tempfile, zlib

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def build_html(spec):
    css = spec.get("css", "")
    rows = []
    for r in spec["runs"]:
        axes = ", ".join(f"'{k}' {v}" for k, v in r.get("axes", {}).items())
        style = (f"font-family:'{r['family']}';font-size:{r.get('size', 1000)}px;"
                 f"font-style:{'italic' if r.get('italic') else 'normal'};"
                 f"font-variation-settings:{axes or 'normal'};"
                 f"font-optical-sizing:none;font-kerning:normal;letter-spacing:0;"
                 f"white-space:nowrap;line-height:1.6;padding:0 100px")
        txt = r["text"].replace("&", "&amp;").replace("<", "&lt;")
        rows.append(f'<div style="{style}">{txt}</div>')
    return ("<!doctype html><html><head><meta charset='utf-8'><style>"
            + css + "@page{size:9000px 12000px;margin:0}body{margin:0}</style></head><body>"
            + "".join(rows) + "</body></html>")


def pdf_objects(data):
    objs = {}
    for m in re.finditer(rb"(\d+)\s+0\s+obj(.*?)endobj", data, re.S):
        objs[int(m.group(1))] = m.group(2)
    return objs


def stream_of(body):
    s = body.split(b"stream", 1)[1].lstrip(b"\r\n").rsplit(b"endstream", 1)[0]
    return zlib.decompress(s) if b"/FlateDecode" in body.split(b"stream", 1)[0] else s


NUM = rb"[-+]?(?:\d+\.?\d*|\.\d+)"


def glyph_path(proc, fm, size, ox, oy):
    """Convert a Type 3 glyph procedure to absolute SVG path data placed at (ox, oy)."""
    sx, sy = fm[0] * size, -fm[3] * size  # y already points down in glyph space
    toks = re.findall(rb"%s|[A-Za-z*]+" % NUM, proc)
    st, out, cur = [], [], None
    P = lambda x, y: f"{ox + float(x) * sx:.2f} {oy + float(y) * sy:.2f}"
    for t in toks:
        if re.fullmatch(NUM, t):
            st.append(t)
            continue
        op = t.decode()
        if op == "m":
            out.append("M" + P(*st[-2:])); cur = st[-2:]
        elif op == "l":
            out.append("L" + P(*st[-2:])); cur = st[-2:]
        elif op == "c":
            a = st[-6:]
            out.append("C" + P(a[0], a[1]) + " " + P(a[2], a[3]) + " " + P(a[4], a[5])); cur = a[4:6]
        elif op == "v":
            a = st[-4:]
            out.append("C" + P(*cur) + " " + P(a[0], a[1]) + " " + P(a[2], a[3])); cur = a[2:4]
        elif op == "y":
            a = st[-4:]
            out.append("C" + P(a[0], a[1]) + " " + P(a[2], a[3]) + " " + P(a[2], a[3])); cur = a[2:4]
        elif op == "h":
            out.append("Z")
        elif op == "re":
            x, y, w, h = [float(v) for v in st[-4:]]
            out.append("M" + P(x, y) + "L" + P(x + w, y) + "L" + P(x + w, y + h) + "L" + P(x, y + h) + "Z")
        st = []
    return "".join(out)


def parse(pdf):
    data = open(pdf, "rb").read()
    objs = pdf_objects(data)
    page = next(b for b in objs.values() if re.search(rb"/Type\s*/Page(?![s\w])", b))
    fonts = dict((n.decode(), int(o)) for n, o in re.findall(rb"/(F\d+)\s+(\d+)\s+0\s+R", page.split(b"/Font", 1)[1].split(b">>", 1)[0]))
    content = stream_of(objs[int(re.search(rb"/Contents\s+(\d+)", page).group(1))])
    finfo = {}
    for name, on in fonts.items():
        fb = objs[on]
        fm = [float(v) for v in re.search(rb"/FontMatrix\s*\[([^\]]+)\]", fb).group(1).split()]
        diffs = re.search(rb"/Differences\s*\[([^\]]+)\]", fb).group(1)
        code, enc = 0, {}
        for t in re.findall(rb"\d+|/[\w.]+", diffs):
            if t.startswith(b"/"):
                enc[code] = t[1:].decode(); code += 1
            else:
                code = int(t)
        cp = re.search(rb"/CharProcs\s*(\d+\s+0\s+R|<<.*?>>)", fb, re.S).group(1)
        if cp.endswith(b"R"):
            cp = objs[int(cp.split()[0])]
        procs = {n.decode(): int(o) for n, o in re.findall(rb"/([\w.]+)\s+(\d+)\s+0\s+R", cp)}
        tu = re.search(rb"/ToUnicode\s+(\d+)", fb)
        uni = {}
        if tu:
            cm = stream_of(objs[int(tu.group(1))])
            for blk in re.findall(rb"beginbfchar(.*?)endbfchar", cm, re.S):
                for a, b in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
                    uni[int(a, 16)] = bytes.fromhex(b.decode()).decode("utf-16-be", "replace")
            for blk in re.findall(rb"beginbfrange(.*?)endbfrange", cm, re.S):
                for a, b, c in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
                    for k in range(int(a, 16), int(b, 16) + 1):
                        uni[k] = chr(int(c, 16) + k - int(a, 16))
        desc = re.search(rb"/FontDescriptor\s+(\d+)", fb)
        fname = re.search(rb"/FontName\s*/([\w+\-]+)", objs[int(desc.group(1))]).group(1).decode() if desc else name
        finfo[name] = dict(fm=fm, enc=enc, procs=procs, uni=uni, fname=fname)
    # walk text objects
    runs = []
    for bt in re.findall(rb"BT(.*?)ET", content, re.S):
        font, size, tlm, glyphs = None, None, None, []
        toks = re.findall(rb"<[0-9A-Fa-f]*>|\[[^\]]*\]|/[\w]+|%s|[A-Za-z*']+" % NUM, bt)
        st = []
        for t in toks:
            if t.startswith(b"<") or t.startswith(b"[") or t.startswith(b"/") or re.fullmatch(NUM, t):
                st.append(t); continue
            op = t.decode()
            if op == "Tf":
                font, size = st[-2][1:].decode(), float(st[-1])
            elif op == "Tm":
                a, b, c, d, e, f = [float(v) for v in st[-6:]]
                tlm = [e, f]; cur = tlm[:]
            elif op == "Td":
                tlm = [tlm[0] + float(st[-2]), tlm[1] - float(st[-1])]; cur = tlm[:]
            elif op == "Tj":
                hexs = st[-1][1:-1].decode()
                for i in range(0, len(hexs), 2):
                    g = int(hexs[i:i + 2], 16)
                    glyphs.append((font, size, g, cur[0], cur[1]))
                    w = re.search(rb"/Widths\s*\[([^\]]+)\]", objs[fonts[font]]).group(1).split()
                    fc = int(re.search(rb"/FirstChar\s+(\d+)", objs[fonts[font]]).group(1))
                    cur = [cur[0] + float(w[g - fc]) * finfo[font]["fm"][0] * size, cur[1]]
            elif op == "TJ":
                for part in re.findall(rb"<[0-9A-Fa-f]*>|%s" % NUM, st[-1]):
                    if part.startswith(b"<"):
                        hexs = part[1:-1].decode()
                        for i in range(0, len(hexs), 2):
                            g = int(hexs[i:i + 2], 16)
                            glyphs.append((font, size, g, cur[0], cur[1]))
                            w = re.search(rb"/Widths\s*\[([^\]]+)\]", objs[fonts[font]]).group(1).split()
                            fc = int(re.search(rb"/FirstChar\s+(\d+)", objs[fonts[font]]).group(1))
                            cur = [cur[0] + float(w[g - fc]) * finfo[font]["fm"][0] * size, cur[1]]
                    else:
                        cur = [cur[0] - float(part) / 1000 * size, cur[1]]
            st = []
        runs.append(glyphs)
    return finfo, runs


def render_run(spec, r, tmp):
    one = {"css": spec.get("css", ""), "runs": [r]}
    html = os.path.join(tmp, r["id"] + ".html")
    open(html, "w").write(build_html(one))
    pdf = os.path.join(tmp, r["id"] + ".pdf")
    prof = os.path.join(tmp, "profile")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                    f"--user-data-dir={prof}", "--virtual-time-budget=10000", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "file://" + html], capture_output=True, timeout=120)
    finfo, blocks = parse(pdf)
    objs = pdf_objects(open(pdf, "rb").read())
    gl = sorted([g for blk in blocks for g in blk], key=lambda g: g[3])
    x0 = gl[0][3]
    items = []
    for font, size, code, x, yy in gl:
        fi = finfo[font]
        proc = stream_of(objs[fi["procs"][fi["enc"].get(code)]])
        wx = float(proc.split()[0])
        body = proc.split(b"d1", 1)[1] if b"d1" in proc else proc.split(b"d0", 1)[1]
        items.append({"ch": fi["uni"].get(code, "?"), "x": round(x - x0, 3), "adv": round(wx * fi["fm"][0] * size, 3),
                      "font": fi["fname"], "d": glyph_path(body, fi["fm"], size, x - x0, 0)})
    fam = r["family"].replace(" ", "").lower()
    bad = [g["font"] for g in items if fam not in g["font"].replace("-", "").lower()]
    if bad:
        sys.exit(f"run {r['id']}: wanted {r['family']} but Chrome used {sorted(set(bad))} (font did not load)")
    return {"size": r.get("size", 1000), "text": r["text"], "glyphs": items}


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    tmp = tempfile.mkdtemp(prefix="glyphs-")
    result = {"runs": {}}
    for r in spec["runs"]:
        result["runs"][r["id"]] = render_run(spec, r, tmp)
    json.dump(result, open(out, "w"), indent=1)
    print(f"wrote {out}: " + ", ".join(f"{k}({''.join(g['ch'] for g in v['glyphs'])} {sorted(set(g['font'] for g in v['glyphs']))})" for k, v in result["runs"].items()))


if __name__ == "__main__":
    main()
