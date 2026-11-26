#!/usr/bin/env python3
"""SocialStream wallpaper for the Mac: one scene, built at several sizes as HyperFrames projects.

  loop/        3840 x 2160, 60 fps, a seamless loop: the moving picture for the lock screen
  still-*/     the same scene at a display's own size, for stills (the desktop wallpaper)

The scene: Night ground, slow blue and violet light, and a stream of reels: soft cards of light in the shape of
the logo's phone, leaning its 15 degrees, drifting up along their lean in three depths, as a feed is swiped. In
the middle a calm dark field with the kit's stacked logo on it, flat, as the guide asks ("No shadows, outlines,
gradients or effects ... use ... a calm area"): the one reel in focus. The lights are sums of sines with whole
cycles in the loop and the cards travel whole patterns, so the last frame runs into the first.

In the film the logo is not a still picture: it builds itself with the kit's own logo animation (the phone
arrives, the S swipes up into it like the next reel, it leans 15 degrees, the cut opens, it settles and the name
comes out from under it), holds, goes, and builds again, once every CYCLE seconds. The stills keep the kit's
finished logo.

Run: python3 build.py            (writes every project)
     python3 build.py draft      (a 1920 x 1080 copy of the loop, for quick stills)
"""
import contextlib, io, json, math, os, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, "../source"))                # the kit's SVG masters
LOOP, FPS = 40.0, 60                  # seconds in the loop; frames a second
STEP = 0.5                            # the motion is baked to straight segments this long
REST = 2.0                            # the moment of the loop the stills are taken at (chosen from ten)
CYCLE, EXIT, GAP = 10.0, 0.3, 0.4     # the logo builds once every CYCLE seconds, fades out over EXIT, and the ground is alone for GAP
LOGO_H = 0.224                        # the finished logo's height in the frame (the stills' logo: 0.28 with its clear space)
TOOLS = os.path.normpath(os.path.join(HERE, "../../tools"))            # make_motion.py, the logo animation

NIGHT = "#05070f"
# the lights: name, centre (fractions of the frame), radius (fraction of the height), colour, and the drift:
# (amplitude x, amplitude y) in fractions of the height, cycles in the loop (x, y), phases (x, y) in turns
LIGHTS = [
    ("blue",   0.20, 0.26, 0.74, "66, 92, 255, 0.58",   (0.10, 0.07), (1, 1), (0.00, 0.25)),
    ("violet", 0.80, 0.74, 0.78, "136, 78, 255, 0.52",  (0.09, 0.08), (1, 2), (0.50, 0.10)),
    ("stream", 0.74, 0.14, 0.52, "127, 161, 196, 0.20", (0.07, 0.05), (2, 1), (0.30, 0.60)),
    ("ember",  0.10, 0.94, 0.46, "255, 82, 114, 0.15",  (0.06, 0.05), (1, 1), (0.75, 0.40)),
]
# the stream of reels. A lane: where it crosses the frame's middle line (fraction of the width from the centre),
# the card's height (fraction of the frame's height), how soft its edge is (fraction of the card's height), its
# strength, the length of its pattern (fraction of the height), where its cards sit in the pattern (0-1, with a
# colour each), and how many patterns it travels up in one loop
BLUE, VIOLET, STREAM, EMBER = "92, 118, 255", "150, 98, 255", "127, 161, 196", "255, 82, 114"
LANES = [
    # far: small, in focus (a hairline of light on the edge), slow
    (-0.415, 0.150, 0.020, 0.34, 0.95, [(0.05, BLUE), (0.50, STREAM), (0.78, VIOLET)], 1),
    (0.300, 0.165, 0.020, 0.32, 1.10, [(0.20, VIOLET), (0.62, BLUE)], 1),
    (0.455, 0.140, 0.020, 0.30, 0.90, [(0.40, STREAM), (0.85, EMBER)], 1),
    (-0.130, 0.120, 0.020, 0.26, 1.30, [(0.72, STREAM)], 1),
    # middle
    (-0.255, 0.300, 0.075, 0.24, 1.45, [(0.10, VIOLET), (0.58, BLUE)], 1),
    (0.185, 0.330, 0.075, 0.24, 1.60, [(0.34, BLUE), (0.86, VIOLET)], 1),
    # near: large, out of focus, faster
    (-0.520, 0.640, 0.220, 0.17, 2.10, [(0.15, BLUE), (0.65, VIOLET)], 1),
    (0.560, 0.700, 0.220, 0.17, 2.30, [(0.45, VIOLET)], 1),
]


def bake(fn):
    """A value over the loop as a list, one entry every STEP seconds, the last equal to the first."""
    n = round(LOOP / STEP)
    return [round(fn(i * STEP), 2) for i in range(n)] + [round(fn(0.0), 2)]


def keyframes(sel, props):
    """One GSAP tween through evenly spaced values, straight between them."""
    body = ", ".join(f"{k}: {json.dumps(v)}" for k, v in props.items())
    return f'tl.to("{sel}", {{ keyframes: {{ {body}, easeEach: "none" }}, duration: {LOOP:g}, ease: "none" }}, 0);'


def scene(W, H, logo_h=0.28, logo=True, mark_only=False, cx=0.5, cy=0.5, grain=True):
    u = H / 1080.0
    html, js, css = [], [], []
    # ---- the lights ----
    for name, x, y, r, col, (ax, ay), (kx, ky), (px, py) in LIGHTS:
        R = r * H
        html.append(f'<i class="lt" id="lt-{name}" data-layout-allow-overflow style="left:{x * W - R:.1f}px;top:{y * H - R:.1f}px;'
                    f'width:{2 * R:.1f}px;height:{2 * R:.1f}px;background:radial-gradient(closest-side,rgba({col}),rgba({col.rsplit(",", 1)[0]},0))"></i>')
        js.append(keyframes(f"#lt-{name}", {
            "x": bake(lambda t: ax * H * math.sin(2 * math.pi * (kx * t / LOOP + px))),
            "y": bake(lambda t: ay * H * math.sin(2 * math.pi * (ky * t / LOOP + py)))}))
    # ---- the stream of reels: a square stage turned 15 degrees about the frame's middle; in it, lanes whose cards
    # run up by whole patterns ----
    S = 2.6 * max(W, H)                                      # the stage covers the frame at any turn
    reach = 0.5 * (H * math.cos(math.radians(15)) + W * math.sin(math.radians(15))) + 0.08 * H   # half the frame, along a lane
    lanes = []
    for li, (lx, ch, soft, a, pat, cards, k) in enumerate(LANES):
        h, C = ch * H, pat * H
        w = h * 9 / 16
        x = S / 2 + lx * W - w / 2
        items = []
        j0, j1 = -int(S / C) - 2, int(S / C) + 2 + k
        for j in range(j0, j1):
            for pos, rgb in cards:
                y = S / 2 + (j + pos) * C - h / 2
                if S / 2 - reach - 1.4 * h < y < S / 2 + reach + k * C + 0.4 * h:      # in the frame at some moment of the loop
                    edge = f",inset 0 0 0 {max(1.0, 0.006 * h):.1f}px rgba(255,255,255,0.10)" if soft < 0.05 else ""
                    items.append(f'<i class="rc" style="top:{y:.1f}px;height:{h:.1f}px;border-radius:{0.16 * w:.1f}px;'
                                 f'background:linear-gradient(165deg,rgba({rgb},{a:.3f}),rgba({rgb},{a * 0.42:.3f}));'
                                 f'box-shadow:0 0 {soft * h:.1f}px {soft * h * 0.35:.1f}px rgba({rgb},{a * 0.5:.3f}){edge}"></i>')
        lanes.append(f'<div class="lane" style="left:{x:.1f}px;width:{w:.1f}px"><div class="run" id="run{li}" data-layout-allow-overflow>{"".join(items)}</div></div>')
        js.append(f'tl.fromTo("#run{li}", {{ y: 0 }}, {{ y: {-k * C:.2f}, duration: {LOOP:g}, ease: "none" }}, 0);')
    html.append(f'<div id="stage" data-layout-allow-overflow style="left:{W / 2 - S / 2:.1f}px;top:{H / 2 - S / 2:.1f}px;width:{S:.1f}px;height:{S:.1f}px">{"".join(lanes)}</div>')
    # ---- the calm field, the shade at the top and the foot (the clock, the name and the password), the grain ----
    html.append('<div class="ff" id="calm"></div><div class="ff" id="shade"></div>' + ('<div class="ff" id="grain"></div>' if grain else ""))
    js.append(keyframes("#calm", {"opacity": bake(lambda t: 0.92 + 0.08 * math.sin(2 * math.pi * 3 * t / LOOP))}))
    # ---- the logo, flat ----
    if logo:
        src, ratio = ("symbol-dark.svg", 1.0) if mark_only else ("logo-stacked-dark.svg", 289 / 256)
        h = logo_h * H
        w = h * ratio
        html.append(f'<img id="logo" src="assets/{src}" alt="SocialStream" style="position:absolute;left:{cx * W - w / 2:.1f}px;top:{cy * H - h / 2:.1f}px;width:{w:.1f}px;height:{h:.1f}px">')
    calm = 0.36 if not mark_only else 0.26
    css.append(f"""
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {NIGHT}; }}
    #root .ff {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; }}
    #root .lt {{ position: absolute; border-radius: 50%; }}
    #root #stage {{ position: absolute; transform: rotate(15deg); transform-origin: 50% 50%; }}
    #root .lane {{ position: absolute; top: 0; height: 100%; }}
    #root .run {{ position: absolute; inset: 0; }}
    #root .rc {{ position: absolute; left: 0; width: 100%; display: block; }}
    #root #calm {{ background: radial-gradient(ellipse {calm * H / W * 100 * 1.2:.1f}% {calm * 100:.0f}% at {cx * 100:.1f}% {cy * 100:.1f}%, rgba(5,7,15,0.74) 0%, rgba(5,7,15,0.46) 46%, rgba(5,7,15,0) 100%); }}
    #root #shade {{ background: linear-gradient(to bottom, rgba(5,7,15,0.5) 0%, rgba(5,7,15,0) 24%, rgba(5,7,15,0) 74%, rgba(5,7,15,0.55) 100%); }}
    #root #grain {{ background: url(assets/grain.png) repeat; opacity: 0.085; mix-blend-mode: overlay; }}""")
    return "\n    ".join(html), "\n    ".join(js), "\n".join(css)


def logo_cycles(W, H):
    """The kit's logo animation (tools/make_motion.py) at this frame's size, on a clear ground, CYCLE seconds long:
    the build, the hold, a fade at the end. Returned once for each cycle of the loop, each copy with its own ids."""
    sys.path.insert(0, TOOLS)
    import make_motion as mm
    mm.FORMATS["wallpaper"] = dict(layout="stacked", size=(W, H), height_frac=LOGO_H, hero_h=LOGO_H * 0.38 / 0.28125,
                                   total=CYCLE - GAP, exit=EXIT, ground="transparent",
                                   master="socialstream-logo-stacked-dark.svg", pad=0.10)
    tmp = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(TOOLS)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            mm.build("wallpaper", tmp)
    finally:
        os.chdir(cwd)
    src = open(os.path.join(tmp, "compositions", "logo.html"), encoding="utf-8").read()
    shutil.rmtree(tmp)
    k = H / 1080.0                                           # the kit's soft arrival is set in px of a 1080 frame
    src = re.sub(r"blur\((\d+)px\)", lambda m: f"blur({round(int(m.group(1)) * k)}px)", src)
    out = []
    for i in range(round(LOOP / CYCLE)):
        t = src.replace("logo-", f"logo{i}-").replace('data-composition-id="logo"', f'data-composition-id="logo{i}"')
        t = t.replace('window.__timelines["logo"]', f'window.__timelines["logo{i}"]')
        assert f'data-composition-id="logo{i}"' in t and f'__timelines["logo{i}"]' in t
        out.append((f"logo{i}", i * CYCLE, t))
    return out


def project(folder, W, H, fps=FPS, animated=False, **kw):
    out = os.path.join(HERE, folder)
    os.makedirs(os.path.join(out, "compositions"), exist_ok=True)
    cycles = logo_cycles(W, H) if animated else []
    for name, start, src in cycles:
        open(os.path.join(out, "compositions", name + ".html"), "w").write(src)
    logos = "".join(f'''
      <div id="{name}" data-composition-id="{name}" data-composition-src="compositions/{name}.html" data-start="{start:g}" data-duration="{CYCLE - GAP:g}" data-track-index="{1 + i}" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: {1 + i}"></div>'''
                    for i, (name, start, src) in enumerate(cycles))
    html, js, css = scene(W, H, **kw)
    open(os.path.join(out, "compositions", "scene.html"), "w").write(f"""<template>
  <style>{css}
  </style>
  <div id="root" data-composition-id="scene" data-width="{W}" data-height="{H}">
    {html}
  </div>
  <script>
  (() => {{
    const tl = gsap.timeline({{ paused: true }});
    {js}
    window.__timelines["scene"] = tl;
  }})();
  </script>
</template>
""")
    open(os.path.join(out, "index.html"), "w").write(f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>SocialStream wallpaper ({W}x{H})</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {NIGHT}; }} #main {{ position: relative; width: 100%; height: 100%; }}</style>
  </head>
  <body>
    <div id="main" data-composition-id="main" data-start="0" data-duration="{LOOP:g}" data-fps="{fps}" data-width="{W}" data-height="{H}">
      <div id="scene" data-composition-id="scene" data-composition-src="compositions/scene.html" data-start="0" data-duration="{LOOP:g}" data-track-index="0" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: 0"></div>{logos}
    </div>
    <script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
""")
    files = {"hyperframes.json": json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                                             "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                                             "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}, indent=2) + "\n",
             "meta.json": json.dumps({"id": f"socialstream-wallpaper-{folder}", "name": f"SocialStream wallpaper ({folder})", "createdAt": "2026-11-24T00:00:00.000Z"}, indent=2) + "\n",
             "package.json": json.dumps({"name": f"socialstream-wallpaper-{folder}", "private": True, "type": "module"}, indent=2) + "\n"}
    for f, t in files.items():
        open(os.path.join(out, f), "w").write(t)
    link = os.path.join(out, "assets")
    if not os.path.islink(link):
        os.symlink("../assets", link)
    print(folder, f"{W}x{H}", fps, "fps")


def main():
    os.makedirs(os.path.join(HERE, "assets"), exist_ok=True)
    for name, src in (("logo-stacked-dark.svg", "socialstream-logo-stacked-dark.svg"), ("symbol-dark.svg", "socialstream-symbol-dark.svg")):
        shutil.copyfile(os.path.join(KIT, src), os.path.join(HERE, "assets", name))
    if sys.argv[1:] == ["draft"]:
        project("draft", 1920, 1080, 30, animated=True, logo=False)
        return
    project("loop", 3840, 2160, animated=True, logo=False)
    # the stills: the MacBook Pro 14's own screen, and 4K for a desk display (the snapshot tool stops at 4096 px
    # wide); with the whole logo, or the phone alone
    project("still-mbp14", 3024, 1964, 30)
    project("still-mbp14-phone", 3024, 1964, 30, mark_only=True, logo_h=0.17)
    project("still-4k", 3840, 2160, 30)
    project("still-4k-phone", 3840, 2160, 30, mark_only=True, logo_h=0.17)


if __name__ == "__main__":
    main()
