#!/usr/bin/env python3
"""The SocialStream sizzle (2026-11-15): a brand film built on the grammar of the Social Chain 2026 sizzle the
founder sent as the reference ("i want it more like that"): every beat says something and shows something happening.
A problem, the claim, what SocialStream does (their clients' reels rising in phones, real comments popping, views
counting up), what it brought (each result with its own client's words), the clients' voices piling up, the promise,
the logo. SocialStream's own type and colours, not Social Chain's look.

Every line is the site's own copy (content.mjs) or a real number or comment (FlyX Tenerife's and Prof Enzo's Facebook
pages, read on 2026-11-15); comments show their words only, not who wrote them. SPEC.md has the beats; T below is the
clock. Run from this folder: python3 build.py   (writes wide/; then render, see README.md)
"""
import json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_TOOLS = os.path.normpath(os.path.join(HERE, "../../../../brand/socialstream-logo/tools"))
FPS, W, H = 25, 1920, 1080
WIPE = 0.32                                   # each scene comes in over the last with a diagonal wipe

# ---- the scenes: id, start, end (seconds of the film) ----
# ---- the music: "What About Action" (Mixkit, free licence; in their CapCut folder), 121 bpm. The film starts 55.975 s
# into it, near the end of its breakdown, so the drop (63.255 s) lands on the turn at 7.28 s; after it, every scene
# lands on a beat (BEAT apart, counted from the drop, never added up) ----
MUSIC, MUSIC_AT = "what-about-action", 55.975
DROP, BEAT = 7.28, 0.4952


def b(k):
    return round((DROP + k * BEAT) * FPS) / FPS


# ---- the scenes: id, start, end (seconds of the film); a scene's content lands when its wipe ends, on a beat ----
LAND = {"make": b(4), "ads": b(10), "measure": b(18), "r1": b(22), "r2": b(30), "r3": b(36), "r4": b(44),
        "voices": b(52), "close": b(60)}
ORDER = ["make", "ads", "measure", "r1", "r2", "r3", "r4", "voices", "close"]
TOTAL = round(b(67) + 2.12, 2)                # the logo's line lands on beat 67 and holds over 2 s
SC = [
    ("open", 0.00, 3.04),       # the reel wall flies in, the logo builds itself
    ("logo", 0.00, 3.04),       # the logo's build (the kit's film-end format), over the opening's wall, under the next wipe
    ("problem", 2.72, LAND["make"]),   # Posztolsz. Hirdetsz. Mégsem jönnek a vevők? / the claim; the turn on the drop
] + [(n, round(LAND[n] - WIPE, 2), LAND[ORDER[i + 1]] if i + 1 < len(ORDER) else TOTAL) for i, n in enumerate(ORDER)]
for n, a, z in SC:                            # (not b: that is the beat)
    for x in (a, z):
        assert abs(x * FPS - round(x * FPS)) < 1e-6, (n, x)

# ---- helpers for every scene's script ----
JS = r"""
    const FPS = 25, W = 1920, H = 1080, START = %START%, AT = (t) => t - START;
    const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v), EZ = {};
    const ez = (n, p) => (EZ[n] || (EZ[n] = gsap.parseEase(n)))(clamp01(p));
    const tl = gsap.timeline({ paused: true });
    // the scene comes in over the last one with a wipe: diagonal from the right or the left, up, or an iris
    const WIPES = {
      dr: ["polygon(132% 0%, 132% 0%, 132% 100%, 162% 100%)", "polygon(-32% 0%, 132% 0%, 132% 100%, -2% 100%)"],
      dl: ["polygon(-32% 0%, -32% 0%, -62% 100%, -32% 100%)", "polygon(-32% 0%, 132% 0%, 102% 100%, -32% 100%)"],
      up: ["polygon(0% 100%, 100% 100%, 100% 100%, 0% 100%)", "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)"],
      iris: ["circle(0% at 50% 50%)", "circle(75% at 50% 50%)"],
    };
    const wipeIn = (t, k = "dr") => tl.fromTo("#wp", { clipPath: WIPES[k][0] }, { clipPath: WIPES[k][1], duration: %WIPE%, ease: "power3.inOut" }, AT(t));
    // words land by focus and opacity, a little apart; a line goes out of focus
    const words = (sel, t, st = 0.07) => tl.fromTo(sel, { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: st }, AT(t));
    const out = (sel, t) => tl.fromTo(sel, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.16, ease: "power2.in", immediateRender: false }, AT(t));
    // a card pops: scale with a little overshoot (position may bounce, opacity never)
    const pop = (sel, t, d = 0.45) => { tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.12, ease: "none" }, AT(t));
      tl.fromTo(sel, { scale: 0.55, y: 30 }, { scale: 1, y: 0, duration: d, ease: "back.out(1.7)" }, AT(t)); };
    // a phone rises from below the frame, leaning, and settles
    const rise = (sel, t, r0, r1) => tl.fromTo(sel, { y: 980, rotation: r0 }, { y: 0, rotation: r1, duration: 0.72, ease: "expo.out" }, AT(t));
    // slow light in a field
    const drift = (sel, t, d, dx, dy) => tl.fromTo(sel, { x: 0, y: 0 }, { x: dx, y: dy, duration: d, ease: "sine.inOut" }, AT(t));
    // a counted number: fixed-width digit boxes, written once per frame as the value changes, never smeared
    const count = (el, t, dur, to, ease = "expo.out") => {
      const ds = [...el.querySelectorAll(".d")]; let last = null;
      for (let i = 0; i <= Math.round(dur * FPS); i++) {
        const tt = t + i / FPS, v = Math.round(to * ez(ease, (tt - t) / dur));
        if (v === last) continue; last = v;
        const s = String(v).padStart(ds.length, " ");
        ds.forEach((d, k) => tl.set(d, { textContent: s[k] === " " ? "" : s[k] }, Math.max(0, AT(tt) - 0.01)));
      }
    };"""


def lights(ls):
    return "".join(f'<i class="lt" id="{i}" data-layout-allow-overflow style="left:{x}%;top:{y}%;width:{s}vmax;height:{s}vmax;'
                   f'margin:-{s / 2}vmax 0 0 -{s / 2}vmax;background:radial-gradient(closest-side,rgba({c}),rgba({c.rsplit(",", 1)[0]},0))"></i>'
                   for i, x, y, s, c in ls)


def field(bg, ls):
    return f'<div class="fld" style="background:{bg}">{lights(ls)}</div>'


def phone(pid, left, top, src, start, dur, track, media=0.0):
    return (f'<div class="phone" id="{pid}" style="left:{left}px;top:{top}px"><div class="scr">'
            f'<video id="{pid}-v" class="clip" src="assets/clips/{src}.mp4" data-start="{start:g}" data-duration="{dur:g}" '
            f'data-media-start="{media:g}" data-hf-media-start-basis="local" data-track-index="{track}" muted playsinline></video>'
            f'</div><div class="isl"></div></div>')


def bubble(bid, left, top, src, text, cls="", width=None):
    w = f";width:{width}px" if width else ""
    return (f'<div class="bub {cls}" id="{bid}" style="left:{left}px;top:{top}px{w}"><span class="av"></span>'
            f'<span class="src">{src}</span>{text}</div>')


def digits(n, cid, gap_after=None):
    gap = ' style="margin-right:0.16em"'
    ds = "".join(f'<span class="d"{gap if gap_after == k else ""}></span>' for k in range(n))
    return f'<span class="cnt" id="{cid}" data-motion-blur="off">{ds}</span>'


def wl(text, cls=""):
    return " ".join(f'<span class="w {cls}">{w}</span>' for w in text.split())


# ---- the reel wall (open and close): 7 x 9 stills of their footage, tilted, none twice on screen ----
ROWS, COLS, CW, CH, GAP, TILT = 7, 9, 230, 409, 28, -10
TILES = [f"t{i:02d}" for i in range(1, 29)]
WALL_W, WALL_H = COLS * CW + (COLS - 1) * GAP, ROWS * CH + (ROWS - 1) * GAP
WALL_CSS = f"""#root .wl-in {{ position: absolute; inset: 0; }}
    #root .wl-tilt {{ position: absolute; left: 50%; top: 50%; width: {WALL_W}px; height: {WALL_H}px; margin: {-WALL_H / 2}px 0 0 {-WALL_W / 2}px; transform: rotate({TILT}deg); }}
    #root .wl-wall {{ position: absolute; inset: 0; }}
    #root .wl-card {{ position: absolute; width: {CW}px; height: {CH}px; overflow: hidden; border-radius: 22px; background: #0b1024;
      box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12), 0 30px 60px -30px rgba(0, 0, 0, 0.8); }}
    #root .wl-card img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
    #root .wl-dim {{ position: absolute; inset: 0; background: rgba(5, 7, 15, 0.2); }}
    #root .glow {{ position: absolute; inset: 0; background: radial-gradient(ellipse 30% 44% at 50% 50%, rgba(5, 7, 15, 0.95) 0%, rgba(5, 7, 15, 0.76) 44%, rgba(5, 7, 15, 0) 100%); }}"""


def wall():
    a, vis = math.radians(TILT), []
    for r in range(ROWS):
        for c in range(COLS):
            x0, y0 = c * (CW + GAP) - WALL_W / 2, r * (CH + GAP) - WALL_H / 2
            pts = [(W / 2 + x * math.cos(a) - y * math.sin(a), H / 2 + x * math.sin(a) + y * math.cos(a))
                   for x, y in ((x0, y0), (x0 + CW, y0), (x0, y0 + CH), (x0 + CW, y0 + CH))]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            if max(xs) > -60 and min(xs) < W + 60 and max(ys) > 0 and min(ys) < H:
                vis.append((r, c))
    vis.sort(key=lambda rc: abs(rc[0] - ROWS // 2) * 2 + abs(rc[1] - COLS // 2))
    m = {rc: TILES[(k * 11) % len(TILES)] for k, rc in enumerate(vis[:len(TILES)])}
    rest = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in m]
    m.update({rc: TILES[(k * 5 + 3) % len(TILES)] for k, rc in enumerate(rest)})
    return "".join(f'<div class="wl-card" style="left:{c * (CW + GAP)}px;top:{r * (CH + GAP)}px">'
                   f'<img src="assets/tiles/{m[(r, c)]}.jpg" alt=""></div>' for r in range(ROWS) for c in range(COLS))


def logo_scene(tmp):
    out = subprocess.run([sys.executable, "make_motion.py", "film-end-wide", "--out", tmp], cwd=LOGO_TOOLS, check=True,
                         capture_output=True, text=True).stdout
    info = json.loads(out[out.index("{"):out.rindex("}") + 1])
    return open(os.path.join(tmp, "compositions", "logo.html")).read(), info


def logo_box(info):
    (x0, y0), (x1, y1) = info["lockup_px"]
    svg = open(os.path.join(HERE, "assets", "logo", "socialstream-logo-stacked-dark.svg")).read()
    wk, hk = [float(v) for v in svg.split('viewBox="')[1].split('"')[0].split()[2:4]]
    f = (y1 - y0) / (hk * 0.8)
    left, top = x0 - (wk - (x1 - x0) / f) / 2 * f, y0 - hk * 0.10 * f
    return f"left:{left:.3f}px;top:{top:.3f}px;width:{wk * f:.3f}px;height:{hk * f:.3f}px"


# ---- the scenes ----
def scene_open(s, e, info):
    html = f"""<div class="wl-in ff" data-layout-allow-overflow id="op-in">
      <div class="wl-tilt"><div class="wl-wall" id="op-wall">{wall()}</div></div>
      <div class="wl-dim"></div></div>
    <div class="glow" id="op-glow"></div>"""
    js = """
    // frame 0 is the thumbnail: the wall is already there, faint and large, and settles
    tl.fromTo("#op-wall .wl-card", { opacity: 0.3, scale: 1.25 }, { opacity: 1, scale: 1, duration: 0.8, ease: "expo.out", stagger: { grid: [7, 9], from: "center", amount: 0.6 } }, 0);
    tl.fromTo("#op-wall", { x: 40 }, { x: -20, duration: 3.04, ease: "none" }, 0);
    tl.fromTo("#op-glow", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.out" }, 0.1);"""
    return html, js, WALL_CSS


def scene_problem(s, e):
    t_turn = 7.28
    feed = "".join('<div class="sk"><i class="sa"></i><i class="sl1"></i><i class="sl2"></i><i class="sm"></i></div>' for _ in range(8))
    html = f"""<div class="fld" style="background:#05070f">{lights([("pb-l0", 15, 10, 90, "66, 92, 255, 0.28"), ("pb-l1", 90, 95, 80, "136, 78, 255, 0.25")])}</div>
    <div class="fld" id="pb-flood" style="background:linear-gradient(140deg,#2a1690 0%,#5a24c8 55%,#1b0f55 100%)">{lights([("pb-l2", 85, 15, 100, "255, 64, 104, 0.45"), ("pb-l3", 5, 95, 90, "56, 160, 255, 0.5")])}</div>
    <div class="phone" id="pb-p0" style="left:1080px;top:160px"><div class="scr"><div class="skf" id="pb-f0">{feed}</div>
      <video id="pb-v0" class="clip" src="assets/clips/flyx-turn.mp4" data-start="{t_turn - s - 0.1:g}" data-duration="{e - t_turn + 0.1:g}" data-media-start="0" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video></div><div class="isl"></div></div>
    <div class="phone" id="pb-p1" style="left:1480px;top:110px"><div class="scr"><div class="skf" id="pb-f1">{feed}</div>
      <video id="pb-v1" class="clip" src="assets/clips/andras-pod.mp4" data-start="{t_turn - s - 0.1:g}" data-duration="{e - t_turn + 0.1:g}" data-media-start="0.6" data-hf-media-start-basis="local" data-track-index="2" muted playsinline></video></div><div class="isl"></div></div>
    <div class="tx" id="pb-a"><div class="hd l1">{wl("Posztolsz.")}</div><div class="hd l1">{wl("Hirdetsz.")}</div>
      <div class="hd l2">{wl("Mégsem jönnek")}</div><div class="hd l2"><span class="w">a</span> <span class="w acc">vevők?</span></div></div>
    <div class="tx" id="pb-b"><div class="hd l3"><span class="w">A</span> <span class="ss"><span class="w">social</span> <span class="w">media</span><i class="stk" id="pb-stk"></i></span></div>
      <div class="it l4" id="pb-m">meghalt.</div></div>
    <div class="tx" id="pb-c"><div class="hd l3"><span class="w">Az</span> <span class="w it big">érdeklődés</span></div>
      <div class="hd l3">{wl("vette át")}</div><div class="hd l3"><span class="w">a</span> <span class="w">helyét<span class="acc">.</span></span></div></div>"""
    css = """
    #root .tx { position: absolute; left: 120px; top: 200px; width: 940px; }
    #root .l1 { font-size: 150px; margin-bottom: 6px; }
    #root .l2 { font-size: 118px; }
    #root .l3 { font-size: 120px; white-space: nowrap; }
    #root .l3 .big { font-size: 150px; }
    #root .l4 { font-size: 240px; line-height: 0.95; margin-left: 160px; }
    #root .ss { position: relative; display: inline-block; }
    #root .stk { position: absolute; left: -0.03em; right: -0.03em; top: 0.5em; height: 0.08em; border-radius: 0.04em; background: #ff5272; transform-origin: 0 50%; }
    #root .skf { position: absolute; left: 0; top: 0; width: 100%; padding: 70px 18px 0; }
    #root .sk { height: 300px; margin-bottom: 18px; border-radius: 22px; background: #1a1f2d; position: relative; }
    #root .sk i { position: absolute; display: block; border-radius: 8px; background: #2a3042; }
    #root .sk .sa { left: 18px; top: 18px; width: 44px; height: 44px; border-radius: 50%; }
    #root .sk .sl1 { left: 76px; top: 24px; width: 150px; height: 14px; }
    #root .sk .sl2 { left: 76px; top: 46px; width: 100px; height: 12px; }
    #root .sk .sm { left: 18px; right: 18px; top: 80px; bottom: 18px; border-radius: 14px; }
    #root .phone .scr video { opacity: 0; }"""
    js = f"""
    wipeIn({s:g});
    drift("#pb-l0", {s:g}, {e - s:g}, 80, 40); drift("#pb-l1", {s:g}, {e - s:g}, -60, -40);
    rise("#pb-p0", {s + 0.1:g}, -12, -4); rise("#pb-p1", {s + 0.22:g}, 10, 5);
    // the grey feed scrolls on and on, nothing in it
    tl.fromTo(["#pb-f0", "#pb-f1"], {{ y: 0 }}, {{ y: -1500, duration: {t_turn - s:g}, ease: "none" }}, AT({s:g}));
    words("#pb-a .l1:nth-child(1) .w", 3.08); words("#pb-a .l1:nth-child(2) .w", 3.56); words("#pb-a .l2 .w", 4.04, 0.08);
    out("#pb-a", 5.56);
    words("#pb-b .l3 .w", 5.72);
    tl.fromTo("#pb-stk", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.26, ease: "power3.out" }}, AT(6.2));
    tl.fromTo("#pb-b .ss .w", {{ opacity: 1 }}, {{ opacity: 0.4, duration: 0.3, ease: "power2.out", immediateRender: false }}, AT(6.32));
    tl.fromTo("#pb-m", {{ opacity: 0, filter: "blur(12px)", scale: 1.04 }}, {{ opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.3, ease: "power2.out" }}, AT(6.44));
    out("#pb-b", 7.12);
    // the turn: the ground floods with colour and the phones play their real reels
    tl.fromTo("#pb-flood", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.inOut" }}, AT({t_turn:g}));
    tl.fromTo(["#pb-v0", "#pb-v1"], {{ opacity: 0, clipPath: "inset(100% 0% 0% 0%)" }}, {{ opacity: 1, clipPath: "inset(0% 0% 0% 0%)", duration: 0.4, ease: "power3.out" }}, AT({t_turn:g}));
    tl.fromTo(["#pb-p0", "#pb-p1"], {{ scale: 1 }}, {{ scale: 1.06, duration: 0.5, ease: "back.out(1.6)", immediateRender: false }}, AT({t_turn:g}));
    words("#pb-c .w", {t_turn + 0.08:g}, 0.08);
    drift("#pb-l2", {t_turn:g}, {e - t_turn:g}, -80, 50); drift("#pb-l3", {t_turn:g}, {e - t_turn:g}, 70, -40);"""
    return html, js, css


def scene_case(s, e, cid, bg, ls, eyebrow, line1, line2, phones, extras_html, extras_js, css_extra=""):
    t0 = s + WIPE
    html = (f"{field(bg, ls)}<div class='cl' id='{cid}-t'><div class='eb' id='{cid}-eb'>{eyebrow}</div>"
            f"<div class='hd cl1'>{wl(line1)}</div><div class='hd cl1'>{line2}</div></div>")
    js = [f"wipeIn({s:g});"]
    for i, l in enumerate(ls):
        js.append(f'drift("#{l[0]}", {s:g}, {e - s:g}, {70 if i % 2 else -80}, {-50 if i % 2 else 60});')
    for k, (left, top, src, r0, r1, media) in enumerate(phones):
        html += phone(f"{cid}-p{k}", left, top, src, 0, round(e - s, 4), k + 1, media)
        js.append(f'rise("#{cid}-p{k}", {s + 0.04 + 0.12 * k:g}, {r0}, {r1});')
    js.append(f'tl.fromTo("#{cid}-eb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out" }}, AT({t0:g}));')
    js.append(f'words("#{cid}-t .cl1 .w", {t0 + 0.06:g}, 0.08);')
    js.append(f'out("#{cid}-t", {e - WIPE - 0.02:g});')
    css = """
    #root .cl { position: absolute; left: 120px; top: 110px; width: 900px; }
    #root .cl .cl1 { font-size: 112px; white-space: nowrap; }
    #root .cl .cl1 .it { font-size: 132px; }""" + css_extra
    return html + extras_html, "\n    ".join(js) + extras_js, css


def scene_make(s, e):
    bts = [("t14", 110, 600, -7), ("t22", 330, 690, 5), ("t10", 560, 620, -4), ("t23", 760, 700, 6)]
    ex = "".join(f'<div class="bts" id="mk-c{k}" style="left:{x}px;top:{y}px"><img src="assets/tiles/{t}.jpg" alt=""></div>'
                 for k, (t, x, y, r) in enumerate(bts))
    ejs = "".join(f'\n    pop("#mk-c{k}", {s + 1.0 + 0.24 * k:g}); tl.set("#mk-c{k}", {{ rotation: {r} }}, 0);' for k, (t, x, y, r) in enumerate(bts))
    css = """
    #root .bts { position: absolute; width: 190px; height: 338px; border-radius: 22px; overflow: hidden; background: #0b1024;
      box-shadow: 0 0 0 4px #fff, 0 30px 60px -24px rgba(0, 0, 0, 0.6); transform-origin: 50% 100%; }
    #root .bts img { width: 100%; height: 100%; object-fit: cover; }"""
    return scene_case(s, e, "mk", "linear-gradient(140deg,#3a1aa8 0%,#7a2bd0 55%,#24105e 100%)",
                      [("mk-l0", 92, 8, 100, "255, 64, 104, 0.45"), ("mk-l1", 4, 96, 90, "56, 160, 255, 0.5")],
                      "Gyenis András · Podcast &amp; interjú", "Mi gyártjuk", '<span class="w">a</span> <span class="w it">videót.</span>',
                      [(1090, 170, "andras-pod", -12, -4, 0.0), (1500, 110, "andras-reel", 10, 5, 0.0)], ex, ejs, css)


def scene_ads(s, e):
    t0 = s + WIPE
    ex = ('<div class="pill" id="ad-pill" style="left:1530px;top:938px"><i></i>'
          + digits(2, "ad-cnt") + 'K megtekintés egy reelen</div>'
          + bubble("ad-b0", 110, 470, "Komment · FlyX Tenerife", "It was brilliant fun… highly recommended it")
          + bubble("ad-b1", 170, 636, "Komment · FlyX Tenerife", "A fantastic experience, absolutely loved it.")
          + bubble("ad-b2", 120, 800, "Komment · FlyX Tenerife", "Enjoyable half hour. Friendly staff.")
          + bubble("ad-b3", 190, 944, "Komment · FlyX Tenerife", "Where is it please?", width=440))
    ejs = (f'\n    pop("#ad-pill", {t0 + 0.495:g}, 0.4); count(document.getElementById("ad-cnt"), {t0 + 0.55:g}, 0.9, 69);'
           + "".join(f'\n    pop("#ad-b{k}", {t0 + 0.74 + 0.495 * k:g});' for k in range(4)))
    css = """
    #root .bub { width: 600px; }
    #root .pill .cnt .d { width: 0.6em; }"""
    return scene_case(s, e, "ad", "linear-gradient(135deg,#f2561f 0%,#ff3f6c 58%,#b82a92 100%)",
                      [("ad-l0", 12, 96, 90, "255, 206, 92, 0.5"), ("ad-l1", 96, 4, 80, "110, 64, 255, 0.5")],
                      "FlyX Tenerife · Élményközpont", "Mi futtatjuk", '<span class="w">a</span> <span class="w it">hirdetést.</span>',
                      [(1090, 170, "flyx-ad", -12, -4, 0.0), (1500, 110, "flyx-reel", 10, 5, 0.0)], ex, ejs, css)


def scene_measure(s, e):
    t0 = s + WIPE
    html = (field("#05070f", [("ms-l0", 80, 80, 90, "255, 64, 104, 0.4"), ("ms-l1", 10, 10, 80, "66, 92, 255, 0.4")])
            + f'<div class="mt" id="ms-t"><div class="hd m1">{wl("És mi mérjük,")}</div>'
              f'<div class="hd m1"><span class="w">mit</span> <span class="w it">hozott.</span></div></div>')
    js = f"""wipeIn({s:g}); drift("#ms-l0", {s:g}, {e - s:g}, -60, -40); drift("#ms-l1", {s:g}, {e - s:g}, 60, 40);
    words("#ms-t .w", {t0 + 0.04:g}, 0.09); out("#ms-t", {e - WIPE - 0.02:g});"""
    css = """
    #root .mt { position: absolute; left: 160px; top: 300px; }
    #root .m1 { font-size: 170px; white-space: nowrap; }
    #root .m1 .it { font-size: 210px; }"""
    return html, js, css


WINS = {
    "w1": dict(bg="linear-gradient(140deg,#1b34c4 0%,#4a20b8 58%,#1d1060 100%)",
               ls=[(90, 90, 100, "255, 64, 104, 0.55"), (6, 4, 80, "56, 160, 255, 0.5")], obj="o-hall-mix",
               eb="Csarnoképítő ügyfél · Meta", n=79, nd=2, unit='<span class="it ui">M Ft</span>',
               lab="Bevétel egy hét alatt, egy B2B kampányból.",
               quote=("Csarnoképítő ügyfél · B2B", "„…annyi ajánlatkérésünk lett, mint korábban fél év alatt összesen.”")),
    "w2": dict(bg="linear-gradient(140deg,#ff3f6c 0%,#a42aa8 55%,#3a1690 100%)",
               ls=[(8, 92, 90, "255, 160, 80, 0.45"), (96, 6, 90, "66, 92, 255, 0.55")], obj="o-door-mix",
               eb="Ajtó webshop · Google Performance Max", n=81, nd=2,
               unit='<span class="x">×</span><span class="u">ROAS</span>', lab="1 forint hirdetésből 81 forint bevétel.", quote=None),
    "w3": dict(bg="linear-gradient(140deg,#4a1fb8 0%,#2a2fc4 55%,#101a66 100%)",
               ls=[(94, 90, 100, "255, 64, 104, 0.5"), (4, 6, 80, "136, 78, 255, 0.55")], obj="o-watch-mix",
               eb="Karóra webshop · Karácsony", n=23, nd=2,
               unit='<span class="x acc">×</span><span class="u">ROAS</span>', lab="Ünnepi kampány, több mint 8M Ft bevétellel.",
               quote=("Karóra webshop", "„…az ünnepi szezon nekünk dolgozik – nem ellenünk.”")),
    "w4": dict(bg="linear-gradient(140deg,#1d7be0 0%,#3a2fc4 55%,#2a1270 100%)",
               ls=[(92, 8, 90, "255, 64, 104, 0.45"), (6, 94, 90, "136, 78, 255, 0.55")], obj="o-webinar-mix",
               eb="Egészségügyi webinár", n=105, nd=3, unit='<span class="it ui">Ft</span>',
               lab="Ennyibe került egy jelentkező.", pill=5700,
               quote=("Egészségügyi szolgáltató", "„…majdnem 5700-nál állt meg, alig hittük el…”")),
}


def scene_win(s, e, wid):
    d, t0 = WINS[wid], s + WIPE
    ls = [(f"{wid}-l{k}",) + l for k, l in enumerate(d["ls"])]
    html = (field(d["bg"], ls)
            + f'<img id="{wid}-obj" src="assets/img/{d["obj"]}.webp" alt="" style="position:absolute;left:1240px;top:90px;width:540px;height:540px">'
            + f'<div class="wn" id="{wid}-t"><div class="eb" id="{wid}-eb">{d["eb"]}</div>'
              f'<div class="hd num" id="{wid}-num">{digits(d["nd"], wid + "-cnt")}{d["unit"]}</div>'
              f'<div class="lab" id="{wid}-lab">{wl(d["lab"])}</div></div>')
    js = [f"wipeIn({s:g});"] + [f'drift("#{l[0]}", {s:g}, {e - s:g}, {70 if k % 2 else -80}, {-50 if k % 2 else 60});' for k, l in enumerate(ls)]
    js += [f'tl.fromTo("#{wid}-obj", {{ opacity: 0, y: 90, scale: 0.85 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.7, ease: "expo.out" }}, AT({t0 - 0.06:g}));',
           f'tl.fromTo("#{wid}-obj", {{ rotation: -2 }}, {{ rotation: 2, duration: {e - s:g}, ease: "sine.inOut" }}, AT({s:g}));',
           f'tl.fromTo("#{wid}-eb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out" }}, AT({t0:g}));',
           f'tl.fromTo("#{wid}-num", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "none" }}, AT({t0 + 0.04:g}));',
           f'count(document.getElementById("{wid}-cnt"), {t0 + 0.04:g}, 1.0, {d["n"]});',
           f'tl.fromTo("#{wid}-num .ui, #{wid}-num .x, #{wid}-num .u", {{ opacity: 0, filter: "blur(12px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }}, AT({t0 + 0.45:g}));',
           f'words("#{wid}-lab .w", {t0 + 0.62:g}, 0.05);',
           f'out("#{wid}-t", {e - WIPE - 0.02:g});']
    if d.get("pill"):
        html += (f'<div class="pill" id="{wid}-pill" style="left:1290px;top:640px">≈&nbsp;' + digits(4, wid + "-pc", gap_after=0)
                 + '&nbsp;jelentkező</div>')
        js += [f'pop("#{wid}-pill", {t0 + 0.3:g}, 0.4);', f'count(document.getElementById("{wid}-pc"), {t0 + 0.35:g}, 1.2, {d["pill"]});']
    if d.get("quote"):
        src, q = d["quote"]
        html += bubble(f"{wid}-q", 960, 780, src, q, "q", 820)
        js.append(f'pop("#{wid}-q", {t0 + 1.0:g}, 0.5);')
    css = """
    #root .wn { position: absolute; left: 130px; top: 190px; }
    #root .num { display: flex; align-items: baseline; margin-top: 10px; white-space: nowrap; }
    #root .num .cnt { font-size: 400px; line-height: 0.86; letter-spacing: -0.05em; }
    #root .num .ui { font-size: 220px; line-height: 0.86; margin-left: 0.14em; }
    #root .num .x { font-family: Sora, Inter, sans-serif; font-weight: 700; font-size: 250px; line-height: 0.86; margin-left: 0.04em; }
    #root .num .u { font-family: Sora, Inter, sans-serif; font-weight: 700; font-size: 110px; margin-left: 0.2em; letter-spacing: -0.03em; }
    #root .lab { margin-top: 26px; font: 600 48px/1.2 Inter, sans-serif; letter-spacing: -0.01em; max-width: 1080px; }
    #root .bub.q { font-size: 40px; }"""
    return "".join(html), "\n    ".join(js), css


RES_CSS = """
    #root .rn { position: absolute; display: flex; align-items: baseline; white-space: nowrap; }
    #root .rn .cnt { font-size: 420px; line-height: 0.86; letter-spacing: -0.05em; }
    #root .rn .ui { font-size: 230px; line-height: 0.86; margin-left: 0.12em; }
    #root .rn .x { font-family: Sora, Inter, sans-serif; font-weight: 700; font-size: 260px; line-height: 0.86; margin-left: 0.03em; }
    #root .rn .u { font-family: Sora, Inter, sans-serif; font-weight: 700; font-size: 110px; margin-left: 0.18em; letter-spacing: -0.03em; }
    #root .lab { font: 600 50px/1.2 Inter, sans-serif; letter-spacing: -0.01em; }
    #root .bub.q { font-size: 40px; }"""
RLIGHT = lambda rid, a, b2: [(f"{rid}-l0",) + a, (f"{rid}-l1",) + b2]


def res_common(rid, s, e, ls, kind):
    js = [f'wipeIn({s:g}, "{kind}");'] + [f'drift("#{l[0]}", {s:g}, {e - s:g}, {70 if k % 2 else -80}, {-50 if k % 2 else 60});' for k, l in enumerate(ls)]
    js.append(f'tl.fromTo("#{rid}-eb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out" }}, AT({s + WIPE:g}));')
    return js


def scene_r1(s, e):
    """79 M Ft in one week: the week's days light up one by one while the revenue climbs; then the client's words."""
    t0, step = s + WIPE, BEAT / 2
    ls = RLIGHT("r1", (92, 88, 100, "255, 64, 104, 0.5"), (6, 6, 80, "56, 160, 255, 0.5"))
    days = ["H", "K", "Sze", "Cs", "P", "Szo", "V"]
    html = (field("linear-gradient(140deg,#1631c0 0%,#3d1fb4 60%,#1a0f5c 100%)", ls)
            + '<div class="eb" id="r1-eb" style="position:absolute;left:130px;top:140px">Csarnoképítő ügyfél · Meta · B2B</div>'
            + f'<div class="hd rn" id="r1-n" style="left:122px;top:196px">{digits(2, "r1-cnt")}<span class="it ui">M Ft</span></div>'
            + f'<div class="lab" id="r1-lab" style="position:absolute;left:130px;top:590px">{wl("bevétel egy hét alatt")}</div>'
            + '<div class="days" id="r1-days">' + "".join(f'<div class="day" id="r1-d{k}">{d}</div>' for k, d in enumerate(days)) + '</div>'
            + bubble("r1-q", 1190, 196, "Csarnoképítő ügyfél · B2B", "„…annyi ajánlatkérésünk lett, mint korábban fél év alatt összesen.”", "q", 620))
    end = t0 + 0.25 + 7 * step
    js = res_common("r1", s, e, ls, "dr") + [
        f'tl.fromTo("#r1-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "none" }}, AT({t0 + 0.1:g}));',
        f'tl.fromTo("#r1-n .ui", {{ opacity: 0, filter: "blur(12px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }}, AT({t0 + 0.2:g}));',
        f'count(document.getElementById("r1-cnt"), {t0 + 0.25:g}, {7 * step:g}, 79, "power1.inOut");']
    for k in range(7):
        t = t0 + 0.25 + (k + 1) * step - 0.1
        js.append(f'tl.fromTo("#r1-d{k}", {{ backgroundColor: "rgba(255,255,255,0.1)", color: "rgba(255,255,255,0.5)" }}, {{ backgroundColor: "#ffffff", color: "#141a4a", duration: 0.12, ease: "power2.out", immediateRender: {"true" if k == 0 else "false"} }}, AT({t:g}));')
        js.append(f'tl.fromTo("#r1-d{k}", {{ scale: 0.9 }}, {{ scale: 1, duration: 0.3, ease: "back.out(2.2)", immediateRender: false }}, AT({t:g}));')
    js += [f'words("#r1-lab .w", {end + 0.1:g}, 0.06);', f'pop("#r1-q", {t0 + 1.1:g}, 0.5);',
           f'out(["#r1-eb", "#r1-n", "#r1-lab", "#r1-days", "#r1-q"], {e - WIPE - 0.02:g});']
    css = RES_CSS + """
    #root .days { position: absolute; left: 130px; top: 790px; display: flex; gap: 22px; }
    #root .day { width: 196px; height: 124px; border-radius: 28px; display: flex; align-items: center; justify-content: center;
      font: 700 46px/1 Sora, Inter, sans-serif; letter-spacing: -0.02em; background: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.5);
      box-shadow: inset 0 0 0 1.5px rgba(255, 255, 255, 0.22); }"""
    return html, "\n    ".join(js), css


def scene_r2(s, e):
    """81× ROAS: one forint, then eighty-one: a coin, then a 9 x 9 grid of coins bursts out while the number climbs."""
    t0 = s + WIPE
    ls = RLIGHT("r2", (8, 92, 90, "255, 160, 80, 0.45"), (96, 6, 90, "66, 92, 255, 0.55"))
    html = (field("linear-gradient(140deg,#ff3f6c 0%,#b02aa8 55%,#3a1690 100%)", ls)
            + '<div class="eb" id="r2-eb" style="position:absolute;left:130px;top:140px">Ajtó webshop · Google Performance Max</div>'
            + f'<div class="hd rn" id="r2-n" style="left:122px;top:196px">{digits(2, "r2-cnt")}<span class="x">×</span><span class="u">ROAS</span></div>'
            + f'<div class="lab" id="r2-lab" style="position:absolute;left:130px;top:590px">{wl("1 forint hirdetésből 81 forint bevétel.")}</div>'
            + '<div class="c1" id="r2-c1"><i class="cn"></i><span>1 Ft</span></div>'
            + '<div class="grid" id="r2-g" data-motion-blur="off">' + '<i class="cn"></i>' * 81 + '</div>'
            + '<div class="gl" id="r2-gl">81 Ft</div>')
    js = res_common("r2", s, e, ls, "dl") + [
        f'pop("#r2-c1", {t0:g}, 0.45);',
        f'tl.fromTo("#r2-g .cn", {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)", stagger: {{ grid: [9, 9], from: "center", amount: 0.6 }} }}, AT({t0 + 0.5:g}));',
        f'tl.fromTo("#r2-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "none" }}, AT({t0 + 0.45:g}));',
        f'count(document.getElementById("r2-cnt"), {t0 + 0.5:g}, 0.9, 81, "power2.out");',
        f'tl.fromTo("#r2-n .x, #r2-n .u", {{ opacity: 0, filter: "blur(12px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }}, AT({t0 + 1.1:g}));',
        f'tl.fromTo("#r2-gl", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }}, AT({t0 + 1.1:g}));',
        f'words("#r2-lab .w", {t0 + 0.9:g}, 0.05);',
        f'out(["#r2-eb", "#r2-n", "#r2-lab", "#r2-c1", "#r2-g", "#r2-gl"], {e - WIPE - 0.02:g});']
    css = RES_CSS + """
    #root .cn { display: block; width: 64px; height: 64px; border-radius: 50%;
      background: radial-gradient(circle at 34% 30%, #ffffff 0%, #ffe8ef 48%, #ffbfd0 100%);
      box-shadow: inset 0 0 0 4px rgba(255, 255, 255, 0.7), 0 10px 20px -8px rgba(40, 0, 40, 0.55); }
    #root .grid { position: absolute; left: 1150px; top: 150px; display: grid; grid-template-columns: repeat(9, 64px); gap: 12px; }
    #root .gl { position: absolute; left: 1150px; top: 852px; width: 672px; text-align: center; font: 700 64px/1 Sora, Inter, sans-serif; letter-spacing: -0.03em; }
    #root .c1 { position: absolute; left: 130px; top: 790px; display: flex; align-items: center; gap: 26px; font: 700 64px/1 Sora, Inter, sans-serif; letter-spacing: -0.03em; transform-origin: 0 50%; }
    #root .c1 .cn { width: 120px; height: 120px; }"""
    return html, "\n    ".join(js), css


def scene_r3(s, e):
    """23× ROAS at Christmas: the number slams into the middle, the holiday revenue counts under it, then their words."""
    t0 = s + WIPE
    ls = RLIGHT("r3", (94, 90, 100, "255, 64, 104, 0.5"), (4, 6, 80, "136, 78, 255, 0.55"))
    html = (field("linear-gradient(140deg,#4a1fb8 0%,#2a2fc4 55%,#101a66 100%)", ls)
            + '<div class="eb" id="r3-eb" style="position:absolute;left:0;right:0;top:130px;text-align:center">Karóra webshop · Karácsony</div>'
            + f'<div class="hd rn" id="r3-n" style="left:0;right:0;top:180px;justify-content:center">{digits(2, "r3-cnt")}<span class="x acc">×</span><span class="u">ROAS</span></div>'
            + '<div class="pc"><div class="pill" id="r3-p"><i></i>Ünnepi kampány · több mint&nbsp;' + digits(1, "r3-pc") + 'M Ft bevétel</div></div>'
            + bubble("r3-q", 530, 760, "Karóra webshop", "„…az ünnepi szezon nekünk dolgozik – nem ellenünk.”", "q", 860))
    js = res_common("r3", s, e, ls, "up") + [
        f'tl.fromTo("#r3-n", {{ opacity: 0, scale: 1.35 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "expo.out" }}, AT({t0:g}));',
        f'count(document.getElementById("r3-cnt"), {t0:g}, 0.7, 23, "power2.out");',
        f'pop("#r3-p", {t0 + 0.7:g}, 0.4);', f'count(document.getElementById("r3-pc"), {t0 + 0.75:g}, 0.5, 8, "power2.out");',
        f'pop("#r3-q", {t0 + 1.2:g}, 0.5);',
        f'out(["#r3-eb", "#r3-n", "#r3-p", "#r3-q"], {e - WIPE - 0.02:g});']
    css = RES_CSS + """
    #root #r3-n { transform-origin: 50% 60%; }
    #root #r3-n .cnt { font-size: 460px; }
    #root .pc { position: absolute; left: 0; right: 0; top: 640px; display: flex; justify-content: center; }
    #root .pill .cnt .d { width: 0.6em; }"""
    return html, "\n    ".join(js), css


def scene_r4(s, e):
    """About 5 700 sign-ups at 105 Ft each: a counter races while sign-up dots fill the frame; the price stamps in."""
    import random
    t0 = s + WIPE
    ls = RLIGHT("r4", (92, 8, 90, "255, 64, 104, 0.45"), (6, 94, 90, "136, 78, 255, 0.55"))
    pts = [(24 + c * 48, 26 + r * 58) for r in range(18) for c in range(40)]
    random.Random(7).shuffle(pts)                     # a fixed order, the same on every render
    dots = "".join(f'<i style="left:{x}px;top:{y}px"></i>' for x, y in pts)
    html = (field("linear-gradient(140deg,#1d7be0 0%,#3a2fc4 55%,#2a1270 100%)", ls)
            + f'<div class="dots" id="r4-dots" data-motion-blur="off">{dots}</div>'
            + '<div class="eb" id="r4-eb" style="position:absolute;left:0;right:0;top:130px;text-align:center">Egészségügyi webinár</div>'
            + f'<div class="hd rn" id="r4-n" style="left:0;right:0;top:180px;justify-content:center"><span class="ap">≈</span>{digits(4, "r4-cnt", gap_after=0)}</div>'
            + f'<div class="lab" id="r4-lab" style="position:absolute;left:0;right:0;top:560px;text-align:center">{wl("jelentkező 600K Ft-ból")}</div>'
            + '<div class="pc"><div class="stamp" id="r4-st">105 Ft <span>/ jelentkező</span></div></div>'
            + bubble("r4-q", 560, 830, "Egészségügyi szolgáltató", "„…majdnem 5700-nál állt meg, alig hittük el…”", "q", 800))
    js = res_common("r4", s, e, ls, "iris") + [
        f'tl.fromTo("#r4-dots i", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "none", stagger: {{ amount: 1.4 }} }}, AT({t0 - 0.1:g}));',
        f'tl.fromTo("#r4-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "none" }}, AT({t0:g}));',
        f'count(document.getElementById("r4-cnt"), {t0 + 0.05:g}, 1.4, 5700, "expo.out");',
        f'words("#r4-lab .w", {t0 + 1.4:g}, 0.06);',
        f'tl.fromTo("#r4-st", {{ opacity: 0, scale: 1.7, rotation: -9 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.32, ease: "expo.out" }}, AT({t0 + 1.5:g}));',
        f'pop("#r4-q", {t0 + 1.9:g}, 0.5);',
        f'out(["#r4-eb", "#r4-n", "#r4-lab", "#r4-st", "#r4-q", "#r4-dots"], {e - WIPE - 0.02:g});']
    css = RES_CSS + """
    #root .dots i { position: absolute; width: 8px; height: 8px; border-radius: 50%; background: rgba(255, 255, 255, 0.28); }
    #root #r4-n .ap { font-size: 220px; line-height: 0.86; margin-right: 0.12em; opacity: 0.8; }
    #root .pc { position: absolute; left: 0; right: 0; top: 660px; display: flex; justify-content: center; }
    #root .stamp { padding: 18px 40px 20px; border-radius: 22px; background: #ff5272; color: #fff; font: 700 84px/1 Sora, Inter, sans-serif;
      letter-spacing: -0.03em; box-shadow: 0 30px 60px -24px rgba(60, 0, 30, 0.6); }
    #root .stamp span { font-size: 52px; font-weight: 600; opacity: 0.9; }"""
    return html, "\n    ".join(js), css


def scene_voices(s, e):
    t0 = s + WIPE
    qs = [("Péter · Hoofbútor", "„Már az induláskor is volt vásárlás…”", 110, 300),
          ("Rita · Rita’s Beauty Corner", "„Rövid időn belül jöttek az eredmények…”", 170, 540),
          ("János · EJ Massage Therapies", "„Csak ajánlani tudom őket.”", 120, 780)]
    html = field("linear-gradient(135deg,#ff3f6c 0%,#9a2ab0 50%,#2f1690 100%)",
                 [("vc-l0", 10, 10, 90, "255, 160, 80, 0.4"), ("vc-l1", 96, 96, 100, "56, 160, 255, 0.45")])
    html += '<div class="eb" id="vc-eb" style="position:absolute;left:120px;top:150px">Ügyfeleink szavaival</div>'
    html += "".join(bubble(f"vc-q{k}", x, y, who, q, "q", 820) for k, (who, q, x, y) in enumerate(qs))
    html += (f'<div class="vr" id="vc-r"><div class="hd vn" id="vc-n">{digits(3, "vc-cnt")}<span class="u">M+ Ft</span></div>'
             f'<div class="lab" id="vc-lab">{wl("kezelt hirdetési büdzsé 2022 óta")}</div>'
             f'<div class="pill" id="vc-p0" style="position:relative;margin-top:44px"><i></i>149K megtekintés egy reelen · Prof Enzo</div>'
             f'<div class="pill" id="vc-p1" style="position:relative;margin-top:18px"><i></i>33K követő · Prof Enzo</div></div>')
    js = [f"wipeIn({s:g});", f'drift("#vc-l0", {s:g}, {e - s:g}, 70, 50); drift("#vc-l1", {s:g}, {e - s:g}, -70, -50);',
          f'tl.fromTo("#vc-eb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out" }}, AT({t0:g}));']
    js += [f'pop("#vc-q{k}", {t0 + 0.1 + 0.38 * k:g}, 0.5);' for k in range(3)]
    js += [f'tl.fromTo("#vc-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "none" }}, AT({t0 + 0.9:g}));',
           f'count(document.getElementById("vc-cnt"), {t0 + 0.9:g}, 1.0, 300);',
           f'words("#vc-lab .w", {t0 + 1.4:g}, 0.05);',
           f'pop("#vc-p0", {t0 + 1.7:g}, 0.4); pop("#vc-p1", {t0 + 1.92:g}, 0.4);',
           f'out(["#vc-eb", "#vc-q0", "#vc-q1", "#vc-q2", "#vc-r"], {e - WIPE - 0.02:g});']
    css = """
    #root .vr { position: absolute; left: 1000px; top: 240px; width: 820px; }
    #root .vn { display: flex; align-items: baseline; white-space: nowrap; }
    #root .vn .cnt { font-size: 250px; line-height: 0.86; letter-spacing: -0.05em; }
    #root .vn .u { font-size: 104px; margin-left: 0.1em; letter-spacing: -0.03em; }
    #root .lab { margin-top: 20px; font: 600 46px/1.2 Inter, sans-serif; }
    #root .bub.q { font-size: 38px; }
    #root .pill { display: inline-flex; }"""
    return "".join(html), "\n    ".join(js), css


def scene_close(s, e, info):
    t0 = s + WIPE
    html = f"""<div class="fld" style="background:#05070f"></div>
    <div class="wl-in ff" data-layout-allow-overflow id="cs-in">
      <div class="wl-tilt"><div class="wl-wall" id="cs-wall">{wall()}</div></div>
      <div class="wl-dim" style="background:rgba(5,7,15,0.62)"></div></div>
    <div class="glow" id="cs-glow"></div>
    <div class="ct" id="cs-t1"><div class="hd c1">{wl("Videók, amiket")}</div><div class="hd c1"><span class="w it">végignéznek.</span></div></div>
    <div class="ct" id="cs-t2"><div class="hd c1">{wl("Hirdetések, amik")}</div><div class="hd c1"><span class="w it">megtérülnek<span class="acc">.</span></span></div></div>
    <img id="cs-logo" src="assets/logo/socialstream-logo-stacked-dark.svg" alt="SocialStream" style="position:absolute;{logo_box(info)}">
    <div class="eb" id="cs-eb" style="position:absolute;left:0;right:0;top:790px;text-align:center">Interest media ügynökség</div>"""
    js = f"""wipeIn({s:g});
    tl.fromTo("#cs-in", {{ scale: 1.5, rotation: 4 }}, {{ scale: 1, rotation: 0, duration: {e - s:g}, ease: "power2.out" }}, AT({s:g}));
    tl.fromTo("#cs-wall", {{ x: 160 }}, {{ x: -40, duration: {e - s:g}, ease: "none" }}, AT({s:g}));
    words("#cs-t1 .w", {t0 + 0.04:g}, 0.09); out("#cs-t1", {b(63) - 0.16:g});
    words("#cs-t2 .w", {b(63):g}, 0.09); out("#cs-t2", {b(66) - 0.36:g});
    tl.fromTo("#cs-glow", {{ opacity: 0.5 }}, {{ opacity: 1, duration: 0.5, ease: "power2.out" }}, AT({b(66) - 0.3:g}));
    tl.fromTo("#cs-logo", {{ opacity: 0, scale: 1.08, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }}, AT({b(66):g}));
    tl.fromTo("#cs-eb", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, AT({b(67):g}));"""
    css = WALL_CSS + """
    #root .ct { position: absolute; left: 0; right: 0; top: 330px; text-align: center; }
    #root .c1 { font-size: 150px; white-space: nowrap; }
    #root .c1 .it { font-size: 190px; }
    #root #cs-logo { transform-origin: 50% 50%; }"""
    return html, js, css


def composition(cid, s, html, js, css):
    common = open(os.path.join(HERE, "common.css")).read()
    return f"""<template>
  <style>
    {common}
    {css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
    <div class="ff" id="wp">
    {html}
    </div>
  </div>
  <script>
  (() => {{{JS.replace("%START%", f"{s:g}").replace("%WIPE%", f"{WIPE:g}")}
    {js}
    window.__timelines["{cid}"] = tl;
  }})();
  </script>
</template>
"""


X = {  # effect: file in assets/audio, where it hits (s into the file), volume
    "whoosh": ("whoosh-deep", 0.63, 0.32), "wind": ("wind-woosh", 1.595, 0.26), "pop": ("pop-bubble", 0.241, 0.55),
    "pop2": ("pop-soap", 0.186, 0.5), "shutter": ("shutter", 0.305, 0.5), "sub": ("rumble-bass", 0.051, 0.55),
    "impact": ("impact-cine", 2.172, 0.75), "coins": ("coins", 0.082, 0.45),
}


def sounds():
    """The effects, from the scenes' own moments: a whoosh on every wipe (two takes, alternating), a pop on every card
    that pops, a shutter on the behind-the-scenes cards, a sub hit on the drop, one cinematic impact on the logo."""
    ev = [("sub", DROP)]
    for i, n in enumerate(ORDER):
        ev.append(("whoosh" if i % 2 == 0 else "wind", LAND[n]))
    t0 = LAND["make"]
    ev += [("shutter", t0 - WIPE + 1.0 + 0.24 * k + 0.12) for k in range(4)]
    t0 = LAND["ads"]
    ev += [("pop2", t0 + 0.495 + 0.12)] + [("pop" if k % 2 == 0 else "pop2", t0 + 0.74 + 0.495 * k + 0.12) for k in range(4)]
    t0 = LAND["r1"]
    ev += [("pop", t0 + 1.1 + 0.12), ("pop2", t0 + 0.25 + 7 * BEAT / 2 + 0.04)]
    t0 = LAND["r2"]
    ev += [("pop", t0 + 0.12), ("coins", t0 + 0.58), ("pop2", t0 + 1.12)]
    t0 = LAND["r3"]
    ev += [("sub", t0), ("pop", t0 + 0.82), ("pop2", t0 + 1.32)]
    t0 = LAND["r4"]
    ev += [("pop2", t0 + 1.45), ("sub", t0 + 1.5), ("pop", t0 + 2.02)]
    t0 = LAND["voices"]
    ev += [("pop" if k % 2 == 0 else "pop2", t0 + 0.1 + 0.38 * k + 0.12) for k in range(3)]
    ev += [("pop2", t0 + 1.7 + 0.12), ("pop", t0 + 1.92 + 0.12)]
    ev.append(("impact", b(66)))
    out = []
    for k, (name, t) in enumerate(ev):
        f, hit, vol = X[name]
        start = round(t + 1 / FPS - hit, 3)
        media = 0.0
        if start < 0:
            media, start = -start, 0.0
        out.append(f'      <audio id="sfx{k}" class="clip" src="assets/audio/{f}.mp3" data-start="{start:g}" data-media-start="{media:g}" '
                   f'data-track-index="{30 + k}" data-volume="{vol}"></audio>')
    out.append(f'      <audio id="music" class="clip" src="assets/audio/{MUSIC}.mp3" data-start="0" data-duration="{TOTAL:g}" '
               f'data-media-start="{MUSIC_AT:g}" data-track-index="29" data-volume="0.72" data-fade-in="0.3" data-fade-out="1.6"></audio>')
    return "\n".join(out)


def index(lang="hu"):
    hosts = "\n".join(f'''      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{a:g}" data-duration="{round(b - a, 4):g}" data-track-index="{z}" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: {z}"></div>'''
                      for z, (n, a, b) in enumerate(SC))
    return f"""<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>SocialStream sizzle ({W}x{H}, {lang})</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #05070f; }} #main {{ position: relative; width: 100%; height: 100%; }}</style>
  </head>
  <body>
    <div id="main" data-motion-blur="on" data-motion-blur-shutter="120" data-composition-id="main" data-start="0" data-duration="{TOTAL:g}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
{hosts}
{sounds()}
    </div>
    <script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
"""


def main():
    out = os.path.join(HERE, "wide")
    comp = os.path.join(out, "compositions")
    os.makedirs(comp, exist_ok=True)
    tmp = os.path.join(HERE, ".logo-wide")
    logo, info = logo_scene(tmp)
    builders = {"open": lambda s, e: scene_open(s, e, info), "problem": scene_problem, "make": scene_make, "ads": scene_ads,
                "measure": scene_measure, "voices": scene_voices,
                "r1": scene_r1, "r2": scene_r2, "r3": scene_r3, "r4": scene_r4, "close": lambda s, e: scene_close(s, e, info)}
    for n, s, e in SC:
        if n == "logo":
            src = logo
        else:
            html, js, css = (builders[n](s, e) if n in builders else scene_win(s, e, n))
            src = composition(n, s, html, js, css)
        open(os.path.join(comp, f"{n}.html"), "w").write(src)
    open(os.path.join(out, "index.html"), "w").write(index())
    cli = "npx --yes hyperframes@0.9.40"
    files = {"hyperframes.json": json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                                             "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                                             "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                                             "media": {"autoProxy": True}}, indent=2) + "\n",
             "meta.json": json.dumps({"id": "socialstream-sizzle-wide", "name": "SocialStream sizzle (wide)", "createdAt": "2026-11-15T00:00:00.000Z"}, indent=2) + "\n",
             "package.json": json.dumps({"name": "socialstream-sizzle-wide", "private": True, "type": "module",
                                         "scripts": {"dev": f"{cli} preview", "check": f"{cli} check", "render": f"{cli} render"}}, indent=2) + "\n",
             ".gitignore": "renders/\n.hyperframes/\n.thumbnails/\nsnapshots/\nnode_modules/\n"}
    for f, t in files.items():
        open(os.path.join(out, f), "w").write(t)
    link = os.path.join(out, "assets")
    if not os.path.islink(link):
        os.symlink("../assets", link)
    subprocess.run(["rm", "-rf", tmp], check=True)
    print("wide", TOTAL)


if __name__ == "__main__":
    main()
