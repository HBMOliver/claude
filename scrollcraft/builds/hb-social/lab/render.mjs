import { chromium } from 'playwright-core';
import fs from 'fs';
const [,, seed, out] = process.argv;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: 2400, height: 1500 } });
await p.setContent(fs.readFileSync('lab/satin.html','utf8').replace('SEED', seed));
await p.screenshot({ path: out, type: 'png' });
await b.close();
