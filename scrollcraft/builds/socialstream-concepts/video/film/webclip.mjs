// node webclip.mjs   (run from a folder with playwright-core, as the site's lab checks are; with the concepts served at
// http://localhost:4560/, see ../../README.md, Run)
// The "Weboldal" (website) reel: their own site, Aurora Mix, scrolled through its services on a phone (540 x 960 CSS
// px at 2x), 33 frames = 1.32 s at 25 fps, in Hungarian and in English. Writes assets/clips/ph-svc-web.mp4 and
// ph-svc-web-en.mp4 (1080 x 1920). Needs Google Chrome.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const BASE = process.env.BASE || 'http://localhost:4560/';
const N = 33, TRAVEL = 520;

const b = await chromium.launch({ channel: 'chrome', headless: true });
for (const lang of ['hu', 'en']) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'webclip-'));
  const p = await b.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await p.addInitScript((l) => { try { localStorage.setItem('ss-lang', l); } catch (e) {} }, lang);
  await p.goto(BASE + 'mix.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const y0 = await p.evaluate(() => document.querySelector('#szolgaltatasok').getBoundingClientRect().top + scrollY - 40);
  await p.evaluate((y) => scrollTo(0, y), y0);
  await p.waitForTimeout(1500);                       // the cards arrive
  for (let i = 0; i < N; i++) {                       // a flick: fast, then slowing
    const k = i / (N - 1), e = 1 - Math.pow(1 - k, 2.2);
    await p.evaluate((y) => scrollTo(0, y), y0 + TRAVEL * e);
    await p.waitForTimeout(40);
    await p.screenshot({ path: path.join(tmp, String(i).padStart(3, '0') + '.png') });
  }
  await p.close();
  const out = path.join(here, 'assets/clips', lang === 'en' ? 'ph-svc-web-en.mp4' : 'ph-svc-web.mp4');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '25', '-i', path.join(tmp, '%03d.png'), '-vf',
    'scale=1080:1920:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-movflags', '+faststart',
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', out]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(lang, out);
}
await b.close();
