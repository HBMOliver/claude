#!/usr/bin/env python3
"""B-roll from Mixkit (Mixkit Stock Video Free License: free for commercial and personal use, no attribution).
Only items whose page states the Free license are downloaded; anything under the Restricted license is refused.
Clips go to ../broll/ (not in git: the license does not allow redistributing the raw files).

usage:
  python3 broll.py search <words...> [--free]   list clips for a topic (--free: only Free-license ones)
  python3 broll.py get <id> [<id> ...]      check the license and download the 1080p (or 720p) file + a .json note
"""
import html, json, os, re, sys
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "broll")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
S = requests.Session(); S.headers.update(UA)


def search(query):
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")
    r = S.get(f"https://mixkit.co/free-stock-video/{slug}/", timeout=40)
    if r.status_code != 200: return []
    items = []
    for path in dict.fromkeys(re.findall(r'href="(/free-stock-video/([a-z0-9-]+)-(\d+)/)"', r.text)):
        url, name, vid = path
        items.append({"id": int(vid), "title": name.replace("-", " "), "page": "https://mixkit.co" + url})
    return items


def info(vid, page=None):
    """Read an item page: title, license, duration, available sizes."""
    if page is None:
        page = f"https://mixkit.co/free-stock-video/x-{vid}/"
    r = S.get(page, timeout=40, allow_redirects=True)
    r.raise_for_status()
    t = r.text
    lic = re.findall(r'data-license="(video[A-Za-z]+)"', t)
    title = html.unescape(re.search(r"<title>(.*?)</title>", t, re.S).group(1)).split("|")[0].strip() if "<title>" in t else ""
    dur = re.search(r"Duration\s*</[^>]+>\s*<[^>]+>\s*([0-9:]+)", t) or re.search(r"Duration\s+([0-9:]+)", re.sub(r"<[^>]+>", " ", t))
    files = {}   # size -> URL; older items: videos/<id>/<id>-<size>.mp4, newer: active_storage/video_items/<id>/<ts>/<id>-video-<size>.mp4
    for u, size in re.findall(rf"(https://assets\.mixkit\.co/videos/{vid}/{vid}-(\d+)\.mp4)", t): files[int(size)] = u
    for u, size in re.findall(rf"(https://assets\.mixkit\.co/active_storage/video_items/{vid}/\d+/{vid}-video-(\d+)\.mp4)", t): files[int(size)] = u
    return {"id": vid, "title": title, "page": r.url, "license": lic[0] if lic else None,
            "restricted": "videoRestricted" in lic, "duration": dur.group(1) if dur else None, "sizes": sorted(files), "files": files}


def get(vid):
    os.makedirs(DIR, exist_ok=True)
    out = os.path.join(DIR, f"{vid}.mp4")
    if os.path.exists(out): return out
    i = info(vid)
    if i["restricted"] or i["license"] != "videoFree":
        raise SystemExit(f"{vid}: not under the Mixkit Stock Video Free License ({i['license']}) - skipped")
    cands = [f"https://assets.mixkit.co/videos/{vid}/{vid}-{size}.mp4" for size in (1080, 720, 2160)]
    known = i["files"]; up = [(sz, u) for sz, u in known.items()]
    for sz, u in sorted(up, key=lambda x: (x[0] != 1080, x[0] != 720, -x[0])):   # listed files first, 1080p preferred
        cands.insert(0, u.replace(f"-video-{sz}.mp4", "-video-1080.mp4")) if "-video-" in u and sz != 1080 else None
        cands.insert(1, u)
    for url in dict.fromkeys(cands):
        size = int(re.search(r"-(\d+)\.mp4$", url).group(1))
        r = S.get(url, stream=True, timeout=120)
        if r.status_code == 200:
            with open(out + ".part", "wb") as f:
                for chunk in r.iter_content(1 << 20): f.write(chunk)
            os.replace(out + ".part", out)
            json.dump({**i, "file": url, "license_name": "Mixkit Stock Video Free License"}, open(out[:-4] + ".json", "w"), indent=1)
            print(f"{vid}: {size}p  {os.path.getsize(out) / 1e6:.1f} MB  {i['title']}")
            return out
    raise SystemExit(f"{vid}: no downloadable file found")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "search":   # --free: open each result and keep only Free-license clips (commercial use allowed)
        free = "--free" in args; words = [a for a in args if a != "--free"]
        for it in search(" ".join(words))[:int(os.environ.get("BROLL_MAX", "14"))]:
            if free:
                i = info(it["id"], it["page"])
                if i["license"] != "videoFree" or i["restricted"]: continue
                print(f"{it['id']:>7}  {i['duration'] or '?':>5}  {it['title']}", flush=True)
            else:
                print(f"{it['id']:>7}  {it['title']}")
    elif cmd == "info":
        for a in args: print(json.dumps(info(int(a)), ensure_ascii=False))
    elif cmd == "get":
        for a in args:
            try: get(int(a))
            except SystemExit as e: print(e)
    else:
        raise SystemExit(__doc__)
