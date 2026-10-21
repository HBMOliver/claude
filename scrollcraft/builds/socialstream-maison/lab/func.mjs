// Functional pass: film + lines, the thumb stop, the form and mailto body, language, phone.
// Run from a folder where playwright-core is installed (npm i): node lab/func.mjs
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL = process.env.URL || 'http://localhost:4520/';
const b = await chromium.launch({ executablePath: CH });
const out = {};
async function centre(p, sel) {
  await p.evaluate((sel) => { const r = document.querySelector(sel).getBoundingClientRect(); scrollTo({ top: r.top + scrollY + r.height / 2 - innerHeight / 2, behavior: 'instant' }); }, sel);
}
const beat = (p) => p.waitForSelector('.beat.is-on', { timeout: 26000 }).then((e) => e.innerText(), () => '(none)');
const film = (p) => p.evaluate(() => { const v = document.querySelector('video[data-film]'); return { src: v.currentSrc.split('/').pop(), playing: !v.paused }; });
// ---- desktop
{
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write']);
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
  await p.goto(URL); await p.waitForTimeout(3000);
  out.film = await film(p);
  out.beatOn = await beat(p);
  // the thumb stop: still while moving, the nearest card plays once scrolling stops
  await centre(p, '#reelRow'); await p.waitForTimeout(1200);
  out.live = await p.evaluate(() => { const c = document.querySelector('.card.is-live'); return c ? { src: c.querySelector('video').currentSrc.split('/').pop(), playing: !c.querySelector('video').paused } : null; });
  out.liveCount = await p.locator('.card.is-live').count();
  out.stopNow = await p.locator('#stopNow').innerText();
  out.filmPausedOffscreen = !(await film(p)).playing;
  await p.mouse.move(720, 450); await p.mouse.wheel(0, 140); await p.waitForTimeout(150);
  out.liveWhileMoving = await p.locator('.card.is-live').count();
  await p.waitForTimeout(900);
  out.liveAfterStop = await p.locator('.card.is-live').count();
  await p.locator('.card').nth(0).locator('.play').click(); await p.waitForTimeout(500);
  out.clickedLive = await p.evaluate(() => [...document.querySelectorAll('.card')].findIndex((c) => c.classList.contains('is-live')));
  // the form: validation, chips, the composed email
  await centre(p, '#appform'); await p.waitForTimeout(400);
  out.chips = await p.locator('#formChips .chip').count();
  await p.locator('#appform button[type=submit]').click();
  out.err = await p.locator('#e-name').innerText();
  await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'teszt@example.com'); await p.fill('#f-brand', 'Teszt Kft');
  await p.selectOption('#f-goal', 'leads');
  await p.locator('#formChips .chip').nth(2).click();
  await p.locator('#appform button[type=submit]').click().catch(() => {});
  await p.waitForTimeout(600);
  out.sent = (await p.locator('#sent').innerText()).slice(0, 60);
  await p.locator('#copyBody').click(); await p.waitForTimeout(300);
  out.body = await p.evaluate(() => navigator.clipboard.readText());
  // english
  await p.locator('[data-set-lang="en"]').first().click(); await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(800);
  out.beatEn = await beat(p);
  out.htmlLang = await p.evaluate(() => document.documentElement.lang);
  out.untranslated = await p.evaluate(() => [...document.querySelectorAll('h1,h2,h3,p,a,li,label,legend,option,button,span,figcaption,b')]
    .filter((e) => e.offsetParent !== null && e.children.length === 0 && /[őűáéíóú]/i.test(e.textContent) && !/Olivér|Péter|Hoofbútor|Lidi|Teszt|hello@/.test(e.textContent))
    .map((e) => e.textContent.trim().slice(0, 40)).slice(0, 12));
  out.overflowD = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  out.errsD = errs;
  await ctx.close();
}
// ---- phone
{
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto(URL); await p.waitForTimeout(3000);
  out.mFilm = await film(p);
  await centre(p, '#reelRow .card:nth-child(3)'); await p.waitForTimeout(1200);
  out.mLive = await p.locator('.card.is-live figcaption').allInnerTexts();
  out.overflowM = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  out.errsM = errs;
  await ctx.close();
}
console.log(JSON.stringify(out, null, 1));
await b.close();
