// Functional pass: cover film + lines, contents rail, saves -> tray -> reply card, language, phone.
// Run from a folder where playwright-core is installed (npm i): node lab/func.mjs
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL = process.env.URL || 'http://localhost:4521/';
const b = await chromium.launch({ executablePath: CH });
const out = {};
async function centre(p, sel) {
  await p.evaluate((sel) => { const r = document.querySelector(sel).getBoundingClientRect(); scrollTo({ top: r.top + scrollY + r.height / 2 - innerHeight / 2, behavior: 'instant' }); }, sel);
  await p.waitForTimeout(350);
}
const beat = (p) => p.waitForSelector('.beat.is-on', { timeout: 26000 }).then((e) => e.innerText(), () => '(none)');
const film = (p) => p.evaluate(() => { const v = document.querySelector('video[data-film]'); return { src: v.currentSrc.split('/').pop(), playing: !v.paused }; });
const checked = (p) => p.$$eval('#formChips input:checked', (a) => a.map((x) => x.value));
async function save(p, id) { await centre(p, `[data-save="${id}"]`); await p.locator(`[data-save="${id}"]`).click(); }
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
  out.trayHiddenAtStart = await p.locator('#tray').isHidden();
  await centre(p, '#eredmenyek');
  out.railCurrent = await p.locator('#toc a[aria-current="true"]').innerText();
  // three saves from three chapters
  await save(p, 'law2'); await save(p, 'svc-ads'); await save(p, 'r-105');
  out.trayN = await p.locator('#trayN').innerText();
  out.trayVisible = await p.locator('#tray').isVisible();
  out.savedLabel = await p.locator('[data-save="law2"] span').innerText();
  out.chipsAfterSaves = await checked(p);
  out.carryNote = await p.locator('#carryNote').innerText();
  // a topic ticked by hand in the form survives a language switch and an un-save
  await centre(p, '#formChips');
  await p.locator('#formChips input[value="web"]').check({ force: true });
  await p.locator('[data-set-lang="en"]').first().click(); await p.waitForTimeout(400);
  out.chipsAfterEn = await checked(p);
  out.carryNoteEn = await p.locator('#carryNote').innerText();
  out.saveLabelEn = await p.locator('[data-save="law2"] span').innerText();
  await p.locator('#trayBtn').click();
  out.trayItems = await p.locator('#trayList li span').allInnerTexts();
  await p.locator('#trayList [data-rm="svc-ads"]').click();
  out.chipsAfterRemove = await checked(p);
  await p.locator('#trayCarry').click(); await p.waitForTimeout(900);
  out.panelClosed = await p.locator('#trayPanel').isHidden();
  out.atAudit = await p.evaluate(() => Math.abs(document.getElementById('audit').getBoundingClientRect().top) < innerHeight);
  // submit: validation, then the composed email carries the saved titles
  await p.locator('[data-set-lang="hu"]').first().click(); await p.waitForTimeout(300);
  await p.locator('#appform button[type=submit]').click();
  out.err = await p.locator('#e-name').innerText();
  await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'teszt@example.com'); await p.fill('#f-brand', 'Teszt Kft');
  await p.locator('#appform button[type=submit]').click().catch(() => {});
  await p.waitForTimeout(600);
  await p.locator('#copyBody').click(); await p.waitForTimeout(300);
  out.body = await p.evaluate(() => navigator.clipboard.readText());
  // saves outlive a reload in the same tab
  await p.reload(); await p.waitForTimeout(1500);
  out.trayNAfterReload = await p.locator('#trayN').innerText();
  out.chipsAfterReload = await checked(p);
  // english sweep
  await p.locator('[data-set-lang="en"]').first().click(); await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(800);
  out.beatEn = await beat(p);
  out.untranslated = await p.evaluate(() => [...document.querySelectorAll('h1,h2,h3,p,a,li,label,legend,option,button,span,figcaption,b')]
    .filter((e) => e.offsetParent !== null && e.children.length === 0 && /[őűáéíóú]/i.test(e.textContent) && !/Olivér|Péter|Hoofbútor|Lidi|János|Teszt|hello@/.test(e.textContent))
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
  out.mRailHidden = await p.locator('.rail').isHidden();
  out.mTopbar = await p.locator('.topbar').isVisible();
  await save(p, 'svc-video');
  out.mTrayN = await p.locator('#trayN').innerText();
  out.overflowM = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  out.errsM = errs;
  await ctx.close();
}
console.log(JSON.stringify(out, null, 1));
await b.close();
