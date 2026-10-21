// Shots and checks for socialstream-edit. Serve the build first (see README), then from a folder with
// playwright-core installed (e.g. ../socialstream-split): node ../socialstream-edit/lab/shots.mjs <outdir> <w> <h> [m]
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [out, W, H, mob] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5] === 'm'];
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const ctx = await b.newContext(mob ? { viewport: { width: W, height: H }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } : { viewport: { width: W, height: H } });
const p = await ctx.newPage(); const errs = [];
p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto('http://localhost:4540/', { waitUntil: 'load' }); await p.waitForTimeout(3500);
let i = 0;
for (const f of [0.03, 0.17, 0.5, 0.63, 0.75, 0.97]) {
  await p.evaluate(f => { const s = document.getElementById('suite'); scrollTo({ top: s.offsetTop + f * (s.offsetHeight - innerHeight), behavior: 'instant' }); }, f);
  await p.waitForTimeout(900);
  if (!mob && i === 2) { const r = await p.locator('#tlBody').boundingBox(); await p.mouse.move(r.x + r.width * 0.08, r.y + 50); await p.waitForTimeout(400); }
  await p.screenshot({ path: `${out}/${String(i++).padStart(2, '0')}.png` });
}
await p.evaluate(() => document.getElementById('audit').scrollIntoView({ behavior: 'instant' })); await p.waitForTimeout(900);
await p.screenshot({ path: `${out}/${String(i++).padStart(2, '0')}.png` });
console.log(JSON.stringify({ errs, overflow: await p.evaluate(() => document.documentElement.scrollWidth - innerWidth), vh: await p.evaluate(() => (document.documentElement.scrollHeight / innerHeight).toFixed(1)) }));
await b.close();
