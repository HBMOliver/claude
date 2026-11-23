#!/usr/bin/env python3
"""Prof Enzo's voice without credits: Hungarian base speech from Piper (hu_HU-imre, CC0), converted to Enzo's timbre
with Seed-VC (zero-shot voice conversion) using a clean stretch of his real voice from the reference reel.
This is an imitation; his original voice lives in HeyGen. The user approved this route (no credits available).

Run with a Python that has seed-vc installed (pip install --no-deps seed-vc + its inference deps).

usage:
  python voice.py variants <text_file> <reference.wav> <out_dir>    sample settings side by side
  python voice.py make <video_dir> [--ref reference.wav]             narration -> build/vo_raw.wav (48 kHz mono)
"""
import argparse, glob, json, os, re, subprocess, sys, wave
import numpy as np

ENGINE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ENGINE)
MODELS = os.environ.get("PROFENZO_MODELS", os.path.expanduser("~/.cache/profenzo"))
PIPER = os.environ.get("PROFENZO_PIPER", os.path.join(MODELS, "hu_HU-imre-medium.onnx"))
SEEDVC_HOME = os.environ.get("PROFENZO_SEEDVC_HOME", os.path.join(MODELS, "seedvc"))   # its HF cache lives here
DEFAULT = {"length_scale": 1.0, "steps": 30, "cfg": 0.7}   # best in tests: sim 0.906 to Enzo, 77% ASR words


def tts_text(script):
    """Narration as it should be spoken (the web address spelled out the way it is pronounced)."""
    return re.sub(r"profenzo\.com-?", "profenzo pont kom", script)


def piper(text, out, length_scale=1.0, noise=0.6, noise_w=0.6):
    from piper import PiperVoice, SynthesisConfig
    v = PiperVoice.load(PIPER)
    with wave.open(out, "wb") as wf:
        v.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=length_scale, noise_scale=noise, noise_w_scale=noise_w))
    return out


class SeedVC:
    """Seed-VC v1 (whisper-small content encoder, 22.05 kHz), models loaded once."""
    def __init__(self):
        import seed_vc
        os.makedirs(SEEDVC_HOME, exist_ok=True); os.chdir(SEEDVC_HOME)   # seed_vc keeps its HF cache in ./checkpoints
        sys.path.insert(0, os.path.dirname(seed_vc.__file__))
        from seed_vc import inference as I
        self.I = I
        (self.model, self.semantic_fn, _, self.vocoder_fn, self.campplus, self.mel_fn, self.mel_args) = I.load_models(
            argparse.Namespace(f0_condition=False, checkpoint=None, config=None, fp16=False))
        self.sr = 22050

    def convert(self, src_wav, ref_wav, steps=30, cfg=0.7, length_adjust=1.0, ref_secs=25):
        import librosa, torch, torchaudio
        I, sr, hop = self.I, self.sr, 256
        dev = I.device
        src = torch.tensor(librosa.load(src_wav, sr=sr)[0]).unsqueeze(0).float().to(dev)
        ref = torch.tensor(librosa.load(ref_wav, sr=sr)[0][: sr * ref_secs]).unsqueeze(0).float().to(dev)
        with torch.no_grad():
            s16 = torchaudio.functional.resample(src, sr, 16000)
            chunks, buf, pos = [], None, 0          # whisper takes 30 s at a time; 5 s overlap between windows
            while pos < s16.size(-1):
                chunk = s16[:, pos:pos + 16000 * 30] if buf is None else torch.cat([buf, s16[:, pos:pos + 16000 * 25]], -1)
                S = self.semantic_fn(chunk)
                chunks.append(S if pos == 0 else S[:, 50 * 5:])
                buf = chunk[:, -16000 * 5:]
                pos += 16000 * 30 if pos == 0 else chunk.size(-1) - 16000 * 5
            S_alt = torch.cat(chunks, 1)
            r16 = torchaudio.functional.resample(ref, sr, 16000)
            S_ori = self.semantic_fn(r16)
            mel, mel2 = self.mel_fn(src.float()), self.mel_fn(ref.float())
            tl = torch.LongTensor([int(mel.size(2) * length_adjust)]).to(dev)
            t2 = torch.LongTensor([mel2.size(2)]).to(dev)
            feat2 = torchaudio.compliance.kaldi.fbank(r16, num_mel_bins=80, dither=0, sample_frequency=16000)
            style2 = self.campplus((feat2 - feat2.mean(0, keepdim=True)).unsqueeze(0))
            cond = self.model.length_regulator(S_alt, ylens=tl, n_quantizers=3, f0=None)[0]
            prompt = self.model.length_regulator(S_ori, ylens=t2, n_quantizers=3, f0=None)[0]
            win = sr // hop * 30 - mel2.size(2); ov = 16; ovw = ov * hop
            out, prev, done = [], None, 0
            while done < cond.size(1):
                cc = cond[:, done:done + win]; last = done + win >= cond.size(1)
                cat = torch.cat([prompt, cc], 1)
                tgt = self.model.cfm.inference(cat, torch.LongTensor([cat.size(1)]).to(dev), mel2, style2, None, steps,
                                               inference_cfg_rate=cfg)[:, :, mel2.size(-1):]
                wav = self.vocoder_fn(tgt.float()).squeeze()[None, :][0].cpu().numpy()
                if prev is None and last: out.append(wav); break
                if prev is None: out.append(wav[:-ovw])
                elif last: out.append(I.crossfade(prev, wav, ovw)); break
                else: out.append(I.crossfade(prev, wav[:-ovw], ovw))
                prev = wav[-ovw:]; done += tgt.size(2) - ov
        return np.concatenate(out).astype(np.float32)


def save(x, out, sr=22050, to_sr=48000):
    tmp = out + ".tmp.wav"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(x / (np.abs(x).max() + 1e-9) * 0.9, -1, 1) * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ar", str(to_sr), "-ac", "1", out], check=True)
    os.remove(tmp); return out


def default_ref():
    return os.path.join(ROOT, "assets", "prof-enzo-hangminta-22s.wav")   # first 22 s of the reel: clean speech, no music


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "variants":
        txt, ref, outd = [os.path.abspath(a) for a in sys.argv[2:5]]; os.makedirs(outd, exist_ok=True)
        text = open(txt, encoding="utf-8").read()
        vc = SeedVC()
        for ls, steps, cfg in [(1.0, 30, 0.5), (1.1, 30, 0.7), (1.1, 50, 0.7)]:
            base = piper(text, os.path.join(outd, f"piper_{ls}.wav"), ls)
            y = vc.convert(base, ref, steps=steps, cfg=cfg)
            print("wrote", save(y, os.path.join(outd, f"vc_ls{ls}_s{steps}_c{cfg}.wav"), to_sr=22050), flush=True)
    elif cmd == "make":   # make <video_dir> [<video_dir> ...] [--ref reference.wav]; models load once
        a = sys.argv[2:]
        ref = os.path.abspath(a[a.index("--ref") + 1]) if "--ref" in a else default_ref()
        dirs = [os.path.abspath(x) for i, x in enumerate(a) if x != "--ref" and (i == 0 or a[i - 1] != "--ref")]
        vc = SeedVC()
        for vd in dirs:
            tl = json.load(open(os.path.join(vd, "timeline.json"), encoding="utf-8"))
            b = os.path.join(vd, "build"); os.makedirs(b, exist_ok=True)
            base = piper(tts_text(tl["script"]), os.path.join(b, "piper.wav"), tl.get("length_scale", DEFAULT["length_scale"]))   # <1 = faster speech
            y = vc.convert(base, ref, steps=DEFAULT["steps"], cfg=DEFAULT["cfg"])
            print("wrote", save(y, os.path.join(b, "vo_raw.wav")), flush=True)
    else:
        raise SystemExit(__doc__)
