// Shots and checks for socialstream-feed. Serve the build first (see README), then from a folder with
// playwright-core installed (e.g. ../socialstream-split): node ../socialstream-feed/lab/shots.mjs <outdir> <w> <h> [m]
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [out, W, H, mob] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5] === 'm'];
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const ctx = await b.newContext(mob ? { viewport: { width: W, height: H }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } : { viewport: { width: W, height: H } });
const p = await ctx.newPage(); const errs = [];
p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto('http://localhost:4541/', { waitUntil: 'load' }); await p.waitForTimeout(3200);
let i = 0; const shot = async () => p.screenshot({ path: `${out}/${String(i++).padStart(2, '0')}.png` });
const go = async (id, wait = 1500) => { await p.evaluate(id => document.getElementById(id).scrollIntoView({ behavior: 'instant' }), id); await p.waitForTimeout(wait); };
await shot();
await go('p2', 3200); await shot();
await go('p3', 2000); await shot();
await go('p5', 1500); await shot();
await p.evaluate(() => { const c = document.querySelector('#p5 .car'); c.scrollTo({ left: c.clientWidth * 2, behavior: 'instant' }); }); await p.waitForTimeout(800); await shot();
await go('p6', 1200); await shot();
await go('p7', 1000); await shot();
await go('p8', 900); await p.locator('[data-story="1"]').click(); await p.waitForTimeout(900); await shot();
await p.locator('#storyClose').click();
await go('p9', 800); await p.locator('.opt[data-ans="yes"]').click(); await p.waitForTimeout(500); await shot();
await go('p10', 2200); await p.fill('#reply', 'Teszt Elek'); await p.press('#reply', 'Enter'); await p.waitForTimeout(1500); await shot();
console.log(JSON.stringify({ errs, overflow: await p.evaluate(() => document.documentElement.scrollWidth - innerWidth) }));
await b.close();
