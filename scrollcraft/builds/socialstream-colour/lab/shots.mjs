// node lab/shots.mjs <outdir> <w> <h> [m] [positions]   (run from a folder with playwright-core)
// Walks the page by scroll position and screenshots each stop, then writes a contact sheet.
// positions: comma-separated viewport-heights from the top (default: a walk through every scene).
import { createRequire } from 'node:module';
import fs from 'node:fs';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [out, W, H, mob, posArg] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5] === 'm', process.argv[6]];
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const ctx = await b.newContext(mob ? { viewport: { width: W, height: H }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } : { viewport: { width: W, height: H } });
const p = await ctx.newPage(); const errs = [];
p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto((process.env.URL || 'http://localhost:4551/') + (process.env.Q || ''), { waitUntil: 'load' }); await p.waitForTimeout(2500);
const total = await p.evaluate(() => (document.documentElement.scrollHeight - innerHeight) / innerHeight);
const pos = posArg ? posArg.split(',').map(Number) : Array.from({ length: Math.ceil(total / 0.35) + 1 }, (_, i) => Math.min(total, i * 0.35));
const shots = [];
for (const v of pos) {
  await p.evaluate(v => scrollTo({ top: v * innerHeight, behavior: 'instant' }), v);
  await p.waitForTimeout(mob ? 700 : 900);
  const f = `${out}/${String(shots.length).padStart(2, '0')}-${v.toFixed(2)}.jpg`;
  await p.screenshot({ path: f, type: 'jpeg', quality: 62 }); shots.push([f, v]);
}
const res = await p.evaluate(() => ({ screens: +(document.documentElement.scrollHeight / innerHeight).toFixed(1), overflow: document.documentElement.scrollWidth - innerWidth, stream: !document.documentElement.classList.contains('no-stream'), keys: [...document.querySelectorAll('[data-k]')].map(k => k.dataset.k).join(' ') }));
res.errs = errs;
const tw = mob ? 190 : 340, th = Math.round(tw * H / W), cols = mob ? 7 : 4;
const html = `<body style="margin:0;background:#222;font:11px sans-serif;color:#ccc;display:grid;grid-template-columns:repeat(${cols},${tw}px);gap:8px;padding:8px">` +
  shots.map(([f, v]) => `<figure style="margin:0"><img src="data:image/jpeg;base64,${fs.readFileSync(f).toString('base64')}" style="width:${tw}px;height:${th}px;display:block"><figcaption>${v.toFixed(2)} vh</figcaption></figure>`).join('') + '</body>';
const sp = await (await b.newContext({ viewport: { width: cols * (tw + 8) + 8, height: 400 } })).newPage();
await sp.setContent(html); await sp.waitForTimeout(300);
await sp.screenshot({ path: `${out}/sheet.jpg`, type: 'jpeg', quality: 72, fullPage: true });
console.log(JSON.stringify(res));
await b.close();
