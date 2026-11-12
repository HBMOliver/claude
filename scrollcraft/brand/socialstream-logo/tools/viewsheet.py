import sys, os, re, subprocess
# the logo-design skill's renderer; override with LOGO_SKILL_SCRIPTS=/path/to/scripts
RENDER = os.path.join(os.environ.get("LOGO_SKILL_SCRIPTS", os.path.expanduser("~/.claude/skills/logo-design/scripts")), "render_png.py")
out = sys.argv[1]; dst = sys.argv[2]
def inner(path):
    s = open(path).read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    body = s.split('</title>', 1)[1].rsplit('</svg>', 1)[0]
    return vb, body
"""Review strip: each lockup and symbol (160/64/32/16 px) on cream and on night blue."""
rows = []; Y = 10
for k in "abcd":
    for scheme, bg, f in (("light", "#f6f4ef", f"concepts/{k}-lockup.svg"), ("night", "#05070f", f"test/{k}-lockup-night.svg")):
        vb, body = inner(os.path.join(out, f))
        w, h = [float(v) for v in vb.split()[2:]]
        H = 180; W = w * H / h
        if W > 680:
            W = 680; H2 = h * W / w
        else:
            H2 = H
        rows.append(f'<rect x="10" y="{Y}" width="1180" height="{H+20}" fill="{bg}"/>')
        rows.append(f'<svg x="20" y="{Y+10+(H-H2)/2}" width="{W}" height="{H2}" viewBox="{vb}">{body}</svg>')
        sym = f"concepts/{k}-symbol.svg" if scheme == "light" else f"test/{k}-symbol-cream.svg"
        vb2, body2 = inner(os.path.join(out, sym))
        x = 20 + W + 30
        for s in (160, 64, 32, 16):
            rows.append(f'<svg x="{x}" y="{Y + 10 + (160 - s)/2}" width="{s}" height="{s}" viewBox="{vb2}">{body2}</svg>')
            x += s + 24
        Y += H + 30
open(dst + ".svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{Y}" viewBox="0 0 1200 {Y}"><rect width="100%" height="100%" fill="#888"/>{"".join(rows)}</svg>')
subprocess.run(["python3", RENDER, dst + ".svg", "-o", dst + ".png", "--width", "1200", "--height", str(Y)])
