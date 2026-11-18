#!/usr/bin/env python3
"""Profenzo video builder: timeline.json (+ optional voiceover) -> render config, SFX/music mix, final MP4.

usage:
  python3 build.py plan   <video_dir> [--vo vo.wav] [--words words.json] [--draft]
  python3 build.py stills <video_dir> t1 t2 ...          (preview frames)
  python3 build.py video  <video_dir>                     (render frames -> video_noaudio.mp4)
  python3 build.py audio  <video_dir>                     (sfx + music + vo -> mix.wav)
  python3 build.py mux    <video_dir>                     (-> final.mp4)

With a HeyGen clip of Prof Enzo speaking, `python3 avatar.py final <video_dir> heygen.mp4` runs everything:
voice + word timings from the clip, keyed animated character instead of the still, captions on the real speech.
"""
import json, os, re, subprocess, sys, difflib, unicodedata
import numpy as np

ENGINE = os.path.dirname(os.path.abspath(__file__))
SR = 48000


# ----------------------------------------------------------------------------- timing
def tokens_of(script):
    return script.split()


def norm(w):
    w = unicodedata.normalize("NFC", w.lower())
    return re.sub(r"[^0-9a-záéíóöőúüű]", "", w)


def syllables(w):
    return max(1, len(re.findall(r"[aáeéiíoóöőuúüű]", w.lower())))


def estimate_timings(tokens, start, total):
    durs, pauses = [], []
    for w in tokens:
        durs.append(0.09 + 0.16 * syllables(w))
        pauses.append(0.34 if w.endswith((".", "?", "!")) else 0.17 if w.endswith((",", ":")) else 0.0)
    k = total / (sum(durs) + sum(pauses[:-1]))
    t, out = start, []
    for d, p in zip(durs, pauses):
        out.append([round(t, 3), round(t + d * k, 3)])
        t += (d + p) * k
    return out


def align_timings(tokens, asr_words):
    """Map script tokens to ASR word timings (sequence alignment on normalised words)."""
    a = [norm(t) for t in tokens]
    b = [norm(w["w"]) for w in asr_words]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    times = [None] * len(tokens)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and (i2 - i1) == (j2 - j1)):
            for k in range(i2 - i1):
                times[i1 + k] = [asr_words[j1 + k]["s"], asr_words[j1 + k]["e"]]
        elif tag == "replace":  # spread the block's span over the tokens
            s, e = asr_words[j1]["s"], asr_words[j2 - 1]["e"]
            n = i2 - i1
            for k in range(n):
                times[i1 + k] = [s + (e - s) * k / n, s + (e - s) * (k + 1) / n]
    # interpolate gaps
    for i in range(len(times)):
        if times[i] is None:
            prev = next((times[j] for j in range(i - 1, -1, -1) if times[j]), [0, 0])
            nxt = next((times[j] for j in range(i + 1, len(times)) if times[j]), [prev[1] + .3, prev[1] + .6])
            times[i] = [prev[1], max(prev[1] + 0.05, min(nxt[0], prev[1] + 0.35))]
    return [[round(s, 3), round(e, 3)] for s, e in times]


ARTICLES = {"a", "az", "egy", "és", "hogy", "ha", "de", "mert", "vagy", "is", "még"}


def auto_captions(toks, keywords, display=None):
    display = {norm(k): v for k, v in (display or {}).items()}
    amber = [norm(k) for k in keywords.get("amber", [])]; green = [norm(k) for k in keywords.get("green", [])]
    def color(t):
        n = norm(t)
        if any(n.startswith(k) for k in green if k): return "green"
        if any(n.startswith(k) for k in amber if k): return "amber"
        return ""
    groups, cur = [], []
    def close():
        if cur: groups.append(list(cur)); cur.clear()
    punct = lambda w: w.endswith((",", ".", "?", "!", ":", ";", "…"))
    for i, t in enumerate(toks):
        chars = sum(len(toks[j]) + 1 for j in cur)
        if cur and (len(cur) >= 4 or chars + len(t) > 26):
            carry = []
            while len(cur) > 1 and norm(toks[cur[-1]]) in ARTICLES and not punct(toks[cur[-1]]):
                carry.insert(0, cur.pop())
            close(); cur.extend(carry)
        cur.append(i)
        if t.endswith((".", "?", "!", "…")): close()
        elif t.endswith((",", ":", ";")) and (len(cur) >= 2 or len(t) >= 7): close()
    close()
    return [{"from": g[0], "to": g[-1], "text": [[display.get(norm(toks[i]), toks[i]).upper(), color(toks[i])] for i in g]} for g in groups]


# ----------------------------------------------------------------------------- plan
def plan(video_dir, vo=None, words=None, draft=False):
    tl = json.load(open(os.path.join(video_dir, "timeline.json"), encoding="utf-8"))
    fps = tl["fps"]
    toks = tokens_of(tl["script"])
    if words:
        wt = align_timings(toks, json.load(open(words, encoding="utf-8")))
    else:
        target = tl.get("speech_target", "auto")
        if target == "auto":
            nat = estimate_timings(toks, 0, 1.0)  # proportions only
            raw = sum(0.09 + 0.16 * syllables(w) for w in toks) + sum(0.34 if w.endswith((".", "?", "!", "…")) else 0.17 if w.endswith((",", ":")) else 0 for w in toks[:-1])
            target = raw * tl.get("pace", 0.86)
        wt = estimate_timings(toks, tl.get("speech_start", 0.15), target)
    dur = tl["duration"] if tl.get("duration") not in (None, "auto") else round(wt[-1][1] + tl.get("tail", 1.4), 2)
    W = lambda i: wt[i][0]
    ntoks = [norm(t) for t in toks]
    cursor = {"i": 0}
    def find_word(marker, after=None):
        m = re.match(r"@(.+?)(?:#(\d+))?$", marker); word, nth = norm(m.group(1)), int(m.group(2) or 1)
        start = cursor["i"] if after is None else after
        hits = [i for i in range(start, len(ntoks)) if ntoks[i] == word] or [i for i in range(start, len(ntoks)) if ntoks[i].startswith(word)]
        if len(hits) < nth: raise ValueError(f"anchor {marker} not found after token {start}")
        return hits[nth - 1]

    # scenes
    scenes, phone = [], None
    for s in tl["scenes"]:
        if s["type"] == "phone":
            idx = find_word(s["at"], 0) if s["at"].startswith("@") else int(s["at"][1:])
            phone = {k: v for k, v in s.items() if k not in ("at", "dur")}
            phone.update({"type": "phone", "start": W(idx), "end": W(idx) + s["dur"]})
    def anchor(a):
        if a.startswith("@"):
            i = find_word(a); cursor["i"] = i; return W(i)
        if a == "t0": return 0.0
        if a == "end": return dur
        if a == "phone": return phone["start"]
        if a == "phone_end": return phone["end"]
        if a.startswith("t") and a[1:].replace(".", "").isdigit(): return float(a[1:])
        if a.startswith("w"): return W(int(a[1:]))
        raise ValueError(a)
    for s in tl["scenes"]:
        if s["type"] == "phone":
            scenes.append(phone); continue
        d = {k: v for k, v in s.items() if k not in ("from", "to", "at", "dur")}
        d.update({"start": anchor(s["from"]), "end": anchor(s["to"])})
        scenes.append(d)
    for d in scenes:
        for k, v in list(d.items()):
            if k.endswith("At") and isinstance(v, str) and v.startswith("@"): d[k] = W(find_word(v, 0)) - d["start"]
            if k.endswith("At") and isinstance(v, list): d[k] = [(W(find_word(x, 0)) - d["start"]) if isinstance(x, str) else x for x in v]
    scenes.sort(key=lambda s: s["start"])
    for a, b in zip(scenes, scenes[1:]):
        a["end"] = b["start"]
    end = next(s for s in scenes if s["type"] == "end")
    type_w = tl.get("end_type_word", 0)
    if isinstance(type_w, str): type_w = find_word(type_w, 0)
    end["typeStart"] = max(end["start"] + 1.0, W(type_w) - 0.35)
    end["sendAt"] = end["typeStart"] + 0.25 + 0.06 * len(end.get("typed", "ALVÁS"))
    end["hintAt"] = end["sendAt"] + 0.55

    # captions
    if tl.get("captions", "auto") == "auto":
        tl["captions"] = auto_captions(toks, tl.get("keywords", {}), tl.get("display"))
    caps = []
    for i, g in enumerate(tl["captions"]):
        s = wt[g["from"]][0]
        nxt = tl["captions"][i + 1] if i + 1 < len(tl["captions"]) else None
        e = wt[nxt["from"]][0] if nxt else min(dur, wt[g["to"]][1] + 1.2)
        caps.append({"start": round(s, 3), "end": round(e, 3), "words": [{"t": t, "c": c} for t, c in g["text"]]})

    # character keyframes (still image for drafts; avatar video later)
    def sc(type_, k=0):
        return [s for s in scenes if s["type"] == type_][k]
    keys = []
    def key(s, e, vis=True, x0=540, x1=540, s0=1.0, s1=1.0):
        keys.append({"start": s, "end": e, "visible": vis, "x0": x0, "x1": x1, "s0": s0, "s1": s1})
    zoom = {"studio": (1.0, 1.06), "chart1": (1.05, 1.01), "chart2": (1.01, 1.05), "neurons": (1.0, 1.04),
            "plate": (1.05, 1.02), "drop": (1.0, 1.04), "olf": (1.03, 1.07)}
    pw = tl.get("punch_in_word")
    punch = (W(find_word(pw, 0)) if isinstance(pw, str) else W(pw)) if pw is not None else -1
    for s in scenes:
        if s["type"] in ("clock", "phone") or s.get("hideChar"):
            key(s["start"], s["end"], vis=False)
        elif s["type"] == "end":
            key(s["start"], s["start"] + 0.45, x0=540, x1=262, s0=1.0, s1=0.84)
            key(s["start"] + 0.45, s["end"], x0=262, x1=262, s0=0.84, s1=0.86)
        elif s["start"] < punch < s["end"] and s["type"] not in ("end",):
            key(s["start"], punch, s0=1.0, s1=1.04)
            key(punch, punch + 0.22, s0=1.04, s1=1.14)
            key(punch + 0.22, s["end"], s0=1.14, s1=1.15)
        else:
            z = zoom.get(s["type"], (1.0, 1.05))
            key(s["start"], s["end"], s0=z[0], s1=z[1])

    cfg = {
        "fps": fps, "duration": dur, "draft": draft, "title": tl.get("title", ""), "tag": tl.get("tag"),
        "scenes": scenes, "captions": caps, "charKeys": keys,
        "capYKeys": ([[0, 1090], [scenes[1]["start"], 880]] if scenes[0]["type"] == "clock" else [[0, 880]]) + [[end["start"], 560]],
        "hideCapRanges": ([[phone["start"], phone["end"]]] if phone else []) + [[s["start"], s["end"]] for s in scenes if s.get("hideCaptions")],
        "flashes": [s["start"] for s in scenes[1:] if s["type"] not in ("phone",)],
        "char": {"src": "file://" + os.path.join(video_dir, "..", "..", "assets", "prof-enzo-kivagott.png"), "w": 533, "h": 942, "bottomPad": 0},
        "avatar": "file://" + os.path.join(video_dir, "..", "..", "assets", "prof-enzo-avatar.png"),
        "words": wt,
    }
    cfg["char"]["src"] = "file://" + os.path.abspath(cfg["char"]["src"][7:])
    cfg["avatar"] = "file://" + os.path.abspath(cfg["avatar"][7:])
    meta_p = os.path.join(video_dir, "build", "avatar", "meta.json")
    if vo and os.path.exists(meta_p):   # animated HeyGen avatar, keyed by avatar.py prep
        m = json.load(open(meta_p)); d = "file://" + os.path.dirname(os.path.abspath(meta_p))
        cfg["char"] = {"src": d + "/f00001.webp", "w": m["box_w"], "h": m["box_h"], "bottomPad": 0,
                       "frames": {"dir": d, "n": m["n"], "fps": m["fps"]}}
    if vo:
        cfg["vo"] = os.path.abspath(vo)
        x = load_audio(vo, 16000)
        hop = 16000 // fps
        env = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(int(len(x) / hop))])
        env = np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1)
        cfg["env"] = [round(float(v), 3) for v in env]
        cfg["envFps"] = fps
    # sfx cue times
    cues = []
    counts = {}
    for c in tl["sfx"]:
        a = c["at"]; off = 0.0
        m = re.match(r"(.+?)\+([0-9.]+)$", a)
        if m: a, off = m.group(1), float(m.group(2))
        if a == "t0": t = 0.0
        elif a.startswith("@"): t = W(find_word(a, 0))
        elif a.startswith("w"): t = W(int(a[1:]))
        elif a.startswith("scene:"):
            nm = a[6:]; k = 0
            if "#" in nm: nm, k = nm.split("#"); k = int(k)
            t = sc(nm, k)["start"]
        elif a == "typing": t = end["typeStart"]
        elif a == "send": t = end["sendAt"]
        elif a == "hint": t = end["hintAt"]
        else: raise ValueError(a)
        cues.append({"t": round(t + off, 3), "kind": c["kind"]})
    cfg["cues"] = cues
    out = os.path.join(video_dir, "build"); os.makedirs(out, exist_ok=True)
    json.dump(cfg, open(os.path.join(out, "render_cfg.json"), "w"), ensure_ascii=False, indent=1)
    print("scenes:"); [print(f"  {s['type']:8s} {s['start']:6.2f} – {s['end']:6.2f}") for s in scenes]
    print("captions:", len(caps), " last word ends", wt[-1][1])
    return cfg


# ----------------------------------------------------------------------------- audio
def load_audio(path, sr=SR):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))


def sine_sweep(f0, f1, dur, curve=2.0):
    n = int(dur * SR); k = np.linspace(0, 1, n) ** curve
    f = f0 + (f1 - f0) * k
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def noise_sweep(dur, f0, f1, bw=0.6, seed=0):
    """spectral-domain swept band noise (whoosh)"""
    rng = np.random.default_rng(seed)
    n = int(dur * SR); hop, N = 256, 2048
    frames = n // hop + 4
    out = np.zeros(frames * hop + N)
    freqs = np.fft.rfftfreq(N, 1 / SR)
    win = np.hanning(N)
    for i in range(frames):
        k = min(1, i / max(1, frames - 1))
        fc = f0 * (f1 / f0) ** k
        mag = np.exp(-0.5 * (np.log2(np.maximum(freqs, 20) / fc) / bw) ** 2)
        spec = mag * np.exp(1j * rng.uniform(0, 2 * np.pi, len(freqs)))
        out[i * hop:i * hop + N] += np.fft.irfft(spec) * win
    out = out[:n]
    e = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    return out / (np.max(np.abs(out)) + 1e-9) * e


def sfx(kind, seed=0):
    if kind == "whoosh": return 0.55 * noise_sweep(0.42, 300, 3000, 0.7, seed)
    if kind == "whoosh_fast": return 0.6 * noise_sweep(0.24, 500, 5000, 0.6, seed)
    if kind == "swoosh_up": return 0.5 * noise_sweep(0.55, 250, 6000, 0.5, seed)
    if kind == "air": return 0.35 * noise_sweep(1.3, 400, 1800, 1.0, seed)
    if kind == "sent": return 0.4 * noise_sweep(0.22, 800, 7000, 0.5, seed)
    if kind == "pop":
        n = int(0.09 * SR); return 0.7 * sine_sweep(950, 330, 0.09, 0.5) * env_ad(n, 0.002, 0.028)
    if kind == "tap":
        n = int(0.07 * SR); return 0.7 * sine_sweep(420, 180, 0.07, 0.6) * env_ad(n, 0.001, 0.02)
    if kind == "tick":
        n = int(0.05 * SR); rng = np.random.default_rng(seed); return 0.6 * (rng.normal(0, 1, n) * env_ad(n, 0.0005, 0.004) + np.sin(2 * np.pi * 3200 * np.arange(n) / SR) * env_ad(n, 0.001, 0.01))
    if kind == "beep":
        n = int(0.11 * SR); b = np.sin(2 * np.pi * 1050 * np.arange(n) / SR) * np.minimum(1, np.arange(n) / 200) * np.exp(-np.arange(n) / (0.09 * SR))
        out = np.zeros(int(0.32 * SR)); out[:n] += b; out[int(0.16 * SR):int(0.16 * SR) + n] += b; return 0.35 * out
    if kind == "bloop":
        n = int(0.38 * SR); return 0.5 * sine_sweep(720, 210, 0.38, 0.8) * env_ad(n, 0.004, 0.16)
    if kind == "alarm":
        out = np.zeros(int(0.8 * SR))
        for i, f in enumerate([880, 660]):
            n = int(0.45 * SR); t = np.arange(n) / SR
            tone = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2.76 * f * t)) * env_ad(n, 0.003, 0.18)
            out[int(i * 0.22 * SR):int(i * 0.22 * SR) + n] += tone
        return 0.28 * out
    if kind == "spark":
        rng = np.random.default_rng(seed); n = int(0.6 * SR); out = np.zeros(n)
        for _ in range(28):
            p = rng.integers(0, n - 2000); m = int(rng.uniform(200, 1200)); out[p:p + m] += rng.normal(0, 1, m) * env_ad(m, 0.0002, 0.002) * rng.uniform(.3, 1)
        out = np.diff(out, prepend=0); return 0.45 * out / (np.max(np.abs(out)) + 1e-9)
    if kind == "chime":
        out = np.zeros(int(1.6 * SR))
        for i, f in enumerate([1046.5, 1318.5, 1568.0]):
            n = int(1.3 * SR); t = np.arange(n) / SR
            tone = sum(a * np.sin(2 * np.pi * f * r * t) for r, a in [(1, 1), (2.76, .35), (5.4, .12)]) * env_ad(n, 0.003, 0.45)
            out[int(i * 0.09 * SR):int(i * 0.09 * SR) + n] += tone
        return 0.18 * out
    if kind == "notify":
        out = np.zeros(int(0.3 * SR))
        for i, f in enumerate([1568, 2093]):
            n = int(0.12 * SR); t = np.arange(n) / SR; out[int(i * 0.08 * SR):int(i * 0.08 * SR) + n] += np.sin(2 * np.pi * f * t) * env_ad(n, 0.002, 0.04)
        return 0.3 * out
    if kind == "plip":
        n = int(0.16 * SR); a = sine_sweep(380, 1500, 0.16, 0.35) * env_ad(n, 0.001, 0.05)
        return 0.55 * a
    if kind == "typing":
        rng = np.random.default_rng(seed); out = np.zeros(int(1.0 * SR))
        for i in range(5):
            m = int(0.03 * SR); click = rng.normal(0, 1, m) * env_ad(m, 0.0003, 0.006)
            click = np.diff(click, prepend=0); p = int((i * 0.14 + rng.uniform(0, .02)) * SR); out[p:p + m] += click
        return 0.5 * out / (np.max(np.abs(out)) + 1e-9)
    raise ValueError(kind)


def reverb(x, secs=2.6, wet=0.32, seed=3):
    rng = np.random.default_rng(seed); n = int(secs * SR)
    ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 3.2)
    ir[:int(0.012 * SR)] = 0
    L = len(x) + n; F = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
    y = y / (np.max(np.abs(y)) + 1e-9) * np.max(np.abs(x))
    return (1 - wet) * x + wet * y


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)


def music(dur, warm_at=None, seed=1):
    """soft night ambient bed: pad chords + gentle plucks + air"""
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    prog = [[53, 57, 60, 64, 67], [57, 60, 64, 67], [50, 53, 57, 60, 64], [46, 50, 53, 57, 60], [53, 57, 60, 64, 67]]
    seg = dur / len(prog); xf = 1.6
    for i, chord in enumerate(prog):
        s0 = max(0, i * seg - xf / 2); s1 = min(dur, (i + 1) * seg + xf / 2)
        a, b = int(s0 * SR), int(s1 * SR); tt = t[a:b] - s0; L = s1 - s0
        e = np.minimum(1, tt / xf) * np.minimum(1, (L - tt) / xf)
        for m in chord:
            f = midi(m)
            for det in (-0.12, 0.12):
                ff = f * 2 ** (det / 12)
                out[a:b] += e * (np.sin(2 * np.pi * ff * tt) + 0.25 * np.sin(2 * np.pi * 2 * ff * tt) + 0.08 * np.sin(2 * np.pi * 3 * ff * tt)) / len(chord)
        out[a:b] += 0.5 * e * np.sin(2 * np.pi * midi(chord[0] - 12) * tt)
    out = onepole_lp(out, 1400)
    rng = np.random.default_rng(seed)
    pent = [72, 74, 77, 79, 81, 84]
    beat = 60 / 64
    k = 0.0
    while k < dur - 1.0:
        f = midi(pent[rng.integers(0, len(pent))]); m = int(1.4 * SR); p = int(k * SR)
        if p + m < n:
            tt = np.arange(m) / SR
            pl = (np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * 2 * f * tt)) * env_ad(m, 0.004, 0.35)
            gain = 0.16 if (warm_at is None or k < warm_at) else 0.24
            out[p:p + m] += gain * pl
        k += beat * (2 if rng.random() < .6 else 1)
    air = onepole_lp(rng.normal(0, 1, n), 900) * 0.04
    out = out + air
    out = reverb(out, 3.0, 0.38)
    fade = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 2.0)
    return out * fade / (np.max(np.abs(out)) + 1e-9)


def audio(video_dir):
    b = os.path.join(video_dir, "build"); cfg = json.load(open(os.path.join(b, "render_cfg.json")))
    dur = cfg["duration"]; n = int(dur * SR)
    fx = np.zeros(n)
    for i, c in enumerate(cfg["cues"]):
        s = sfx(c["kind"], seed=i); p = int(c["t"] * SR)
        if p >= n: continue
        m = min(len(s), n - p); fx[p:p + m] += s[:m]
    warm_at = next((s["start"] for s in cfg["scenes"] if s["type"] == "studio" and s.get("warm", 0) > .5), None)
    mus = music(dur, warm_at)
    vo = np.zeros(n)
    if cfg.get("vo"):
        v = load_audio(cfg["vo"]); m = min(len(v), n); vo[:m] = v[:m]
        vo = vo / (np.max(np.abs(vo)) + 1e-9) * 0.89
    # duck music under speech
    if np.any(vo):
        hop = 480; env = np.array([np.sqrt(np.mean(vo[i:i + hop] ** 2)) for i in range(0, n, hop)])
        env = np.convolve(env, np.ones(20) / 20, mode="same"); env = env / (env.max() + 1e-9)
        duck = np.repeat(1 - 0.45 * np.clip(env * 3, 0, 1), hop)[:n]
    else:
        duck = np.ones(n)
    mix = vo + 0.20 * mus * duck + 0.30 * fx
    stereo = np.stack([mix, mix], 1).astype(np.float32)
    raw = os.path.join(b, "mix_raw.wav")
    import wave
    with wave.open(raw, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes())
    target = "-14" if np.any(vo) else "-20"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"loudnorm=I={target}:TP=-1.5:LRA=11", "-ar", str(SR), os.path.join(b, "mix.wav")], check=True)
    print("audio mixed ->", os.path.join(b, "mix.wav"), "target LUFS", target)


def render(video_dir, stills=None, parts=3):
    b = os.path.join(video_dir, "build"); cfgp = os.path.join(b, "render_cfg.json"); cfg = json.load(open(cfgp))
    js = os.path.join(ENGINE, "render.js")
    if stills:
        for t in stills:
            f = int(round(float(t) * cfg["fps"]))
            subprocess.run(["node", js, cfgp, os.path.join(b, f"still_{float(t):05.2f}.jpg"), str(f)], check=True)
        return
    N = int(round(cfg["duration"] * cfg["fps"])); step = (N + parts - 1) // parts
    procs = []
    for k in range(parts):
        a, z = k * step, min(N, (k + 1) * step)
        procs.append(subprocess.Popen(["node", js, cfgp, os.path.join(b, f"part{k}.mp4"), str(a), str(z)]))
    for p in procs:
        if p.wait() != 0: raise SystemExit("render failed")
    lst = os.path.join(b, "parts.txt")
    open(lst, "w").write("".join(f"file 'part{k}.mp4'\n" for k in range(parts)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(b, "video_noaudio.mp4")], check=True)
    print("video ->", os.path.join(b, "video_noaudio.mp4"))


def mux(video_dir, name="final.mp4"):
    b = os.path.join(video_dir, "build")
    out = os.path.join(b, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(b, "video_noaudio.mp4"), "-i", os.path.join(b, "mix.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], check=True)
    print("final ->", out)


if __name__ == "__main__":
    cmd, vd = sys.argv[1], os.path.abspath(sys.argv[2])
    args = sys.argv[3:]
    if cmd == "plan":
        vo = args[args.index("--vo") + 1] if "--vo" in args else None
        words = args[args.index("--words") + 1] if "--words" in args else None
        plan(vd, vo, words, "--draft" in args)
    elif cmd == "stills": render(vd, stills=args)
    elif cmd == "video": render(vd)
    elif cmd == "audio": audio(vd)
    elif cmd == "mux": mux(vd, *(args[:1]))
