#!/usr/bin/env python3
"""Free lip-sync for Prof Enzo from real HeyGen animation frames (no credits).

A library is a set of keyed avatar frames (avatar.py prep output) with the speech they were animated to. For new
speech, every output frame picks the library frame whose original audio context sounds most like the new audio at
that moment (log-mel features), so HeyGen's own audio->mouth mapping carries over. A Viterbi search keeps the motion
natural: playing on to the next library frame is free, jumps cost more the more the head pose differs, holds cost a
little. The result is written as an avatar frame sequence that build.py uses like a HeyGen clip.

usage:
  python3 lipsync.py library <avatar_dir> <speech.wav> <lib.npz>     index a library (frames + their speech)
  python3 lipsync.py make <video_dir> <lib.npz> [<lib2.npz> ...]     build/vo.wav -> build/avatar/ (+ meta.json)
  python3 lipsync.py final <video_dir> <lib.npz> [...]                build/vo_raw.wav -> finished build/vegleges.mp4
"""
import glob, json, os, sys
import numpy as np

FPS = 30
LAG = 2   # the reel's mouth trails its audio by ~2 frames (measured); library frame k shows audio at k - LAG


def mel_frames(wav, n):
    """Log-mel (24 bands) + energy per video frame, n frames at 30 fps."""
    import librosa
    y, sr = librosa.load(wav, sr=16000)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=512, hop_length=160, n_mels=24, fmin=60, fmax=7600)
    L = np.log(S + 1e-6).T                                   # (frames@100Hz, 24)
    out = np.zeros((n, 25), np.float32)
    for i in range(n):
        a, b = int(i * 100 / FPS), int((i + 1) * 100 / FPS)
        seg = L[a:max(b, a + 1)]
        if len(seg): out[i, :24] = seg.mean(0); out[i, 24] = seg.mean()
        else: out[i] = out[i - 1] if i else -13.8
    d = np.vstack([out[:1] * 0, np.diff(out, axis=0)])        # dynamics: how the sound is changing
    return np.hstack([out, 0.5 * d]).astype(np.float32)


def pose_features(frames):
    """Head position (tracked on the eyes/nose) and a small face thumbnail without the mouth, per library frame."""
    from PIL import Image
    G = [np.asarray(Image.open(f).convert("L").resize((475, 589)), np.float32) for f in frames]
    med = np.median(np.stack(G), 0); T = med[225:320, 165:375]
    feats = []
    for g in G:
        best = (1e18, 0, 0)
        for dy in range(-20, 21, 2):
            for dx in range(-20, 21, 2):
                d = np.abs(g[225 + dy:320 + dy, 165 + dx:375 + dx] - T).mean()
                if d < best[0]: best = (d, dy, dx)
        _, dy, dx = best
        thumb = np.asarray(Image.fromarray(g[150 + dy:320 + dy, 150 + dx:390 + dx].astype(np.uint8)).resize((24, 17)), np.float32) / 255
        feats.append(np.concatenate([[dy / 10.0, dx / 10.0], thumb.ravel() * 2.0]))
    return np.array(feats, np.float32)


def library(avatar_dir, wav, out):
    frames = sorted(glob.glob(os.path.join(avatar_dir, "f*.webp")))
    meta = json.load(open(os.path.join(avatar_dir, "meta.json")))
    n = len(frames)
    if abs(meta["fps"] - FPS) > 0.01: raise SystemExit("library frames must be 30 fps")
    A = mel_frames(wav, n + LAG)
    feats = np.vstack([A[:1].repeat(LAG, 0), A[:n - LAG]]) if LAG else A[:n]   # what each frame's mouth is "saying"
    np.savez(out, frames=np.array(frames), audio=feats, pose=pose_features(frames), box=np.array([meta["box_w"], meta["box_h"]]))
    print(f"library: {n} frames -> {out}")


def make(video_dir, libs, jump=2.2, hold=1.0, pose_w=1.8, reverse=0.25):
    L = [np.load(p, allow_pickle=False) for p in libs]
    frames = np.concatenate([l["frames"] for l in L]); F = np.vstack([l["audio"] for l in L]); P = np.vstack([l["pose"] for l in L])
    box = L[0]["box"]
    K = len(frames); seg_end = np.cumsum([len(l["frames"]) for l in L]) - 1
    vo = os.path.join(video_dir, "build", "vo.wav")
    import soundfile as sf
    dur = sf.info(vo).duration; T = int(np.ceil(dur * FPS))
    X = mel_frames(vo, T)
    mu, sd = F.mean(0), F.std(0) + 1e-3
    Fn, Xn = (F - mu) / sd, (X - mu) / sd
    E = ((Xn[:, None, :] - Fn[None, :, :]) ** 2).mean(2)                    # (T, K) how well each frame fits each moment
    Pd = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).mean(2))            # (K, K) head-pose distance
    cont = np.zeros(K, bool); cont[:-1] = Pd[np.arange(K - 1), np.arange(1, K)] < np.percentile(Pd, 5)
    cont[seg_end] = False                                                     # never "play on" across library seams
    trans = jump + pose_w * Pd                                                # jump cost j -> k
    trans[np.arange(K), np.arange(K)] = hold
    idx = np.where(cont)[0]; trans[idx, idx + 1] = 0.0                        # natural playback is free
    trans[idx + 1, idx] = np.minimum(trans[idx + 1, idx], reverse)             # playing a run backwards looks natural too
    cost = E[0].copy(); back = np.zeros((T, K), np.int32)
    for t in range(1, T):
        tot = cost[:, None] + trans                                           # (from, to)
        back[t] = np.argmin(tot, 0); cost = tot[back[t], np.arange(K)] + E[t]
    path = np.zeros(T, np.int32); path[-1] = int(np.argmin(cost))
    for t in range(T - 1, 0, -1): path[t - 1] = back[t, path[t]]
    out = os.path.join(video_dir, "build", "avatar"); os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "f*.webp")): os.remove(f)
    for t, k in enumerate(path):
        os.symlink(os.path.abspath(str(frames[k])), os.path.join(out, f"f{t + 1:05d}.webp"))
    runs = int((np.abs(np.diff(path)) != 1).sum())
    json.dump({"n": T, "fps": FPS, "box_w": int(box[0]), "box_h": int(box[1]), "matte": "lipsync", "libraries": libs,
               "jumps": runs, "mean_fit": float(E[np.arange(T), path].mean())}, open(os.path.join(out, "meta.json"), "w"), indent=1)
    print(f"lip-sync: {T} frames, {runs} cuts between library runs (avg run {T / max(1, runs):.1f} frames) -> {out}")


def final(video_dir, libs):
    """Free route end to end: build/vo_raw.wav (voice.py make) -> word timings -> lip-synced Enzo -> plan with B-roll
    -> render -> mix -> build/vegleges.mp4 (+ vegleges_drive.mp4 for the Drive connector)."""
    import shutil, subprocess
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import avatar, build
    b = os.path.join(video_dir, "build")
    vo, words = os.path.join(b, "vo.wav"), os.path.join(b, "words.json")
    shutil.copyfile(os.path.join(b, "vo_raw.wav"), vo)
    avatar.transcribe(vo, words)
    make(video_dir, libs)
    build.plan(video_dir, vo, words)
    build.render(video_dir)
    build.audio(video_dir)
    build.mux(video_dir, "vegleges.mp4")
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), "drive_preview.sh"),
                    os.path.join(b, "vegleges.mp4"), os.path.join(b, "vegleges_drive.mp4")], check=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "library": library(os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3]), os.path.abspath(sys.argv[4]))
    elif cmd == "make": make(os.path.abspath(sys.argv[2]), [os.path.abspath(p) for p in sys.argv[3:]])
    elif cmd == "final": final(os.path.abspath(sys.argv[2]), [os.path.abspath(p) for p in sys.argv[3:]])
    else: raise SystemExit(__doc__)
