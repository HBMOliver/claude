// Shots and checks for socialstream-exhibit. Serve the build first (see README), then from a folder with
// playwright-core installed (e.g. ../socialstream-split): node ../socialstream-exhibit/lab/shots.mjs <outdir> <w> <h> [m]
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const [out, W, H, mob] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5] === 'm'];
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const ctx = await b.newContext(mob ? { viewport: { width: W, height: H }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } : { viewport: { width: W, height: H } });
await ctx.grantPermissions(['clipboard-read', 'clipboard-write']);
const p = await ctx.newPage(); const errs = []; const res = {};
p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
await p.goto('http://localhost:4542/', { waitUntil: 'load' }); await p.waitForTimeout(3000);
let i = 0; const shot = async () => p.screenshot({ path: `${out}/${String(i++).padStart(2, '0')}.png` });
const go = async (sel, wait = 1300, dy = 0) => { await p.evaluate(([s, dy]) => { document.querySelector(s).scrollIntoView({ behavior: 'instant' }); scrollBy(0, dy); }, [sel, dy]); await p.waitForTimeout(wait); };
const light = async (fx, fy) => { if (!mob) { await p.mouse.move(W * fx, H * fy, { steps: 6 }); await p.waitForTimeout(500); } };
await light(0.62, 0.38); await shot();
res.reelPlaying = await p.evaluate(() => { const v = document.getElementById('reel'); return [!!v.currentSrc, v.paused, v.currentSrc.split('/').pop()]; });
await go('#terem1', 1300); await light(0.3, 0.55); await shot();
await go('#terem1 .vitrines', 1100, -H * 0.15); await light(0.5, 0.5); await shot();
await go('#terem2', 1300); await light(0.7, 0.4); await shot();
await go('#terem2 .salon', 1600, -H * 0.1); await light(0.55, 0.5); await shot();
await go('#terem2 .salon .w4', 1300, -H * 0.2); await light(0.45, 0.5); await shot();
res.videoFramePlaying = await p.evaluate(() => { const v = document.querySelector('[data-video] video'); return [!!v.currentSrc, v.paused]; });
await go('#terem3', 1300); await light(0.5, 0.35); await shot();
await go('#terem3 .directory', 1100, -H * 0.1); await light(0.5, 0.5); await shot();
await go('#terem4', 1300); await light(0.4, 0.45); await shot();
await go('#terem4 .stills', 2000, -H * 0.05); await light(0.3, 0.6); await shot();
res.counts = await p.evaluate(() => [...document.querySelectorAll('[data-count]')].map(c => c.textContent).join(','));
await go('#terem5', 1300); await light(0.5, 0.5); await shot();
await go('#terem5 .portraits', 1300, -H * 0.1); await light(0.5, 0.5); await shot();
await go('#terem5 .founder', 1300, -H * 0.05); await light(0.4, 0.5); await shot();
await go('#vendegkonyv', 1300); await light(0.5, 0.5); await shot();
await go('#vendegkonyv .book', 1300, -H * 0.1); await light(0.5, 0.5); await shot();
await go('#penztar', 1300); await light(0.7, 0.5); await shot();
// the ticket: empty submit shows errors, then a full email
await go('#appform', 900, -H * 0.1);
await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(300);
res.err = await p.locator('#e-name').innerText();
await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'nem-email'); await p.fill('#f-brand', 'Teszt Kft');
await p.locator('#appform button[type=submit]').click(); await p.waitForTimeout(200);
res.errMail = await p.locator('#e-email').innerText();
await p.fill('#f-email', 'teszt@example.com'); await p.fill('#f-web', 'teszt.hu');
await p.selectOption('#f-budget', '1-3m'); await p.selectOption('#f-goal', 'leads');
await p.locator('#chips input[value="video"]').check({ force: true }); await p.locator('#chips input[value="ads"]').check({ force: true });
await p.fill('#f-msg', 'Szeretnénk több ajánlatkérést.');
await light(0.6, 0.5); await shot();
await p.locator('#appform button[type=submit]').click().catch(() => {}); await p.waitForTimeout(600);
res.sent = (await p.locator('#sent').innerText()).slice(0, 60);
if (!mob) { await p.locator('#copyBody').click(); await p.waitForTimeout(300); res.body = await p.evaluate(() => navigator.clipboard.readText()); }
await shot();
// lights on
await p.locator('#lights').click(); await p.waitForTimeout(1000); await go('#terem2 .salon', 1200, -H * 0.1); await shot();
await p.locator('#lights').click(); await p.waitForTimeout(300);
// english everywhere
await p.locator('[data-set-lang="en"]').click(); await p.waitForTimeout(400);
res.untranslated = await p.evaluate(() => [...document.querySelectorAll('h1,h2,h3,p,a,li,label,legend,option,button,span,figcaption,b,small,em')]
  .filter(e => e.children.length === 0 && /[őűáéíóú]/i.test(e.textContent) && !/Olivér|András|Gyenis|Hoofbútor|Péter|János|hello@|Teszt|Szeretnénk/.test(e.textContent))
  .map(e => e.textContent.trim().slice(0, 50)).slice(0, 15));
res.chipsEn = await p.locator('#chips .chip span').allInnerTexts();
res.chipsKept = await p.evaluate(() => [...document.querySelectorAll('#chips input:checked')].map(c => c.value).join(','));
await go('#terem4', 1200); await light(0.5, 0.5); await shot();
res.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
res.height = await p.evaluate(() => (document.documentElement.scrollHeight / innerHeight).toFixed(1));
res.errs = errs;
console.log(JSON.stringify(res, null, 1));
await b.close();
