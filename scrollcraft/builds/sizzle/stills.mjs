import { createRequire } from 'module'; import fs from 'fs'; import path from 'path';
const require = createRequire(import.meta.url); const pw = require('playwright-core');
const ts = process.argv.slice(2).map(Number);
const m = JSON.parse(fs.readFileSync('manifest.json','utf8'));
const b = await pw.chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.addInitScript(x => { window.MANIFEST = x; }, m);
await p.goto('file://' + path.resolve('render.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
fs.mkdirSync('lab', { recursive: true });
for (const t of ts) { await p.evaluate(x => window.render(x), t); await p.screenshot({ path: `lab/t${t}.jpg`, type: 'jpeg', quality: 80 }); }
await b.close();
