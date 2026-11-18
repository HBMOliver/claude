#!/usr/bin/env python3
"""Writes gyartasi-csomag.md for a video from timeline.json + build/render_cfg.json (run build.py plan first)."""
import json, os, re, sys

def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"

def main(vd):
    tl = json.load(open(os.path.join(vd, "timeline.json"), encoding="utf-8"))
    cfg = json.load(open(os.path.join(vd, "build", "render_cfg.json"), encoding="utf-8"))
    caps = cfg["captions"]
    def caps_in(a, b):
        out = []
        for g in caps:
            if a - 0.05 <= g["start"] < b - 0.05:
                out.append(" ".join(f"**{w['t']}**" + ("🟧" if w["c"] == "amber" else "🟩" if w["c"] == "green" else "") if w["c"] else w["t"] for w in g["words"]))
        return " / ".join(out)
    sfx = cfg["cues"]
    def sfx_in(a, b):
        ks = []
        for c in sfx:
            if a <= c["t"] < b and c["kind"] not in ks: ks.append(c["kind"])
        return ", ".join(ks)
    L = []
    L.append(f"# Prof Enzo – {tl['title']}\n")
    L.append(f"**Kategória:** {tl.get('category','')} · **Formátum:** 9:16, 1080×1920 · **Becsült hossz:** {cfg['duration']:.0f} mp (a végleges hang időzítése szerint változhat)\n")
    L.append("## 1. Narráció (Prof Enzo hangján)\n")
    sents = re.split(r"(?<=[.!?…”])\s+", tl["script"])
    L += [f"> {s}  " for s in sents]
    L.append("\nAz utolsó mondat a stratégia egységes CTA-ja. Kiejtés: „profenzo.com” = *profenzo pont kom*.\n")
    L.append("## 2. Produkciós táblázat\n")
    L.append("Feliratjelölés: 🟧 borostyán = tényszerű/biológiai kulcsszó, 🟩 pasztellzöld = megoldás/CTA. Állandó elem: bal felső jelvény „Prof. Enzo AI • profenzo.com”. Prof Enzo alul középen, a záró CTA-ban balra húzódik.\n")
    L.append("| Időkód | Vizuális kép & B-roll | Képernyőfelirat | SFX |")
    L.append("|---|---|---|---|")
    for s in cfg["scenes"]:
        desc = s.get("desc", "")
        L.append(f"| {mmss(s['start'])}–{mmss(s['end'])} | {desc or s['type']} | {caps_in(s['start'], s['end']) or '–'} | {sfx_in(s['start'], s['end']) or '–'} |")
    L.append("\nZene: halk, meleg lo-fi / ambient alap, a beszéd alatt kb. –24 dB, a végén lecseng.\n")
    if tl.get("post"):
        L.append("## 3. TikTok-leírás és hashtagek\n")
        L.append(f"> {tl['post']['caption']}\n")
        L.append("**Hashtagek:** " + " ".join(tl["post"]["hashtags"]) + "\n")
    if tl.get("compliance"):
        L.append("## 4. Szakmai és compliance-ellenőrzés\n")
        L += [f"- {c}" for c in tl["compliance"]]
        L.append("- A stratégia 8A ellenőrzőlistáját a **kész** videón kell lefuttatni: szöveg, felirat, B-roll, leírás és tervezett kommentválaszok együtt.\n")
    if tl.get("sources"):
        L.append("## 5. Források (publikálás előtt ellenőrizendő)\n")
        L += [f"- {s}" for s in tl["sources"]]
        L.append("")
    L.append("## 6. Gyártási állapot\n")
    L.append("- ✅ Szöveg, idővonal, feliratok, grafikák, SFX, zene: a vázlat renderelve (`build/vazlat.mp4`).")
    L.append("- ⏳ Prof Enzo hangja és szájszinkronja: HeyGen API-kulcsra vagy kreditfeltöltésre vár. A vázlatban a karakter állókép, a feliratok időzítése becsült.")
    open(os.path.join(vd, "gyartasi-csomag.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("written", os.path.join(vd, "gyartasi-csomag.md"))


def to_html(vd):
    """Drive-friendly HTML (colour-coded caption words, ASCII-safe entities) for Google Docs import."""
    import html as H
    tl = json.load(open(os.path.join(vd, "timeline.json"), encoding="utf-8"))
    cfg = json.load(open(os.path.join(vd, "build", "render_cfg.json"), encoding="utf-8"))
    col = {"amber": "#b45309", "green": "#047857"}
    def cap_html(a, b):
        out = []
        for g in cfg["captions"]:
            if a - 0.05 <= g["start"] < b - 0.05:
                out.append(" ".join(f'<b style="color:{col[w["c"]]}">{H.escape(w["t"])}</b>' if w["c"] in col else H.escape(w["t"]) for w in g["words"]))
        return " / ".join(out) or "–"
    def sfx_in(a, b):
        ks = []
        for c in cfg["cues"]:
            if a <= c["t"] < b and c["kind"] not in ks: ks.append(c["kind"])
        return ", ".join(ks) or "–"
    P = []
    P.append(f"<h1>Prof Enzo – {H.escape(tl['title'])}</h1>")
    P.append(f"<p><b>Kategória:</b> {H.escape(tl.get('category', ''))} · <b>Formátum:</b> 9:16, 1080×1920 · <b>Becsült hossz:</b> {cfg['duration']:.0f} mp</p>")
    P.append("<h2>1. Narráció (Prof Enzo hangján)</h2>")
    for s in re.split(r"(?<=[.!?…”])\s+", tl["script"]):
        P.append(f"<p>{H.escape(s)}</p>")
    P.append("<p><i>Az utolsó mondat a stratégia egységes CTA-ja. Kiejtés: „profenzo.com” = profenzo pont kom.</i></p>")
    P.append("<h2>2. Produkciós táblázat</h2>")
    P.append(f'<p>Feliratszínek: <b style="color:{col["amber"]}">borostyán</b> = tényszerű/biológiai kulcsszó, <b style="color:{col["green"]}">zöld</b> = megoldás/CTA. '
             "Állandó elem: bal felső jelvény „Prof. Enzo AI • profenzo.com”. Prof Enzo alul középen, a záró CTA-ban balra húzódik.</p>")
    P.append('<table><tr><th>Időkód</th><th>Vizuális kép &amp; B-roll</th><th>Képernyőfelirat</th><th>SFX</th></tr>')
    for s in cfg["scenes"]:
        P.append(f"<tr><td>{mmss(s['start'])}–{mmss(s['end'])}</td><td>{H.escape(s.get('desc', s['type']))}</td><td>{cap_html(s['start'], s['end'])}</td><td>{sfx_in(s['start'], s['end'])}</td></tr>")
    P.append("</table><p>Zene: halk, meleg lo-fi / ambient alap, a beszéd alatt kb. –24 dB, a végén lecseng.</p>")
    if tl.get("post"):
        P.append("<h2>3. TikTok-leírás és hashtagek</h2>")
        P.append(f"<p>{H.escape(tl['post']['caption'])}</p><p><b>Hashtagek:</b> {H.escape(' '.join(tl['post']['hashtags']))}</p>")
    if tl.get("compliance"):
        P.append("<h2>4. Szakmai és compliance-ellenőrzés</h2><ul>")
        P += [f"<li>{H.escape(c)}</li>" for c in tl["compliance"]]
        P.append("<li>A stratégia 8A ellenőrzőlistáját a <b>kész</b> videón kell lefuttatni: szöveg, felirat, B-roll, leírás és tervezett kommentválaszok együtt.</li></ul>")
    if tl.get("sources"):
        P.append("<h2>5. Források (publikálás előtt ellenőrizendő)</h2><ul>")
        for s in tl["sources"]:
            name, _, url = s.rpartition(" – ")
            P.append(f'<li>{H.escape(name)} – <a href="{H.escape(url)}">{H.escape(url)}</a></li>')
        P.append("</ul>")
    P.append("<h2>6. Gyártási állapot</h2><ul><li>✅ Szöveg, idővonal, feliratok, grafikák, SFX, zene: a vázlat elkészült.</li>"
             "<li>⏳ Prof Enzo hangja és szájszinkronja: HeyGen API-kulcsra vagy kreditfeltöltésre vár. A vázlatban a karakter állókép, a feliratok időzítése becsült.</li></ul>")
    css = "<style>body{font-family:Arial,sans-serif} table{border-collapse:collapse} td,th{border:1px solid #999;padding:4px 6px;vertical-align:top}</style>"
    doc = f'<!doctype html><html><head><meta charset="utf-8">{css}</head><body>{"".join(P)}</body></html>'
    doc = "".join(c if ord(c) < 128 else f"&#x{ord(c):X};" for c in doc)
    return doc


if __name__ == "__main__":
    # python3 package.py <video dir>...         -> gyartasi-csomag.md
    # python3 package.py --html <video dir>...  -> build/gyartasi-csomag.html (Google Docs import, Drive folder "2 - Gyartasi csomagok")
    args = sys.argv[1:]
    as_html = "--html" in args
    for vd in (a for a in args if a != "--html"):
        vd = os.path.abspath(vd)
        if as_html:
            out = os.path.join(vd, "build", "gyartasi-csomag.html")
            open(out, "w", encoding="ascii").write(to_html(vd))
            print("written", out)
        else:
            main(vd)
