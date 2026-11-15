#!/usr/bin/env python3
"""The brand film v5, "Through the phone", as two HyperFrames projects on one clock: wide/ (1920 x 1080) and tall/
(1080 x 1920). The site crossfades between the two cuts, so every beat sits on the same frame in both.

One camera keeps moving: it dives into the logo's S, flies through the claim, through a stream of their reels,
into the FlyX reel, swipes through results inside the phone, comes back out, and ends in the reel wall the film
started with. SPEC.md has the shot list; the clock is TM below (seconds of the whole film), shared by every scene.

The scenes in scenes/ serve both cuts (the tall layout is in their portrait media queries and in the per-cut
numbers below); this script fills them in, adds the logo animation (the logo kit's make_motion.py, formats
film-wide and film-tall, which end by diving into the S), writes each project's index.html and project files, and
links each project's assets/ to ../assets. Run from this folder: python3 build.py   (then render; see README.md)
"""
import json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_TOOLS = os.path.normpath(os.path.join(HERE, "../../../../brand/socialstream-logo/tools"))
FPS = 25
CUTS = {"wide": (1920, 1080, "film-wide"), "tall": (1080, 1920, "film-tall")}
# each language gets both cuts: wide/ and tall/ (Hungarian), wide-en/ and tall-en/ (English, for the site in English)
OUTS = [("wide", "hu", "wide"), ("tall", "hu", "tall"), ("wide", "en", "wide-en"), ("tall", "en", "tall-en")]
# every line of the film in both languages; the English is the site's own English copy (content.mjs) where it has one
TEXT = {
    "hu": dict(
        lineA=('<div class="cl-txt"><div class="hd cl-a1"><W0>A</W0> <span class="ss"><W1>social</W1><br class="t"> '
               '<W2>media</W2></span></div><div class="it cl-a2"><W3>meghalt.</W3></div></div>'),
        lineB=('<div class="cl-txt"><div class="hd cl-b1"><W0>Az</W0><br class="t"> <W1 class="it">érdeklődés</W1></div>'
               '<div class="hd cl-b2"><W2>vette</W2> <W3>át</W3><br class="t"> <W4>a</W4> '
               '<W5>helyét<span class="acc">.</span></W5></div></div>'),
        flyx_eb="Élményközpont · Social &amp; video",
        pod_eb="Gyártás · Vágás · Feliratozás", pod1="Podcast &amp;", pod2="interjú",
        services=["Videó", "Social", "Hirdetés", "Weboldal", "Automatizáció", "Stratégia"],
        roas=(["legjobb", "eredmény"], "Ajtó webshop · Google PMax"),
        mft=(["bevétel", "egy", "hét", "alatt"], "B2B Meta kampány"),
        m300=(["kezelt", "hirdetési", "büdzsé"], "2022 óta az új korban"),
        win1='<span>Mi</span> <span>ebben</span><br class="t"> <span>a</span> <span>korban</span>', win2="győzünk",
    ),
    "en": dict(
        lineA=('<div class="cl-txt"><div class="hd cl-a1"><span class="ss"><W0>Social</W0><br class="t"> '
               '<W1>media</W1></span></div><div class="it cl-a2"><W2>is dead.</W2></div></div>'),
        lineB=('<div class="cl-txt"><div class="hd cl-b1"><W0 class="it">Interest</W0></div>'
               '<div class="hd cl-b2"><W1>has</W1> <W2>taken</W2><br class="t"> <W3>its</W3> '
               '<W4>place<span class="acc">.</span></W4></div></div>'),
        flyx_eb="Experience centre · Social &amp; video",
        pod_eb="Production · Editing · Subtitles", pod1="Podcast &amp;", pod2="interview",
        services=["Video", "Social", "Ads", "Website", "Automation", "Strategy"],
        roas=(["best", "result"], "Door webshop · Google PMax"),
        mft=(["revenue", "in", "one", "week"], "B2B Meta campaign"),
        m300=(["ad", "budget", "managed"], "In the new era since 2022"),
        win1='<span>In</span> <span>this</span> <span>era,</span>', win2="we win",
    ),
}
# Sora 700 digit widths (em, at the film's -0.05em tracking), so each odometer column is as wide as its own digit
DIGW = [0.713, 0.378, 0.582, 0.582, 0.622, 0.594, 0.637, 0.557, 0.617, 0.637]

# ---- the clock (seconds of the whole film) ----
TM = dict(
    total=35.4,
    dive0=3.25, dive0d=0.7,              # the camera dives into the logo's S (make_motion.py film formats)
    claim=3.85, strike=4.62, meghalt=5.0, claA_out=6.55,   # "A social media meghalt."
    claB=6.8, claB_out=8.85,                                 # "Az érdeklődés vette át a helyét."
    s0=8.9, land=11.3, f=1000, travel=6000,                  # the stream: the camera flies and brakes; FlyX lands
    flyxT=11.4,                          # FlyX Tenerife
    d1=13.85, d1d=0.55,                  # into the FlyX reel
    sw=0.38,                             # a swipe inside the phone
    swRoas=14.75, swMft=17.15, swPod=19.55,
    out1=19.9, out1d=0.7,                # out of the phone, onto the podcast reel
    svc0=23.05, svcStep=0.5, svcSw=0.3,  # the six services, one swipe each
    d2=26.05, d2d=0.6,                   # into the reel again; 300 M Ft swipes in
    swWin=28.85, swLast=31.35,
    back=31.75, backd=0.8,               # out into the wall
    closeBand=32.55, logoIn=32.85, logoOut=34.45, wallOut=34.55,
)
TOTAL = TM["total"]
assert abs(TOTAL * FPS - round(TOTAL * FPS)) < 1e-9

# the scenes: name, start, end; the order is the paint order (later is on top)
SCENES = [
    ("sky", 0.0, TOTAL),                          # the moving light behind everything
    ("open", 0.0, 4.0),                           # the reel wall and the night band
    ("claim", 3.8, TM["s0"] + 0.45),              # the claim, flying at the camera word by word
    ("flyx", TM["land"], TM["d1"] + TM["d1d"]),   # FlyX Tenerife, beside the reel (behind the phone)
    ("wall", TM["back"], TOTAL),                  # back out into the reel wall
    ("feed", TM["s0"], TM["back"]),               # the phone: lands, takes us inside, swipes, comes back out
    ("stream", TM["s0"], TM["land"]),             # their reels rushing past (in front of the phone)
    ("side", TM["out1"] + 0.2, TM["d2"] + 0.4),   # Podcast & interjú, the six services
    ("logo", 0.0, 4.0),                           # the logo builds itself, then the dive (generated)
    ("close", TM["closeBand"], TOTAL),            # the band and the logo, then back to the first frame
]

# ---- footage: (file in assets/clips without .mp4, box width, box height, offset into the file in s, focus x, focus y)
# boxes have the files' shape; scenes scale them to cover their cards, keeping the focus (0-1) as central as they can
FOOT = {
    "hero": ("ph-flyx", 1080, 1920, 0.0, 0.5, 0.5),          # the FlyX reel: lands, stands, fills the frame
    "pod": ("ph-pod", 1080, 1920, 0.0, 0.5, 0.62),           # the podcast reel: full frame (faces low), then the phone
    "svc": [("ph-svc-video", 1080, 1920, 0.0, 0.5, 0.5), ("ph-svc-social", 1080, 1920, 0.0, 0.5, 0.5),
            ("ph-svc-ads", 1080, 1920, 0.0, 0.5, 0.5), ("ph-svc-web", 1080, 1920, 0.0, 0.5, 0.5),
            ("ph-svc-auto", 1080, 1920, 0.0, 0.5, 0.5), ("ph-svc-strat", 1080, 1920, 0.0, 0.5, 0.5)],
    "last": {"wide": ("ph-last-wide", 1920, 1080, 0.0, 0.8, 0.4), "tall": ("ph-last-tall", 1080, 1920, 0.0, 0.5, 0.5)},  # the sun
    "stream": [f"st-{i:02d}" for i in range(1, 15)],   # 540 x 960 each
}
# footage that shows words, in each language's own version (the website reel is their site, scrolled in English)
FOOT_LANG = {"en": {"ph-svc-web": "ph-svc-web-en"}}

# ---- per cut: the phone and the type that has to fit ----
PHONE = {
    "wide": dict(w=400, r=28, flyx=(600, 540), pod=(1450, 540)),
    "tall": dict(w=560, r=36, flyx=(540, 1210), pod=(540, 1210)),
}
SVCSIZE = {"wide": 138, "tall": 118}

# ---- the reel wall (open and close): 7 rows x 9 columns of their reel stills, tilted ----
ROWS, COLS, CW, CH, GAP, TILT, DRIFT = 7, 9, 230, 409, 28, -10, 60
REELS = ["p02", "p03", "p04", "p05", "p06", "p07", "p08", "p09", "p10", "p11", "p13", "p14", "p15", "p16", "p17",
         "p18", "p19", "p20", "p21", "p22", "p23", "p24"]
WALL_W, WALL_H = COLS * CW + (COLS - 1) * GAP, ROWS * CH + (ROWS - 1) * GAP
WALL_CSS = f"""#root .wl-in {{ position: absolute; inset: 0; }}
    #root .wl-tilt {{ position: absolute; left: 50%; top: 50%; width: {WALL_W}px; height: {WALL_H}px; margin: {-WALL_H / 2}px 0 0 {-WALL_W / 2}px; transform: rotate({TILT}deg); }}
    #root .wl-wall {{ position: absolute; inset: 0; }}
    #root .wl-card {{ position: absolute; width: {CW}px; height: {CH}px; overflow: hidden; border-radius: 22px; background: #0b1024;
      box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12), 0 30px 60px -30px rgba(0, 0, 0, 0.8); }}
    #root .wl-card img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
    #root .wl-dim {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 50%, rgba(5, 7, 15, 0.45), rgba(5, 7, 15, 0.74)); }}
    #root .wl-band {{ position: absolute; left: 0; right: 0; top: 21.5%; height: 57%;
      background: linear-gradient(180deg, rgba(5, 7, 15, 0) 0%, #05070f 17.5%, #05070f 82.5%, rgba(5, 7, 15, 0) 100%); }}"""
MID_R, MID_C = ROWS // 2, COLS // 2       # the middle card, which the phone becomes at the end


def wall(skip_middle=False):
    cards = []
    for r in range(ROWS):
        for c in range(COLS):
            img = REELS[(r * 5 + c * 3) % len(REELS)]
            # the middle card stays in the grid (so the fly-in keeps its order) but hidden: the phone takes its place
            hide = ";visibility:hidden" if skip_middle and (r, c) == (MID_R, MID_C) else ""
            cards.append(f'<div class="wl-card" style="left:{c * (CW + GAP)}px;top:{r * (CH + GAP)}px{hide}">'
                         f'<img src="assets/reels/{img}.jpg" alt=""></div>')
    return "".join(cards)


# ---- the logo ----
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


# ---- the claim: each line drawn once per word ----
def copies(line, prefix, strike=False):
    n = len(re.findall(r"<W\d", line))
    out = []
    for k in range(n):
        s = re.sub(r"<W(\d)( class=\"([^\"]*)\")?>",
                   lambda m: f'<span class="w {"on" if int(m.group(1)) == k else "off"} {m.group(3) or ""}">', line)
        out.append(f'<div class="ff" id="{prefix}{k}">{re.sub(r"</W[0-9]>", "</span>", s)}</div>')
    if strike:
        s = re.sub(r"<W(\d)( class=\"([^\"]*)\")?>", lambda m: f'<span class="w ghost {m.group(3) or ""}">', line)
        out.append(f'<div class="ff strike" id="{prefix}s">{re.sub(r"</W[0-9]>", "</span>", s)}</div>')
    return "".join(out), n


# ---- the feed: slides inside the phone ----
def odo(prefix, digits):
    """An odometer: one column of 30 digits per figure, rolled to the third run; each column as wide as its digit."""
    cols = []
    for j, d in enumerate(digits):
        cells = "".join(f"<b>{i % 10}</b>" for i in range(30))
        cols.append(f'<span class="dg" style="width:{DIGW[int(d)]}em"><span class="ds" id="{prefix}-c{j}">{cells}</span></span>')
    return "".join(cols)


NUMBERS = {
    # id: digits, unit html, lights (x %, y %, size vmax, rgba)
    "roas": ("81", '<span class="x acc">×</span><span class="u">ROAS</span>',
             [(86, 78, 70, "136, 78, 255, 0.5"), (78, 8, 34, "255, 64, 104, 0.32")]),
    "mft": ("79", '<span class="ui">M Ft</span>', [(90, 30, 66, "66, 92, 255, 0.5"), (60, 100, 40, "255, 64, 104, 0.3")]),
    "m300": ("300", '<span class="ui">M Ft</span>', [(84, 86, 70, "120, 104, 255, 0.5"), (96, 10, 38, "56, 160, 255, 0.34")]),
}
WIN_LIGHTS = [(80, 85, 72, "255, 64, 104, 0.34"), (10, 0, 60, "136, 78, 255, 0.45")]


def lights(ls):
    return "".join(f'<i class="lt" style="left:{x}%;top:{y}%;width:{s}vmax;height:{s}vmax;margin:-{s / 2}vmax 0 0 -{s / 2}vmax;'
                   f'background:radial-gradient(closest-side, rgba({c}), rgba({c.rsplit(",", 1)[0]}, 0))"></i>'
                   for x, y, s, c in ls)


def number_slide(sid, lang):
    digits, unit, ls = NUMBERS[sid]
    words, eb = TEXT[lang][sid]
    lab = " ".join(f"<span>{w}</span>" for w in words)
    return (f'<div class="sl sl-t" id="sl-{sid}">{lights(ls)}<div class="nb">'
            f'<div class="eb" id="{sid}-eb"><span class="dot"></span>{eb}</div>'
            f'<div class="num">{odo(sid, digits)}{unit}</div>'
            f'<div class="lab" id="{sid}-lab">{lab}</div></div></div>')


def win_slide(lang):
    T = TEXT[lang]
    return (f'<div class="sl sl-t" id="sl-win">{lights(WIN_LIGHTS)}<div class="wn">'
            f'<div class="hd" id="wn-1">{T["win1"]}</div>'
            f'<div class="it" id="wn-2"><span>{T["win2"]}<span class="acc">.</span></span></div></div></div>')


def media_slide(sid, foot, start, dur, track, lang):
    f, bw, bh, ms, fx, fy = foot
    f = FOOT_LANG.get(lang, {}).get(f, f)
    return (f'<div class="sl media" id="sl-{sid}" style="width:{bw}px;height:{bh}px">'
            f'<video id="sl-v-{sid}" class="clip" src="assets/clips/{f}.mp4" data-start="{start:.2f}" data-duration="{dur:.2f}" '
            f'data-media-start="{ms:.2f}" data-hf-media-start-basis="local" data-track-index="{track}" muted playsinline></video></div>')


def feed(cut, lang):
    """The feed scene's slides, their timing, and the JS for the type slides."""
    T = TM
    s0 = T["s0"]
    svc_in = [T["svc0"] + i * T["svcStep"] for i in range(6)]
    # (id, kind, foot, swipe in at, swipe length, ease)
    order = [("flyx", "m", FOOT["hero"], None, 0, "")]
    order += [("roas", "t", None, T["swRoas"], T["sw"], "power3.inOut"),
              ("mft", "t", None, T["swMft"], T["sw"], "power3.inOut"),
              ("pod", "m", FOOT["pod"], T["swPod"], T["sw"], "power3.inOut")]
    order += [(f"svc{i}", "m", FOOT["svc"][i], svc_in[i], T["svcSw"], "power3.inOut") for i in range(6)]
    order += [("m300", "t", None, T["d2"], T["d2d"], "power3.inOut"),
              ("win", "t", None, T["swWin"], T["sw"], "power3.inOut"),
              ("last", "m", FOOT["last"][cut], T["swLast"], T["sw"], "power3.inOut")]
    html, data = [], []
    for i, (sid, kind, foot, tin, din, ease) in enumerate(order):
        nxt = order[i + 1][3] + order[i + 1][4] if i + 1 < len(order) else T["back"]
        t_on = s0 if tin is None else tin
        # each slide sits in a full-frame window (slw-), cut to the card's shape where the slide is, so a slide
        # that is larger than the card (footage scaled to cover it) moves as one card when it is swiped
        if kind == "m":
            start = max(0.0, t_on - 0.12 - s0)
            dur = min(T["back"] - s0, nxt - s0 + 0.12) - start
            html.append(f'<div class="slw" id="slw-{sid}">{media_slide(sid, foot, start, dur, i + 1, lang)}</div>')
            data.append(dict(id=f"sl-{sid}", win=f"slw-{sid}", kind="m", bw=foot[1], bh=foot[2], fx=foot[4], fy=foot[5],
                             tin=t_on, din=din, ease=ease or "none"))
        else:
            html.append(f'<div class="slw" id="slw-{sid}">{number_slide(sid, lang) if sid in NUMBERS else win_slide(lang)}</div>')
            data.append(dict(id=f"sl-{sid}", win=f"slw-{sid}", kind="t", tin=t_on, din=din, ease=ease))
    # the type slides' own motion
    js = []
    for sid, (digits, *_r) in NUMBERS.items():
        t_in = dict(roas=T["swRoas"], mft=T["swMft"], m300=T["d2"])[sid]
        d_in = T["d2d"] if sid == "m300" else T["sw"]
        land = t_in + d_in * 0.55
        js.append(f'tl.fromTo("#{sid}-eb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, AT({land - 0.1:.3f}));')
        for j, d in enumerate(digits):
            a = (int(d) + 4 + 3 * j) % 10          # where the column starts: not on its own digit
            js.append(f'tl.fromTo("#{sid}-c{j}", {{ yPercent: {-a / 30 * 100:.4f} }}, {{ yPercent: {-(20 + int(d)) / 30 * 100:.4f}, '
                      f'duration: 1.15, ease: "expo.out" }}, AT({land - 0.05 + 0.09 * j:.3f}));')
        js.append(f'tl.fromTo("#{sid}-lab span", {{ opacity: 0.12 }}, {{ opacity: 1, duration: 0.25, ease: "power1.out", stagger: 0.08 }}, AT({land + 0.55:.3f}));')
    wl = T["swWin"] + T["sw"] * 0.5
    js.append(f'tl.fromTo("#wn-1 span", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: 0.067 }}, AT({wl:.3f}));')
    js.append(f'tl.fromTo("#wn-2 > span", {{ opacity: 0, filter: "blur(10px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }}, AT({wl + 0.36:.3f}));')
    # the story bars: (shown from, to, segments)
    groups = [
        dict(**{"from": s0, "to": T["swPod"] + T["sw"] / 2}, segs=[[T["land"], T["swRoas"]], [T["swRoas"], T["swMft"]], [T["swMft"], T["swPod"]]]),
        dict(**{"from": T["swPod"] + T["sw"] / 2, "to": svc_in[0] + T["svcSw"] / 2}, segs=[[T["swPod"], svc_in[0]]]),
        dict(**{"from": svc_in[0] + T["svcSw"] / 2, "to": T["d2"] + T["d2d"] / 2}, segs=[[a, a + T["svcStep"]] for a in svc_in]),
        dict(**{"from": T["d2"] + T["d2d"] / 2, "to": T["back"] + 1}, segs=[[T["d2"], T["swWin"]], [T["swWin"], T["swLast"]], [T["swLast"], T["back"]]]),
    ]
    bars = "".join("<span><i></i></span>" for _ in range(6))
    return "".join(html), data, "\n    ".join(js), groups, bars


# ---- the stream: their reels standing in depth ----
def stream(cut):
    """The reels stand on a widening spiral around the camera's path (a tunnel of their work), one every 360 px of
    depth, so they pass the camera one after another and leave the frame at its edges before they get large."""
    w0 = 400 if cut == "wide" else 470
    rx, ry = (1000, 700) if cut == "wide" else (720, 1150)
    golden = math.pi * (3 - math.sqrt(5))
    reels, html = [], []
    n = len(FOOT["stream"])
    for i in range(n):
        ang = 0.9 + i * golden
        X, Y = rx * math.cos(ang), ry * math.sin(ang)
        Z = 2400 + 4000 * i / (n - 1)
        k = 0.9 + 0.2 * ((i * 5) % n) / n
        w, h = w0 * k, w0 * k * 16 / 9
        reels.append(dict(X=round(X, 1), Y=round(Y, 1), Z=round(Z, 1), w=round(w, 1), h=round(h, 1)))
        html.append(f'<div class="reel" id="st-r{i}" style="width:{w:.1f}px;height:{h:.1f}px;border-radius:{w * 0.07:.1f}px;visibility:hidden">'
                    f'<video id="st-v{i}" class="clip" src="assets/clips/{FOOT["stream"][i]}.mp4" data-start="0" '
                    f'data-duration="{TM["land"] - TM["s0"]:.2f}" data-track-index="{i + 1}" muted playsinline></video></div>')
    return "\n    ".join(html), reels


# ---- filling the scenes ----
def fill(src, **kw):
    for k, v in kw.items():
        src = src.replace(f"%{k}%", str(v))
    left = re.findall(r"%[A-Z0-9]+%", src)
    assert not left, f"unfilled placeholders: {left}"
    return src


def scene(name, cut, lang, common, commonjs, logo_css):
    W, H = CUTS[cut][:2]
    start = next(s for n, s, e in SCENES if n == name)
    src = open(os.path.join(HERE, "scenes", f"{name}.html")).read()
    src = src.replace("/*COMMON*/", common).replace("/*COMMONJS*/", commonjs.replace("%START%", f"{start:g}"))
    src = src.replace("/*WALLCSS*/", WALL_CSS)
    kw = dict(W=W, H=H)
    if name == "sky":
        kw["TOTAL"] = f"{TOTAL:g}"
    if name == "open":
        src = src.replace("<!--WALL-->", wall())
        kw.update(ROWS=ROWS, COLS=COLS)
    if name == "wall":
        src = src.replace("<!--WALL-->", wall(skip_middle=True))
        f, bw, bh, ms, fx, fy = FOOT["last"][cut]
        # the phone's last slide started swiping in at swLast; carry on from where it is at TM.back
        ms2 = ms + (TM["back"] - (TM["swLast"] - 0.12))
        hero = (f'<div class="media" id="wa-m" style="width:{bw}px;height:{bh}px"><video id="wa-v" class="clip" '
                f'src="assets/clips/{f}.mp4" data-start="0" data-duration="{TOTAL - TM["back"]:.2f}" '
                f'data-media-start="{ms2:.2f}" data-track-index="1" muted playsinline></video></div>')
        kw.update(ROWS=ROWS, COLS=COLS, HERO=hero, HERODATA=json.dumps(dict(bw=bw, bh=bh, fx=fx, fy=fy)),
                  SLOT=json.dumps(dict(w=CW, h=CH, r=22, tilt=TILT, x0=DRIFT)))
    if name == "claim":
        a, na = copies(TEXT[lang]["lineA"], "cl-a", strike=True)
        b, nb = copies(TEXT[lang]["lineB"], "cl-b")
        kw.update(LINEA=a, LINEB=b, NA=na - 1, NB=nb)          # line A: every word but the last comes from depth
    if name == "stream":
        html, reels = stream(cut)
        kw.update(REELS=html, REELDATA=json.dumps(reels))
    if name == "feed":
        html, data, js, groups, bars = feed(cut, lang)
        P = PHONE[cut]
        kw.update(SLIDES=html, SLIDEDATA=json.dumps(data), SLIDEJS=js, BARGROUPS=json.dumps(groups), BARS=bars,
                  PHONE=json.dumps(dict(w=P["w"], h=round(P["w"] * 16 / 9, 2), r=P["r"], flyx=P["flyx"], pod=P["pod"])))
    if name == "side":
        svc = TEXT[lang]["services"]
        names = "".join(f'<div class="hd" id="sd-n{i}">{t}<span class="acc">.</span></div>' for i, t in enumerate(svc))
        kw.update(NAMES=names, NSVC=len(svc), SVCSIZE=SVCSIZE[cut], PODEB=TEXT[lang]["pod_eb"], POD1=TEXT[lang]["pod1"],
                  POD2=TEXT[lang]["pod2"])
    if name == "flyx":
        kw.update(FXEB=TEXT[lang]["flyx_eb"])
    if name == "close":
        kw.update(LOGOBOX=logo_css)
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
    <title>SocialStream brand film ({W}x{H}, {lang})</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #05070f; }}
      #main {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <!-- motion blur at render time: fast moves (swipes, the phone growing, the stream) are smeared along their path -->
    <div id="main" data-motion-blur="on" data-composition-id="main" data-start="0" data-duration="{TOTAL:g}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
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
    only = sys.argv[1:]                                   # e.g. python3 build.py wide-en
    for cut, lang, folder in OUTS:
        if only and folder not in only:
            continue
        W, H, fmt = CUTS[cut]
        out = os.path.join(HERE, folder)
        comp = os.path.join(out, "compositions")
        os.makedirs(comp, exist_ok=True)
        for old in os.listdir(comp):                      # scenes v4 had and v5 does not
            if old.endswith(".html") and old[:-5] not in [n for n, s, e in SCENES]:
                os.remove(os.path.join(comp, old))
        tmp = os.path.join(HERE, ".logo-" + folder)
        logo, info = logo_scene(fmt, tmp)
        css = logo_box(info)
        commonjs = (commonjs_src.replace("%TM%", json.dumps(TM)).replace("%W%", str(W)).replace("%H%", str(H))
                    .replace("%FPS%", str(FPS)))
        for name, start, end in SCENES:
            src = logo if name == "logo" else scene(name, cut, lang, common, commonjs, css)
            open(os.path.join(comp, f"{name}.html"), "w").write(src)
        open(os.path.join(out, "index.html"), "w").write(index(W, H, lang))
        cli = "npx --yes hyperframes@0.9.40"
        files = {
            "hyperframes.json": json.dumps({
                "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                "media": {"autoProxy": True}}, indent=2) + "\n",
            "meta.json": json.dumps({"id": f"socialstream-film-{folder}", "name": f"SocialStream brand film ({folder})",
                                     "createdAt": "2026-11-15T00:00:00.000Z"}, indent=2) + "\n",
            "package.json": json.dumps({"name": f"socialstream-film-{folder}", "private": True, "type": "module",
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
        print(folder, W, H, lang, "logo box:", css)


if __name__ == "__main__":
    main()
