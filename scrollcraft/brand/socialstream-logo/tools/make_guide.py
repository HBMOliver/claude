#!/usr/bin/env python3
"""One-page (A4) logo usage guide for the SocialStream kit.
Usage: python3 make_guide.py <kit-folder>   -> <kit>/guide/socialstream-logo-guide.html
Render with: python3 render_page.py <html> --png <png> --size 794x1123 --scale 2 --pdf <pdf>
"""
import os, re, sys

KIT = sys.argv[1]
SRC = os.path.join(KIT, "source")
COL = [("Night", "#05070F", "5 7 15", "67 53 0 94", "Dark grounds; the logo on light"),
       ("Cream", "#F1EEE6", "241 238 230", "0 1 5 5", "The logo on dark; light grounds"),
       ("Stream Blue", "#7FA1C4", "127 161 196", "35 18 0 23", "STREAM on dark grounds"),
       ("Deep Stream", "#40658C", "64 101 140", "54 28 0 45", "STREAM on light grounds")]


def art(name, style="", transform=None, recolour=None, par="xMidYMid meet"):
    s = open(os.path.join(SRC, name)).read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    body = s.split("</title>", 1)[1].rsplit("</svg>", 1)[0]
    for a, b in (recolour or {}).items():
        body = body.replace(a, b)
    if transform:
        body = f'<g transform="{transform}">{body}</g>'
    return f'<svg viewBox="{vb}" style="{style}" preserveAspectRatio="{par}" aria-hidden="true">{body}</svg>'


def clear_space():
    hs = open(os.path.join(SRC, "socialstream-logo-horizontal-light.svg")).read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', hs).group(1).split()]
    body = hs.split("</title>", 1)[1].rsplit("</svg>", 1)[0]
    pad = vb[3] * 0.14            # the master's own padding around the artwork
    cap = vb[3] * 0.72 / 1.75     # cap height of SOCIAL (the symbol is 1.75 x the cap height)
    x0, y0, x1, y1 = pad - cap, pad - cap, vb[2] - pad + cap, vb[3] - pad + cap
    m = cap * 0.35
    lab = lambda x, y: f'<text x="{x}" y="{y}" font-size="{cap * 0.55:.0f}" font-weight="600" fill="#40658C" text-anchor="middle" font-family="Montserrat,Helvetica">x</text>'
    return (f'<svg viewBox="{x0 - m} {y0 - m} {x1 - x0 + 2 * m} {y1 - y0 + 2 * m}" style="width:100%;height:auto">'
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#e9e4d8" stroke="#9a937f" stroke-width="3" stroke-dasharray="10 8"/>'
            f'<rect x="{pad}" y="{pad}" width="{vb[2] - 2 * pad}" height="{vb[3] - 2 * pad}" fill="#F1EEE6"/>{body}'
            + lab((x0 + pad) / 2, pad + cap * 0.2) + lab(vb[2] / 2, (y0 + pad) / 2 + cap * 0.2) + "</svg>")


def main():
    out = os.path.join(KIT, "guide")
    os.makedirs(out, exist_ok=True)
    title_mark = art("socialstream-wordmark-light.svg", "height:30px;width:auto")
    hl = art("socialstream-logo-horizontal-light.svg", "width:100%;height:auto")
    hd = art("socialstream-logo-horizontal-dark.svg", "width:100%;height:auto")
    st = art("socialstream-logo-stacked-light.svg", "height:92px;width:auto")
    sd = art("socialstream-logo-stacked-dark.svg", "height:92px;width:auto")
    sy = art("socialstream-symbol-light.svg", "height:84px;width:auto")
    syd = art("socialstream-symbol-dark.svg", "height:84px;width:auto")
    dont = [
        (art("socialstream-logo-horizontal-light.svg", "width:100%;height:34px", par="none"), "Don't stretch or squash"),
        (art("socialstream-symbol-light.svg", "height:54px;width:auto", transform="rotate(-15 128 128)"), "Don't straighten the phone"),
        (art("socialstream-symbol-light.svg", "height:54px;width:auto", transform="translate(256 0) scale(-1 1)"), "Don't mirror it"),
        (art("socialstream-logo-horizontal-light.svg", "width:100%;height:auto", recolour={"#40658C": "#E2553B"}), "Don't recolour it"),
        (art("socialstream-logo-horizontal-light.svg", "width:100%;height:auto"), "Don't put the light version on dark", "#05070F"),
        ('<div class="typed">SOCIAL<span>STREAM</span></div>', "Don't retype it in a font"),
    ]
    dont_html = "".join(
        f'<div class="dont"><div class="dbox" style="background:{d[2] if len(d) > 2 else "#fff"}">{d[0]}<span class="x">✕</span></div><p>{d[1]}</p></div>'
        for d in dont)
    swatches = "".join(
        f'<div class="sw"><div class="chip" style="background:{h};{"border:1px solid #d9d3c4;" if n == "Cream" else ""}"></div>'
        f'<b>{n}</b> <code>{h}</code><span>RGB {r} · CMYK {c}*</span><em>{u}</em></div>' for n, h, r, c, u in COL)
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SocialStream logo guide</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@400;600&display=swap">
<style>
@page{{size:A4;margin:0}}
*{{box-sizing:border-box}}
body{{margin:0;background:#fff;color:#05070F;font:400 11px/1.42 'Plus Jakarta Sans',Helvetica,sans-serif}}
.page{{width:210mm;height:297mm;padding:10mm 13mm 8mm;display:flex;flex-direction:column;gap:3.8mm;overflow:hidden}}
header{{display:flex;align-items:center;gap:4mm}} header h1{{font:600 15px Montserrat,Helvetica;letter-spacing:2px;text-transform:uppercase;color:#40658C;margin:0}}
.lead{{margin:0;font-size:12px;max-width:170mm}}
h2{{font:600 9.5px Montserrat,Helvetica;letter-spacing:1.8px;text-transform:uppercase;color:#40658C;margin:0 0 2mm}}
.row{{display:grid;gap:4mm}} .row>*{{min-width:0}}
.c2{{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}} .c4{{grid-template-columns:repeat(4,minmax(0,1fr))}} .c6{{grid-template-columns:repeat(6,minmax(0,1fr))}}
.tile{{border-radius:2.5mm;padding:4.5mm 6mm;display:flex;align-items:center;justify-content:center;min-width:0}} .tile svg{{max-width:100%}}
.cream{{background:#F1EEE6}} .night{{background:#05070F}}
.note{{font-size:10px;color:#57534a;margin:1.6mm 0 0}}
table{{border-collapse:collapse;width:100%;font-size:10.3px}} td,th{{text-align:left;padding:1.1mm 1.6mm;border-bottom:1px solid #e7e2d6;vertical-align:top}} th{{font-weight:600}}
.sw{{display:flex;flex-direction:column;font-size:10px;line-height:1.35}} .chip{{height:8mm;border-radius:1.8mm;margin-bottom:1.4mm}}
.sw code{{font:600 10.5px Montserrat}} .sw em{{color:#57534a;font-style:normal}}
.type .a{{font:800 17px/1.15 Montserrat;letter-spacing:.2px}} .type .b{{font:300 15px/1.2 Montserrat}} .type .c{{font:400 12px 'Plus Jakarta Sans'}}
.dont{{font-size:9.5px;line-height:1.3}} .dbox{{position:relative;height:17mm;border:1px solid #e7e2d6;border-radius:1.8mm;display:flex;align-items:center;justify-content:center;padding:2.4mm;overflow:hidden}}
.dbox svg{{max-height:12mm}} .x{{position:absolute;top:.6mm;right:1.6mm;color:#E2553B;font-size:12px;font-weight:700}} .dont p{{margin:1mm 0 0}}
.typed{{font:800 9.5px Montserrat,Helvetica;white-space:nowrap}} .typed span{{font-weight:300}}
.files td:first-child{{font:600 10px Montserrat;white-space:nowrap}}
</style></head><body><div class="page">
<header>{title_mark}<h1>Logo guide</h1></header>
<p class="lead">A bold S on a 9:16 phone that leans in at 15°; its foot is sliced off at the same 15° as the A in SOCIAL. Every cut and lean in the logo is 15°. Always use the files; never rebuild the logo.</p>

<section><h2>Versions</h2>
<div class="row c2"><div class="tile cream">{hl}</div><div class="tile night">{hd}</div></div>
<div class="row c4" style="margin-top:3.4mm"><div class="tile cream">{st}</div><div class="tile night">{sd}</div><div class="tile cream">{sy}</div><div class="tile night">{syd}</div></div>
<p class="note">Horizontal is the default; stacked for square formats and shirts; the phone alone where the name is already there (profile pictures, favicon, the corner of a reel). Light versions (Night + Deep Stream) go on cream or white, dark versions (Cream + Stream Blue) on night blue or calm, dark photos.</p></section>

<section class="row c2"><div><h2>Clear space</h2>{clear_space()}
<p class="note">Keep at least <b>x</b> clear on every side: x is the cap height of SOCIAL. For the phone alone, x is half the phone's width.</p></div>
<div><h2>Minimum size</h2><table><tr><th>Version</th><th>Screen</th><th>Print</th></tr>
<tr><td>Horizontal</td><td>140 px wide</td><td>35 mm wide</td></tr>
<tr><td>Stacked</td><td>80 px wide</td><td>20 mm wide</td></tr>
<tr><td>Phone</td><td>24 px; small cut below 32 px</td><td>6 mm, small cut</td></tr>
<tr><td>Favicon</td><td>16 px: web/favicon.*</td><td>–</td></tr></table></div></section>

<section><h2>Colour</h2><div class="row c4">{swatches}</div>
<p class="note">* CMYK values are plain conversions from RGB: have the printer proof them with their profile. Pantone matches are not set yet; choose them from a physical guide at the first print job.</p></section>

<section class="row c2"><div class="type"><h2>Typefaces</h2>
<div class="a">A SOCIAL MEDIA MEGHALT.</div><div class="b">Az érdeklődés vette át a helyét.</div>
<p class="note">Montserrat for headlines: ExtraBold caps for statements, Light for the second voice. <span class="c">Plus Jakarta Sans</span> for body text. Both are free (SIL Open Font License). The logo's letters are custom outlines based on Montserrat (the sliced A, S terminals cut at 75°, an M at exact 60°), so the logo can't be typed.</p></div>
<div><h2>Which file</h2><table class="files">
<tr><td>source/</td><td>SVG masters, light and dark: every lockup, the symbol, its small cut, the favicon drawing</td></tr>
<tr><td>digital/</td><td>transparent PNGs (512–2400 px); one-colour SVGs in black, white, cream and night</td></tr>
<tr><td>web/</td><td>favicons (ico, svg, 16–48 px), app icons, webmanifest, &lt;head&gt; snippet</td></tr>
<tr><td>social/</td><td>1080 px profile pictures (night, cream) and a stacked square</td></tr>
<tr><td>print/</td><td>vector PDFs (RGB): horizontal, stacked, symbol in light, dark, black, white</td></tr></table></div></section>

<section><h2>Please don't</h2><div class="row c6">{dont_html}</div>
<p class="note">No shadows, outlines, gradients or effects. Don't rearrange or resize the parts of a lockup. On busy photos use the phone alone or a calm area.</p></section>
</div></body></html>"""
    path = os.path.join(out, "socialstream-logo-guide.html")
    open(path, "w").write(html)
    print("wrote", path)


if __name__ == "__main__":
    main()
