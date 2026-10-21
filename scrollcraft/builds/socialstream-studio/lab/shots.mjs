// Section shots for every version, with the pointer placed so the light, lens and tilt respond.
// node lab/shots.mjs <outdir> [width height]   (run from a folder with playwright-core installed)
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const out = process.argv[2], W = +process.argv[3] || 1440, H = +process.argv[4] || 900;
const URL = process.env.URL || 'http://localhost:4530/';
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const ctx = await b.newContext(process.env.MOBILE ? { viewport: { width: W, height: H }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } : { viewport: { width: W, height: H }, deviceScaleFactor: 1 });
const p = await ctx.newPage();
const errs = [];
p.on('pageerror', (e) => errs.push(e.message));
p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
await p.goto(URL, { waitUntil: 'load' });
const at = async (id, f) => {
  await p.evaluate(([id, f]) => { const s = document.getElementById(id); const pin = s.classList.contains('sc-act--pinned');
    scrollTo({ top: s.offsetTop + (pin ? f * (s.offsetHeight - innerHeight) : f * s.offsetHeight - innerHeight * 0.1), behavior: 'instant' }); }, [id, f]);
};
const glide = async (x0, y0, x1, y1) => { for (let i = 0; i <= 12; i++) { await p.mouse.move(x0 + (x1 - x0) * i / 12, y0 + (y1 - y0) * i / 12); await p.waitForTimeout(30); } };
let n = 0;
const shot = async (tag) => p.screenshot({ path: `${out}/${String(n++).padStart(2, '0')}-${tag}.png` });
for (const v of ['oxblood', 'cream', 'black', 'dusk']) {
  await p.locator(`.ver button[data-v="${v}"]`).click();
  if (v === 'oxblood') { await p.evaluate(() => scrollTo(0, 0)); await p.mouse.move(W * 0.7, H * 0.4); await p.waitForTimeout(3600); await shot(v + '-reel'); }
  await at('hero', 0.25); await glide(W * 0.2, H * 0.7, W * 0.62, H * 0.3); await p.waitForTimeout(1100); await shot(v + '-hero');
  await at('lencse', 0.32); await p.waitForTimeout(400);
  const fb = await p.locator('#feedbox').boundingBox();
  await glide(fb.x + fb.width * 0.15, fb.y + fb.height * 0.5, fb.x + fb.width * 0.38, fb.y + fb.height * 0.45); await p.waitForTimeout(900); await shot(v + '-lens');
  if (v === 'oxblood') { await at('rendszer', 0.3); await p.mouse.move(W * 0.5, H * 0.5); await p.waitForTimeout(800); await shot(v + '-tk-mid'); }
  await at('rendszer', 0.95); await p.waitForTimeout(800); await shot(v + '-tk-end');
  if (v === 'oxblood') { await at('szamok', 0.25); await p.waitForTimeout(1800); await shot(v + '-nums'); await at('audit', 0.3); await p.waitForTimeout(900); await shot(v + '-close'); }
}
const info = await p.evaluate(() => ({ docVh: (document.documentElement.scrollHeight / innerHeight).toFixed(1), overflow: document.documentElement.scrollWidth - innerWidth,
  gl: !!document.getElementById('mat').getContext('webgl'), reel: document.getElementById('reel').currentSrc.split('/').pop() }));
console.log(JSON.stringify({ info, errs }, null, 1));
await b.close();
