#!/usr/bin/env python3
"""Builds a showreel (intro card, a highlight from each video with a banner, outro card) from the rendered drafts."""
import json, os, subprocess, sys, tempfile
import numpy as np

ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ENGINE)
V = os.path.join(ROOT, "videok")
SEG = 5.5
SEGMENTS = [  # (folder, start, banner number, title, category)
    ("00-hajnali-3-ebredes", 6.6, "00", "A hajnali 3 órás ébredés", "Brief • B2 esti rituálék"),
    ("01-ot-illoolaj", 5.2, "01", "Van otthon öt illóolajad?", "C3 • készletalapú rutin"),
    ("02-diffuzor", 24.5, "02", "A diffúzorod nem varázspálca", "C2 • illatkörnyezet"),
    ("03-higitas", 16.8, "03", "Hígítás: nem a mennyiség számít", "C1 • alkalmazás és hígítás"),
    ("04-citrus-napfeny", 8.4, "04", "Citromolaj a bőrön, aztán napfény?", "C1 • fényérzékenység, címkeolvasás"),
    ("05-citromle-vagy-citromolaj", 9.3, "05", "Citromlé vagy citromolaj?", "C1 • EU-s felhasználási kategória"),
    ("06-tiszta-vagy-illatos", 3.4, "06", "Tiszta, vagy csak jó illatú?", "B3 • otthon és tisztaság"),
    ("07-bor-nem-csempe", 7.6, "07", "A bőröd nem csempe", "B1 • testápolási alaprutin"),
    ("08-wellnessrutin-forditva", 15.5, "08", "Fordítva építed a rutinodat?", "B3 • wellnesspiramis"),
    ("09-etrend-kiegeszitok", 24.7, "09", "Tele a szekrényed kapszulával?", "B3 • étrend-kiegészítők"),
    ("10-labor-az-uvegcse-mogott", 19.6, "10", "Labor az üvegcse mögött", "C3 • tudástár és szakértők"),
    ("03-higitas", 45.5, "CTA", "Egységes zárás: profenzo.com chat", "Minden videó végén"),
]
INTRO, OUTRO = 4.0, 7.0


def run(cmd):
    subprocess.run(cmd, check=True)


def cards(work):
    spec = {
        "avatar": "file://" + os.path.join(ROOT, "assets", "prof-enzo-avatar.png"),
        "enzo": "file://" + os.path.join(ROOT, "assets", "prof-enzo-kivagott.png"),
    }
    jobs = [dict(spec, kind="intro", out=os.path.join(work, "intro.png")),
            dict(spec, kind="outro", out=os.path.join(work, "outro.png"),
                 done=[["✅", "11 videó vázlata (00–10)"], ["✅", "Narráció a stratégia szerint, egységes CTA-val"], ["✅", "Automatikus, színkódolt feliratok"],
                       ["✅", "21 jelenetsablon, effektek, zene"], ["✅", "Gyártási csomagok, compliance, források"]],
                 todo=[["⏳", "Prof Enzo hangja + szájszinkron"], ["🔑", "HeyGen API-kulcs vagy kredit"]],
                 drive="Drive: Prof Enzo – TikTok videók (Claude)")]
    for i, (_, _, num, title, cat) in enumerate(SEGMENTS):
        jobs.append({"kind": "banner", "num": num, "title": title, "cat": cat, "out": os.path.join(work, f"banner_{i:02d}.png")})
    js = os.path.join(work, "cards.js")
    open(js, "w").write("""
const { chromium } = require('playwright'); const fs = require('fs');
(async () => { const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.argv[3]);
  for (const j of jobs) { await p.evaluate(s => window.renderCard(s), j); await p.screenshot({ path: j.out, omitBackground: j.kind === 'banner' }); }
  await b.close(); })().catch(e => { console.error(e); process.exit(1); });
""")
    jp = os.path.join(work, "jobs.json"); json.dump(jobs, open(jp, "w"), ensure_ascii=False)
    run(["node", js, jp, os.path.join(ENGINE, "showcard.html")])


def main(out):
    work = tempfile.mkdtemp(prefix="showreel_")
    cards(work)
    enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30", "-an"]
    parts = []
    def still(png, dur, name, zin=True):
        o = os.path.join(work, name); fr = int(dur * 30)
        z = f"zoompan=z='1+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s=1080x1920:fps=30" if zin else f"zoompan=z='1':d={fr}:s=1080x1920:fps=30"
        run(["ffmpeg", "-v", "error", "-y", "-i", png, "-vf", z + ",fade=t=in:st=0:d=0.3", "-t", str(dur)] + enc + [o]); return o
    parts.append(still(os.path.join(work, "intro.png"), INTRO, "p_intro.mp4"))
    for i, (folder, start, *_ ) in enumerate(SEGMENTS):
        o = os.path.join(work, f"p_{i:02d}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(SEG), "-i", os.path.join(V, folder, "build", "vazlat.mp4"),
             "-loop", "1", "-i", os.path.join(work, f"banner_{i:02d}.png"),
             "-filter_complex", "[1:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1[b];[0:v][b]overlay=0:0:shortest=1", "-t", str(SEG)] + enc + [o])
        parts.append(o)
    parts.append(still(os.path.join(work, "outro.png"), OUTRO, "p_outro.mp4"))
    lst = os.path.join(work, "list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    vid = os.path.join(work, "video.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
    # audio: continuous music bed + whoosh on every cut
    sys.path.insert(0, ENGINE); import build
    total = INTRO + SEG * len(SEGMENTS) + OUTRO; n = int(total * build.SR)
    mus = build.music(total, warm_at=INTRO + SEG * 5)
    fx = np.zeros(n)
    cuts = [INTRO + SEG * i for i in range(len(SEGMENTS) + 1)]
    for k, t in enumerate(cuts):
        s = build.sfx("whoosh", seed=k); p = int(max(0, t - 0.2) * build.SR); m = min(len(s), n - p); fx[p:p + m] += s[:m]
    s = build.sfx("chime", seed=99); fx[int(0.4 * build.SR):int(0.4 * build.SR) + len(s)] += s[:max(0, n - int(0.4 * build.SR))][:len(s)]
    mix = 0.5 * mus + 0.35 * fx
    wav = os.path.join(work, "mix.wav")
    import wave
    with wave.open(wav, "wb") as w:
        st = np.stack([mix, mix], 1); w.setnchannels(2); w.setsampwidth(2); w.setframerate(build.SR)
        w.writeframes((np.clip(st / (np.abs(st).max() + 1e-9) * 0.9, -1, 1) * 32767).astype("<i2").tobytes())
    run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", wav, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
         "-shortest", "-movflags", "+faststart", out])
    print("showreel ->", out, f"{total:.1f}s")


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]))
