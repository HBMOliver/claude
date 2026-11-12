// H=<16:9 film> V=<vertical film> node ../socialstream-concepts/video/recut.mjs   (run from a folder with
// playwright-core, e.g. ../socialstream-split; needs ffmpeg and Google Chrome)
//
// Re-cuts the brand film's title card with the approved logo (direction G2). Both cuts of the client's film (25 fps,
// 750 frames, 30 s, silent) carry the old Fraunces "Social Stream" title baked into the reel mosaic, at the start and
// at the end. It cannot be lifted out, so a full-frame Night card with the logo kit's stacked dark lockup covers every
// frame where it shows, ghosts included (frames 0-89 and 670-749, the union of both cuts):
//   frames 0-89     the card, the lockup in place from the first frame (the poster's frame), pushing in 2.5 % and
//                   fading out by frame 86; the card dissolves into the claim's black over 90-93
//   frames 670-749  the card dissolves in over the claim's fade-out (670-675); the lockup fades in from 684 and
//                   holds to the last frame, so the loop (749 -> 0) is seamless
// The two cuts get the same frames, and the lockup is the same share of the frame's height in both (28.125 %), so on
// Aurora Mix the wide film can hand over to the upright cut mid-title with one logo on screen.
//
// Colour: the sources are tagged BT.601 (bt470bg), TV range. The card is composited in the film's own YUV, with the
// overlay converted by that matrix, and every output is tagged bt470bg like the source.
//
// Writes to OUT (default video/out, not committed):
//   hero-1080.mp4 hero-540.mp4 hero-v-720.mp4   the site's three cuts, two-pass at the old bitrates
//   hero-poster.jpg hero-v-poster.jpg           frame 0, the card with the logo
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
const FRAMES = 750;

// the timeline, frame by frame: card alpha, lockup opacity, lockup scale (null = no overlay on this frame)
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = t => t * t * (3 - 2 * t);
const outCubic = t => 1 - Math.pow(1 - t, 3);
const inOut = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
function state(f) {
  if (f <= 93) {
    const a = f <= 89 ? 1 : 1 - (f - 89) / 5;
    const o = 1 - smooth(clamp((f - 72) / 14));
    const s = 1 + 0.025 * inOut(clamp(f / 86));
    return [a, o, s];
  }
  if (f >= 670) {
    const a = f >= 675 ? 1 : (f - 669) / 6;
    const o = smooth(clamp((f - 684) / 18));
    const s = 0.975 + 0.025 * outCubic(clamp((f - 684) / 24));
    return [a, o, s];
  }
  return null;
}

const run = (cmd, args) => execFileSync(cmd, args, { stdio: ['ignore', 'ignore', 'inherit'] });
const ff = args => run('ffmpeg', ['-v', 'error', '-y', ...args]);
const TAGS = ['-colorspace', 'bt470bg', '-color_range', 'tv'];
const X264 = ['-c:v', 'libx264', '-preset', 'slow', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-g', '50', '-keyint_min', '25', '-an', ...TAGS];

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
  // frames without the card share one transparent picture
  await page.evaluate(() => window.set(0, 0, 1));
  const empty = await page.screenshot({ omitBackground: true });
  for (let f = 0; f < FRAMES; f++) {
    const st = state(f), file = path.join(dir, String(f).padStart(4, '0') + '.png');
    if (!st) { fs.writeFileSync(file, empty); continue; }
    await page.evaluate(([a, o, s]) => window.set(a, o, s), st);
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

  // composite in the film's own YUV: the overlay converted by the source's matrix (BT.601), TV range
  const inter = path.join(OUT, cut + '-inter.mp4');
  ff(['-i', SRC[cut], '-framerate', '25', '-i', path.join(dir, '%04d.png'), '-filter_complex',
    '[1:v]format=rgba,scale=out_color_matrix=bt601:out_range=tv,format=yuva444p[o];[0:v]format=yuv444p[m];[m][o]overlay=0:0:format=yuv444:eof_action=pass,format=yuv420p[v]',
    '-map', '[v]', '-frames:v', String(FRAMES), '-fps_mode', 'passthrough', ...X264, '-crf', '8', inter]);
  const n = +execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v', '-count_packets', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', inter]).toString().trim();
  if (n !== FRAMES) throw new Error(`${cut}: ${n} frames composited, not ${FRAMES}`);
  // the masters for the founder, full size
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
  console.log(out);
}
site(path.join(OUT, 'h-inter.mp4'), 'hero-1080.mp4', 2130);
site(path.join(OUT, 'h-inter.mp4'), 'hero-540.mp4', 1100, '960:540');
site(path.join(OUT, 'v-inter.mp4'), 'hero-v-720.mp4', 1520, '720:1280');

// the posters: frame 0, the card with the logo in place, straight from the rendered frame (exact sRGB colours)
ff(['-i', path.join(OUT, 'h-overlay', '0000.png'), '-vf', 'scale=1600:900:flags=lanczos', '-q:v', '2', path.join(OUT, 'hero-poster.jpg')]);
ff(['-i', path.join(OUT, 'v-overlay', '0000.png'), '-vf', 'scale=720:1280:flags=lanczos', '-q:v', '2', path.join(OUT, 'hero-v-poster.jpg')]);
console.log('done:', OUT);
