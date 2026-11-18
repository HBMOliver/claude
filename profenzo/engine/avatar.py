#!/usr/bin/env python3
"""Animated Prof Enzo: a HeyGen avatar clip -> voice track, word timings and keyed RGBA frames placed like the still.

usage:
  python3 avatar.py prep  <video_dir> <heygen.mp4> [--matte auto|green|ai] [--scale k] [--dx px] [--dy px]
  python3 avatar.py final <video_dir> <heygen.mp4> [same options]   (prep + plan + video + audio + mux + Drive preview)

prep writes build/vo.wav, build/words.json, build/avatar/f00001.webp… and build/avatar/meta.json.
`build.py plan <video_dir> --vo build/vo.wav --words build/words.json` then shows the frames instead of the still.

Best input: HeyGen render on a solid #00FF00 background (fast, clean chroma key). Any other background
falls back to BiRefNet matting (slow on CPU: roughly 1-2 s per frame).
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter

ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ENGINE)
STILL = os.path.join(ROOT, "assets", "prof-enzo-kivagott.png")
STILL_BOX = (533, 942)   # display size of the still in render.html (render_cfg char.w / char.h), bottom-anchored
Q = 1.25                 # frames are stored at Q x display size so the punch-in zoom stays sharp
MODELS = os.environ.get("PROFENZO_MODELS", os.path.expanduser("~/.cache/profenzo"))
WHISPER_ROOT = os.environ.get("PROFENZO_WHISPER_ROOT")  # optional faster-whisper download_root


def run(cmd):
    subprocess.run(cmd, check=True)


def probe(src):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", src],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out); s = j["streams"][0]; num, den = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(num) / float(den), float(j["format"]["duration"])


def frames(src, w, h):
    """Yield every frame of src as an RGB uint8 array (h, w, 3)."""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE, bufsize=w * h * 3 * 2)
    n = w * h * 3
    try:
        while True:
            buf = p.stdout.read(n)
            if len(buf) < n: break
            yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    finally:   # also runs when the caller stops early: end ffmpeg quietly instead of a broken pipe
        if p.poll() is None: p.kill()
        p.stdout.close(); p.wait()


# ----------------------------------------------------------------------------- matting
def key_green(rgb):
    """Alpha from green dominance: G - max(R, B) <= 38 stays opaque, >= 90 is keyed out (teal scrubs survive)."""
    f = rgb.astype(np.int16)
    d = f[..., 1] - np.maximum(f[..., 0], f[..., 2])
    return 1.0 - np.clip((d - 38) / 52.0, 0, 1)


def despill(rgb, a):
    """Pull green spill out of the pixels near the matte edge only (Enzo's own green stays green)."""
    near = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))) < 250
    out = rgb.copy()
    g = out[..., 1].astype(np.int16); mx = np.maximum(out[..., 0], out[..., 2]).astype(np.int16)
    fix = near & (g > mx)
    out[..., 1][fix] = mx[fix].astype(np.uint8)
    return out


class AIMatte:
    MEAN, STD = np.array([0.485, 0.456, 0.406], np.float32), np.array([0.229, 0.224, 0.225], np.float32)

    def __init__(self):
        import onnxruntime as ort
        path = os.environ.get("PROFENZO_BIREFNET") or os.path.join(MODELS, "birefnet_lite.onnx")
        if not os.path.exists(path):
            from huggingface_hub import hf_hub_download
            os.makedirs(MODELS, exist_ok=True)
            got = hf_hub_download("onnx-community/BiRefNet_lite-ONNX", "onnx/model.onnx", local_dir=os.path.join(MODELS, "birefnet_hf"))
            os.replace(got, path)
        self.s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        i = self.s.get_inputs()[0]; self.name = i.name
        self.res = i.shape[-1] if isinstance(i.shape[-1], int) else 1024

    def __call__(self, rgb):
        h, w = rgb.shape[:2]
        x = np.asarray(Image.fromarray(rgb).resize((self.res, self.res), Image.BICUBIC), np.float32) / 255.0
        x = ((x - self.MEAN) / self.STD).transpose(2, 0, 1)[None].astype(np.float32)
        m = self.s.run(None, {self.name: x})[-1]
        m = m[0, 0] if m.ndim == 4 else m[0]
        if m.min() < 0 or m.max() > 1: m = 1 / (1 + np.exp(-m))
        m = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        return np.asarray(m, np.float32) / 255.0


def detect_mode(src, w, h):
    """'green' if the frame border is mostly solid green screen, else 'ai'."""
    for k, rgb in enumerate(frames(src, w, h)):
        border = np.concatenate([rgb[:8].reshape(-1, 3), rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)]).astype(np.int16)
        green = (border[:, 1] - np.maximum(border[:, 0], border[:, 2]) > 90).mean()
        return "green" if green > 0.6 else "ai"
    raise SystemExit("no frames in " + src)


# ----------------------------------------------------------------------------- placement
def metrics(a):
    """Character extent in an alpha map: top, bottom, left, right and the head's horizontal centre."""
    m = a > 0.5
    rows, cols = np.where(m.any(1))[0], np.where(m.any(0))[0]
    if len(rows) < 10: return None
    top, bot = int(rows[0]), int(rows[-1])
    band = m[top:top + max(3, int(0.22 * (bot - top)))]
    return {"top": top, "bot": bot, "left": int(cols[0]), "right": int(cols[-1]), "head_cx": float(np.where(band)[1].mean())}


def still_metrics():
    im = Image.open(STILL); s = STILL_BOX[0] / im.size[0]
    m = metrics(np.asarray(im)[:, :, 3] / 255.0)
    bw, bh = STILL_BOX   # relative to the box's bottom-centre anchor (display px)
    return {"top": m["top"] * s - bh, "bot": (m["bot"] + 1) * s - bh, "head_cx": m["head_cx"] * s - bw / 2}


def prep(video_dir, src, mode="auto", scale=None, dx=0.0, dy=0.0):
    b = os.path.join(video_dir, "build"); os.makedirs(b, exist_ok=True)
    out = os.path.join(b, "avatar"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".webp"): os.remove(os.path.join(out, f))
    w, h, fps, dur = probe(src)
    print(f"source {w}x{h} @ {fps:.2f} fps, {dur:.1f}s")

    # 1) voice + word timings
    vo = os.path.join(b, "vo.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "48000", vo])
    words_path = os.path.join(b, "words.json")
    transcribe(vo, words_path)

    # 2) matte: sample frames to fit the character onto the still's placement
    mode = detect_mode(src, w, h) if mode == "auto" else mode
    matte = key_green if mode == "green" else AIMatte()
    print("matte:", mode)
    n_est = max(1, int(dur * fps)); step = max(1, n_est // 24)
    samples = [metrics(matte(rgb)) for i, rgb in enumerate(frames(src, w, h)) if i % step == 0]
    samples = [s for s in samples if s]
    if not samples: raise SystemExit("could not find the character in the clip")
    med = {k: float(np.median([s[k] for s in samples])) for k in ("top", "bot", "head_cx")}
    st = still_metrics()
    if med["bot"] < h - 4:
        print("note: the character does not reach the bottom edge; fitting head-to-bottom height anyway (use --scale to adjust)")
    k = scale or (st["bot"] - st["top"]) / (med["bot"] + 1 - med["top"])   # display px per source px
    def to_rel(x, y):   # source px -> display px relative to the bottom-centre anchor
        return (x - med["head_cx"]) * k + st["head_cx"] + dx, (y - med["bot"] - 1) * k + st["bot"] + dy
    xl, yt = to_rel(min(s["left"] for s in samples), min(s["top"] for s in samples))
    xr, _ = to_rel(max(s["right"] for s in samples), 0)
    half_w = max(-xl, xr, STILL_BOX[0] / 2) + 0.06 * STILL_BOX[0]
    box_w, box_h = int(round(2 * half_w)), int(round(max(-yt + 0.05 * STILL_BOX[1], STILL_BOX[1])))
    ow, oh = int(round(box_w * Q)), int(round(box_h * Q))
    # box (display px, rel. to anchor) -> source crop
    sx0 = (-half_w - st["head_cx"] - dx) / k + med["head_cx"]; sx1 = (half_w - st["head_cx"] - dx) / k + med["head_cx"]
    sy0 = (-box_h - st["bot"] - dy) / k + med["bot"] + 1; sy1 = (0 - st["bot"] - dy) / k + med["bot"] + 1
    crop = tuple(int(round(v)) for v in (sx0, sy0, sx1, sy1))
    print(f"fit: scale {k:.3f}, box {box_w}x{box_h} (stored {ow}x{oh}), source crop {crop}")

    # 3) all frames -> keyed, cropped, resized RGBA WebP
    cx0, cy0, cx1, cy1 = max(0, crop[0]), max(0, crop[1]), min(w, crop[2]), min(h, crop[3])
    n = 0
    for rgb in frames(src, w, h):
        part = rgb[cy0:cy1, cx0:cx1]
        a = matte(part) if mode == "green" else matte(rgb)[cy0:cy1, cx0:cx1]
        if mode == "green": part = despill(part, a)
        rgba = np.dstack([part, (a * 255).astype(np.uint8)])
        canvas = Image.new("RGBa", (crop[2] - crop[0], crop[3] - crop[1]))
        canvas.paste(Image.fromarray(rgba, "RGBA").convert("RGBa"), (cx0 - crop[0], cy0 - crop[1]))
        img = canvas.resize((ow, oh), Image.LANCZOS).convert("RGBA")
        n += 1
        img.save(os.path.join(out, f"f{n:05d}.webp"), "WEBP", quality=90, method=3)
        if n % 150 == 0: print(f"  {n} frames")
    meta = {"n": n, "fps": fps, "box_w": box_w, "box_h": box_h, "q": Q, "scale": k, "dx": dx, "dy": dy, "matte": mode,
            "source": os.path.abspath(src), "source_size": [w, h], "duration": dur}
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"), indent=1)
    print(f"avatar frames: {n} -> {out}")
    return vo, words_path


def transcribe(wav, out):
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).copy()
    m = WhisperModel("medium", device="cpu", compute_type="int8", download_root=WHISPER_ROOT)
    segs, _ = m.transcribe(x, language="hu", word_timestamps=True, beam_size=5, vad_filter=False)
    words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)} for s in segs for w in s.words]
    json.dump(words, open(out, "w"), ensure_ascii=False, indent=0)
    print("asr:", " ".join(w["w"] for w in words))


def final(video_dir, src, **kw):
    sys.path.insert(0, ENGINE); import build
    vo, words = prep(video_dir, src, **kw)
    build.plan(video_dir, vo, words)
    build.render(video_dir)
    build.audio(video_dir)
    build.mux(video_dir, "vegleges.mp4")
    b = os.path.join(video_dir, "build")
    run([os.path.join(ENGINE, "drive_preview.sh"), os.path.join(b, "vegleges.mp4"), os.path.join(b, "vegleges_drive.mp4")])


if __name__ == "__main__":
    cmd, vd, src = sys.argv[1], os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3])
    a = sys.argv[4:]
    opt = lambda k, d=None, f=str: f(a[a.index(k) + 1]) if k in a else d
    kw = {"mode": opt("--matte", "auto"), "scale": opt("--scale", None, float), "dx": opt("--dx", 0.0, float), "dy": opt("--dy", 0.0, float)}
    {"prep": prep, "final": final}[cmd](vd, src, **kw)
