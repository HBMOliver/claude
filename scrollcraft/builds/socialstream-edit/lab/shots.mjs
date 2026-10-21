// node edit2-shots.mjs <outdir> <w> <h> [m]   (run from a folder with playwright-core)
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [out, W, H, mob] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5] === 'm'];
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const ctx = await b.newContext(mob ? { viewport: { width: W, height: H }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } : { viewport: { width: W, height: H } });
const p = await ctx.newPage(); const errs = []; const res = {};
p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto('http://localhost:4540/', { waitUntil: 'load' }); await p.waitForTimeout(2500);
let i = 0; const shot = async (name) => p.screenshot({ path: `${out}/${String(i++).padStart(2, '0')}${name ? '-' + name : ''}.png` });
const at = async (pp, wait = 900) => { await p.evaluate(pp => { const s = document.getElementById('suite'); scrollTo({ top: s.offsetTop + pp * (s.offsetHeight - innerHeight), behavior: 'instant' }); }, pp); await p.waitForTimeout(wait); };
const ch = (c, s) => 0.05 + 0.95 * ((c + s) / 9);
await shot('full');
await at(0.025, 700); await shot('docking');
await at(0.05, 900); await shot('docked');
res.film = await p.evaluate(() => { const v = document.getElementById('film'); return { src: v.currentSrc.split('/').pop(), paused: v.paused }; });
for (const [c, s, n] of [[1, 0.2, 'law1-count'], [1, 0.8, 'law1'], [2, 0.6, 'law2'], [3, 0.85, 'law3'], [4, 0.05, 'svc1'], [4, 0.75, 'svc5'], [5, 0.05, 'res1'], [5, 0.3, 'res2'], [6, 0.05, 'q1'], [7, 0.5, 'team'], [8, 0.8, 'export-card']]) { await at(ch(c, s), 1300); await shot(n); }
if (!mob) {
  const r = await p.locator('#tlBody').boundingBox();
  await p.mouse.move(r.x + r.width * 0.6, r.y + r.height * 0.6, { steps: 3 }); await p.waitForTimeout(400); await shot('preview');
  await p.mouse.move(r.x + r.width * 0.2, r.y + 40); await p.mouse.down(); await p.mouse.move(r.x + r.width * 0.42, r.y + 40, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(500);
  res.afterDrag = await p.evaluate(() => document.getElementById('chName').textContent);
}
await p.evaluate(() => document.getElementById('audit').scrollIntoView({ behavior: 'instant' })); await p.waitForTimeout(900); await shot('audit');
await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(300);
res.err = await p.locator('#e-name').innerText();
await p.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' })); await p.waitForTimeout(700); await shot('foot');
await p.locator('[data-set-lang="en"]').first().click(); await p.waitForTimeout(400); await at(ch(1, 0.8), 1100); await shot('en-law1');
res.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
res.vh = await p.evaluate(() => (document.documentElement.scrollHeight / innerHeight).toFixed(1));
res.errs = errs;
console.log(JSON.stringify(res));
await b.close();
