#!/usr/bin/env python3
"""SocialStream logo animation (direction G2): the horizontal lockup, 1920 x 1080, as a HyperFrames project.

The logo builds itself the way it was designed: a phone appears, the next reel (the S) swipes up into it, it
leans in at 15 degrees, a 15-degree cut takes its foot off, then it settles into the lockup while the name
streams out from behind it, and the A's cut opens like the phone's. The geometry is the kit's own
(kitmark.py, build_kit.py, caps.py), so the last frame is the dark horizontal master
(kit/source/socialstream-logo-horizontal-dark.svg, the reversed drawing) at WIDTH_FRAC of the frame width.

Writes <out>/index.html (the video: length, colour variables, the scene host) and
<out>/compositions/logo.html (the scene). With --reference <file.html> it also writes a still page that
places the kit master exactly where the last frame puts the logo, to diff the two.
Usage: python3 make_motion.py <out-dir> [--reference ref.html]
"""
import json, math, os, sys
from logolib import *
from caps import letters, inter, sliced_A
from refine import recut_terminals
from kitmark import g2_symbol
from build_kit import SYMBOLS, CAP, COLOURS, word

W, H = 1920, 1080
WIDTH_FRAC = 0.60          # final lockup width / frame width
HERO = 3.0                 # the phone's size during its own beats, relative to its lockup size
TOTAL = 4.6                # seconds; the last 2 s are a still hold
KIND = "reversed"          # the drawing made for dark grounds
LEAN = 15                  # degrees

# beat clock (seconds): start, duration
T = dict(
    arrive=(0.00, 0.50),   # phone fades/scales in, upright and empty
    blur_in=(0.00, 0.45),
    swipe=(0.25, 0.50),    # the S slides up into the screen from below
    lean=(0.75, 0.55),     # 0 -> 15 degrees, small overshoot
    cut=(1.15, 0.22),      # the phone's cut opens from a hairline
    settle=(1.45, 0.65),   # hero size -> lockup size and place
    wipe=(1.90, 0.65),     # the name is revealed from behind the phone, left to right
    social=(1.90, 0.70),   # SOCIAL slides out a little
    stream=(2.02, 0.70),   # STREAM follows
    blur_name=(1.90, 0.50),
    acut=(None, 0.20),     # the A's cut: once the wipe has passed the A and the name is sharp (computed)
)
EASE = dict(arrive="expo.out", blur_in="power2.out", swipe="expo.out", lean="back.out(1.4)", cut="expo.out",
            settle="power3.inOut", wipe="power3.out", social="expo.out", stream="expo.out",
            blur_name="power2.out", acut="expo.out")
SLIDE_PX = 40              # how far each word slides while it is revealed
EPS = 0.6                  # overlap of the gap fills into the cut pieces (symbol units), against seams


# ---------- geometry ----------
def g2_parts(weight=800, fill=0.80, ratio=16 / 9, r=0.18, gap=0.075, margin=0.08, sy=0.0, ang_local=30, recut=True):
    """kitmark.g2_symbol with the tilt left out and every part kept: the uncut tile, the two cut pieces,
    the S, and the cut band in the frame rotated by ang_local (where the cut is horizontal)."""
    S = letters(f"m{weight}")[0][0]
    if recut:
        S = recut_terminals(S, 75)
    x0, y0, x1, y1 = bbox(S)
    S = scale(S, 150.0 / (y1 - y0))
    x0, y0, x1, y1 = bbox(S)
    S = translate(S, 128 - (x0 + x1) / 2, 128 - (y0 + y1) / 2)
    tw = (x1 - x0) / fill
    th = tw * ratio
    tile = rrect(128 - tw / 2, 128 - th / 2, tw, th, tw * r, smooth=1.2)
    R = lambda p, a: rotate(p, a, 128, 128)
    t_rot, s_rot = R(tile, ang_local), R(S, ang_local)
    y_top = bbox(s_rot)[3] + margin * tw
    y_bot = y_top + gap * tw
    main, _ = cut_y(t_rot[0], y_top, "above")
    foot, _ = cut_y(t_rot[0], y_bot, "below")
    S = translate(S, 0, sy * th)
    return dict(tile=tile, main=R([main], -ang_local), foot=R([foot], -ang_local), S=S,
                y_top=y_top, y_bot=y_bot, tw=tw, th=th, r=tw * r, ang=ang_local)


def maxdiff(a, b):
    """Largest coordinate difference between two paths of the same structure."""
    m = 0.0
    for sa, sb in zip(a, b):
        for ga, gb in zip(sa, sb):
            for pa, pb in zip(ga[1:], gb[1:]):
                m = max(m, abs(pa[0] - pb[0]), abs(pa[1] - pb[1]))
    return m


def a_lines(A, ang=15):
    """The lines caps.sliced_A cuts the A with (same defaults as the kit wordmark)."""
    k = math.tan(math.radians(ang))
    pts = [s[1] for s in A[0] if s[0] in ("M", "L")]
    p0, p1, p2, p3, p4, p5, p6, p7 = pts[:8]
    xb0, yb0, xb1, yb1 = bbox([A[0]])
    stem = abs(p3[0] - p4[0])
    bar_t, gap, centre_y = stem * 0.62, stem * 0.26, -(-yb0) * 0.30
    c_mid = centre_y + k * (xb0 + xb1) / 2
    L1 = c_mid + bar_t / 2          # lower edge of the bar
    L0 = L1 + gap                   # upper edge of the foot
    return dict(OR=(p2, p3), IR=(p4, p5), L1=L1, L0=L0, k=k)


def rot_pt(p, deg, c=(0, 0)):
    a = math.radians(deg); co, si = math.cos(a), math.sin(a)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + co * x - si * y, c[1] + si * x + co * y)


def pts_d(pts):
    return "M" + "L".join(f"{fmt(x)} {fmt(y)}" for x, y in pts) + "Z"


def main():
    args = sys.argv[1:]
    out = args[0] if args else "../kit/motion/horizontal"
    ref = args[args.index("--reference") + 1] if "--reference" in args else None

    # --- the phone, untilted, and proof that tilting it gives the kit's symbol exactly
    P = g2_parts(**SYMBOLS[KIND])
    kit_sym, _ = g2_symbol(**SYMBOLS[KIND])
    mine = rotate([P["main"][0], P["foot"][0]] + P["S"], LEAN, 128, 128)
    assert maxdiff(mine, kit_sym) < 1e-6, "untilted parts do not match the kit symbol"

    # --- placement of the symbol in the lockup (as build_kit.horizontal does it)
    w = word()
    sx0, sy0, sx1, sy1 = bbox(kit_sym)
    k = CAP * 1.75 / (sy1 - sy0)
    wx0 = bbox_many([p for p, c in w])[0]
    tx = wx0 - CAP * 0.5 - k * sx1
    ty = -CAP / 2 - k * (sy0 + sy1) / 2
    M_sym = (k, 0, 0, k, tx, ty)

    # --- the lockup in the frame
    lock = [tf(kit_sym, M_sym)] + [p for p, c in w]
    lx0, ly0, lx1, ly1 = bbox_many(lock)
    sL = W * WIDTH_FRAC / (lx1 - lx0)
    txL = W / 2 - sL * (lx0 + lx1) / 2
    tyL = H / 2 - sL * (ly0 + ly1) / 2
    M_lock = (sL, 0, 0, sL, txL, tyL)
    px = lambda x, y: (sL * x + txL, sL * y + tyL)
    sym_px = lambda x, y: px(k * x + tx, k * y + ty)
    cx_f, cy_f = sym_px(128, 128)                  # phone centre in the last frame
    u = sL * k                                     # px per symbol unit at lockup size
    HX = (W / 2 - cx_f) / u                        # hero offset, symbol units (parent space of #logo-hero)
    HY = (H / 2 - cy_f) / u

    # --- the cut band fills: the uncut tile between the cut lines, split at the middle (band frame, where the
    # cut is horizontal); each half collapses onto its own edge so the cut opens from a hairline
    yt, yb = P["y_top"], P["y_bot"]
    yc = (yt + yb) / 2
    span = 240
    t_rot = rotate(P["tile"], P["ang"], 128, 128)[0]
    upper, _ = cut_y(t_rot, yc + EPS, "above")
    gap_up, _ = cut_y(upper, yt - EPS, "below")
    lower, _ = cut_y(t_rot, yc - EPS, "below")
    gap_dn, _ = cut_y(lower, yb + EPS, "above")
    anc_up, anc_dn = yt - EPS, yb + EPS          # the edge each half collapses onto
    h_up, h_dn = (yc + EPS) - anc_up, anc_dn - (yc - EPS)
    # the halves stay put and exact; a clip rect over each shrinks onto its edge, so nothing ever crosses
    # the phone's outline while the cut opens
    tile_clip = P["tile"]                         # keeps the S inside the screen while it swipes in

    # --- the S starts below the screen
    s_top = bbox(P["S"])[1]
    swipe_d = (128 + P["th"] / 2) - s_top + 4

    # --- the A's cut fills (the right leg between the bar and the foot), in the A's band frame
    # x offset of the A in the wordmark: the kit A against the raw glyph, sliced the same way
    A_raw = letters("m800")[4][0]
    ax = bbox(w[4][0])[0] - bbox(sliced_A(A_raw))[0]
    al = a_lines(A_raw)
    I = lambda line, c: inter(line[0], line[1], c, al["k"])
    eA = 0.012 * CAP
    Lm = (al["L1"] + al["L0"]) / 2
    up_q = [I(al["OR"], al["L1"] - eA), I(al["OR"], Lm + eA), I(al["IR"], Lm + eA), I(al["IR"], al["L1"] - eA)]
    dn_q = [I(al["OR"], Lm - eA), I(al["OR"], al["L0"] + eA), I(al["IR"], al["L0"] + eA), I(al["IR"], Lm - eA)]
    up_q = [(x + ax, y) for x, y in up_q]
    dn_q = [(x + ax, y) for x, y in dn_q]
    Q = ((up_q[0][0] + up_q[3][0]) / 2, (up_q[0][1] + up_q[3][1]) / 2)   # band-frame origin on the bar edge
    to_band = lambda p: rot_pt((p[0] - Q[0], p[1] - Q[1]), 15)           # inverse of translate(Q) rotate(-15)
    up_b, dn_b = [to_band(p) for p in up_q], [to_band(p) for p in dn_q]

    # --- the reveal: a slanted (15 degree) wipe whose left edge is the phone's right side
    tan15 = math.tan(math.radians(15))
    side_local = (128 + (P["tw"] / 2) / math.cos(math.radians(LEAN)), 128)   # right side at the centre height
    side_x = k * side_local[0] + tx                    # lockup units
    yc_l = k * 128 + ty                                # = -CAP/2
    wipe_y0, wipe_h = -CAP * 1.35, CAP * 1.7
    wipe_x = side_x + tan15 * yc_l                     # rect x so the skewed left edge passes (side_x, yc_l)
    word_x1 = bbox_many([p for p, c in w])[2]
    wipe_w = (word_x1 - side_x) + tan15 * (CAP * 1.35) + CAP * 0.3 + SLIDE_PX / sL
    # check: the left edge clears every letter in the last frame
    for p, c in w:
        for (x, y) in [seg[-1] for sub in p for seg in sub if seg[0] != "Z"]:
            assert x > wipe_x - tan15 * y + 1, "wipe edge clips a letter in the last frame"
    # when does the wipe pass the A? (power3.out: 1-(1-t)^3)
    a_right = max(x - (wipe_x - tan15 * y) for x, y in up_q + dn_q)
    frac = min(1.0, a_right / wipe_w)
    t_frac = 1 - (1 - frac) ** (1 / 3)
    acut_start = T["wipe"][0] + t_frac * T["wipe"][1] + 0.12
    # ...but not before the name is sharp: the A's cut is the last accent, it should be seen
    acut_start = round(max(acut_start, T["blur_name"][0] + T["blur_name"][1] - 0.08), 3)
    T["acut"] = (acut_start, T["acut"][1])

    # ---------- markup ----------
    # Every animated transform is an explicit SVG transform string that GSAP interpolates number by number
    # (attr tweens), so the pivots are exact and the last frame is the kit geometry, not GSAP's origin maths.
    mat = lambda m: "matrix(" + " ".join(f"{v:.6f}".rstrip("0").rstrip(".") for v in m) + ")"
    num = lambda v: f"{v:.4f}".rstrip("0").rstrip(".") if abs(v) > 1e-9 else "0"
    about = lambda sx, sy, ox, oy, dx=0.0, dy=0.0: (      # scale (sx, sy) about (ox, oy), then move by (dx, dy)
        f"translate({num(ox + dx)} {num(oy + dy)}) scale({num(sx)} {num(sy)}) translate({num(-ox)} {num(-oy)})")
    tr = dict(
        hero=(about(HERO, HERO, 128, 128, HX, HY), about(1, 1, 128, 128)),
        arrive=(about(0.9, 0.9, 128, 128), about(1, 1, 128, 128)),
        lean=(f"rotate(0 128 128)", f"rotate({LEAN} 128 128)"),
        s=(f"translate(0 {num(swipe_d)})", "translate(0 0)"),
    )
    a_top, a_mid_up = min(p[1] for p in up_b), max(p[1] for p in up_b)
    a_mid_dn, a_bot = min(p[1] for p in dn_b), max(p[1] for p in dn_b)
    a_x0 = min(p[0] for p in up_b + dn_b) - 20
    a_w = max(p[0] for p in up_b + dn_b) + 20 - a_x0
    slide = SLIDE_PX / sL
    tr.update(
        social=(f"translate({num(-slide)} 0)", "translate(0 0)"),
        stream=(f"translate({num(-slide)} 0)", "translate(0 0)"),
    )

    phone = (
        f'<path class="ink" d="{to_d(P["main"])}"/>'
        f'<path class="ink" d="{to_d(P["foot"])}"/>'
        f'<g transform="rotate({-P["ang"]} 128 128)">'
        f'<path class="ink" clip-path="url(#logo-cut-clip-up)" d="{to_d([gap_up])}"/>'
        f'<path class="ink" clip-path="url(#logo-cut-clip-dn)" d="{to_d([gap_dn])}"/>'
        f'</g>'
        f'<g clip-path="url(#logo-tile-clip)">'
        f'<g id="logo-s" transform="{tr["s"][0]}"><path class="hole" d="{to_d(P["S"])}"/></g>'
        f'</g>'
    )
    phone_svg = (
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        f'<defs><clipPath id="logo-tile-clip"><path d="{to_d(tile_clip)}"/></clipPath>'
        f'<clipPath id="logo-cut-clip-up"><rect id="logo-cut-up" x="{num(128 - span)}" y="{num(anc_up)}" '
        f'width="{num(2 * span)}" height="{num(h_up)}"/></clipPath>'
        f'<clipPath id="logo-cut-clip-dn"><rect id="logo-cut-dn" x="{num(128 - span)}" y="{num(yc - EPS)}" '
        f'width="{num(2 * span)}" height="{num(h_dn)}"/></clipPath></defs>'
        f'<g transform="{mat(M_lock)}"><g transform="{mat(M_sym)}">'
        f'<g id="logo-hero" transform="{tr["hero"][0]}"><g id="logo-arrive" transform="{tr["arrive"][0]}" opacity="0">'
        f'<g id="logo-lean" transform="{tr["lean"][0]}">{phone}</g></g></g>'
        f'</g></g></svg>'
    )
    social = "".join(f'<path class="ink" d="{to_d(p)}"/>' for p, c in w[:6])
    agap = (f'<g transform="translate({num(Q[0])} {num(Q[1])}) rotate(-15)">'
            f'<clipPath id="logo-acut-clip-up"><rect id="logo-acut-up" x="{num(a_x0)}" y="{num(a_top)}" '
            f'width="{num(a_w)}" height="{num(a_mid_up - a_top)}"/></clipPath>'
            f'<clipPath id="logo-acut-clip-dn"><rect id="logo-acut-dn" x="{num(a_x0)}" y="{num(a_mid_dn)}" '
            f'width="{num(a_w)}" height="{num(a_bot - a_mid_dn)}"/></clipPath>'
            f'<path class="ink" clip-path="url(#logo-acut-clip-up)" d="{pts_d(up_b)}"/>'
            f'<path class="ink" clip-path="url(#logo-acut-clip-dn)" d="{pts_d(dn_b)}"/></g>')
    stream = "".join(f'<path class="acc" d="{to_d(p)}"/>' for p, c in w[6:])
    word_svg = (
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        f'<defs><clipPath id="logo-wipe-clip"><rect id="logo-wipe" transform="skewX(-15)" x="{num(wipe_x)}" '
        f'y="{num(wipe_y0)}" width="0" height="{num(wipe_h)}"/></clipPath></defs>'
        f'<g transform="{mat(M_lock)}"><g clip-path="url(#logo-wipe-clip)">'
        f'<g id="logo-social" transform="{tr["social"][0]}">{social}{agap}</g>'
        f'<g id="logo-stream" transform="{tr["stream"][0]}">{stream}</g>'
        f'</g></g></svg>'
    )

    def tw_(sel, frm, to, key):
        t0, d = T[key]
        return f'      tl.fromTo("{sel}", {{ {frm} }}, {{ {to}, duration: {d}, ease: "{EASE[key]}" }}, {t0});'

    def tw_tr(sel, name, key, extra_from="", extra_to=""):
        f0, f1 = tr[name]
        return tw_(sel, f'{extra_from}attr: {{ transform: "{f0}" }}', f'{extra_to}attr: {{ transform: "{f1}" }}', key)

    js = "\n".join([
        '      const tl = gsap.timeline({ paused: true });',
        '      // 1. the phone arrives, upright and empty',
        tw_tr("#logo-arrive", "arrive", "arrive", "opacity: 0, ", "opacity: 1, "),
        tw_("#logo-phone-soft", 'filter: "blur(14px)"', 'filter: "blur(0px)"', "blur_in"),
        '      // 2. the next reel swipes up into the screen: the S',
        tw_tr("#logo-s", "s", "swipe"),
        '      // 3. it leans in, 15 degrees',
        tw_tr("#logo-lean", "lean", "lean"),
        '      // 4. the 15-degree cut opens from a hairline',
        tw_("#logo-cut-up", f"attr: {{ height: {num(h_up)} }}", "attr: { height: 0 }", "cut"),
        tw_("#logo-cut-dn", f"attr: {{ y: {num(yc - EPS)}, height: {num(h_dn)} }}",
            f"attr: {{ y: {num(anc_dn)}, height: 0 }}", "cut"),
        '      // 5. it settles into the lockup',
        tw_tr("#logo-hero", "hero", "settle"),
        '      // 6. the name streams out from behind it: SOCIAL, then STREAM',
        tw_("#logo-wipe", "attr: { width: 0 }", f"attr: {{ width: {num(wipe_w)} }}", "wipe"),
        tw_tr("#logo-social", "social", "social"),
        tw_tr("#logo-stream", "stream", "stream"),
        tw_("#logo-word-soft", 'filter: "blur(8px)"', 'filter: "blur(0px)"', "blur_name"),
        "      // 7. the A's cut opens like the phone's",
        tw_("#logo-acut-up", f"attr: {{ height: {num(a_mid_up - a_top)} }}", "attr: { height: 0 }", "acut"),
        tw_("#logo-acut-dn", f"attr: {{ y: {num(a_mid_dn)}, height: {num(a_bot - a_mid_dn)} }}",
            f"attr: {{ y: {num(a_bot)}, height: 0 }}", "acut"),
        '      window.__timelines["logo"] = tl;',
    ])

    scene = f"""<template>
  <style>
    #root {{
      position: absolute;
      inset: 0;
      background: var(--night, {COLOURS["night"]});
    }}
    #logo-name,
    #logo-phone,
    #logo-word-soft,
    #logo-phone-soft {{
      position: absolute;
      inset: 0;
    }}
    #logo-name {{
      z-index: 1;
    }}
    #logo-phone {{
      z-index: 2;
    }}
    #root svg {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      overflow: visible;
    }}
    #root .ink {{
      fill: var(--cream, {COLOURS["cream"]});
    }}
    #root .acc {{
      fill: var(--stream, {COLOURS["stream"]});
    }}
    #root .hole {{
      fill: var(--night, {COLOURS["night"]});
    }}
  </style>
  <div id="root" data-composition-id="logo" data-width="{W}" data-height="{H}">
    <!-- SOCIALSTREAM: revealed from behind the phone (layer under the phone) -->
    <div id="logo-name" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="1">
      <div id="logo-word-soft">
        {word_svg}
      </div>
    </div>
    <!-- the phone: arrives, takes its S, leans in, is cut, settles -->
    <div id="logo-phone" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2">
      <div id="logo-phone-soft">
        {phone_svg}
      </div>
    </div>
  </div>
  <script>
{js}
  </script>
</template>
"""
    variables = [
        {"id": "night", "type": "color", "label": "Ground (Night)", "default": COLOURS["night"]},
        {"id": "cream", "type": "color", "label": "Phone and SOCIAL (Cream)", "default": COLOURS["cream"]},
        {"id": "stream", "type": "color", "label": "STREAM (Stream Blue)", "default": COLOURS["stream"]},
    ]
    index = f"""<!doctype html>
<html lang="en" data-composition-variables='{json.dumps(variables)}'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>SocialStream logo animation</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        width: {W}px;
        height: {H}px;
        overflow: hidden;
        background: var(--night, {COLOURS["night"]});
      }}
      #main {{
        width: 100%;
        height: 100%;
      }}
    </style>
  </head>
  <body>
    <div
      id="main"
      data-composition-id="main"
      data-start="0"
      data-duration="{TOTAL}"
      data-width="{W}"
      data-height="{H}"
    >
      <div
        id="logo"
        data-composition-id="logo"
        data-composition-src="compositions/logo.html"
        data-start="0"
        data-duration="{TOTAL}"
        data-track-index="1"
        data-track-kind="graphics"
        data-width="{W}"
        data-height="{H}"
      ></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    os.makedirs(os.path.join(out, "compositions"), exist_ok=True)
    open(os.path.join(out, "index.html"), "w").write(index)
    open(os.path.join(out, "compositions", "logo.html"), "w").write(scene)
    # project files (what `hyperframes init` would write, minus its agent notes)
    cli = "npx --yes hyperframes@0.9.40"
    files = {
        "hyperframes.json": json.dumps({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True}}, indent=2) + "\n",
        "meta.json": json.dumps({"id": "socialstream-logo-horizontal",
                                 "name": "SocialStream logo animation (horizontal)",
                                 "createdAt": "2026-11-13T00:00:00.000Z"}, indent=2) + "\n",
        "package.json": json.dumps({"name": "socialstream-logo-horizontal", "private": True, "type": "module",
                                    "scripts": {"dev": f"{cli} preview", "check": f"{cli} check",
                                                "render": f"{cli} render"}}, indent=2) + "\n",
        ".gitignore": "renders/\n.hyperframes/\n.thumbnails/\nsnapshots/\nnode_modules/\n",
    }
    for name, text in files.items():
        open(os.path.join(out, name), "w").write(text)

    info = dict(scale_px_per_unit=sL, lockup_px=[px(lx0, ly0), px(lx1, ly1)], phone_centre_px=(cx_f, cy_f),
                hero_offset_units=(HX, HY), swipe_units=swipe_d, a_cut_start=acut_start, cap_px=CAP * sL)
    print(json.dumps(info, indent=1, default=lambda v: round(v, 3)))

    if ref:
        # the kit master, placed where the last frame puts the logo
        src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kit", "source",
                                           "socialstream-logo-horizontal-dark.svg"))
        txt = open(src).read()
        vb = [float(v) for v in txt.split('viewBox="')[1].split('"')[0].split()]
        Wk, Hk = vb[2], vb[3]
        pad = 0.14
        s_k = Hk * (1 - 2 * pad) / (ly1 - ly0)           # kit units per lockup unit (build_kit.write)
        bx0 = (Wk - (lx1 - lx0) * s_k) / 2
        f = sL / s_k                                      # px per kit unit
        left, top = px(lx0, ly0)[0] - bx0 * f, px(lx0, ly0)[1] - Hk * pad * f
        # inline SVG (an <img> would be snapped to whole pixels): the kit file's own paths, in its own units
        import re
        body = re.sub(r"<title[^>]*>.*?</title>", "", txt.split(">", 1)[1].rsplit("</svg>", 1)[0], flags=re.S)
        page = (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;width:{W}px;height:{H}px;'
                f'overflow:hidden;background:{COLOURS["night"]}}}svg{{position:absolute;inset:0}}</style></head><body>'
                f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}"><g transform="matrix({f:.8f} 0 0 {f:.8f} '
                f'{left:.6f} {top:.6f})">{body}</g></svg></body></html>')
        open(ref, "w").write(page)
        print("wrote", ref)


if __name__ == "__main__":
    main()
