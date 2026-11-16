#!/usr/bin/env python3
"""Cuts everything the sizzle (draft 4) plays into assets/ (not in git): the wall's reels and tiles, the phones'
and cards' clips, the full-frame shot, the polaroids, and the music and effects.

All of it is the team's own or their clients' published work: FlyX Tenerife's reels and promo, Prof Enzo's reels,
Gyenis András's podcast reel, the Latvia content challenge, Up To Youth, Miskolc Plaza, Bridle Up Hope in Sóskút,
Bálint's showreel. Left out on purpose: the Nike and RYZE spec ads, the Prof Enzo reel with a film clip and a
fast-food sign, shots with a child in the foreground.

usage: python3 -I clips.py <photos-exports-folder> <prof-enzo-folder>
  <photos-exports-folder>: the founder's Photos originals in latvia/, turkiye/ and bridleup/
  <prof-enzo-folder>: Prof Enzo's five published reels (as the site session downloaded them)
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
PH, EZ = sys.argv[1], sys.argv[2]
C = HOME + "/Movies/CapCut"
BAL = HOME + "/Downloads/Balint portfolio (YouTube)"
V6 = os.path.normpath(os.path.join(HERE, "../film-v6/assets"))
FF = "/usr/local/bin/ffmpeg"
BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
OUT = ["-an", "-c:v", "libx264", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]
GREY = "hue=s=0,eq=brightness=-0.07:contrast=0.88"

S = {  # sources
    "rain": C + "/Rainy day.mp4", "calima": C + "/Calima.mp4", "ad1": C + "/Flyx AD 1.mp4", "ad2": C + "/Flyx AD 2.mp4",
    "reels": C + "/FlyX Reels.mp4", "melodie": C + "/Melodie FlyX.mp4", "buddies": C + "/Buddies.mp4",
    "costa": C + "/Costa Adeje.mp4", "szolg": C + "/Szolgálat.mp4",
    "car": C + "/Andras posts/Gyenis Andras posztok/2026-11-13 19.00 – Jobb Ferrariban sírni.mp4",
    "ez1": EZ + "/7662730135665315074.mp4", "ez2": EZ + "/7664967202709294358.mp4",
    "ez3": EZ + "/7663105318838177046.mp4", "ez4": EZ + "/7680539169742933270.mp4",
    "lv_yellow": PH + "/latvia/IMG_1686.MOV", "lv_cap": PH + "/latvia/IMG_1790.MOV", "lv_hood": PH + "/latvia/IMG_1692.MOV",
    "lv_sun": PH + "/latvia/IMG_1737.MOV", "horse": PH + "/bridleup/IMG_2767.MOV",
    "uty": HOME + "/Downloads/copy_C6D41801-5C0E-404C-8A06-E036C9BCF8FE.MOV",
    "misk": BAL + "/05 Miskolc Plaza sakk promóció [h2ZJTq3HAO0].mp4",
}
# captions for the Latvia clips: the words spoken in them (the site session's transcript), as (from, to, text)
CAPS = {
    "lv_yellow": (1.0, [(0.0, 1.46, "ROKAS IS A\nGREAT FRIEND"), (1.46, 4.18, "AND I THINK\nHIS PROJECT"), (4.18, 5.3, "WILL BE REALLY\nSUCCESSFUL")]),
    "lv_cap": (0.0, [(0.0, 1.46, "FRIENDLY AND\nALWAYS"), (1.46, 4.0, "ASK HOW\nI'M DOING")]),
    "lv_hood": (0.8, [(0.0, 1.12, "FIRST THING\nTHAT COMES"), (1.12, 2.7, "TO YOUR MIND\nABOUT ROKAS")]),
}


def run(args):
    subprocess.run([FF, "-v", "error", "-y"] + args, check=True)


def chain(key, start, w, h, tmp):
    """Cover-crop to w x h, with the clip's spoken captions burned in when it has them."""
    c = [f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={w}:{h}"]
    if key in CAPS:
        base, caps = CAPS[key]
        for i, (a, b, text) in enumerate(caps):
            a2, b2 = a + base - start, b + base - start            # in the cut's own time
            if b2 <= 0:
                continue
            p = os.path.join(tmp, f"{key}-{w}-{i}.txt")
            open(p, "w").write(text)
            c.append(f"drawtext=textfile='{p}':text_align=C:x=(w-text_w)/2:fontfile='{BLACK}':fontsize={w * 0.078:.1f}:"
                     f"fontcolor=white:borderw={w * 0.009:.1f}:bordercolor=black:line_spacing={w * 0.01:.1f}:y=h*0.56:"
                     f"enable='between(t,{max(0, a2):.2f},{b2:.2f})'")
    return c


SPEED = {"fx1b": 0.78}     # the sunset shot is 1.7 s long and its phone shows it for 2 s: slowed a little


def clip(name, key, start, dur, w, h, crf, tmp, sub="clips", pad=0.0):
    c = chain(key, start, w, h, tmp)
    sp = SPEED.get(name, 1.0)
    if sp != 1.0:
        c.insert(0, f"setpts=PTS/{sp}")
    if pad:
        c.append(f"tpad=stop_mode=clone:stop_duration={pad}")
    c += ["fps=25", "format=yuv420p"]
    out = os.path.join(HERE, "assets", sub, name + ".mp4")
    run(["-ss", str(start), "-t", str(dur), "-i", S[key], "-vf", ",".join(c), "-t", f"{dur / sp + pad:.2f}"] + OUT + ["-crf", str(crf), out])
    return out


def still(name, src, at, w, h, sub, vf_pre=""):
    out = os.path.join(HERE, "assets", sub, name + ".jpg")
    run(["-ss", str(at), "-i", src, "-frames:v", "1", "-vf",
         f"{vf_pre}scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}", "-q:v", "3", out])
    return out


def grey(path):
    run(["-i", path, "-vf", GREY, "-q:v", "4", path[:-4] + "-g.jpg"])


def main():
    for d in ("clips", "wall", "pol", "audio"):
        os.makedirs(os.path.join(HERE, "assets", d), exist_ok=True)
    tmp = tempfile.mkdtemp()

    # ---- the wall: 14 reels that play (360 x 640, 8.0 s), each with the frame it freezes on (frame 182 = 7.28 s,
    # where the film says "meghalt.") ----
    LIVE = [("w01", "rain", 2.4), ("w02", "ad1", 8.0), ("w03", "calima", 11.5), ("w04", "ez1", 1.5), ("w05", "ez2", 4.0),
            ("w06", "ez3", 5.0), ("w07", "lv_yellow", 1.0), ("w08", "lv_hood", 0.8), ("w09", "uty", 2.0), ("w10", "misk", 0.0),
            ("w11", "horse", 7.2), ("w12", "szolg", 1.0), ("w13", "melodie", 56.0), ("w14", "ez4", 5.5)]
    for name, key, start in LIVE:
        out = clip(name, key, start, 8.0, 360, 640, 23, tmp, sub="wall")
        f = os.path.join(HERE, "assets", "wall", name + ".jpg")
        run(["-i", out, "-vf", r"select=eq(n\,182)", "-frames:v", "1", "-q:v", "3", f])
        grey(f)
    # ---- the wall: reels and shots that stand still ----
    STILLS = [("s01", S["buddies"], 8.0), ("s02", S["costa"], 5.0), ("s03", S["ad2"], 10.0), ("s04", S["reels"], 14.5),
              ("s05", S["ez4"], 7.0), ("s06", S["ez2"], 13.0), ("s07", S["lv_cap"], 1.0), ("s08", S["car"], 2.5)]
    for name, src, at in STILLS:
        grey(still(name, src, at, 360, 640, "wall"))
    for k, t in enumerate(["t05", "t07", "t09", "t10", "t12", "t13", "t14", "t15", "t16", "t18", "t19", "t22", "t23", "t24",
                           "t25", "t27", "t28", "t01", "t04"]):
        f = os.path.join(HERE, "assets", "wall", f"s{k + 9:02d}.jpg")
        run(["-i", os.path.join(V6, "tiles", t + ".jpg"), "-vf", "scale=360:640:force_original_aspect_ratio=increase,crop=360:640", "-q:v", "3", f])
        grey(f)
    # the full-frame shot of the turn: the FlyX cinema from behind, heads against the bright screen (their promo, 4K);
    # and the wall's middle card: a card-sized window on that shot's middle, where it opens from
    turn = os.path.join(HERE, "assets", "clips", "w-turn.mp4")
    run(["-ss", "25.24", "-t", "3.4", "-i", HOME + "/Downloads/DMC Promo video.mp4", "-vf", "scale=1920:1080:flags=lanczos,fps=25,format=yuv420p"]
        + OUT + ["-crf", "18", turn])
    grey(still("mid", turn, 0.0, 360, 640, "wall", vf_pre="crop=300:533:765:273,"))

    # ---- the phones and cards (720 x 1280) ----
    P = [("fx1a", "rain", 2.4, 3.0), ("fx1b", "ad1", 8.02, 1.66), ("fx2a", "reels", 5.2, 3.0), ("fx2b", "calima", 13.2, 3.0),
         ("fx3a", "melodie", 57.0, 3.0), ("fx3b", "ad2", 16.2, 3.0),
         ("ez1a", "ez1", 2.5, 3.0), ("ez1b", "ez1", 11.0, 3.0), ("ez2a", "ez2", 3.0, 3.0), ("ez2b", "ez2", 12.0, 3.0),
         ("ez3a", "ez3", 6.0, 3.0), ("ez3b", "ez3", 21.0, 3.0),
         ("pr1", "lv_yellow", 1.0, 3.2), ("pr2", "uty", 4.0, 3.2), ("pr3", "szolg", 2.0, 3.2), ("pr4", "misk", 0.5, 3.2),
         ("pr5", "horse", 11.0, 3.2), ("pr6", "lv_cap", 0.0, 3.2)]
    for name, key, start, dur in P:
        clip(name, key, start, dur, 720, 1280, 20, tmp)

    # ---- polaroids: the team at work (stills from Bálint's showreel and the Latvia shoot) ----
    for k, t in enumerate(["t14", "t22", "t16", "t10", "t23", "t27", "t24", "t17", "t15", "t09"]):
        run(["-i", os.path.join(V6, "tiles", t + ".jpg"), "-vf", "scale=400:500:force_original_aspect_ratio=increase,crop=400:500", "-q:v", "3",
             os.path.join(HERE, "assets", "pol", f"p{k + 1:02d}.jpg")])

    # ---- the music and the effects (Mixkit, free licence; in their CapCut folder) ----
    A = C + "/top tenerife assets"
    for dst, src in [("what-about-action", "music/What About Action - Mixkit"), ("whoosh-deep", "sfx/impact_whoosh_deep_1143"),
                     ("wind-woosh", "sfx/wind_woosh_1168"), ("pop-bubble", "sfx/pop_bubble_2357"), ("pop-soap", "sfx/pop_soap_bubble_2925"),
                     ("shutter", "sfx/camera_shutter_digital_1432"), ("rumble-bass", "sfx/rumble_bass_2297"),
                     ("impact-cine", "sfx/impact_big_cine_788"), ("coins", "sfx/coins_clinking_1993"), ("cheer", "sfx/cheer_huge_crowd_462")]:
        shutil.copy(f"{A}/{src}.mp3", os.path.join(HERE, "assets", "audio", dst + ".mp3"))
    shutil.rmtree(tmp)
    print("done:", len(os.listdir(os.path.join(HERE, "assets", "wall"))), "wall files,", len(os.listdir(os.path.join(HERE, "assets", "clips"))), "clips")


if __name__ == "__main__":
    main()
