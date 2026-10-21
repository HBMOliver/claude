// Screenshots chosen moments of a renderer. usage: [PAGE=render-vertical.html W=1080 H=1920] node stills.mjs 1.6 5.2 ...
import { createRequire } from 'module'; import fs from 'fs'; import path from 'path';
const require = createRequire(import.meta.url); const pw = require('playwright-core');
const ts = process.argv.slice(2).map(Number);
const page = process.env.PAGE || 'render.html', W = +(process.env.W || 1920), H = +(process.env.H || 1080), tag = process.env.TAG || '';
const m = JSON.parse(fs.readFileSync('manifest.json','utf8'));
const b = await pw.chromium.launch({ executablePath: process.env.SCROLLCRAFT_CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: W, height: H } });
await p.addInitScript(x => { window.MANIFEST = x; }, m);
await p.goto('file://' + path.resolve(page)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
fs.mkdirSync('lab', { recursive: true });
for (const t of ts) { await p.evaluate(x => window.render(x), t); await p.screenshot({ path: `lab/${tag}t${t}.jpg`, type: 'jpeg', quality: 80 }); }
await b.close();
