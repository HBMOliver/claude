#!/usr/bin/env python3
"""The brand film v6: "Through the phone", reworked (2026-11-15), as HyperFrames projects on one clock: wide/
(1920 x 1080) and tall/ (1080 x 1920), each in Hungarian and English (wide-en/, tall-en/).

The founder found v5 (../film/) too empty and dark, its footage weak, its motion not premium and the film too long.
v6 keeps v5's idea (one camera through the phone: dive into the logo's S, swipe through reels, back out into the
reel wall) and changes the rest: 22.52 s instead of 35.4; every frame is full (full-frame footage from 4K sources or
a full colour field, never small things on night blue); no face in more than one beat; results on colour fields;
titles land and then stay still (no odometer, no smeared numbers); the film opens on the wall with the finished
logo, which is also its last frame, so the loop is seamless. SPEC.md has the shot list; TM below is the clock
(seconds of the whole film), shared by every scene.

Run from this folder: python3 build.py [wide wide-en tall tall-en]   (then render; see README.md)
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_TOOLS = os.path.normpath(os.path.join(HERE, "../../../../brand/socialstream-logo/tools"))
FPS = 25
CUTS = {"wide": (1920, 1080, "film-end-wide"), "tall": (1080, 1920, "film-end-tall")}
OUTS = [("wide", "hu", "wide"), ("tall", "hu", "tall"), ("wide", "en", "wide-en"), ("tall", "en", "tall-en")]

# every line of the film in both languages: v5's copy, the English approved by the founder on 2026-11-15
TEXT = {
    "hu": dict(
        claimA=('<span class="w">A</span> <span class="ss"><span class="w">social</span><br class="t"> '
                '<span class="w">media</span><i class="stk" id="ca-stk"></i></span>', "meghalt."),
        claimB=('<div class="hd"><span class="w">Az</span> <span class="w it">érdeklődés</span></div>'
                '<div class="hd"><span class="w">vette</span> <span class="w">át</span><br class="t"> '
                '<span class="w">a</span> <span class="w">helyét<span class="acc">.</span></span></div>'),
        flyx=("Élményközpont · Social &amp; video", "FlyX", "Tenerife"),
        roas=(["legjobb", "eredmény"], "Ajtó webshop · Google PMax"),
        mft=(["bevétel", "egy", "hét", "alatt"], "B2B Meta kampány"),
        m300=(["kezelt", "hirdetési", "büdzsé"], "2022 óta az új korban"),
        services=["Videó", "Social", "Hirdetés", "Weboldal", "Automatizáció", "Stratégia"],
        win=(["Mi", "ebben", "a", "korban"], "győzünk"),
    ),
    "en": dict(
        claimA=('<span class="ss"><span class="w">Social</span><br class="t"> <span class="w">media</span>'
                '<i class="stk" id="ca-stk"></i></span>', "is dead."),
        claimB=('<div class="hd"><span class="w it">Interest</span></div>'
                '<div class="hd"><span class="w">has</span> <span class="w">taken</span><br class="t"> '
                '<span class="w">its</span> <span class="w">place<span class="acc">.</span></span></div>'),
        flyx=("Experience centre · Social &amp; video", "FlyX", "Tenerife"),
        roas=(["best", "result"], "Door webshop · Google PMax"),
        mft=(["revenue", "in", "one", "week"], "B2B Meta campaign"),
        m300=(["ad", "budget", "managed"], "In the new era since 2022"),
        services=["Video", "Social", "Ads", "Website", "Automation", "Strategy"],
        win=(["In", "this", "era,"], "we win"),
    ),
}

# ---- the clock (seconds of the whole film; every value a whole frame) ----
TM = dict(
    total=22.52,
    dive=1.32, dived=0.72,                # the camera dives into the logo's S (log scale x260, power2.in)
    flood=1.96, floodd=0.28,              # claim A's colour field comes up through the S's night
    claimA=2.16, strike=2.64, meghalt=2.92,
    sw=0.38,                              # a swipe inside the phone (power3.inOut)
    swB=3.96, swF=6.04, swR=7.88, swM=9.76, swS=11.64, sw3=14.28, swW=16.16,
    svc=[12.28, 12.68, 13.08, 13.48, 13.88],   # the services after the first: a hard cut every 0.4 s
    winOut=18.96,                         # the last line (on for 2 s and more) blurs out before the frame backs out
    back=19.12, backd=0.80,               # out into the reel wall (power3.inOut)
    glow=19.36, glowd=0.48,               # the night glow comes up behind where the logo will be
    logo=19.52,                           # the logo builds itself (the kit's film-end format, 3.0 s); its phone
                                          # arrives as the sunset's card shrinks into the wall's middle behind it
    wallV=12,                             # the wall's drift, px a second
)
TOTAL = TM["total"]
for k, v in TM.items():                   # every moment (not every length) sits on a frame
    for x in (v if isinstance(v, list) else [v]):
        if k not in ("wallV", "dived", "floodd", "sw", "backd", "glowd"):
            assert abs(x * FPS - round(x * FPS)) < 1e-6, f"{k} is not on a frame"
assert abs(TM["logo"] + 3.0 - TOTAL) < 1e-9
FEED0 = 1.90                              # the feed scene starts just before the flood
LEAD = 0.12                               # footage starts this much before its slide swipes in

# the slides inside the phone, in order: id, kind, when it swipes in (claim A comes up with the flood)
SLIDES = [("claimA", "field", TM["flood"]), ("claimB", "media", TM["swB"]), ("flyx", "media", TM["swF"]),
          ("roas", "field", TM["swR"]), ("mft", "field", TM["swM"]), ("svc", "field", TM["swS"]),
          ("m300", "field", TM["sw3"]), ("win", "media", TM["swW"])]

# ---- footage (assets/clips; clips.sh): file, box w, box h, focus x, focus y ----
FOOT = {
    "wide": {"claimB": ("w-crowd", 1920, 1080), "flyx": ("w-screen", 1920, 1080), "win": ("w-sunset", 1920, 1080),
             "win_focus": (0.55, 0.5)},
    "tall": {"claimB": ("t-crowd", 1080, 1920), "flyx": ("t-screen", 1080, 1920), "win": ("t-sunset", 1080, 1920),
             "win_focus": (0.5, 0.5)},
}
SVC_CLIPS = ["ph-svc-stage", "ph-svc-social", "ph-svc-ads2", "ph-svc-web", "ph-svc-auto", "ph-svc-strat"]
FOOT_LANG = {"en": {"ph-svc-web": "ph-svc-web-en"}}   # footage that shows words, in each language's version

# ---- the colour fields: ground, lights (x %, y %, size vmax, rgba, drift px) ----
FIELDS = {
    "claimA": ("#0b1034", [(84, 12, 120, "136, 78, 255, 0.85", (-80, 60)), (8, 96, 110, "66, 92, 255, 0.8", (90, -50)),
                           (100, 100, 50, "255, 64, 104, 0.32", (-40, -30))]),
    "roas": ("#26137a", [(92, 92, 105, "255, 64, 104, 0.68", (-70, -40)), (4, 4, 85, "56, 160, 255, 0.55", (60, 40))]),
    "mft": ("#0e2bb0", [(96, 8, 100, "136, 78, 255, 0.75", (-60, 50)), (0, 100, 95, "56, 160, 255, 0.6", (70, -40))]),
    "svc": ("#120d3a", [(10, 10, 100, "66, 92, 255, 0.75", (60, 40)), (70, 100, 90, "136, 78, 255, 0.7", (-50, -40))]),
    "m300": ("#3f1596", [(100, 0, 105, "255, 64, 104, 0.62", (-70, 50)), (0, 100, 100, "66, 92, 255, 0.75", (60, -50))]),
}
NUMBERS = {"roas": ("81", '<span class="x acc">×</span><span class="u">ROAS</span>'),
           "mft": ("79", '<span class="ui">M Ft</span>'),
           "m300": ("300", '<span class="ui">M Ft</span>')}

# ---- the reel wall (open and close): 7 rows x 9 columns of stills from their footage, tilted ----
ROWS, COLS, CW, CH, GAP, TILT = 7, 9, 230, 409, 28, -10
TILES = [f"t{i:02d}" for i in range(1, 23)]
WALL_W, WALL_H = COLS * CW + (COLS - 1) * GAP, ROWS * CH + (ROWS - 1) * GAP
MID_R, MID_C = ROWS // 2, COLS // 2       # the middle card, which the phone becomes at the end
WALL_CSS = f"""#root .wl-in {{ position: absolute; inset: 0; }}
    #root .wl-tilt {{ position: absolute; left: 50%; top: 50%; width: {WALL_W}px; height: {WALL_H}px; margin: {-WALL_H / 2}px 0 0 {-WALL_W / 2}px; transform: rotate({TILT}deg); }}
    #root .wl-wall {{ position: absolute; inset: 0; }}
    #root .wl-card {{ position: absolute; width: {CW}px; height: {CH}px; overflow: hidden; border-radius: 22px; background: #0b1024;
      box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12), 0 30px 60px -30px rgba(0, 0, 0, 0.8); }}
    #root .wl-card img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
    #root .wl-dim {{ position: absolute; inset: 0; background: rgba(5, 7, 15, 0.2); }}"""


def wall(cut, skip_middle=False):
    cards = []
    for r in range(ROWS):
        for c in range(COLS):
            img = f"tiles/{TILES[(r * 5 + c * 3) % len(TILES)]}.jpg"
            hide = ""
            if (r, c) == (MID_R, MID_C):
                img = f"tiles/mid-{cut}.jpg"        # the sunset where the close leaves it: the loop's seam
                if skip_middle:                     # stays in the grid (the fly-in keeps its order) but hidden
                    hide = ";visibility:hidden"
            cards.append(f'<div class="wl-card" style="left:{c * (CW + GAP)}px;top:{r * (CH + GAP)}px{hide}">'
                         f'<img src="assets/{img}" alt=""></div>')
    return "".join(cards)


def middle_still(cut):
    """The middle card of the opening's wall: the sunset's frame on the film's last frame, cut as the close's card
    shows it (the footage covering the card at its focus)."""
    f, bw, bh = FOOT[cut]["win"]
    fx, fy = FOOT[cut]["win_focus"]
    ms_close = TM["back"] - (TM["swW"] - LEAD)
    t_media = ms_close + (TOTAL - 1 / FPS - TM["back"])
    z = max(CW / bw, CH / bh)
    sw, sh = bw * z, bh * z
    ox = min(0.0, max(CW - sw, CW / 2 - sw * fx))      # the box's offset inside the card (coverAt)
    oy = min(0.0, max(CH - sh, CH / 2 - sh * fy))
    cw, ch, cx, cy = CW / z, CH / z, -ox / z, -oy / z
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t_media:.3f}", "-i", os.path.join(HERE, "assets", "clips", f + ".mp4"),
                    "-frames:v", "1", "-vf", f"crop={cw:.1f}:{ch:.1f}:{cx:.1f}:{cy:.1f},scale=460:818:flags=lanczos",
                    "-q:v", "3", os.path.join(HERE, "assets", "tiles", f"mid-{cut}.jpg")], check=True)


# ---- the logo ----
def logo_scene(fmt, tmp):
    """The logo build for this cut, and where its last frame puts the lockup and the S (px)."""
    out = subprocess.run([sys.executable, "make_motion.py", fmt, "--out", tmp], cwd=LOGO_TOOLS, check=True,
                         capture_output=True, text=True).stdout
    info = json.loads(out[out.index("{"):out.rindex("}") + 1])
    return open(os.path.join(tmp, "compositions", "logo.html")).read(), info


def logo_box(info):
    """CSS box that puts the kit's stacked dark master exactly where the build's last frame has the lockup."""
    (x0, y0), (x1, y1) = info["lockup_px"]
    svg = open(os.path.join(HERE, "assets", "logo", "socialstream-logo-stacked-dark.svg")).read()
    wk, hk = [float(v) for v in svg.split('viewBox="')[1].split('"')[0].split()[2:4]]
    pad = 0.10                                         # build_kit.write(..., pad=0.10) for the stacked lockup
    f = (y1 - y0) / (hk * (1 - 2 * pad))               # px per kit unit
    content_w = (x1 - x0) / f
    left, top = x0 - (wk - content_w) / 2 * f, y0 - hk * pad * f
    return f"left:{left:.3f}px;top:{top:.3f}px;width:{wk * f:.3f}px;height:{hk * f:.3f}px"


# ---- the feed: the slides inside the phone ----
def rel(t):
    return round(t - FEED0, 4)


def lights(sid):
    base, ls = FIELDS[sid]
    out = "".join(f'<i class="lt" id="lt-{sid}-{k}" data-layout-allow-overflow style="left:{x}%;top:{y}%;width:{s}vmax;height:{s}vmax;'
                  f'margin:-{s / 2}vmax 0 0 -{s / 2}vmax;background:radial-gradient(closest-side, rgba({c}), '
                  f'rgba({c.rsplit(",", 1)[0]}, 0))"></i>' for k, (x, y, s, c, d) in enumerate(ls))
    return f'<div class="fld" style="background:{base}">{out}</div>'


def slide_end(i):
    """When slide i has left the frame (the next one's swipe is over), or the end of the feed."""
    return SLIDES[i + 1][2] + TM["sw"] if i + 1 < len(SLIDES) else TM["back"]


def video(vid, f, start, end, track, cls="full", media=0.0):
    return (f'<video id="{vid}" class="clip {cls}" src="assets/clips/{f}.mp4" data-start="{rel(start):g}" '
            f'data-duration="{round(end - start, 4):g}" data-media-start="{media:g}" data-hf-media-start-basis="local" '
            f'data-track-index="{track}" muted playsinline></video>')


def feed(cut, lang):
    T, X = TM, TEXT[lang]
    html, js = [], []
    track = 1
    for i, (sid, kind, tin) in enumerate(SLIDES):
        t_out = slide_end(i)
        inner = ""
        if kind == "field":
            inner += lights(sid)
        if sid == "claimA":
            words, last = X["claimA"]
            inner += (f'<div class="ca"><div class="hd ca1">{words}</div>'
                      f'<div class="it ca2" id="ca-m">{last}</div></div>')
        elif sid == "claimB":
            f = FOOT[cut]["claimB"][0]
            inner += video("v-claimB", f, tin - LEAD, t_out, track) + f'<div class="cb" id="cb">{X["claimB"]}</div>'
            track += 1
        elif sid == "flyx":
            f = FOOT[cut]["flyx"][0]
            eb, name, place = X["flyx"]
            letters = "".join(f'<span class="l">{ch}</span>' for ch in name)
            inner += video("v-flyx", f, tin - LEAD, t_out, track) + (
                f'<div class="fx"><div class="eb" id="fx-eb"><span class="dot"></span>{eb}</div>'
                f'<div class="fx-t"><span class="hd fx-n">{letters}</span><br class="t"> '
                f'<span class="it fx-p" id="fx-p">{place}</span></div></div>')
            track += 1
        elif sid in NUMBERS:
            digits, unit = NUMBERS[sid]
            words, eb = X[sid]
            lab = " ".join(f'<span class="w">{w}</span>' for w in words)
            inner += (f'<div class="nb"><div class="eb" id="{sid}-eb">{eb}</div>'
                      f'<div class="num" id="{sid}-num"><span class="hd dg">{digits}</span>{unit}</div>'
                      f'<div class="lab" id="{sid}-lab">{lab}</div></div>')
        elif sid == "svc":
            cuts = [tin] + T["svc"] + [t_out]
            names, reels = [], []
            for k, name in enumerate(X["services"]):
                a, b = cuts[k], cuts[k + 1]
                names.append(f'<div class="hd sv-w clip" id="svw-{k}" data-start="{rel(a):g}" data-duration="{round(b - a, 4):g}" '
                             f'data-track-index="{track}">{name}<span class="acc">.</span></div>')
                track += 1
                f = FOOT_LANG.get(lang, {}).get(SVC_CLIPS[k], SVC_CLIPS[k])
                reels.append(video(f"v-svc{k}", f, a - (LEAD if k == 0 else 0), b, track, cls=""))
                track += 1
            inner += "".join(names) + f'<div class="sv-reel">{"".join(reels)}</div>'
        elif sid == "win":
            f = FOOT[cut]["win"][0]
            words, last = X["win"]
            w1 = " ".join(f'<span class="w">{w}</span>' for w in words)
            inner += video("v-win", f, tin - LEAD, T["back"], track) + (
                f'<div class="wn" id="wn"><div class="hd wn1">{w1}</div>'
                f'<div class="it wn2"><span class="w" id="wn-2">{last}<span class="acc">.</span></span></div></div>')
            track += 1
        html.append(f'<div class="sl" id="sl-{sid}" data-layout-allow-overflow>{inner}</div>')

        # ---- motion ----
        land = tin + (T["floodd"] if i == 0 else T["sw"])
        if i == 0:
            js.append(f'tl.fromTo("#sl-claimA", {{ opacity: 0 }}, {{ opacity: 1, duration: TM.floodd, ease: "power2.inOut" }}, AT(TM.flood));')
        else:
            prev = SLIDES[i - 1][0]
            js.append(f'tl.set("#sl-{sid}", {{ y: H }}, 0);')
            js.append(f'tl.fromTo("#sl-{sid}", {{ y: H }}, {{ y: 0, duration: TM.sw, ease: "power3.inOut", immediateRender: false }}, AT({tin:g}));')
            js.append(f'tl.fromTo("#sl-{prev}", {{ y: 0 }}, {{ y: -H, duration: TM.sw, ease: "power3.inOut", immediateRender: false }}, AT({tin:g}));')
        if kind == "field":                       # the field's lights drift slowly while it is on screen
            for k, (x, y, s, c, (dx, dy)) in enumerate(FIELDS[sid][1]):
                js.append(f'tl.fromTo("#lt-{sid}-{k}", {{ x: 0, y: 0 }}, {{ x: {dx}, y: {dy}, duration: {round(t_out - tin, 3)}, ease: "sine.inOut" }}, AT({tin:g}));')
        if sid == "claimA":
            js.append('tl.fromTo("#sl-claimA .ca1 .w", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: 0.067 }, AT(TM.claimA));')
            js.append('tl.fromTo("#ca-stk", { scaleX: 0 }, { scaleX: 1, duration: 0.26, ease: "power3.out" }, AT(TM.strike));')
            js.append('tl.fromTo("#sl-claimA .ss .w", { opacity: 1 }, { opacity: 0.45, duration: 0.3, ease: "power2.out", immediateRender: false }, AT(TM.strike + 0.12));')
            js.append('tl.fromTo("#ca-m", { opacity: 0, filter: "blur(12px)", scale: 1.04 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.3, ease: "power2.out" }, AT(TM.meghalt));')
        elif sid == "claimB":
            js.append(f'tl.fromTo("#cb .w", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: 0.08 }}, AT({land - 0.04:g}));')
        elif sid == "flyx":
            js.append(f'tl.fromTo("#fx-eb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, AT({land - 0.06:g}));')
            js.append(f'tl.fromTo("#sl-flyx .fx-n .l", {{ opacity: 0.25, filter: "blur(5px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power2.out", stagger: 0.1 }}, AT({land:g}));')
            js.append(f'tl.fromTo("#fx-p", {{ opacity: 0, filter: "blur(12px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }}, AT({land + 0.42:g}));')
        elif sid in NUMBERS:
            js.append(f'tl.fromTo("#{sid}-eb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, AT({land - 0.08:g}));')
            js.append(f'tl.fromTo("#{sid}-num", {{ opacity: 0, scale: 1.05 }}, {{ opacity: 1, scale: 1, duration: 0.55, ease: "expo.out" }}, AT({land - 0.04:g}));')
            js.append(f'tl.fromTo("#{sid}-num", {{ filter: "blur(16px)" }}, {{ filter: "blur(0px)", duration: 0.3, ease: "power2.out" }}, AT({land - 0.04:g}));')
            js.append(f'tl.fromTo("#{sid}-lab .w", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: 0.06 }}, AT({land + 0.2:g}));')
        elif sid == "win":
            js.append(f'tl.fromTo("#wn .wn1 .w", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: 0.08 }}, AT({land + 0.02:g}));')
            js.append(f'tl.fromTo("#wn-2", {{ opacity: 0, filter: "blur(12px)", scale: 1.04 }}, {{ opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.3, ease: "power2.out" }}, AT({land + 0.38:g}));')
            js.append('tl.fromTo("#wn .w", { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.16, ease: "power2.in", immediateRender: false }, AT(TM.winOut));')
    # the story bars: one segment per slide, filling while it is on screen; they come with the flood and go with
    # the last line
    segs = [(SLIDES[i][2], SLIDES[i + 1][2] if i + 1 < len(SLIDES) else T["back"]) for i in range(len(SLIDES))]
    js.append('tl.fromTo("#fd-bars", { opacity: 0 }, { opacity: 1, duration: TM.floodd, ease: "power2.inOut" }, AT(TM.flood));')
    js.append('tl.fromTo("#fd-bars", { opacity: 1 }, { opacity: 0, duration: 0.16, ease: "power2.in", immediateRender: false }, AT(TM.winOut));')
    for k, (a, b) in enumerate(segs):
        js.append(f'tl.fromTo("#fd-b{k}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {round(b - a, 3)}, ease: "none" }}, AT({a:g}));')
    bars = "".join(f'<span><i id="fd-b{k}"></i></span>' for k in range(len(segs)))
    return "\n    ".join(html), "\n    ".join(js), bars


# ---- filling the scenes ----
def fill(src, **kw):
    for k, v in kw.items():
        src = src.replace(f"%{k}%", str(v))
    left = re.findall(r"%[A-Z0-9]+%", src)
    assert not left, f"unfilled placeholders: {left}"
    return src


SCENES = [  # name, start, end; the order is the paint order (later is on top)
    ("open", 0.0, 2.30),
    ("close", TM["back"], TOTAL),
    ("feed", FEED0, TM["back"]),
    ("logo", TM["logo"], TOTAL),
]


def scene(name, cut, lang, common, commonjs, info):
    W, H = CUTS[cut][:2]
    start = next(s for n, s, e in SCENES if n == name)
    src = open(os.path.join(HERE, "scenes", f"{name}.html")).read()
    src = src.replace("/*COMMON*/", common).replace("/*COMMONJS*/", commonjs.replace("%START%", f"{start:g}"))
    src = src.replace("/*WALLCSS*/", WALL_CSS)
    kw = dict(W=W, H=H)
    if name == "open":
        src = src.replace("<!--WALL-->", wall(cut))
        kw.update(LOGOBOX=logo_box(info), SCENTRE=json.dumps([round(v, 3) for v in info["s_centre_px"]]))
    if name == "close":
        src = src.replace("<!--WALL-->", wall(cut, skip_middle=True))
        f, bw, bh = FOOT[cut]["win"]
        fx, fy = FOOT[cut]["win_focus"]
        ms = TM["back"] - (TM["swW"] - LEAD)      # where the feed's sunset is when the close takes it over
        hero = (f'<div class="media" id="cs-m" style="width:{bw}px;height:{bh}px"><video id="cs-v" class="clip" '
                f'src="assets/clips/{f}.mp4" data-start="0" data-duration="{round(TOTAL - TM["back"], 4):g}" '
                f'data-media-start="{ms:g}" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video></div>')
        kw.update(HERO=hero, HERODATA=json.dumps(dict(bw=bw, bh=bh, fx=fx, fy=fy)),
                  SLOT=json.dumps(dict(w=CW, h=CH, r=22, tilt=TILT)), ROWS=ROWS, COLS=COLS)
    if name == "feed":
        html, js, bars = feed(cut, lang)
        kw.update(SLIDES=html, SLIDEJS=js, BARS=bars)
    return fill(src, **kw)


def index(W, H, lang):
    hosts = []
    for z, (name, start, end) in enumerate(SCENES):
        hosts.append(f'''      <div
        id="{name}"
        data-composition-id="{name}"
        data-composition-src="compositions/{name}.html"
        data-start="{start:g}"
        data-duration="{round(end - start, 4):g}"
        data-track-index="{z}"
        data-track-kind="graphics"
        data-width="{W}"
        data-height="{H}"
        style="z-index: {z}"
      ></div>''')
    return f"""<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>SocialStream brand film v6 ({W}x{H}, {lang})</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #05070f; }}
      #main {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <!-- motion blur at render time, with a short shutter (100 degrees, not the default 240): the swipes, the dive and
         the back-out carry a light smear along their path; type only lands by focus and opacity, so it is never
         smeared in place -->
    <div id="main" data-motion-blur="on" data-motion-blur-shutter="100" data-composition-id="main" data-start="0" data-duration="{TOTAL:g}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
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
    commonjs_src = open(os.path.join(HERE, "common.js")).read()
    only = sys.argv[1:]                                   # e.g. python3 build.py wide
    for cut, lang, folder in OUTS:
        if only and folder not in only:
            continue
        W, H, fmt = CUTS[cut]
        out = os.path.join(HERE, folder)
        comp = os.path.join(out, "compositions")
        os.makedirs(comp, exist_ok=True)
        tmp = os.path.join(HERE, ".logo-" + folder)
        logo, info = logo_scene(fmt, tmp)
        middle_still(cut)
        commonjs = (commonjs_src.replace("%TM%", json.dumps(TM)).replace("%W%", str(W)).replace("%H%", str(H))
                    .replace("%FPS%", str(FPS)))
        for name, start, end in SCENES:
            src = logo if name == "logo" else scene(name, cut, lang, common, commonjs, info)
            open(os.path.join(comp, f"{name}.html"), "w").write(src)
        open(os.path.join(out, "index.html"), "w").write(index(W, H, lang))
        cli = "npx --yes hyperframes@0.9.40"
        files = {
            "hyperframes.json": json.dumps({
                "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                "media": {"autoProxy": True}}, indent=2) + "\n",
            "meta.json": json.dumps({"id": f"socialstream-film-v6-{folder}", "name": f"SocialStream brand film v6 ({folder})",
                                     "createdAt": "2026-11-15T00:00:00.000Z"}, indent=2) + "\n",
            "package.json": json.dumps({"name": f"socialstream-film-v6-{folder}", "private": True, "type": "module",
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
        print(folder, W, H, lang)


if __name__ == "__main__":
    main()
