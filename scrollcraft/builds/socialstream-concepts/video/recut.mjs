// H=<16:9 film> V=<vertical film> node ../socialstream-concepts/video/recut.mjs   (run from a folder with
// playwright-core, e.g. ../socialstream-split; needs ffmpeg and Google Chrome)
//
// Re-cuts the brand film's title card with the approved logo (direction G2), over the film's own reel wall. Both cuts
// of the client's film (25 fps, 750 frames, 30 s, silent) carry the old Fraunces "Social Stream" title baked into the
// reel wall, at the start (source frames ~19-88) and at the end (~680-746). It cannot be lifted out, so a soft Night
// band through the middle of the frame covers it, with the logo kit's stacked dark lockup on the band, while the wall
// keeps playing above and below (titlecard.html). The new film is 798 frames (31.92 s), both cuts on the same frames:
//   new 0-137     the opening, 5.5 s (it was 3.6): the wall from the source's first frame (0-77), blending over 12
//                 frames into the wall of the source's ending (680-739), so the wall keeps moving at its own speed;
//                 the band and the lockup are there from the first frame (the poster's frame), the lockup pushing in
//                 3 % and fading out by 126, the card closing over the wall by 130
//   new 138-789   the source's 90-741, untouched (the card dissolves into the claim's black over 138-141)
//   new 718-797   the ending: the card dissolves in over the claim's fade-out, opens onto the band and the wall, the
//                 lockup fades in and holds; the last 8 frames blend the wall into the source's first frame, so the
//                 loop (797 -> 0) is seamless
// The band and the lockup are shares of the frame's height in both cuts, so on Aurora Mix the wide film can hand over
// to the upright cut with one band and one logo on screen. WALL_FIRST=<frames, at most 18> lets the wall play alone
// that long before the band and the lockup come in (the poster then comes from frame 60).
//
// Colour: the sources are tagged BT.601 (bt470bg), TV range. The overlay is composited in the film's own YUV,
// converted by that matrix, and every output is tagged bt470bg like the source.
//
// Writes to OUT (default video/out, not committed):
//   hero-1080.mp4 hero-540.mp4 hero-v-720.mp4   the site's three cuts, two-pass at the old bitrates
//   hero-poster.jpg hero-v-poster.jpg           the poster frame, from the composited film
//   socialstream-film-16x9.mp4 socialstream-film-9x16.mp4   full-size, high-quality masters
// Then copy the five site files into ../assets. DESC=1 adds "Interest media ügynökség" under the lockup (off by
// default: the kit defines no lockup with a line).
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(process.env.OUT || path.join(here, 'out'));
const SRC = { h: process.env.H, v: process.env.V };
for (const [k, f] of Object.entries(SRC)) if (!f || !fs.existsSync(f)) throw new Error(`set ${k.toUpperCase()}= to the ${k === 'h' ? '16:9' : 'vertical'} film`);
const SIZE = { h: [1920, 1080], v: [1080, 1920] };
const FRAMES = 798, SHIFT = 48; // the opening grows by 48 frames: source frame s (90-741) lands at s + 48
const WALL = Math.min(18, Math.max(0, +(process.env.WALL_FIRST || 0)));
const POSTER = WALL ? 60 : 0;

// the overlay, frame by frame: band opacity, card alpha, lockup opacity, lockup scale (null = no overlay)
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const outCubic = t => 1 - Math.pow(1 - clamp(t), 3);
const inOut = t => { t = clamp(t); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
function state(f) {
  if (f <= 141) {                                   // the opening
    const v = f >= 138 ? 0 : WALL ? smooth((f - (WALL - 10)) / 10) : 1;
    const a = f <= 117 ? 0 : f <= 137 ? smooth((f - 117) / 13) : 1 - (f - 137) / 5;
    const o = WALL ? smooth((f - WALL) / 16) * (1 - smooth((f - 110) / 16)) : 1 - smooth((f - 110) / 16);
    const s = 1 + 0.03 * inOut((f - WALL) / (126 - WALL));
    return [v, a, o, s];
  }
  if (f >= 718) {                                   // the ending
    const a = f <= 723 ? (f - 717) / 6 : 1 - smooth((f - 723) / 15);
    const o = smooth((f - 732) / 18);
    const s = 0.975 + 0.025 * outCubic((f - 732) / 24);
    return [1, a, o, s];
  }
  return null;
}

const run = (cmd, args) => execFileSync(cmd, args, { stdio: ['ignore', 'ignore', 'inherit'] });
const ff = args => run('ffmpeg', ['-v', 'error', '-y', ...args]);
const count = f => +execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v', '-count_packets', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', f]).toString().trim();
const TAGS = ['-colorspace', 'bt470bg', '-color_range', 'tv'];
const X264 = ['-c:v', 'libx264', '-preset', 'slow', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-g', '50', '-keyint_min', '25', '-an', ...TAGS];
// the wall's new timeline: source 0-89 blending into 680-739 (12 frames from new 78), the source's 90-741, then
// 742-748 blending into a hold of the source's first frame (pure from new 797)
const BG = [
  '[0:v]trim=start_frame=0:end_frame=90,setpts=PTS-STARTPTS[a]',
  '[0:v]trim=start_frame=680:end_frame=740,setpts=PTS-STARTPTS[b]',
  '[a][b]xfade=transition=fade:duration=0.48:offset=3.12[ab]',
  '[0:v]trim=start_frame=90:end_frame=742,setpts=PTS-STARTPTS[c]',
  '[0:v]trim=start_frame=742:end_frame=749,setpts=PTS-STARTPTS[d]',
  '[0:v]trim=start_frame=0:end_frame=1,setpts=PTS-STARTPTS,loop=loop=7:size=1:start=0,setpts=N/(25*TB)[f0]',
  '[d][f0]xfade=transition=fade:duration=0.28:offset=0[df]',
  '[ab][c][df]concat=n=3:v=1:a=0[bg]',
].join(';');

fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
for (const cut of ['h', 'v']) {
  const [w, h] = SIZE[cut], dir = path.join(OUT, cut + '-overlay');
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(here, 'titlecard.html')).href, { waitUntil: 'networkidle' });
  if (process.env.DESC === '1') {
    await page.addStyleTag({ url: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400&display=block' });
    await page.evaluate(() => document.documentElement.classList.add('desc'));
  }
  await page.evaluate(() => document.fonts.ready);
  if (!(await page.evaluate(() => document.getElementById('logo').naturalWidth))) throw new Error('the lockup did not load');
  await page.evaluate(() => window.set(0, 0, 0, 1));
  const empty = await page.screenshot({ omitBackground: true }); // frames without an overlay share it
  for (let f = 0; f < FRAMES; f++) {
    const st = state(f), file = path.join(dir, String(f).padStart(4, '0') + '.png');
    if (!st) { fs.writeFileSync(file, empty); continue; }
    await page.evaluate(([v, a, o, s]) => window.set(v, a, o, s), st);
    await page.screenshot({ path: file, omitBackground: true });
    // Chrome writes a fully opaque frame as an RGB PNG; ffmpeg rebuilds its filters when the sequence switches
    // between RGB and RGBA and drops a frame there, so every frame is kept RGBA (PNG colour type 6)
    if (fs.readFileSync(file)[25] !== 6) {
      ff(['-i', file, '-pix_fmt', 'rgba', file + '.rgba.png']);
      fs.renameSync(file + '.rgba.png', file);
    }
  }
  await page.close();
  console.log(cut, 'overlay frames written');

  // the wall's new timeline, then the overlay, in the film's own YUV (BT.601, TV range)
  const inter = path.join(OUT, cut + '-inter.mp4');
  ff(['-i', SRC[cut], '-framerate', '25', '-i', path.join(dir, '%04d.png'), '-filter_complex',
    BG + ';[1:v]format=rgba,scale=out_color_matrix=bt601:out_range=tv,format=yuva444p[o];[bg]format=yuv444p[m];[m][o]overlay=0:0:format=yuv444:eof_action=pass,format=yuv420p[v]',
    '-map', '[v]', '-frames:v', String(FRAMES), '-fps_mode', 'passthrough', ...X264, '-crf', '8', inter]);
  if (count(inter) !== FRAMES) throw new Error(`${cut}: ${count(inter)} frames composited, not ${FRAMES}`);
  ff(['-i', inter, ...X264, '-crf', '16', '-movflags', '+faststart', path.join(OUT, cut === 'h' ? 'socialstream-film-16x9.mp4' : 'socialstream-film-9x16.mp4')]);
  console.log(cut, 'composited');
}
await browser.close();

// the site's cuts, two-pass at the bitrates the old files had
function site(inter, out, kbps, scale) {
  const log = path.join(OUT, 'pass-' + path.basename(out, '.mp4'));
  const vf = scale ? ['-vf', `scale=${scale}:flags=lanczos`] : [];
  const rate = ['-b:v', kbps + 'k', '-maxrate', Math.round(kbps * 1.5) + 'k', '-bufsize', kbps * 2 + 'k'];
  ff(['-i', inter, ...vf, ...X264, ...rate, '-pass', '1', '-passlogfile', log, '-f', 'null', '-']);
  ff(['-i', inter, ...vf, ...X264, ...rate, '-pass', '2', '-passlogfile', log, '-movflags', '+faststart', path.join(OUT, out)]);
  for (const f of fs.readdirSync(OUT)) if (f.startsWith('pass-')) fs.rmSync(path.join(OUT, f));
  if (count(path.join(OUT, out)) !== FRAMES) throw new Error(out + ': wrong frame count');
  console.log(out);
}
site(path.join(OUT, 'h-inter.mp4'), 'hero-1080.mp4', 2130);
site(path.join(OUT, 'h-inter.mp4'), 'hero-540.mp4', 1100, '960:540');
site(path.join(OUT, 'v-inter.mp4'), 'hero-v-720.mp4', 1520, '720:1280');

// the posters: the poster frame of the composited film, TV-range BT.601 to a full-range JPEG
const poster = (inter, out, size) => ff(['-i', inter, '-vf', `select=eq(n\\,${POSTER}),scale=${size}:in_range=tv:out_range=pc:flags=lanczos`, '-frames:v', '1', '-pix_fmt', 'yuvj420p', '-q:v', '2', path.join(OUT, out)]);
poster(path.join(OUT, 'h-inter.mp4'), 'hero-poster.jpg', '1600:900');
poster(path.join(OUT, 'v-inter.mp4'), 'hero-v-poster.jpg', '720:1280');
console.log('done:', OUT, `(${FRAMES} frames, ${FRAMES / 25} s; source frame s >= 90 lands at s + ${SHIFT})`);
