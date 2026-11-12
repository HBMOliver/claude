// node ../socialstream-concepts/tools/og.mjs   (run from a folder with playwright-core, e.g. ../socialstream-split)
// Renders tools/og.html, the share image for socialstream.hu (the logo, the claim and three of their reels on Aurora
// Mix's night blue), to assets/og-image.jpg at 1200 x 630. tools/site.mjs links it as the page's og:image.
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const here = path.dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await p.goto(pathToFileURL(path.join(here, 'og.html')).href, { waitUntil: 'networkidle' });
await p.evaluate(() => document.fonts.ready);
const missing = await p.evaluate(() => [...document.images].filter(i => !i.naturalWidth).map(i => i.src));
if (missing.length) throw new Error('images did not load: ' + missing.join(', '));
const out = path.join(here, '..', 'assets', 'og-image.jpg');
await p.screenshot({ path: out, type: 'jpeg', quality: 88 });
await b.close();
console.log('wrote', out);
