#!/usr/bin/env python3
"""The SocialStream sizzle, draft 4 (2026-11-16). SPEC.md is the plan: the grammar of the Social Chain 2026 sizzle
the founder sent (footage as the picture, a new world every few seconds, quiet lines and giant numbers, proof that
looks like the platforms, clips changing on the beat) telling SocialStream's own story in SocialStream's own look.

The feed dies ("A social media meghalt."), one card comes back to life on the music's drop and takes the frame
("Az érdeklődés vette át a helyét."); three client worlds (FlyX Tenerife, Prof Enzo, the team's productions); how
they work; five results; their clients' and viewers' words; the promise; the logo.

Every line is the site's own copy (../../content.mjs) or a real number or comment (SPEC.md, Honesty).
Run from this folder: python3 clips.py <photos> <enzo>, then python3 build.py (writes wide/; then render, README.md).
"""
import json, math, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_TOOLS = os.path.normpath(os.path.join(HERE, "../../../../brand/socialstream-logo/tools"))
FPS, W, H = 25, 1920, 1080
WIPE = 0.32                                   # a scene comes in over the last one with a wipe this long

# ---- the music: "What About Action" (Mixkit, free licence; in their CapCut folder), 121 bpm. The film starts
# 53.975 s into it, in its breakdown, so the hook plays over the quiet part and the drop (63.255 s) lands at 9.28 s;
# every beat is counted from the drop, never added up ----
MUSIC, MUSIC_AT = "what-about-action", 53.975
DROP, BEAT = 9.28, 0.4952


def b(k):
    return round((DROP + k * BEAT) * FPS) / FPS


def r2(v):
    return round(v + 1e-9, 2)


TOTAL = r2(b(76) + 2.48)
# the hook's clock (before the drop)
P1, P2, P3, P3_OUT = b(-12), b(-10), b(-8), 6.64          # Posztolsz. / Hirdetsz. / Mégsem jönnek a vevők?
CA, STRIKE, DEATH, CA_OUT = b(-5), 7.08, b(-4), 8.72      # A social media (struck) meghalt.: the wall dies
SPARK, GROW = b(-1), 8.92                                 # the middle card comes back; it grows into the frame

# ---- the scenes: id, start, end (seconds of the film); the order is the paint order ----
SC = [
    ("open", 0.0, b(4)),                                  # the feed, the problem, the diagnosis, the turn
    ("logo", 0.0, 3.0),                                   # the logo builds over the feed (the kit's film-open format)
    ("flyx", r2(b(4) - WIPE), b(12)),                     # FlyX Tenerife
    ("enzo", r2(b(12) - WIPE), r2(b(20) + 0.6)),          # Prof Enzo (the polaroids cover it)
    ("prod", r2(b(20) - 0.12), b(28)),                    # the team's productions
    ("how", r2(b(28) - WIPE), b(36)),                     # Mi gyártjuk a videót, mi futtatjuk a hirdetést, ...
    ("r1", r2(b(36) - WIPE), b(40)), ("r2", r2(b(40) - WIPE), b(44)), ("r3", r2(b(44) - WIPE), b(48)),
    ("r4", r2(b(48) - WIPE), b(52)), ("m300", r2(b(52) - WIPE), b(56)),
    ("voices", r2(b(56) - WIPE), r2(b(68) + 0.04)),       # Ne nekünk higgy. Nekik.
    ("close", r2(b(68) - WIPE), TOTAL),                   # the promise, the logo
]
for _n, _a, _z in SC:
    for _x in (_a, _z):
        assert abs(_x * FPS - round(_x * FPS)) < 1e-6, (_n, _x)
assert abs(TOTAL * FPS - round(TOTAL * FPS)) < 1e-6

# ---- every line of the film in both languages. Hungarian is the site's copy; the English is the site's own English
# for the same line (../../content.mjs), so nothing is translated twice. Comments on FlyX's reels were written in
# English and stay as they are ----
TEXT = {
    "hu": dict(
        p1="Posztolsz.", p2="Hirdetsz.", p3='Mégsem jönnek a <span class="acc">vevők?</span>',
        ca=('<span class="w">A</span> <span class="ss"><span class="w">social</span> <span class="w">media</span>'
            '<i class="stk" id="op-stk"></i></span>'),
        ca2="meghalt.",
        cb=('<div class="hd cb1"><span class="w">Az</span> <span class="w it">érdeklődés</span></div>\n'
            '      <div class="hd cb1"><span class="w">vette</span> <span class="w">át</span> <span class="w">a</span> '
            '<span class="w">helyét<span class="acc">.</span></span></div>'),
        fx_eb="FlyX Tenerife · Élményközpont", fx_lab="megtekintés egy reelen", comment="Komment",
        ez_eb="Prof Enzo · Facebook-reelek", ez_lab="megtekintés", ez_f="33K követő",
        pr_eb="Részletek a videóinkból", tags=["Forgatás", "Vágás", "Feliratozás", "Reels", "Podcast &amp; interjú"],
        how=['Mi gyártjuk a <span class="it">videót</span>,', 'mi futtatjuk a <span class="it">hirdetést</span>,', "és mi mérjük,",
             'mit <span class="it hz">hozott</span><span class="acc">.</span>'],
        r1_eb="Csarnoképítő ügyfél · B2B · Meta", r1_lab="bevétel egy hét alatt", days=["H", "K", "Sze", "Cs", "P", "Szo", "V"],
        r2_eb="Ajtó webshop · Google Performance Max",
        r3_eb="Karóra webshop · Karácsony", r3_p=("több mint&nbsp;", "M Ft bevétel"),
        r4_eb="Egészségügyi webinár", r4_lab="jelentkező 600K Ft-ból", r4_st=("105 Ft", "egy jelentkező"), thou="",
        m3_eb="2022 óta", m3_lab="kezelt büdzsé",        # the year is said once, above the number
        v0=("big", "Ne nekünk higgy."), v1="Nekik",
        # their clients' reviews of them, from the site, cut only with "…". (FlyX's viewers' comments are about
        # FlyX's videos, not about SocialStream: they stay in FlyX's world.)
        voices=[
            ("q", "Péter · Hoofbútor", "„Már az induláskor is volt vásárlás…”"),
            ("q", "Csarnoképítő ügyfél · B2B", "„…annyi ajánlatkérésünk lett, mint korábban fél év alatt összesen.”"),
            ("q", "Karóra webshop", "„…az ünnepi szezon nekünk dolgozik – nem ellenünk.”"),
            ("q", "Egészségügyi szolgáltató", "„…majdnem 5700-nál állt meg, alig hittük el…”"),
            ("q", "Rita · Rita’s Beauty Corner", "„Rövid időn belül jöttek az eredmények…”"),
            ("q", "János · EJ Massage Therapies", "„Csak ajánlani tudom őket.”"),
        ], qm=("„", "”"),
        c1=("Videók, amiket", "végignéznek"), c2=("Hirdetések, amik", "megtérülnek"), cs_eb="Interest media ügynökség",
    ),
    "en": dict(
        p1="You post.", p2="You advertise.", p3='And still no <span class="acc">buyers?</span>',
        ca='<span class="ss"><span class="w">Social</span> <span class="w">media</span><i class="stk" id="op-stk"></i></span>',
        ca2="is dead.",
        cb=('<div class="hd cb1"><span class="w it">Interest</span></div>\n'
            '      <div class="hd cb1"><span class="w">has</span> <span class="w">taken</span> <span class="w">its</span> '
            '<span class="w">place<span class="acc">.</span></span></div>'),
        fx_eb="FlyX Tenerife · Experience centre", fx_lab="views on one reel", comment="Comment",
        ez_eb="Prof Enzo · Facebook reels", ez_lab="views", ez_f="33K followers",
        pr_eb="Clips from our videos", tags=["Shooting", "Editing", "Subtitles", "Reels", "Podcast &amp; interview"],
        how=['We make the <span class="it">video</span>,', 'we run the <span class="it">ads</span>,', "and we measure",
             'what they <span class="it hz">bring in</span><span class="acc">.</span>'],
        r1_eb="Industrial hall builder · B2B · Meta", r1_lab="revenue in one week", days=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        r2_eb="Door webshop · Google Performance Max",
        r3_eb="Watch webshop · Christmas", r3_p=("over&nbsp;", "M Ft in revenue"),
        r4_eb="Healthcare webinar", r4_lab="registrants from 600K Ft", r4_st=("105 Ft", "per registrant"), thou=",",
        m3_eb="Since 2022", m3_lab="budget managed",
        v0=("mid", "Don’t take our word for it."), v1="Take theirs",
        voices=[
            ("q", "Péter · Hoofbútor", "“There were purchases from launch day…”"),
            ("q", "Hall-building client · B2B", "“…as many quote requests as we used to get in half a year.”"),
            ("q", "Watch webshop", "“…the holiday season felt like it was working for us, not against us.”"),
            ("q", "Healthcare provider", "“…the counter stopped at almost 5,700, we could hardly believe it…”"),
            ("q", "Rita · Rita’s Beauty Corner", "“Results came quickly…”"),
            ("q", "János · EJ Massage Therapies", "“I can only recommend them.”"),
        ], qm=("“", "”"),
        c1=("Videos people watch", "to the end"), c2=("Ads that", "pay off"), cs_eb="Interest media agency",
    ),
}
TX = TEXT["hu"]                                             # the language being built (main() switches it)
OUTS = [("hu", "wide"), ("en", "wide-en")]

# ---- helpers every scene's script starts with ----
JS = r"""
    const FPS = 25, W = 1920, H = 1080, START = %START%, AT = (t) => t - START;
    const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v), EZ = {};
    const ez = (n, p) => (EZ[n] || (EZ[n] = gsap.parseEase(n)))(clamp01(p));
    const tl = gsap.timeline({ paused: true });
    // a scene comes in over the last one with a wipe: diagonal from the right or the left, up, or an iris
    const WIPES = {
      dr: ["polygon(132% 0%, 132% 0%, 132% 100%, 162% 100%)", "polygon(-32% 0%, 132% 0%, 132% 100%, -2% 100%)"],
      dl: ["polygon(-32% 0%, -32% 0%, -62% 100%, -32% 100%)", "polygon(-32% 0%, 132% 0%, 102% 100%, -32% 100%)"],
      up: ["polygon(0% 100%, 100% 100%, 100% 100%, 0% 100%)", "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)"],
      iris: ["circle(0% at 50% 50%)", "circle(75% at 50% 50%)"],
    };
    const wipeIn = (t, k) => tl.fromTo("#wp", { clipPath: WIPES[k][0] }, { clipPath: WIPES[k][1], duration: %WIPE%, ease: "power3.inOut" }, AT(t));
    // one phrase at a time: it comes into focus, and goes when the next one comes
    const say = (sel, tin, tout) => {
      tl.fromTo(sel, { opacity: 0, filter: "blur(12px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power2.out" }, AT(tin));
      if (tout !== undefined) tl.fromTo(sel, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(12px)", duration: 0.1, ease: "power2.in", immediateRender: false }, AT(tout));
    };
    const words = (sel, t, st = 0.07) => tl.fromTo(sel, { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: st }, AT(t));
    const out = (sel, t) => tl.fromTo(sel, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.16, ease: "power2.in", immediateRender: false }, AT(t));
    const fade = (sel, t, d = 0.25) => tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: d, ease: "power2.out" }, AT(t));
    // a card pops: scale and position with a little overshoot (opacity never bounces)
    const pop = (sel, t, d = 0.45) => {
      tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.1, ease: "none" }, AT(t));
      tl.fromTo(sel, { scale: 0.55, y: 30 }, { scale: 1, y: 0, duration: d, ease: "back.out(1.7)" }, AT(t));
    };
    // a phone or a card rises from below the frame, turning, and settles
    const rise = (sel, t, r0, r1, d = 0.72) => tl.fromTo(sel, { y: 1150, rotation: r0 }, { y: 0, rotation: r1, duration: d, ease: "expo.out" }, AT(t));
    const drift = (sel, t, d, dx, dy) => tl.fromTo(sel, { x: 0, y: 0 }, { x: dx, y: dy, duration: d, ease: "sine.inOut" }, AT(t));
    // a comment types itself, a word at a time
    const type = (sel, t, st = 0.045) => tl.fromTo(sel + " .tw", { opacity: 0 }, { opacity: 1, duration: 0.02, ease: "none", stagger: st }, AT(t));
    // a heart rises from the work, sways and goes
    const heart = (sel, t, x, y, up, sway, d) => {
      tl.fromTo(sel, { x, y, scale: 0.3 }, { x: x + sway, y: y - up, scale: 1, duration: d, ease: "power1.out" }, AT(t));
      tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.12, ease: "none" }, AT(t));
      tl.fromTo(sel, { opacity: 1 }, { opacity: 0, duration: 0.3, ease: "power1.in", immediateRender: false }, AT(t + d - 0.3));
    };
    // a counted number: fixed-width digit boxes, written once per frame as the value changes, never smeared
    const count = (el, t, dur, to, ease = "expo.out") => {
      const ds = [...el.querySelectorAll(".d")]; let last = null;
      for (let i = 0; i <= Math.round(dur * FPS); i++) {
        const tt = t + i / FPS, v = Math.round(to * ez(ease, (tt - t) / dur));
        if (v === last) continue; last = v;
        const s = String(v).padStart(ds.length, " ");
        ds.forEach((d, k) => tl.set(d, { textContent: s[k] === " " ? "" : s[k] }, Math.max(0, AT(tt) - 0.01)));
      }
      const sep = el.querySelector(".sep");                 // a thousands comma: there once there are thousands
      if (sep) tl.fromTo(sep, { opacity: 0 }, { opacity: 1, duration: 0.02, ease: "none" }, AT(t + dur * 0.12));
    };"""

HEART = ('<svg viewBox="0 0 24 22"><path d="M12 21.2S2.4 14.9 2.4 8.3C2.4 5 4.9 2.4 8 2.4c1.7 0 3.2.8 4 2.1.8-1.3 2.3-2.1 4-2.1 '
         '3.1 0 5.6 2.6 5.6 5.9 0 6.6-9.6 12.9-9.6 12.9z" fill="#ff3f6c"/></svg>')


# ---- small builders ----
def lights(ls):
    return "".join(f'<i class="lt" id="{i}" data-layout-allow-overflow style="left:{x}%;top:{y}%;width:{s}vmax;height:{s}vmax;'
                   f'margin:-{s / 2}vmax 0 0 -{s / 2}vmax;background:radial-gradient(closest-side,rgba({c}),rgba({c.rsplit(",", 1)[0]},0))"></i>'
                   for i, x, y, s, c in ls)


def field(bg, ls=()):
    return f'<div class="fld" style="background:{bg}">{lights(ls)}</div>'


def tile(name, color="#fff"):
    row = "".join(f"<span>{name}</span>" for _ in range(9))
    return f'<div class="tile" data-layout-allow-overflow data-layout-ignore style="color:{color}">' + "".join(f"<div>{row}</div>" for _ in range(9)) + "</div>"


def video(vid, path, start, dur, track, cls=""):
    return (f'<video id="{vid}" class="clip {cls}" src="assets/{path}.mp4" data-start="{r2(start):g}" data-duration="{r2(dur):g}" '
            f'data-media-start="0" data-hf-media-start-basis="local" data-track-index="{track}" muted playsinline></video>')


def phone(pid, left, top, clips, track, z=1):
    """clips: (file, start in the scene, seconds); one after another on the same screen."""
    vids = "".join(video(f"{pid}-v{k}", f"clips/{f}", st, du, track + k) for k, (f, st, du) in enumerate(clips))
    return f'<div class="phone" id="{pid}" style="left:{left}px;top:{top}px;z-index:{z}"><div class="scr">{vids}</div><div class="isl"></div></div>'


def card(cid, left, top, w, h, clips, track, z=1):
    vids = "".join(video(f"{cid}-v{k}", f"clips/{f}", st, du, track + k) for k, (f, st, du) in enumerate(clips))
    return f'<div class="card" id="{cid}" style="left:{left}px;top:{top}px;width:{w}px;height:{h}px;z-index:{z}">{vids}</div>'


def tw(text):
    ws = text.split(" ")
    return "".join(f'<span class="tw">{w}{" " if i < len(ws) - 1 else ""}</span>' for i, w in enumerate(ws))


def bubble(bid, left, top, src, text, cls="", width=None):
    w = f";width:{width}px" if width else ""
    return (f'<div class="bub {cls}" id="{bid}" style="left:{left}px;top:{top}px{w}"><span class="av"></span>'
            f'<span class="src">{src}</span>{tw(text)}</div>')


def digits(n, cid, gap_after=None, sep=""):
    """n digit boxes; after box gap_after a thousands gap (Hungarian) or, with sep, a comma (English)."""
    gap = ' style="margin-right:0.16em"'
    ds = "".join(f'<span class="d"{gap if gap_after == k and not sep else ""}></span>'
                 + (f'<span class="sep">{sep}</span>' if gap_after == k and sep else "") for k in range(n))
    return f'<span class="cnt" id="{cid}" data-motion-blur="off">{ds}</span>'


def wl(text, cls=""):
    return " ".join(f'<span class="w {cls}">{w}</span>' for w in text.split())


def hearts(prefix, n, t0, t1, box, seed):
    """n hearts rising between t0 and t1 from inside box (x0, y0, x1, y1): their markup and their script."""
    rnd = random.Random(seed)
    html, js = [], []
    for k in range(n):
        size = rnd.choice([30, 36, 44, 54])
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        t = t0 + (t1 - t0) * (k + rnd.random() * 0.6) / n
        html.append(f'<i class="hrt" id="{prefix}{k}" data-layout-ignore style="width:{size}px;height:{size}px">{HEART}</i>')
        js.append(f'heart("#{prefix}{k}", {t:.2f}, {x:.0f}, {y:.0f}, {rnd.uniform(240, 420):.0f}, {rnd.uniform(-50, 50):.0f}, {rnd.uniform(1.3, 1.9):.2f});')
    return "".join(html), "\n    ".join(js)


# ---- the wall: a tilted grid of their reels; some play, the rest stand still ----
ROWS, COLS, CW, CH, GAP, TILT = 5, 9, 300, 533, 24, -10
WALL_W, WALL_H = COLS * CW + (COLS - 1) * GAP, ROWS * CH + (ROWS - 1) * GAP
MID = (ROWS // 2, COLS // 2)
WALL_X0, WALL_V = 80, 16                                    # the drift: where it starts, px a second
WALL_X1 = WALL_X0 - WALL_V * DEATH - 8                      # where it has stopped after the wall dies
LIVE = ["w02", "w15", "w04", "w07", "w16", "w11", "w03", "w09", "w05", "w13", "w10", "w06", "w08", "w01", "w14", "w12"]
STILL = ["s02", "s04", "s10", "s06", "s12", "s15", "s01", "s18", "s05", "s20", "s07", "s23", "s03", "s14", "s11", "s13",
         "s16", "s17", "s19", "s21", "s22", "s24", "s25", "s26", "s27", "s09", "s08"]
WALL_CSS = f"""#root .wl-tilt {{ position: absolute; left: 50%; top: 50%; width: {WALL_W}px; height: {WALL_H}px; margin: {-WALL_H / 2}px 0 0 {-WALL_W / 2}px; transform: rotate({TILT}deg); }}
    #root .wl-card {{ width: {CW}px; height: {CH}px; }}"""


def wall_map():
    """Which reel each card shows: the ones in the frame get the playing reels and no reel twice; nearest the
    middle first, playing and still in turn."""
    a, vis = math.radians(TILT), []
    for r in range(ROWS):
        for c in range(COLS):
            x0, y0 = c * (CW + GAP) - WALL_W / 2, r * (CH + GAP) - WALL_H / 2
            pts = [(W / 2 + x * math.cos(a) - y * math.sin(a), H / 2 + x * math.sin(a) + y * math.cos(a))
                   for x, y in ((x0, y0), (x0 + CW, y0), (x0, y0 + CH), (x0 + CW, y0 + CH))]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            if max(xs) > -90 and min(xs) < W + 90 and max(ys) > 0 and min(ys) < H and (r, c) != MID:
                vis.append((r, c))
    vis.sort(key=lambda rc: (abs(rc[0] - MID[0]) * 1.6 + abs(rc[1] - MID[1]), rc))
    live, still, m = list(LIVE), list(STILL), {MID: "mid"}
    for k, rc in enumerate(vis):
        m[rc] = live.pop(0) if (k % 2 == 0 and live) or not still else still.pop(0)
    rest = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in m]
    for k, rc in enumerate(rest):
        m[rc] = STILL[(k * 5 + 2) % len(STILL)]
    return m


def wall(prefix, dur):
    """The wall's cards. A playing reel is a still (the frame it freezes on), the video over it, and its grey copy."""
    m, out, track = wall_map(), [], 1
    for r in range(ROWS):
        for c in range(COLS):
            t = m[(r, c)]
            vid = ""
            if t.startswith("w"):
                vid = video(f"{prefix}-v{r}{c}", f"wall/{t}", 0, dur, track)
                track += 1
            out.append(f'<div class="wl-card" style="left:{c * (CW + GAP)}px;top:{r * (CH + GAP)}px">'
                       f'<img src="assets/wall/{t}.jpg" alt="">{vid}<img class="g" src="assets/wall/{t}-g.jpg" alt=""></div>')
    return "".join(out)


def logo_scene(tmp):
    out = subprocess.run([sys.executable, "make_motion.py", "film-open-wide", "--out", tmp], cwd=LOGO_TOOLS, check=True,
                         capture_output=True, text=True).stdout
    info = json.loads(out[out.index("{"):out.rindex("}") + 1])
    return open(os.path.join(tmp, "compositions", "logo.html")).read(), info


def logo_box(info):
    """CSS box that puts the kit's stacked dark master exactly where the logo's build leaves the lockup."""
    (x0, y0), (x1, y1) = info["lockup_px"]
    svg = open(os.path.join(HERE, "assets", "logo", "socialstream-logo-stacked-dark.svg")).read()
    wk, hk = [float(v) for v in svg.split('viewBox="')[1].split('"')[0].split()[2:4]]
    f = (y1 - y0) / (hk * 0.8)
    left, top = x0 - (wk - (x1 - x0) / f) / 2 * f, y0 - hk * 0.10 * f
    return f"left:{left:.3f}px;top:{top:.3f}px;width:{wk * f:.3f}px;height:{hk * f:.3f}px"


# ================================ the scenes ================================
def scene_open(s, e, info):
    """The feed with the logo; the problem; "A social media meghalt." and the wall dies; on the drop the middle card
    comes back and grows into the frame: "Az érdeklődés vette át a helyét." """
    cx = W / 2 + WALL_X1
    inset0 = f"inset({H / 2 - CH / 2:.1f}px {W - cx - CW / 2:.1f}px {H / 2 - CH / 2:.1f}px {cx - CW / 2:.1f}px round 26px)"
    html = f"""<div class="fld" style="background:#05070f"></div>
    <div class="wl-in ff" data-layout-allow-overflow id="op-in">
      <div class="wl-tilt"><div class="wl-wall" id="op-wall">{wall("op", DEATH)}</div></div>
    </div>
    <div class="ff" id="op-dim" style="background:#05070f"></div>
    <div class="glow" id="op-glow"></div>
    <div class="glow wide" id="op-glow2"></div>
    <div class="rsv" id="op-p1"><div class="hd big">{TX['p1']}</div></div>
    <div class="rsv" id="op-p2"><div class="hd big">{TX['p2']}</div></div>
    <div class="rsv" id="op-p3"><div class="hd mid">{TX['p3']}</div></div>
    <div class="rsv" id="op-ca"><div><div class="hd big">{TX['ca']}</div>
      <div class="it huge" id="op-m">{TX['ca2']}</div></div></div>
    <div class="ff" id="op-rot" data-layout-allow-overflow><div class="ff" id="op-hcard">{video("op-hv", "clips/w-turn", SPARK - 0.04, e - SPARK + 0.04, 20, "full")}</div></div>
    <div class="ff" id="op-shade"></div>
    <div class="cb" id="op-cb">{TX['cb']}</div>"""
    css = WALL_CSS + """
    #root video.full { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
    #root #op-shade { background: linear-gradient(24deg, rgba(5, 7, 15, 0.86) 0%, rgba(5, 7, 15, 0.4) 36%, rgba(5, 7, 15, 0) 62%); }
    #root .cb { position: absolute; left: 130px; bottom: 120px; }
    #root .cb1 { font-size: 136px; white-space: nowrap; }
    #root .cb1 .it { font-size: 176px; }"""
    js = f"""
    // the wall: whole from the first frame (the thumbnail), settling back a little; it drifts until it dies
    tl.fromTo("#op-in", {{ scale: 1.12 }}, {{ scale: 1, duration: 1.4, ease: "expo.out" }}, 0);
    tl.fromTo("#op-wall", {{ x: {WALL_X0} }}, {{ x: {WALL_X0 - WALL_V * DEATH:.1f}, duration: {DEATH:g}, ease: "none" }}, 0);
    tl.fromTo("#op-wall", {{ x: {WALL_X0 - WALL_V * DEATH:.1f} }}, {{ x: {WALL_X1:.1f}, duration: 0.6, ease: "power2.out", immediateRender: false }}, AT({DEATH:g}));
    fade("#op-glow", 0.1, 0.5);
    tl.fromTo("#op-dim", {{ opacity: 0.1 }}, {{ opacity: 0.5, duration: 0.4, ease: "power2.inOut" }}, AT(2.9));
    fade("#op-glow2", 2.9, 0.4);
    // the problem, one phrase at a time
    say("#op-p1", {P1:g}, {P2 - 0.06:g}); say("#op-p2", {P2:g}, {P3 - 0.06:g}); say("#op-p3", {P3:g}, {P3_OUT:g});
    // the diagnosis: struck through, then "meghalt." and every card freezes and turns grey, from the middle outwards
    words("#op-ca .big .w", {CA:g});
    tl.fromTo("#op-stk", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.2, ease: "power3.out" }}, AT({STRIKE:g}));
    tl.fromTo("#op-ca .ss .w", {{ opacity: 1 }}, {{ opacity: 0.42, duration: 0.25, ease: "power2.out", immediateRender: false }}, AT({STRIKE + 0.1:g}));
    tl.fromTo("#op-m", {{ opacity: 0, filter: "blur(14px)", scale: 1.06 }}, {{ opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.26, ease: "power2.out" }}, AT({DEATH:g}));
    tl.fromTo("#op-wall .g", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: "power2.out", stagger: {{ grid: [{ROWS}, {COLS}], from: "center", amount: 0.5 }} }}, AT({DEATH:g}));
    tl.fromTo("#op-dim", {{ opacity: 0.5 }}, {{ opacity: 0.64, duration: 0.5, ease: "power2.out", immediateRender: false }}, AT({DEATH:g}));
    out("#op-ca", {CA_OUT:g});
    // the turn: the middle card comes back in colour, then grows into the whole frame and lands on the drop
    tl.fromTo("#op-hcard", {{ clipPath: "{inset0}" }}, {{ clipPath: "inset(0px 0px 0px 0px round 0px)", duration: {DROP - GROW:g}, ease: "power2.inOut" }}, AT({GROW:g}));
    tl.fromTo("#op-rot", {{ rotation: {TILT} }}, {{ rotation: 0, duration: {DROP - GROW:g}, ease: "power2.inOut" }}, AT({GROW:g}));
    fade("#op-rot", {SPARK:g}, 0.08);
    tl.fromTo(["#op-glow", "#op-glow2"], {{ opacity: 1 }}, {{ opacity: 0, duration: 0.14, ease: "power2.in", immediateRender: false }}, AT({SPARK - 0.08:g}));
    tl.fromTo("#op-in", {{ scale: 1 }}, {{ scale: 1.3, duration: {DROP - GROW:g}, ease: "power2.in", immediateRender: false }}, AT({GROW:g}));
    fade("#op-shade", {DROP - 0.08:g}, 0.3);
    words("#op-cb .w", {DROP:g}, 0.08);"""
    return html, js, css


def scene_flyx(s, e):
    """FlyX Tenerife: orange. Three phones fan out, their clips change on the bar; the reach counts up; three real
    comments type themselves; hearts rise; one slow push."""
    t0, cut = b(4), b(8)
    ls = [("fx-l0", 6, 96, 92, "255, 214, 102, 0.55"), ("fx-l1", 97, 5, 86, "150, 60, 255, 0.42")]
    ph = [("fx-p0", 880, 250, -20, -12, "fx1a", "fx1b", 1), ("fx-p2", 1490, 230, 18, 9, "fx3a", "fx3b", 1), ("fx-p1", 1180, 150, -10, -3, "fx2a", "fx2b", 2)]
    phones = "".join(phone(pid, x, y, [(fa, 0, cut - s), (fb, cut - s, e - cut)], 1 + 2 * k, z)
                     for k, (pid, x, y, r0, r1, fa, fb, z) in enumerate(ph))
    cm = [("fx-c0", 110, 548, "It was brilliant fun… highly recommended it", 640, b(6)),
          ("fx-c1", 150, 722, "A fantastic experience, absolutely loved it.", 640, b(7.5)),
          ("fx-c2", 110, 896, "Where is it please?", None, b(9))]
    hh, hj = hearts("fx-h", 11, b(5), b(11), (900, 640, 1820, 980), 4)
    html = (field("linear-gradient(135deg,#ff8a1f 0%,#ff5a3c 48%,#e0306f 100%)", ls) + tile("FlyX Tenerife")
            + f'<div class="fxt"><div class="eb" id="fx-eb">{TX["fx_eb"]}</div>'
              f'<div class="hd fxn" id="fx-n">{digits(2, "fx-cnt")}<span class="k">K</span></div>'
              f'<div class="lab" id="fx-lab">{wl(TX["fx_lab"])}</div></div>'
            + f'<div class="ff" id="fx-grp" data-layout-allow-overflow>{phones}</div>'
            + "".join(bubble(cid, x, y, TX["comment"] + " · FlyX Tenerife", text, width=w) for cid, x, y, text, w, t in cm) + hh)
    css = """
    #root .fxt { position: absolute; left: 110px; top: 92px; }
    #root .fxn { display: flex; align-items: baseline; margin-top: 14px; white-space: nowrap; font-size: 290px; line-height: 0.86; letter-spacing: -0.05em; }
    #root .fxt .lab { margin-top: 20px; }
    #root #fx-grp { transform-origin: 1370px 545px; }"""
    js = [f'wipeIn({s:g}, "dr");', f'drift("#fx-l0", {s:g}, {e - s:g}, 80, -50); drift("#fx-l1", {s:g}, {e - s:g}, -70, 50);',
          f'drift("#wp .tile", {s:g}, {e - s:g}, -60, 0);']
    js += [f'rise("#{pid}", {s + 0.04 + 0.09 * i:g}, {r0}, {r1});' for i, (pid, x, y, r0, r1, fa, fb, z) in enumerate(reversed(ph))]
    js += [f'fade("#fx-eb", {t0 - 0.1:g});', f'tl.fromTo("#fx-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "none" }}, AT({t0 - 0.04:g}));',
           f'count(document.getElementById("fx-cnt"), {t0:g}, 0.9, 69);', f'words("#fx-lab .w", {t0 + 0.08:g}, 0.06);']
    for cid, x, y, text, w, t in cm:
        js += [f'pop("#{cid}", {t - 0.08:g});', f'type("#{cid}", {t + 0.06:g});']
    js += [hj, f'tl.fromTo("#fx-grp", {{ scale: 1 }}, {{ scale: 1.08, duration: {b(12) - cut:g}, ease: "power1.inOut" }}, AT({cut:g}));']
    return html, "\n    ".join(js), css


def scene_enzo(s, e):
    """Prof Enzo: green. Three reels fill the height; the total of their plays counts over them; the best reels'
    counts pop along the bottom."""
    t0, cut = b(12), b(16)
    ls = [("ez-l0", 4, 6, 90, "190, 255, 120, 0.4"), ("ez-l1", 96, 96, 90, "20, 60, 160, 0.45")]
    cl = [("ez-c0", 170, "ez1a", "ez1b"), ("ez-c1", 710, "ez2a", "ez2b"), ("ez-c2", 1250, "ez3a", "ez3b")]
    cards = "".join(card(cid, x, 96, 500, 889, [(fa, 0, cut - s), (fb, cut - s, e - cut)], 1 + 2 * k) for k, (cid, x, fa, fb) in enumerate(cl))
    chips = [("149K", 250, b(15)), ("122K", 610, b(16)), ("105K", 970, b(17)), ("82K", 1330, b(18))]
    hh, hj = hearts("ez-h", 12, b(13), b(19.5), (200, 760, 1720, 1000), 9)
    html = (field("linear-gradient(140deg,#16c172 0%,#0b8f7a 52%,#075e63 100%)", ls) + tile("Prof Enzo") + cards
            + '<div class="ff" id="ez-scrim" style="background:rgba(4,20,22,0.42)"></div>'
            + f'<div class="ezo"><div class="ezrow"><div class="hd ezn" id="ez-n">{digits(3, "ez-cnt")}<span>K</span></div>'
              f'<div class="hd ezn" id="ez-m" style="opacity:0">1M+</div></div><div class="hd ezl" id="ez-lab">{TX["ez_lab"]}</div></div>'
            + f'<div class="pill" id="ez-eb" style="left:200px;top:128px">{TX["ez_eb"]}</div>'
            + f'<div class="pill" id="ez-f" style="left:1440px;top:128px">{TX["ez_f"]}</div>'
            + "".join(f'<div class="chip" id="ez-k{k}" style="left:{x}px;top:872px"><i></i>{v}</div>' for k, (v, x, t) in enumerate(chips)) + hh)
    css = """
    #root #ez-scrim, #root .ezo, #root #ez-eb, #root #ez-f, #root .chip { z-index: 4; }
    #root .ezo { position: absolute; left: 0; right: 0; top: 262px; text-align: center; }
    #root .ezrow { position: relative; height: 390px; }
    #root .ezn { position: absolute; left: 0; right: 0; top: 0; display: flex; justify-content: center; align-items: baseline; white-space: nowrap;
      font-size: 440px; line-height: 0.9; letter-spacing: -0.05em; text-shadow: 0 14px 70px rgba(0, 0, 0, 0.5); }
    #root .ezl { font-size: 108px; text-shadow: 0 10px 50px rgba(0, 0, 0, 0.5); }
    #root #ez-m { transform-origin: 50% 60%; }"""
    js = [f'wipeIn({s:g}, "dl");', f'drift("#ez-l0", {s:g}, {e - s:g}, 70, 50); drift("#ez-l1", {s:g}, {e - s:g}, -70, -50);',
          f'drift("#wp .tile", {s:g}, {e - s:g}, 60, 0);']
    js += [f'rise("#{cid}", {s + 0.04 + 0.08 * k:g}, {(-6, 0, 6)[k]}, 0);' for k, (cid, x, fa, fb) in enumerate(cl)]
    js += [f'fade("#ez-scrim", {t0 - 0.12:g}, 0.3);', f'pop("#ez-eb", {t0 - 0.06:g}, 0.4);',
           f'tl.fromTo("#ez-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "none" }}, AT({t0 - 0.02:g}));',
           f'count(document.getElementById("ez-cnt"), {t0:g}, {b(14) - t0 - 0.04:g}, 999, "power2.in");',
           f'fade("#ez-lab", {t0 + 0.1:g});',
           # the hit: the count becomes "1M+" exactly on the beat
           f'tl.set("#ez-n", {{ opacity: 0 }}, AT({b(14):g}));', f'tl.set("#ez-m", {{ opacity: 1 }}, AT({b(14):g}));',
           f'tl.fromTo("#ez-m", {{ scale: 1.28 }}, {{ scale: 1, duration: 0.5, ease: "back.out(2.2)" }}, AT({b(14):g}));',
           f'pop("#ez-f", {b(14.5):g}, 0.4);']
    js += [f'pop("#ez-k{k}", {t - 0.08:g}, 0.4);' for k, (v, x, t) in enumerate(chips)]
    js.append(hj)
    return html, "\n    ".join(js), css


def scene_prod(s, e):
    """The team's productions: polaroids of them at work pile over the frame (and over Prof Enzo's world) and
    scatter; behind them, violet: five reel cards and what they do to a video."""
    t0 = b(20)
    rnd = random.Random(21)
    ls = [("pr-l0", 94, 8, 96, "255, 64, 104, 0.4"), ("pr-l1", 4, 96, 90, "56, 160, 255, 0.5")]
    # the pile: five columns, three rows, jittered; each flies in from outside and out again
    pols, pj, order = [], [], list(range(15))
    rnd.shuffle(order)
    for i in range(15):
        c, r = i % 5, i // 5
        x, y = -30 + c * 392 + rnd.uniform(-26, 26), -80 + r * 345 + rnd.uniform(-22, 22)
        rot = rnd.uniform(-11, 11)
        dx, dy = x + 200 - W / 2, y + 250 - H / 2
        n = math.hypot(dx, dy) or 1
        fx, fy = dx / n * 1700 + rnd.uniform(-100, 100), dy / n * 1700 + rnd.uniform(-100, 100)
        k = order.index(i)
        pols.append(f'<div class="pol" id="pr-p{i}" data-layout-ignore style="left:{x:.0f}px;top:{y:.0f}px;z-index:{10 + k}"><img src="assets/pol/p{i % 10 + 1:02d}.jpg" alt=""></div>')
        pj.append(f'tl.fromTo("#pr-p{i}", {{ x: {fx:.0f}, y: {fy:.0f}, rotation: {rot + rnd.uniform(-35, 35):.1f} }}, {{ x: 0, y: 0, rotation: {rot:.1f}, duration: 0.5, ease: "expo.out" }}, AT({t0 - 0.1 + 0.03 * k:.2f}));')
        pj.append(f'tl.fromTo("#pr-p{i}", {{ x: 0, y: 0, rotation: {rot:.1f} }}, {{ x: {fx * 1.05:.0f}, y: {fy * 1.05:.0f}, rotation: {rot + rnd.uniform(-25, 25):.1f}, duration: 0.45, ease: "power3.in", immediateRender: false }}, AT({t0 + 1.24 + 0.014 * k:.2f}));')
    t_c = t0 + 1.2                                          # the cards come as the polaroids leave
    cl = [("pr-c0", 60, 351, 280, 498, [("pr1", t_c - s, b(26) - t_c), ("pr6", b(26) - s, e - b(26))]),
          ("pr-c1", 380, 298, 340, 604, [("pr2", t_c - s, b(26) - t_c), ("pr4", b(26) - s, e - b(26))]),
          ("pr-c2", 760, 245, 400, 711, [("pw2", t_c - s, e - t_c)]),
          ("pr-c3", 1200, 298, 340, 604, [("pw1", t_c - s, b(26) - t_c), ("pr5", b(26) - s, e - b(26))]),
          ("pr-c4", 1580, 351, 280, 498, [("pr3", t_c - s, e - t_c)])]
    cards, track = "", 1
    for cid, x, y, w, h, clips in cl:
        cards += card(cid, x, y, w, h, clips, track)
        track += len(clips)
    tags = TX["tags"]
    hh, hj = hearts("pr-h", 8, b(24), b(27.5), (200, 760, 1700, 1000), 13)
    html = (f'<div class="ff" id="pr-g">{field("linear-gradient(140deg,#4a22c8 0%,#3418a0 52%,#1c0d58 100%)", ls)}{tile("SocialStream")}</div>'
            + f'<div class="eb" id="pr-eb" style="position:absolute;left:60px;top:70px">{TX["pr_eb"]}</div>'
            + '<div id="pr-tags" data-layout-allow-overflow>' + "".join(f'<div class="tag" id="pr-t{k}">{t}</div>' for k, t in enumerate(tags)) + '</div>'
            + cards + hh + "".join(pols))
    css = """
    #root #pr-tags { position: absolute; left: 60px; top: 124px; display: flex; gap: 18px; }
    #root #pr-tags .tag { position: relative; font-size: 40px; padding: 17px 30px; }"""
    js = pj + [f'fade("#pr-g", {t0 + 0.34:g}, 0.2);',
               f'drift("#pr-l0", {t0:g}, {e - t0:g}, -70, 50); drift("#pr-l1", {t0:g}, {e - t0:g}, 70, -50);',
               f'fade("#pr-eb", {t_c:g});']
    js += [f'rise("#{cid}", {t_c - 0.04 + 0.06 * k:g}, {(-8, -4, 0, 4, 8)[k]}, 0, 0.66);' for k, (cid, *_r) in enumerate(cl)]
    js += [f'pop("#pr-t{k}", {b(24) + 0.5 * BEAT * k - 0.08:.2f}, 0.4);' for k in range(len(tags))]
    js.append(hj)
    return html, "\n    ".join(js), css


def scene_how(s, e):
    """Night. How they work, one phrase every two beats, each with what it is about around it: their reels, the
    platforms, the numbers that follow."""
    T = [b(28), b(30), b(32), b(34)]
    ls = [("hw-l0", 14, 10, 90, "66, 92, 255, 0.36"), ("hw-l1", 88, 92, 90, "136, 78, 255, 0.34"), ("hw-l2", 96, 6, 50, "255, 64, 104, 0.22")]

    def ring(n, a0, w, h, rx=770, ry=395):
        return [(W / 2 + rx * math.cos(a0 + i * 2 * math.pi / n) - w / 2, H / 2 + ry * math.sin(a0 + i * 2 * math.pi / n) - h / 2) for i in range(n)]

    g0 = "".join(f'<div class="card mini g0" style="left:{x:.0f}px;top:{y:.0f}px;width:170px;height:302px;transform:rotate({(-7, 5, -4, 8, -6, 4)[i]}deg)">'
                 f'<img src="assets/wall/{t}.jpg" alt=""></div>' for i, ((x, y), t) in enumerate(zip(ring(6, 0.42, 170, 302, 740, 360), ["w02", "w04", "w07", "w15", "w09", "w10"])))
    g1 = "".join(f'<div class="tag g1" style="left:{x:.0f}px;top:{y:.0f}px">{t}</div>' for (x, y), t in zip(ring(4, 0.85, 230, 92, 700, 350), ["Meta", "TikTok", "Google", "Reels"]))
    g2 = "".join(f'<div class="chip g2" style="left:{x:.0f}px;top:{y:.0f}px">{t}</div>' for (x, y), t in zip(ring(4, 0.3, 270, 104, 700, 350), ["81×", "79M Ft", "23×", "105 Ft"]))
    html = (field("#05070f", ls) + g0 + g1 + g2
            + f'<div class="rsv" id="hw-0"><div class="hd mid">{TX["how"][0]}</div></div>'
            + f'<div class="rsv" id="hw-1"><div class="hd mid">{TX["how"][1]}</div></div>'
            + f'<div class="rsv" id="hw-2"><div class="hd mid">{TX["how"][2]}</div></div>'
            + f'<div class="rsv" id="hw-3"><div class="hd big" id="hw-3t">{TX["how"][3]}</div></div>')
    css = """
    #root .mini { border-radius: 22px; }
    #root .g1 { font-size: 50px; padding: 21px 38px; border-radius: 60px; }
    #root .g2 { font-size: 56px; padding: 24px 36px; border-radius: 60px; }
    #root .hz { font-size: 196px; }
    #root #hw-3t { transform-origin: 50% 50%; }"""
    js = [f'wipeIn({s:g}, "iris");', f'drift("#hw-l0", {s:g}, {e - s:g}, 60, 40); drift("#hw-l1", {s:g}, {e - s:g}, -60, -40);',
          f'say("#hw-0", {T[0]:g}, {T[1] - 0.06:g}); say("#hw-1", {T[1]:g}, {T[2] - 0.06:g}); say("#hw-2", {T[2]:g}, {T[3] - 0.06:g}); say("#hw-3", {T[3]:g});']
    for k in range(3):                                      # each ring flies in around its phrase and goes with it
        js.append(f'tl.fromTo(".g{k}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "none", stagger: 0.04 }}, AT({T[k] - 0.06:g}));')
        js.append(f'tl.fromTo(".g{k}", {{ scale: 0.3 }}, {{ scale: 1, duration: 0.5, ease: "back.out(1.6)", stagger: 0.04 }}, AT({T[k] - 0.06:g}));')
        js.append(f'tl.fromTo(".g{k}", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.14, ease: "power2.in", immediateRender: false }}, AT({T[k + 1] - 0.12:g}));')
    # the last phrase is the door to the numbers: the camera goes through it
    js.append(f'tl.fromTo("#hw-3t", {{ scale: 1 }}, {{ scale: 3.2, duration: 0.3, ease: "power3.in" }}, AT({b(36) - 0.34:g}));')
    js.append(f'tl.fromTo("#hw-3t", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.2, ease: "power2.in", immediateRender: false }}, AT({b(36) - 0.24:g}));')
    return html, "\n    ".join(js), css


RES_CSS = """
    #root .rn { position: absolute; display: flex; align-items: baseline; white-space: nowrap; }
    #root .rn .cnt { font-size: 520px; line-height: 0.84; letter-spacing: -0.055em; }
    #root .rn .ui { font-size: 290px; line-height: 0.84; margin-left: 0.12em; }
    #root .rn .x { font-family: Sora, Inter, sans-serif; font-weight: 700; font-size: 320px; line-height: 0.84; margin-left: 0.02em; }
    #root .rn .u { font-family: Sora, Inter, sans-serif; font-weight: 700; font-size: 128px; margin-left: 0.16em; letter-spacing: -0.03em; }"""


def res_open(rid, s, e, kind, ls):
    js = [f'wipeIn({s:g}, "{kind}");'] + [f'drift("#{l[0]}", {s:g}, {e - s:g}, {70 if k % 2 else -80}, {-50 if k % 2 else 60});' for k, l in enumerate(ls)]
    js.append(f'fade("#{rid}-eb", {s + WIPE - 0.1:g});')
    return js


def scene_r1(s, e):
    """79 M Ft in one week, blue: the week's days light up one by one while the revenue climbs."""
    t0, step = b(36), 0.118
    ls = [("r1-l0", 94, 90, 100, "255, 64, 104, 0.5"), ("r1-l1", 4, 4, 86, "56, 190, 255, 0.5")]
    days = TX["days"]
    html = (field("linear-gradient(140deg,#1b3cff 0%,#3a22d8 58%,#1a0f6c 100%)", ls)
            + f'<div class="eb" id="r1-eb" style="position:absolute;left:130px;top:110px">{TX["r1_eb"]}</div>'
            + f'<div class="hd rn" id="r1-n" style="left:118px;top:168px">{digits(2, "r1-cnt")}<span class="it ui">M Ft</span></div>'
            + f'<div class="lab" id="r1-lab" style="position:absolute;left:130px;top:650px">{wl(TX["r1_lab"])}</div>'
            + '<div class="days">' + "".join(f'<div class="day" id="r1-d{k}">{d}</div>' for k, d in enumerate(days)) + '</div>'
            + '<img id="r1-obj" src="assets/img/o-hall-mix.webp" alt="" style="position:absolute;left:1340px;top:120px;width:500px;height:500px">')
    css = RES_CSS + """
    #root .days { position: absolute; left: 130px; top: 800px; display: flex; gap: 18px; }
    #root .day { width: 180px; height: 116px; border-radius: 28px; display: flex; align-items: center; justify-content: center;
      font: 700 46px/1 Sora, Inter, sans-serif; letter-spacing: -0.02em; background: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.5);
      box-shadow: inset 0 0 0 1.5px rgba(255, 255, 255, 0.22); }"""
    js = res_open("r1", s, e, "iris", ls) + [
        f'tl.fromTo("#r1-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "none" }}, AT({t0 - 0.06:g}));',
        f'count(document.getElementById("r1-cnt"), {t0:g}, {7 * step:g}, 79, "power1.inOut");',
        f'words("#r1-lab .w", {t0 - 0.02:g}, 0.05);',
        f'tl.fromTo("#r1-obj", {{ opacity: 0, y: 90, scale: 0.8, rotation: -8 }}, {{ opacity: 1, y: 0, scale: 1, rotation: 0, duration: 0.6, ease: "back.out(1.5)" }}, AT({t0 - 0.12:g}));']
    for k in range(7):
        t = t0 + (k + 1) * step - 0.06
        js.append(f'tl.fromTo("#r1-d{k}", {{ backgroundColor: "rgba(255,255,255,0.1)", color: "rgba(255,255,255,0.5)" }}, {{ backgroundColor: "#ffffff", color: "#141a4a", duration: 0.1, ease: "power2.out" }}, AT({t:.2f}));')
        js.append(f'tl.fromTo("#r1-d{k}", {{ scale: 0.86 }}, {{ scale: 1, duration: 0.3, ease: "back.out(2.4)" }}, AT({t:.2f}));')
    return html, "\n    ".join(js), css


def scene_r2(s, e):
    """81x ROAS, red-pink: one forint, then eighty-one: a coin, then a 9 x 9 grid of coins bursts out."""
    t0 = b(40)
    ls = [("r2-l0", 6, 94, 92, "255, 170, 80, 0.5"), ("r2-l1", 96, 6, 90, "110, 60, 255, 0.5")]
    html = (field("linear-gradient(140deg,#ff2d5f 0%,#d81d74 55%,#7a1690 100%)", ls)
            + f'<div class="eb" id="r2-eb" style="position:absolute;left:130px;top:110px">{TX["r2_eb"]}</div>'
            + f'<div class="hd rn" id="r2-n" style="left:118px;top:168px">{digits(2, "r2-cnt")}<span class="x">×</span><span class="u">ROAS</span></div>'
            + '<div class="c1" id="r2-c1"><i class="cn"></i><span>1 Ft</span><b>→</b></div>'
            + '<div class="grid" id="r2-g" data-motion-blur="off">' + '<i class="cn"></i>' * 81 + '</div>'
            + '<div class="gl" id="r2-gl">81 Ft</div>')
    css = RES_CSS + """
    #root .cn { display: block; width: 62px; height: 62px; border-radius: 50%;
      background: radial-gradient(circle at 34% 30%, #ffffff 0%, #ffe8ef 48%, #ffbfd0 100%);
      box-shadow: inset 0 0 0 4px rgba(255, 255, 255, 0.7), 0 10px 20px -8px rgba(40, 0, 40, 0.55); }
    #root #r2-n .cnt { font-size: 460px; }
    #root #r2-n .x { font-size: 280px; }
    #root #r2-n .u { font-size: 112px; }
    #root .grid .cn { width: 54px; height: 54px; }
    #root .grid { position: absolute; left: 1284px; top: 170px; display: grid; grid-template-columns: repeat(9, 54px); gap: 10px; }
    #root .gl { position: absolute; left: 1284px; top: 764px; width: 566px; text-align: center; font: 700 76px/1 Sora, Inter, sans-serif; letter-spacing: -0.03em; }
    #root .c1 { position: absolute; left: 130px; top: 720px; display: flex; align-items: center; gap: 28px; font: 700 96px/1 Sora, Inter, sans-serif; letter-spacing: -0.03em; transform-origin: 0 50%; }
    #root .c1 .cn { width: 150px; height: 150px; }
    #root .c1 b { font-weight: 700; margin-left: 20px; opacity: 0.85; }"""
    js = res_open("r2", s, e, "dl", ls) + [
        f'pop("#r2-c1", {t0 - 0.12:g}, 0.4);',
        f'tl.fromTo("#r2-g .cn", {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: 0.28, ease: "back.out(2)", stagger: {{ grid: [9, 9], from: "center", amount: 0.5 }} }}, AT({t0 + 0.16:g}));',
        f'tl.fromTo("#r2-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "none" }}, AT({t0 - 0.06:g}));',
        f'count(document.getElementById("r2-cnt"), {t0:g}, 0.8, 81, "power2.out");',
        f'tl.fromTo("#r2-n .x, #r2-n .u", {{ opacity: 0, filter: "blur(12px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.24, ease: "power2.out" }}, AT({t0 + 0.4:g}));',
        f'tl.fromTo("#r2-gl", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }}, AT({t0 + 0.7:g}));']
    return html, "\n    ".join(js), css


def scene_r3(s, e):
    """23x ROAS at Christmas, white: the number slams in ink; the holiday revenue counts under it; the watch drops in."""
    t0 = b(44)
    html = ('<div class="fld" style="background:#f3f5fb"></div>'
            + f'<div class="eb" id="r3-eb" style="position:absolute;left:0;right:0;top:106px;text-align:center;color:#3a4266">{TX["r3_eb"]}</div>'
            + f'<div class="hd rn" id="r3-n" style="left:0;right:0;top:160px;justify-content:center">{digits(2, "r3-cnt")}<span class="x acc">×</span><span class="u">ROAS</span></div>'
            + f'<div class="pc"><div class="pill" id="r3-p">{TX["r3_p"][0]}' + digits(1, "r3-pc") + f'{TX["r3_p"][1]}</div></div>'
            + '<img id="r3-obj" src="assets/img/o-watch-mix.webp" alt="" style="position:absolute;left:1390px;top:560px;width:460px;height:460px">')
    css = RES_CSS + """
    #root #r3-n { color: #0b1030; transform-origin: 50% 60%; }
    #root #r3-n .cnt { font-size: 580px; }
    #root .pc { position: absolute; left: 0; right: 0; top: 720px; display: flex; justify-content: center; }
    #root #r3-p { position: relative; background: #0b1030; color: #fff; font: 700 54px/1 Sora, Inter, sans-serif; letter-spacing: -0.02em; padding: 24px 40px; box-shadow: none; }
    #root #r3-p .cnt .d { width: 0.6em; }"""
    js = [f'wipeIn({s:g}, "up");', f'fade("#r3-eb", {s + WIPE - 0.1:g});',
          f'tl.fromTo("#r3-n", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.36, ease: "expo.out" }}, AT({t0 - 0.04:g}));',
          f'count(document.getElementById("r3-cnt"), {t0 - 0.04:g}, 0.5, 23, "power2.out");',
          f'pop("#r3-p", {t0 + 0.42:g}, 0.4);', f'count(document.getElementById("r3-pc"), {t0 + 0.46:g}, 0.4, 8, "power2.out");',
          f'tl.fromTo("#r3-obj", {{ opacity: 0, y: -260, rotation: 24 }}, {{ opacity: 1, y: 0, rotation: 8, duration: 0.7, ease: "bounce.out" }}, AT({t0 + 0.2:g}));']
    return html, "\n    ".join(js), css


def scene_r4(s, e):
    """About 5 700 sign-ups at 105 Ft each, violet: a counter races while dots fill the frame; the price stamps in."""
    t0 = b(48)
    ls = [("r4-l0", 94, 8, 92, "255, 64, 104, 0.45"), ("r4-l1", 6, 94, 92, "56, 190, 255, 0.5")]
    pts = [(24 + c * 48, 26 + r * 58) for r in range(18) for c in range(40)]
    random.Random(7).shuffle(pts)                           # a fixed order, the same on every render
    dots = "".join(f'<i style="left:{x}px;top:{y}px"></i>' for x, y in pts)
    html = (field("linear-gradient(140deg,#7a35ff 0%,#5020d0 55%,#2a1280 100%)", ls)
            + f'<div class="dots" id="r4-dots" data-motion-blur="off" data-layout-ignore>{dots}</div>'
            + f'<div class="eb" id="r4-eb" style="position:absolute;left:0;right:0;top:106px;text-align:center">{TX["r4_eb"]}</div>'
            + f'<div class="hd rn" id="r4-n" style="left:0;right:0;top:170px;justify-content:center"><span class="ap">≈</span>{digits(4, "r4-cnt", gap_after=0, sep=TX["thou"])}</div>'
            + f'<div class="lab" id="r4-lab" style="position:absolute;left:0;right:0;top:590px;text-align:center">{wl(TX["r4_lab"])}</div>'
            + f'<div class="pc"><div class="stamp" id="r4-st" style="opacity:0">{TX["r4_st"][0]} <span>{TX["r4_st"][1]}</span></div></div>')
    css = RES_CSS + """
    #root .dots i { position: absolute; width: 8px; height: 8px; border-radius: 50%; background: rgba(255, 255, 255, 0.3); }
    #root .pc { z-index: 3; }
    #root #r4-n .cnt { font-size: 420px; }
    #root #r4-n .ap { font-size: 240px; line-height: 0.84; margin-right: 0.1em; opacity: 0.8; }
    #root #r4-lab { font-size: 64px; }
    #root .pc { position: absolute; left: 0; right: 0; top: 720px; display: flex; justify-content: center; }
    #root .stamp { padding: 22px 46px 26px; border-radius: 26px; background: #ff3f6c; color: #fff; font: 700 104px/1 Sora, Inter, sans-serif;
      letter-spacing: -0.03em; box-shadow: 0 30px 60px -24px rgba(40, 0, 60, 0.6); }
    #root .stamp span { font-size: 60px; font-weight: 600; opacity: 0.92; }"""
    js = res_open("r4", s, e, "dr", ls) + [
        f'tl.fromTo("#r4-dots i", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "none", stagger: {{ amount: 0.7 }} }}, AT({t0 - 0.2:g}));',
        f'tl.fromTo("#r4-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "none" }}, AT({t0 - 0.06:g}));',
        f'count(document.getElementById("r4-cnt"), {t0:g}, 0.6, 5700, "expo.out");',
        f'words("#r4-lab .w", {t0 + 0.1:g}, 0.05);',
        # the stamp is a hit: it is there on the beat, then settles
        f'tl.set("#r4-st", {{ opacity: 1 }}, AT({b(49):g}));',
        f'tl.fromTo("#r4-st", {{ scale: 1.7, rotation: -10 }}, {{ scale: 1, rotation: -4, duration: 0.3, ease: "expo.out" }}, AT({b(49):g}));']
    return html, "\n    ".join(js), css


def scene_m300(s, e):
    """300M+ Ft managed since 2022: night, the widest number of the film."""
    t0 = b(52)
    ls = [("m3-l0", 12, 90, 100, "66, 92, 255, 0.5"), ("m3-l1", 90, 8, 96, "136, 78, 255, 0.5"), ("m3-l2", 60, 110, 60, "255, 64, 104, 0.3")]
    html = (field("#070a1c", ls)
            + f'<div class="eb" id="m3-eb" style="position:absolute;left:0;right:0;top:150px;text-align:center">{TX["m3_eb"]}</div>'
            + f'<div class="hd rn" id="m3-n" style="left:0;right:0;top:220px;justify-content:center">{digits(3, "m3-cnt")}<span class="mp">M+</span><span class="it ui">Ft</span></div>'
            + f'<div class="lab" id="m3-lab" style="position:absolute;left:0;right:0;top:720px;text-align:center">{wl(TX["m3_lab"])}</div>')
    css = RES_CSS + """
    #root #m3-n .cnt, #root #m3-n .mp { font-size: 440px; line-height: 0.84; letter-spacing: -0.055em; }
    #root #m3-n .ui { font-size: 330px; }
    #root #m3-lab { font-size: 76px; font-weight: 700; font-family: Sora, Inter, sans-serif; letter-spacing: -0.03em; }"""
    js = res_open("m3", s, e, "iris", ls) + [
        f'tl.fromTo("#m3-n", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "none" }}, AT({t0 - 0.06:g}));',
        f'count(document.getElementById("m3-cnt"), {t0:g}, 0.9, 300, "expo.out");',
        f'words("#m3-lab .w", {t0 + 0.3:g}, 0.06);']
    return html, "\n    ".join(js), css


def scene_voices(s, e):
    """"Ne nekünk higgy. Nekik." Then their clients' reviews stack up the frame, one a beat, typing themselves;
    the last lands four beats before the wall returns, so the stack can be read."""
    BASE, STEP, CWD = 826, 214, 1060
    VOICES = TX["voices"]
    t_i = [b(59 + i) for i in range(len(VOICES))]         # the last one lands two beats before the wall returns
    ls = [("vc-l0", 8, 12, 80, "66, 92, 255, 0.3"), ("vc-l1", 94, 90, 84, "255, 64, 104, 0.24")]
    cards = "".join(bubble(f"vc-q{i}", (W - CWD) // 2, BASE + i * STEP, src, text, "q" if kind == "q" else "", CWD)
                    for i, (kind, src, text) in enumerate(VOICES))
    rnd = random.Random(5)
    bubs, bj = [], []
    for k in range(10):                                     # quotation marks drift up at the sides
        size = rnd.choice([200, 260, 320, 400])
        x = rnd.uniform(30, 330 - size * 0.4) if k % 2 == 0 else rnd.uniform(1600, 1900 - size * 0.4)
        y0 = rnd.uniform(700, 1080)
        tt = b(59) - 0.3 + rnd.uniform(0, 3.4)
        bubs.append(f'<div class="qm it" id="vc-b{k}" data-layout-ignore style="font-size:{size}px">{TX["qm"][k % 2]}</div>')
        bj.append(f'heart("#vc-b{k}", {tt:.2f}, {x:.0f}, {y0:.0f}, {rnd.uniform(420, 760):.0f}, {rnd.uniform(-30, 30):.0f}, {rnd.uniform(2.2, 3.0):.2f});')
    html = (field("#05070f", ls) + "".join(bubs)
            + f'<div class="rsv" id="vc-0"><div class="hd {TX["v0"][0]}">{TX["v0"][1]}</div></div>'
            + f'<div class="rsv" id="vc-1"><div class="it huge">{TX["v1"]}<span class="acc">.</span></div></div>'
            + f'<div class="ff" id="vc-st" data-layout-allow-overflow>{cards}</div>')
    css = """
    #root .bub { padding: 26px 44px 28px 118px; border-radius: 32px; font-size: 38px; }
    #root .bub.q { font-size: 52px; }
    #root .bub .av { left: 32px; top: 28px; width: 60px; height: 60px; }
    #root .bub .src { font-size: 24px; }
    #root .qm { position: absolute; left: 0; top: 0; line-height: 0.7; color: rgba(255, 255, 255, 0.2); }"""
    js = [f'wipeIn({s:g}, "dl");', f'drift("#vc-l0", {s:g}, {e - s:g}, 60, 40); drift("#vc-l1", {s:g}, {e - s:g}, -60, -40);',
          f'say("#vc-0", {b(56):g}, {b(58) - 0.06:g}); say("#vc-1", {b(58):g}, {b(59) - 0.12:g});']
    for i, t in enumerate(t_i):
        if i:                                               # the stack steps up one card just before the next lands
            js.append(f'tl.fromTo("#vc-st", {{ y: {-(i - 1) * STEP} }}, {{ y: {-i * STEP}, duration: 0.3, ease: "power3.inOut", immediateRender: false }}, AT({t - 0.34:g}));')
        js += [f'pop("#vc-q{i}", {t - 0.1:g}, 0.4);', f'type("#vc-q{i}", {t + 0.02:g}, 0.04);']
    js += bj
    return html, "\n    ".join(js), css


def scene_close(s, e, info):
    """The wall is alive again and pulls back; the promise, a line every four beats; the logo."""
    T1, T2, TL = b(68), b(72), b(76)
    html = f"""<div class="fld" style="background:#05070f"></div>
    <div class="wl-in ff" data-layout-allow-overflow id="cs-in">
      <div class="wl-tilt"><div class="wl-wall" id="cs-wall">{wall("cs", e - s)}</div></div>
    </div>
    <div class="ff" id="cs-dim" style="background:rgba(5,7,15,0.52)"></div>
    <div class="glow wide" id="cs-glow2"></div>
    <div class="glow" id="cs-glow"></div>
    <div class="rsv" id="cs-1"><div><div class="hd big">{TX['c1'][0]}</div><div class="it huge">{TX['c1'][1]}<span class="acc">.</span></div></div></div>
    <div class="rsv" id="cs-2"><div><div class="hd big">{TX['c2'][0]}</div><div class="it huge">{TX['c2'][1]}<span class="acc">.</span></div></div></div>
    <img id="cs-logo" src="assets/logo/socialstream-logo-stacked-dark.svg" alt="SocialStream" style="position:absolute;opacity:0;{logo_box(info)}">
    <div class="eb" id="cs-eb" style="position:absolute;left:0;right:0;top:790px;text-align:center">{TX['cs_eb']}</div>"""
    css = WALL_CSS + """
    #root .huge { font-size: 220px; }
    #root #cs-logo { transform-origin: 50% 50%; }"""
    js = f"""wipeIn({s:g}, "up");
    tl.fromTo("#cs-in", {{ scale: 1.5, rotation: 5 }}, {{ scale: 1, rotation: 0, duration: {e - s:g}, ease: "power2.out" }}, AT({s:g}));
    tl.fromTo("#cs-wall", {{ x: 150 }}, {{ x: -30, duration: {e - s:g}, ease: "none" }}, AT({s:g}));
    say("#cs-1", {T1:g}, {T2 - 0.1:g}); say("#cs-2", {T2:g}, {TL - 0.3:g});
    tl.fromTo("#cs-glow2", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.3, ease: "power2.inOut", immediateRender: false }}, AT({TL - 0.3:g}));
    fade("#cs-glow", {TL - 0.3:g}, 0.4);
    // the logo is a hit: on the beat, sharp, then it holds
    tl.set("#cs-logo", {{ opacity: 1 }}, AT({TL:g}));
    tl.fromTo("#cs-logo", {{ scale: 1.12, filter: "blur(10px)" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, AT({TL:g}));
    fade("#cs-eb", {b(77):g}, 0.3);"""
    return html, js, css


# ================================ the sound ================================
X = {  # effect: file in assets/audio, where it hits (s into the file), volume
    "whoosh": ("whoosh-deep", 0.63, 0.3), "wind": ("wind-woosh", 1.595, 0.26), "pop": ("pop-bubble", 0.241, 0.5),
    "pop2": ("pop-soap", 0.186, 0.45), "shutter": ("shutter", 0.305, 0.5), "sub": ("rumble-bass", 0.051, 0.5),
    "impact": ("impact-cine", 2.172, 0.75), "coins": ("coins", 0.082, 0.45), "cheer": ("cheer", 0.636, 0.3),
}


def sounds():
    """The music, and an effect on every visible action that needs one: each placed so that its hit lands a frame
    after its picture. (name, when it hits, optional (seconds it plays, fade-out))."""
    ev = [("sub", DEATH, (1.6, 1.3), 0.3), ("wind", DROP), ("sub", DROP), ("cheer", DROP, (2.6, 1.4)),
          ("whoosh", b(4)), ("pop2", b(4) + 0.9), ("pop", b(6)), ("pop2", b(7.5)), ("pop", b(9)),
          ("wind", b(12)), ("pop2", b(14)), ("pop", b(15)), ("pop2", b(16)), ("pop", b(17)), ("pop2", b(18)),
          ("shutter", b(20) - 0.04), ("shutter", b(20) + 0.14), ("shutter", b(20) + 0.34), ("shutter", b(20) + 0.56),
          ("whoosh", b(20) + 1.5), ("pop", b(24)), ("pop2", b(25)), ("pop", b(26)),
          ("wind", b(28)), ("pop2", b(30)), ("pop", b(32)),
          ("whoosh", b(36)), ("pop2", b(36) + 0.83), ("coins", b(40) + 0.24), ("pop2", b(40) + 0.8),
          ("sub", b(44)), ("pop", b(44) + 0.5), ("pop2", b(48) + 0.6), ("sub", b(49)), ("whoosh", b(52)), ("pop2", b(52) + 0.9),
          ("wind", b(56))]
    ev += [("pop2", b(58))] + [("pop" if i % 2 == 0 else "pop2", b(59 + i)) for i in range(len(TX["voices"]))]
    ev += [("whoosh", b(68)), ("impact", b(76))]
    out = []
    for k, (name, t, *rest) in enumerate(ev):
        f, hit, vol = X[name]
        if len(rest) > 1:
            vol = rest[1]
        if name == "sub" and not rest:                      # the low hit rings for 6 s in its file: two are enough
            rest = [(2.0, 1.5)]
        start = round(t + 1 / FPS - hit, 3)
        media = 0.0
        if start < 0:
            media, start = -start, 0.0
        extra = f' data-duration="{rest[0][0]:g}" data-fade-out="{rest[0][1]:g}"' if rest else ""
        out.append(f'      <audio id="sfx{k}" class="clip" src="assets/audio/{f}.mp3" data-start="{start:g}" data-media-start="{media:g}" '
                   f'data-track-index="{40 + k}" data-volume="{vol}"{extra}></audio>')
    out.append(f'      <audio id="music" class="clip" src="assets/audio/{MUSIC}.mp3" data-start="0" data-duration="{TOTAL:g}" '
               f'data-media-start="{MUSIC_AT:g}" data-track-index="39" data-volume="0.72" data-fade-in="0.3" data-fade-out="1.6"></audio>')
    return "\n".join(out)


# ================================ the project ================================
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


def index(lang="hu"):
    hosts = "\n".join(f'''      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{a:g}" data-duration="{round(z - a, 4):g}" data-track-index="{k}" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index: {k}"></div>'''
                      for k, (n, a, z) in enumerate(SC))
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
    global TX
    only = sys.argv[1:]                                     # e.g. python3 build.py wide-en
    for lang, folder in OUTS:
        if only and folder not in only:
            continue
        TX = TEXT[lang]
        out = os.path.join(HERE, folder)
        comp = os.path.join(out, "compositions")
        os.makedirs(comp, exist_ok=True)
        for old in os.listdir(comp):
            if old.endswith(".html") and old[:-5] not in [n for n, a, z in SC]:
                os.remove(os.path.join(comp, old))
        tmp = os.path.join(HERE, ".logo-" + folder)
        logo, info = logo_scene(tmp)
        builders = {"open": lambda s, e: scene_open(s, e, info), "flyx": scene_flyx, "enzo": scene_enzo, "prod": scene_prod,
                    "how": scene_how, "r1": scene_r1, "r2": scene_r2, "r3": scene_r3, "r4": scene_r4, "m300": scene_m300,
                    "voices": scene_voices, "close": lambda s, e: scene_close(s, e, info)}
        for n, s, e in SC:
            if n == "logo":
                src = logo
            else:
                html, js, css = builders[n](s, e)
                src = composition(n, s, html, js, css)
            open(os.path.join(comp, f"{n}.html"), "w").write(src)
        open(os.path.join(out, "index.html"), "w").write(index(lang))
        cli = "npx --yes hyperframes@0.9.40"
        files = {"hyperframes.json": json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                                                 "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                                                 "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                                                 "media": {"autoProxy": True}}, indent=2) + "\n",
                 "meta.json": json.dumps({"id": f"socialstream-sizzle-{folder}", "name": f"SocialStream sizzle ({folder})", "createdAt": "2026-11-15T00:00:00.000Z"}, indent=2) + "\n",
                 "package.json": json.dumps({"name": f"socialstream-sizzle-{folder}", "private": True, "type": "module",
                                             "scripts": {"dev": f"{cli} preview", "check": f"{cli} check", "render": f"{cli} render"}}, indent=2) + "\n",
                 ".gitignore": "renders/\n.hyperframes/\n.thumbnails/\nsnapshots/\nnode_modules/\n"}
        for f, t in files.items():
            open(os.path.join(out, f), "w").write(t)
        link = os.path.join(out, "assets")
        if not os.path.islink(link):
            os.symlink("../assets", link)
        subprocess.run(["rm", "-rf", tmp], check=True)
        print(folder, lang, TOTAL, "s; drop", DROP)


if __name__ == "__main__":
    main()
