# Cuts Aurora Mix's reel snippets: short silent loops (360x640 H.264) plus a poster (486x864 JPEG) per reel,
# with captions burned in where the words are real (speech heard in the clip, the film's own subtitles, the ad's
# own lines). Clips that already carry their captions (FlyX, András, Prof Enzo, Up To Youth, Miskolc Plaza) keep them.
# usage: python3 -I tools/reels.py assets [ids...]   (from socialstream-concepts; needs ffmpeg 7+ for text_align)
# The sources are the founder's own files on the founder's Mac, so the paths below only work there. FOOT is where the logo
# session exported the Türkiye, Latvia and Sóskút clips from Photos (a scratch folder: re-export from Photos if it is
# gone); ENZO holds Prof Enzo's TikToks 7664967202709294358 and 7662730135665315074 (yt-dlp, tiktok.com/@profenzohungary).
# The Latvia clips are Up To Youth's event videos (the founder, 2026-11-16: "make it look like its event videos not just
# talking about someone"), so they carry event titles at the top instead of the speakers' words. The Türkiye ones carry
# the film's own English subtitles, the Nike ones the spec ad's own end lines. The two smartwatch ads
# (found by the founder on 2026-11-16, cleared for the site) are a creator's video, captioned with the creator's own
# first words (transcribed the same way), and the V89 Valentine's ad, which keeps its own captions.
import os, subprocess, sys, tempfile

HOME = os.path.expanduser('~')
FOOT = '/private/tmp/claude-501/-Users-oliver-Library-Application-Support-Claude-scratch-workspaces-be1b34bf-46d7-457c-81d6-2aac65a38964-9a1f68e9-c364-444f-aa7e-edb8bc0aaa12-scratch-2026-10-20-f59575/fbe060e9-3cee-4055-b959-1d2793e78c59/scratchpad/footage/exports'
ENZO = os.environ.get('ENZO', HOME + '/Downloads/profenzo')
BAL = HOME + '/Downloads/Balint portfolio (YouTube)'
FILM = FOOT + '/turkiye/copy_FCE53987-21D8-4AF3-8984-32930C2FC7FE.mov'
ANDRAS = [HOME + '/Movies/CapCut/Andras posts/Gyenis Andras posztok/2026-11-13 19.00 – Jobb Ferrariban sírni.mp4', HOME + '/Movies/CapCut/Andras posts/Gyenis Andras posztok/2026-11-11 12.00 – Sikeresnek tűnik.mp4']
WATCH = [HOME + '/Downloads/19b0c63d-6504-42db-82f4-ea4c69db33a3.MP4', HOME + '/Downloads/V89_5.MOV']
FFMPEG = '/usr/local/bin/ffmpeg'
BLACK = '/System/Library/Fonts/Supplemental/Arial Black.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'

# id: (source, start s, length s, frame, poster at s into the snippet, captions [(from, to, text, style[, top as a share of the height])])
# frame: 'v' = already vertical; a number = centre of a 9:16 crop of a wide frame; (w, h, x, y) = a fixed crop first
R = {
    'r-uty':       (HOME + '/Downloads/copy_C6D41801-5C0E-404C-8A06-E036C9BCF8FE.MOV', 4.0, 4.0, 'v', 2.1, []),
    # Up To Youth's event in Latvia (June 2025, the Baltic coast at Bernāti): one title each, over the whole clip
    'r-lv-sunset': (FOOT + '/latvia/IMG_1758.MOV', 8.0, 3.5, 'v', 1.0, [(0.0, 3.5, 'SUNSET ON THE\nBALTIC COAST', 'reel', 0.06)]),
    'r-lv-yellow': (FOOT + '/latvia/IMG_1686.MOV', 1.0, 5.3, 'v', 0.8, [(0.0, 5.3, 'UP TO YOUTH\nIN LATVIA', 'reel', 0.06)]),
    'r-lv-hoodie': (FOOT + '/latvia/IMG_1692.MOV', 0.8, 2.7, 'v', 0.5, [(0.0, 2.7, 'MEET THE\nPARTICIPANTS', 'reel', 0.06)]),
    'r-lv-cap':    (FOOT + '/latvia/IMG_1790.MOV', 0.0, 4.0, 'v', 0.7, [(0.0, 4.0, 'WHAT HAPPENS\nAT UP TO YOUTH', 'reel', 0.06)]),
    'r-miskolc':   (BAL + '/05 Miskolc Plaza sakk promóció [h2ZJTq3HAO0].mp4', 0.0, 4.0, 'v', 2.69, []),
    'r-nike-1':    (BAL + '/02 Nike ad creative [zfiaI92RW4g].mp4', 22.5, 3.2, (480, 852, 720, 114), 1.8, [
        (0.0, 3.2, "NOBODY'S\nWATCHING.", 'ad')]),
    'r-nike-2':    (BAL + '/02 Nike ad creative [zfiaI92RW4g].mp4', 11.4, 2.5, (480, 852, 682, 114), 0.8, [
        (0.0, 2.5, 'DO IT\nANYWAY.', 'ad')]),
    'r-enzo-1':    (ENZO + '/7664967202709294358.mp4', 4.5, 4.0, 'v', 1.5, []),
    'r-enzo-2':    (ENZO + '/7662730135665315074.mp4', 14.0, 4.0, 'v', 2.0, []),  # food only: its B-roll has stock people elsewhere
    'r-soskut':    (FOOT + '/bridleup/IMG_2767.MOV', 11.0, 4.5, 'v', 4.0, []),
    'r-tr-smile':  (FILM, 214.6, 4.0, 0.55, 3.0, [
        (0.0, 1.9, 'Or is this the silence\nafter a collapse', 'sub'), (2.4, 4.0, 'Can you feel\nhow near it is', 'sub')]),
    'r-tr-friends': (FILM, 198.0, 3.6, (426, 756, 747, 60), 2.0, [(0.0, 3.6, 'How loud\nsilence can be', 'sub')]),  # the film's lead, between two friends; a closer crop
    'r-flyx-1':    (HOME + '/Downloads/ssstik.io_@flyx.tenerife_1792102133763.mp4', 0.3, 4.0, 'v', 0.5, []),
    'r-flyx-2':    (HOME + '/Movies/CapCut/FlyX Reels.mp4', 27.6, 2.6, 'v', 1.4, []),  # after the family shot, before the end card
    'r-flyx-3':    (HOME + '/Downloads/ssstik.io_@flyx.tenerife_1792102178013.mp4', 15.05, 2.2, 'v', 0.5, []),  # two couples in the seats
    'r-andras-1':  (ANDRAS[0], 1.5, 4.0, 'v', 1.0, []),
    'r-andras-2':  (ANDRAS[1], 5.3, 2.9, 'v', 0.5, []),  # András alone, after the guest's shot
    # the creator's opening line, set at the top like a hook title so the watch in the creator's hand stays clear
    'r-watch-1':   (WATCH[0], 0.0, 4.9, 'v', 3.5, [
        (0.0, 2.1, 'EZT MUSZÁJ\nMEGMUTATNOM', 'reel', 0.045), (2.1, 4.9, 'MERT KELLEMESEN\nMEGLEPETT', 'reel', 0.045)]),
    'r-watch-2':   (WATCH[1], 5.62, 2.1, 'v', 1.5, []),  # the watch going on, under the ad's own "EGY V89-ES OKOSÓRÁVAL"; ends before the webshop page
}

def frame(spec, w, h):
    if spec == 'v':
        return f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}'
    if isinstance(spec, tuple):
        cw, ch, x, y = spec
        return f'crop={cw}:{ch}:{x}:{y},scale={w}:{h}'
    return f"crop=w=trunc(ih*9/16/2)*2:h=ih:x='max(0,min(iw-ow,iw*{spec}-ow/2))':y=0,scale={w}:{h}"

def caption(tmp, i, a, b, text, style, w, at=None, top=None):
    p = os.path.join(tmp, f'c{i}.txt')
    open(p, 'w').write(text)
    if style == 'reel':
        look = f"fontfile='{BLACK}':fontsize={w * 0.078:.1f}:fontcolor=white:borderw={w * 0.009:.1f}:bordercolor=black:line_spacing={w * 0.01:.1f}"
    elif style == 'ad':
        look = f"fontfile='{BLACK}':fontsize={w * 0.09:.1f}:fontcolor=white:borderw={w * 0.006:.1f}:bordercolor=black@0.7:line_spacing={w * 0.008:.1f}"
    else:  # the film's own subtitles, set as captions in the vertical frame
        look = f"fontfile='{BOLD}':fontsize={w * 0.068:.1f}:fontcolor=white:shadowcolor=black@0.85:shadowx=1:shadowy=1:borderw={w * 0.004:.1f}:bordercolor=black@0.6:line_spacing={w * 0.012:.1f}"
    top = top if top is not None else {'reel': 0.56, 'ad': 0.58}.get(style, 0.78)
    on = '' if at is not None else f":enable='between(t,{a},{b})'"
    return f"drawtext=textfile='{p}':text_align=C:x=(w-text_w)/2:{look}:y=h*{top}{on}"

def build(rid, out):
    src, start, dur, spec, poster, caps = R[rid]
    with tempfile.TemporaryDirectory() as tmp:
        for (w, h, kind) in ((360, 640, 'mp4'), (486, 864, 'jpg')):
            chain = [frame(spec, w, h)]
            for i, c in enumerate(caps):
                a, b, text, style = c[:4]
                if kind == 'jpg' and not (a <= poster < b):
                    continue
                chain.append(caption(tmp, f'{kind}{i}', a, b, text, style, w, poster if kind == 'jpg' else None, c[4] if len(c) > 4 else None))
            if kind == 'mp4':
                chain.append('fps=30')
                cmd = [FFMPEG, '-v', 'error', '-y', '-ss', str(start), '-t', str(dur), '-i', src, '-vf', ','.join(chain),
                       '-an', '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '27', '-pix_fmt', 'yuv420p',
                       '-map_metadata', '-1', '-write_tmcd', '0',  # no source tags or the .MOV's timecode track
                       '-movflags', '+faststart', os.path.join(out, rid + '.mp4')]
            else:
                cmd = [FFMPEG, '-v', 'error', '-y', '-ss', str(start + poster), '-i', src, '-frames:v', '1', '-vf', ','.join(chain),
                       '-q:v', '4', os.path.join(out, rid + '.jpg')]
            subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)

if __name__ == '__main__':
    out = sys.argv[1]
    for rid in (sys.argv[2:] or list(R)):
        build(rid, out)
        print(rid, os.path.getsize(os.path.join(out, rid + '.mp4')), os.path.getsize(os.path.join(out, rid + '.jpg')))
