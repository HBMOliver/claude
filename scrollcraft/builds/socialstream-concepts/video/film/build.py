#!/usr/bin/env python3
"""The brand film, remade in the site's look (Aurora Mix, blue-purple with red-pink accents), as two HyperFrames
projects on one clock: wide/ (1920 x 1080) and tall/ (1080 x 1920). The site crossfades between the two cuts, so
every beat sits on the same frame in both.

The scenes in scenes/ are shared by both cuts (the tall cut's layout is in their portrait media queries); this
script fills in their placeholders, adds the logo animation (from the logo kit's make_motion.py, formats film-wide
and film-tall), writes each project's index.html and project files, and links each project's assets/ to ../assets.
Run from this folder: python3 build.py   (then render each project; see README.md)
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_TOOLS = os.path.normpath(os.path.join(HERE, "../../../../brand/socialstream-logo/tools"))
TOTAL = 32.1
FPS = 25
CUTS = {"wide": (1920, 1080, "film-wide"), "tall": (1080, 1920, "film-tall")}

# the film's clock: scene, start, length (seconds); the beats follow the original film's order and words
SCENES = [
    ("sky", 0.0, TOTAL),     # the moving light behind everything
    ("open", 0.0, 4.0),      # the reel wall and the night band
    ("logo", 0.0, 4.0),      # the logo builds itself (generated)
    ("claim", 4.0, 5.0),     # A social media meghalt. Az érdeklődés vette át a helyét.
    ("flyx", 9.0, 3.0),      # FlyX Tenerife, three reels
    ("roas", 12.0, 2.4),     # 81× ROAS
    ("mft", 14.4, 2.5),      # 79 M Ft
    ("pod", 16.9, 3.0),      # Podcast & interjú, three reels
    ("svc", 19.9, 3.0),      # the six services
    ("m300", 22.9, 2.7),     # 300 M Ft
    ("win", 25.6, 3.1),      # Mi ebben a korban győzünk.
    ("close", 28.7, 3.4),    # the wall and the logo again, then back to the first frame
]

RESULTS = {
    "roas": dict(SIDE="right", C1="roas-1", C2="roas-2", C3="roas-3", DUR="2.4", TO="81", COUNT="1.3", OUT="2.18",
                 UNIT='<small>× ROAS</small>', LABEL="legjobb eredmény", SUB="Ajtó webshop · Google PMax"),
    "mft": dict(SIDE="left", C1="mft-1", C2="mft-2", C3="mft-3", DUR="2.5", TO="79", COUNT="1.4", OUT="2.28",
                UNIT='<small class="it">M Ft</small>', LABEL="bevétel egy hét alatt", SUB="B2B Meta kampány"),
    "m300": dict(SIDE="right", C1="m300-1", C2="m300-2", C3="m300-3", DUR="2.7", TO="300", COUNT="1.3", OUT="2.48",
                 UNIT='<small class="it">M Ft</small>', LABEL="kezelt hirdetési büdzsé", SUB="2022 óta az új korban"),
}
SIDE_CSS = {
    "right": "#{i}-r {{ left: 150px; }} #{i}-q1 {{ left: 940px; top: 291px; }} #{i}-q2 {{ left: 1240px; top: 291px; }} "
             "#{i}-q3 {{ left: 1540px; top: 291px; }}",
    "left": "#{i}-r {{ left: 1100px; }} #{i}-q1 {{ left: 130px; top: 291px; }} #{i}-q2 {{ left: 430px; top: 291px; }} "
            "#{i}-q3 {{ left: 730px; top: 291px; }}",
}
SERVICES = [("Videó", "svc-video"), ("Social", "svc-social"), ("Hirdetés", "svc-ads"), ("Weboldal", "svc-web"),
            ("Automatizáció", "svc-auto"), ("Stratégia", "svc-strat")]

# the reel wall: 7 rows x 9 columns of their reel stills, tilted, large enough to cover both cuts while it drifts
ROWS, COLS, CW, CH, GAP = 7, 9, 230, 409, 28
REELS = ["p02", "p03", "p04", "p05", "p06", "p07", "p08", "p09", "p10", "p11", "p13", "p14", "p15", "p16", "p17",
         "p18", "p19", "p20", "p21", "p22", "p23", "p24"]
WALL_W, WALL_H = COLS * CW + (COLS - 1) * GAP, ROWS * CH + (ROWS - 1) * GAP
WALL_CSS = f"""#root .wl-in {{ position: absolute; inset: 0; }}
    #root .wl-tilt {{ position: absolute; left: 50%; top: 50%; width: {WALL_W}px; height: {WALL_H}px; margin: {-WALL_H / 2}px 0 0 {-WALL_W / 2}px; transform: rotate(-10deg); }}
    #root .wl-wall {{ position: absolute; inset: 0; }}
    #root .wl-card {{ position: absolute; width: {CW}px; height: {CH}px; overflow: hidden; border-radius: 22px; background: #0b1024;
      box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12), 0 30px 60px -30px rgba(0, 0, 0, 0.8); }}
    #root .wl-card img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
    #root .wl-dim {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 50%, rgba(5, 7, 15, 0.45), rgba(5, 7, 15, 0.74)); }}
    #root .wl-band {{ position: absolute; left: 0; right: 0; top: 21.5%; height: 57%;
      background: linear-gradient(180deg, rgba(5, 7, 15, 0) 0%, #05070f 17.5%, #05070f 82.5%, rgba(5, 7, 15, 0) 100%); }}"""


def wall():
    cards = []
    for r in range(ROWS):
        for c in range(COLS):
            img = REELS[(r * 5 + c * 3) % len(REELS)]
            cards.append(f'<div class="wl-card" style="left:{c * (CW + GAP)}px;top:{r * (CH + GAP)}px">'
                         f'<img src="assets/reels/{img}.jpg" alt=""></div>')
    return "".join(cards)


def logo_scene(fmt, tmp):
    """The logo animation for this cut, and where its last frame puts the lockup (px)."""
    out = subprocess.run([sys.executable, "make_motion.py", fmt, "--out", tmp], cwd=LOGO_TOOLS, check=True,
                         capture_output=True, text=True).stdout
    info = json.loads(out[out.index("{"):out.rindex("}") + 1])
    return open(os.path.join(tmp, "compositions", "logo.html")).read(), info


def logo_box(info):
    """CSS box that puts the kit's stacked dark master exactly where the animation's last frame has the lockup."""
    (x0, y0), (x1, y1) = info["lockup_px"]
    svg = open(os.path.join(HERE, "assets", "logo", "socialstream-logo-stacked-dark.svg")).read()
    wk, hk = [float(v) for v in svg.split('viewBox="')[1].split('"')[0].split()[2:4]]
    pad = 0.10                                         # build_kit.write(..., pad=0.10) for the stacked lockup
    f = (y1 - y0) / (hk * (1 - 2 * pad))               # px per kit unit
    content_w = (x1 - x0) / f
    left, top = x0 - (wk - content_w) / 2 * f, y0 - hk * pad * f
    return f"left:{left:.3f}px;top:{top:.3f}px;width:{wk * f:.3f}px;height:{hk * f:.3f}px"


def fill(src, **kw):
    for k, v in kw.items():
        src = src.replace(f"%{k}%", str(v))
    left = re.findall(r"%[A-Z0-9]+%", src)
    assert not left, f"unfilled placeholders: {left}"
    return src


def scene(name, W, H, common, logo_css):
    if name in RESULTS:
        r = RESULTS[name]
        src = open(os.path.join(HERE, "scenes", "result.html")).read()
        src = src.replace("/*SIDECSS*/", SIDE_CSS[r["SIDE"]].format(i=name))
        src = fill(src, ID=name, **r, W=W, H=H)
    else:
        src = open(os.path.join(HERE, "scenes", f"{name}.html")).read()
        if name in ("open", "close"):
            src = src.replace("/*WALLCSS*/", WALL_CSS).replace("<!--WALL-->", wall())
        if name == "svc":
            names = "".join(f'<div class="hd" id="sv-n{i}">{t}<span class="acc">.</span></div>' for i, (t, c) in enumerate(SERVICES))
            slides = "".join(
                f'<div class="sv-s" id="sv-s{i}"><video id="sv-v{i}" class="clip" src="assets/clips/{c}.mp4" '
                f'data-start="{max(0.0, i * 0.5 - 0.1):g}" data-duration="{(0.85 if i < 5 else 3.0 - (i * 0.5 - 0.1)):g}" '
                f'data-track-index="{i + 1}" muted playsinline></video></div>' for i, (t, c) in enumerate(SERVICES))
            bars = "".join(f'<span><i id="sv-b{i}"></i></span>' for i in range(len(SERVICES)))
            src = src.replace("%NAMES%", names).replace("%SLIDES%", slides).replace("%BARS%", bars)
        src = fill(src, W=W, H=H, TOTAL=f"{TOTAL:g}", ROWS=ROWS, COLS=COLS, LOGOBOX=logo_css)
    return src.replace("/*COMMON*/", common)


def index(W, H):
    hosts = []
    for z, (name, start, dur) in enumerate(SCENES):
        hosts.append(f'''      <div
        id="{name}"
        data-composition-id="{name}"
        data-composition-src="compositions/{name}.html"
        data-start="{start:g}"
        data-duration="{dur:g}"
        data-track-index="{z}"
        data-track-kind="graphics"
        data-width="{W}"
        data-height="{H}"
        style="z-index: {z}"
      ></div>''')
    return f"""<!doctype html>
<html lang="hu">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>SocialStream brand film ({W}x{H})</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #05070f; }}
      #main {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-duration="{TOTAL:g}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def main():
    common = open(os.path.join(HERE, "common.css")).read()
    for cut, (W, H, fmt) in CUTS.items():
        out = os.path.join(HERE, cut)
        os.makedirs(os.path.join(out, "compositions"), exist_ok=True)
        tmp = os.path.join(HERE, ".logo-" + cut)
        logo, info = logo_scene(fmt, tmp)
        css = logo_box(info)
        for name, start, dur in SCENES:
            src = logo if name == "logo" else scene(name, W, H, common, css)
            open(os.path.join(out, "compositions", f"{name}.html"), "w").write(src)
        open(os.path.join(out, "index.html"), "w").write(index(W, H))
        cli = "npx --yes hyperframes@0.9.40"
        files = {
            "hyperframes.json": json.dumps({
                "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                "media": {"autoProxy": True}}, indent=2) + "\n",
            "meta.json": json.dumps({"id": f"socialstream-film-{cut}", "name": f"SocialStream brand film ({cut})",
                                     "createdAt": "2026-11-15T00:00:00.000Z"}, indent=2) + "\n",
            "package.json": json.dumps({"name": f"socialstream-film-{cut}", "private": True, "type": "module",
                                        "scripts": {"dev": f"{cli} preview", "check": f"{cli} check",
                                                    "render": f"{cli} render"}}, indent=2) + "\n",
            ".gitignore": "renders/\n.hyperframes/\n.thumbnails/\nsnapshots/\nnode_modules/\n",
        }
        for fname, text in files.items():
            open(os.path.join(out, fname), "w").write(text)
        link = os.path.join(out, "assets")
        if not os.path.islink(link):
            os.symlink("../assets", link)
        subprocess.run(["rm", "-rf", tmp], check=True)
        print(cut, W, H, "logo box:", css)


if __name__ == "__main__":
    main()
