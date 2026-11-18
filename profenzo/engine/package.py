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

if __name__ == "__main__":
    for vd in sys.argv[1:]: main(os.path.abspath(vd))
