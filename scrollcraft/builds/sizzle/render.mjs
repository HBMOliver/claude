// Renders render.html frame by frame to out/NNNNN.jpg.
// usage: node render.mjs <dir> [fromSec] [toSec] [width] [height] [chromePath]
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright-core'); } catch { pw = require('playwright'); }
const [, , dir = '.', from = '0', to = '30', W = '1920', H = '1080', chrome] = process.argv;
const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'manifest.json'), 'utf8'));
const out = path.join(dir, 'out'); fs.mkdirSync(out, { recursive: true });
const browser = await pw.chromium.launch(chrome ? { executablePath: chrome } : {});
const page = await browser.newPage({ viewport: { width: +W, height: +H } });
await page.addInitScript(m => { window.MANIFEST = m; }, manifest);
await page.goto('file://' + path.resolve(dir, 'render.html'));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(800);
const fps = 25, a = Math.round(+from * fps), b = Math.round(+to * fps);
const t0 = Date.now();
for (let f = a; f < b; f++) {
  await page.evaluate(t => window.render(t), f / fps);
  await page.screenshot({ path: path.join(out, String(f).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 90 });
  if (f % 50 === 0) console.log('frame', f, ((Date.now() - t0) / 1000).toFixed(1) + 's');
}
await browser.close();
console.log('done', b - a, 'frames');
