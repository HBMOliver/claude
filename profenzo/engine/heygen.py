#!/usr/bin/env python3
"""HeyGen API client for Prof Enzo: find his avatar and voice in the HeyGen account, have HeyGen speak each video's
narration on a green screen, download the clip and hand it to avatar.py (key, captions on the real speech, final mix).

The API key is never stored in this repository or passed on the command line: save it in the Claude environment's
Network secrets (host api.heygen.com, header X-Api-Key); the proxy adds it to every request.
The chosen avatar and voice go to ../videok/heygen.json (not in git).

usage:
  python3 heygen.py check                         access test + remaining quota
  python3 heygen.py list                          avatars, photo avatars and voices -> ../videok/heygen_inventory.json
  python3 heygen.py use <character> <voice_id>    save the choice; character = talking_photo:<id> | avatar:<id>
  python3 heygen.py voice-match <reference.wav>   rank Hungarian/custom voices by similarity to Enzo's reference voice
  python3 heygen.py generate <video_dir>          start the green-screen clip for one video (build/heygen_job.json)
  python3 heygen.py wait <video_dir>              poll that job, download build/heygen.mp4
  python3 heygen.py batch [--final] [NN ...]      every (or the listed) NN-* video: generate, wait, download, + avatar.py final
"""
import glob, json, os, re, subprocess, sys, time
import requests

ENGINE = os.path.dirname(os.path.abspath(__file__))
VIDEOK = os.path.join(os.path.dirname(ENGINE), "videok")
SETTINGS, INVENTORY = os.path.join(VIDEOK, "heygen.json"), os.path.join(VIDEOK, "heygen_inventory.json")
API = "https://api.heygen.com"
S = requests.Session()
S.headers.update({"X-Api-Key": os.environ.get("HEYGEN_API_KEY", "set-by-proxy"), "Accept": "application/json"})
GREEN = "#00FF00"


def call(method, path, **kw):
    try:
        r = S.request(method, API + path, timeout=90, **kw)
    except requests.exceptions.ProxyError as e:
        raise SystemExit("api.heygen.com is not reachable: the HeyGen key is not in the environment's Network secrets yet "
                         f"(host api.heygen.com, header X-Api-Key). ({e.__class__.__name__})")
    try:
        j = r.json()
    except ValueError:
        raise SystemExit(f"{method} {path}: HTTP {r.status_code} {r.text[:300]}")
    if r.status_code >= 400 or j.get("error"):
        raise SystemExit(f"{method} {path}: HTTP {r.status_code} {json.dumps(j, ensure_ascii=False)[:800]}")
    return j.get("data", j)


def settings():
    if not os.path.exists(SETTINGS): raise SystemExit("no avatar/voice chosen yet: run `heygen.py list`, then `heygen.py use <character> <voice_id>`")
    return json.load(open(SETTINGS))


def tts_text(script):
    """Narration as HeyGen should say it: the web address spelled the way it is pronounced."""
    return re.sub(r"profenzo\.com-?", "profenzo pont kom", script)   # profenzo.com-ra -> profenzo pont komra


# ----------------------------------------------------------------------------- account
def check():
    print(json.dumps(call("GET", "/v2/user/remaining_quota"), ensure_ascii=False, indent=1))


def list_all():
    inv = {"avatars": call("GET", "/v2/avatars")}
    try:
        groups = call("GET", "/v2/avatar_group.list", params={"include_public": "false"})
        inv["groups"] = groups
        inv["group_looks"] = {}
        for g in groups.get("avatar_group_list", []):
            try: inv["group_looks"][g["id"]] = call("GET", f"/v2/avatar_group/{g['id']}/avatars")
            except SystemExit as e: inv["group_looks"][g["id"]] = {"error": str(e)}
    except SystemExit as e:
        inv["groups_error"] = str(e)
    inv["voices"] = call("GET", "/v2/voices")
    json.dump(inv, open(INVENTORY, "w"), ensure_ascii=False, indent=1)
    av = inv["avatars"]
    print(f"avatars: {len(av.get('avatars', []))}, photo avatars: {len(av.get('talking_photos', []))}, "
          f"groups: {len((inv.get('groups') or {}).get('avatar_group_list', []))}, voices: {len(inv['voices'].get('voices', []))}")
    print("\nPossible Enzo characters:")
    for a in av.get("talking_photos", []):
        print(f"  talking_photo:{a.get('talking_photo_id')}  {a.get('talking_photo_name')}")
    for a in av.get("avatars", []):
        if "enzo" in json.dumps(a).lower() or a.get("type") == "custom": print(f"  avatar:{a.get('avatar_id')}  {a.get('avatar_name')}")
    for gid, looks in inv.get("group_looks", {}).items():
        for l in looks.get("avatar_list", []) if isinstance(looks, dict) else []:
            print(f"  group {gid}: look {l.get('id')}  {l.get('name')}  (type {l.get('avatar_type') or l.get('type')})")
    print("\nHungarian and custom voices:")
    for v in hu_or_custom(inv["voices"].get("voices", [])):
        print(f"  {v.get('voice_id')}  {v.get('name')}  [{v.get('language')}, {v.get('gender')}]")


def hu_or_custom(voices):
    return [v for v in voices if re.search(r"hungar|magyar|\bhu\b", json.dumps(v, ensure_ascii=False).lower())
            or "enzo" in (v.get("name") or "").lower() or v.get("type") in ("custom", "cloned") or v.get("is_custom")]


def use(character, voice):
    if not re.match(r"^(talking_photo|avatar):\S+$", character): raise SystemExit("character must be talking_photo:<id> or avatar:<id>")
    s = {"character": character, "voice": voice, "avatar_iv": True, "speed": 1.0}
    if os.path.exists(SETTINGS): s = {**json.load(open(SETTINGS)), "character": character, "voice": voice}
    json.dump(s, open(SETTINGS, "w"), indent=1); print("saved", SETTINGS, s)


def voice_match(ref, top=12):
    """Speaker similarity (WeSpeaker ResNet34) between Enzo's reference audio and each candidate voice preview."""
    import numpy as np, sherpa_onnx
    from huggingface_hub import hf_hub_download
    model = hf_hub_download("csukuangfj/speaker-embedding-models", "wespeaker_en_voxceleb_resnet34.onnx")
    ext = sherpa_onnx.SpeakerEmbeddingExtractor(sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=model, num_threads=4))
    def emb(path):
        x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                         capture_output=True, check=True).stdout, dtype=np.float32)
        out = []
        for i in range(0, max(1, len(x) - 96000), 192000):
            st = ext.create_stream(); st.accept_waveform(16000, x[i:i + 192000]); st.input_finished()
            e = np.array(ext.compute(st)); out.append(e / np.linalg.norm(e))
        m = np.mean(out, 0); return m / np.linalg.norm(m)
    r = emb(ref)
    inv = json.load(open(INVENTORY))
    cache = os.path.join(VIDEOK, "_voice_previews"); os.makedirs(cache, exist_ok=True)
    scores = []
    for v in hu_or_custom(inv["voices"].get("voices", [])):
        url = v.get("preview_audio")
        if not url: continue
        p = os.path.join(cache, re.sub(r"\W", "_", v["voice_id"]) + os.path.splitext(url.split("?")[0])[1])
        if not os.path.exists(p):
            try:
                resp = S.get(url, timeout=60); resp.raise_for_status(); open(p, "wb").write(resp.content)
            except requests.exceptions.RequestException as e:
                print(f"  preview not reachable for {v.get('name')}: {e.__class__.__name__} ({url.split('/')[2]})"); continue
        scores.append((float(r @ emb(p)), v))
    for s, v in sorted(scores, key=lambda x: -x[0])[:top]:
        print(f"  {s:.3f}  {v['voice_id']}  {v.get('name')}  [{v.get('language')}, {v.get('gender')}]")


# ----------------------------------------------------------------------------- videos
def generate(vd):
    s = settings()
    tl = json.load(open(os.path.join(vd, "timeline.json"), encoding="utf-8"))
    kind, cid = s["character"].split(":", 1)
    ch = {"type": "avatar", "avatar_id": cid, "avatar_style": "normal"} if kind == "avatar" else {"type": "talking_photo", "talking_photo_id": cid}
    if kind == "talking_photo" and s.get("avatar_iv"): ch["use_avatar_iv_model"] = True
    body = {"title": ("Prof Enzo – " + tl["title"])[:100], "dimension": {"width": 1080, "height": 1920},
            "video_inputs": [{"character": ch,
                              "voice": {"type": "text", "input_text": tts_text(tl["script"]), "voice_id": s["voice"], "speed": s.get("speed", 1.0)},
                              "background": {"type": "color", "value": GREEN}}]}
    d = call("POST", "/v2/video/generate", json=body)
    os.makedirs(os.path.join(vd, "build"), exist_ok=True)
    json.dump({"video_id": d["video_id"], "started": time.time(), "request": body},
              open(os.path.join(vd, "build", "heygen_job.json"), "w"), ensure_ascii=False, indent=1)
    print(os.path.basename(vd), "-> HeyGen video", d["video_id"])
    return d["video_id"]


def wait(vd, poll=20, timeout=3 * 3600):
    job = json.load(open(os.path.join(vd, "build", "heygen_job.json")))
    t0 = time.time()
    while True:
        d = call("GET", "/v1/video_status.get", params={"video_id": job["video_id"]})
        st = d.get("status")
        if st == "completed": break
        if st == "failed": raise SystemExit(f"{os.path.basename(vd)}: HeyGen render failed: {json.dumps(d.get('error'), ensure_ascii=False)}")
        if time.time() - t0 > timeout: raise SystemExit(f"{os.path.basename(vd)}: still {st} after {timeout}s")
        time.sleep(poll)
    out = os.path.join(vd, "build", "heygen.mp4")
    try:
        with S.get(d["video_url"], stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(out + ".part", "wb") as f:
                for chunk in r.iter_content(1 << 20): f.write(chunk)
    except requests.exceptions.ProxyError:
        raise SystemExit(f"download host not allowed yet: {d['video_url'].split('/')[2]} (add it to the environment's allowed hosts)")
    os.replace(out + ".part", out)
    print(os.path.basename(vd), "->", out, f"({d.get('duration')}s)")
    return out


def batch(names, final=False):
    dirs = sorted(d for d in glob.glob(os.path.join(VIDEOK, "[0-9][0-9]-*")) if os.path.isdir(d))
    if names: dirs = [d for d in dirs if os.path.basename(d)[:2] in names]
    for d in dirs:   # HeyGen renders in parallel, so start them all first
        if not os.path.exists(os.path.join(d, "build", "heygen.mp4")) and not os.path.exists(os.path.join(d, "build", "heygen_job.json")):
            generate(d)
    for d in dirs:
        if not os.path.exists(os.path.join(d, "build", "heygen.mp4")): wait(d)
    if final:
        sys.path.insert(0, ENGINE); import avatar
        for d in dirs:
            if not os.path.exists(os.path.join(d, "build", "vegleges.mp4")):
                avatar.final(d, os.path.join(d, "build", "heygen.mp4"))


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == "check": check()
    elif cmd == "list": list_all()
    elif cmd == "use": use(a[0], a[1])
    elif cmd == "voice-match": voice_match(os.path.abspath(a[0]))
    elif cmd == "generate": generate(os.path.abspath(a[0]))
    elif cmd == "wait": wait(os.path.abspath(a[0]))
    elif cmd == "batch": batch([x for x in a if x != "--final"], "--final" in a)
    else: raise SystemExit(__doc__)
