// Functional pass: dwell -> peak -> form carry -> submit; language; follow; phone reveal.
import { chromium } from 'playwright-core';
const CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const URL = process.env.URL || 'http://localhost:4510/';
const b = await chromium.launch({ executablePath: CH });
const out = {};
async function scrollToAct(p, id, f) {
  await p.evaluate(([id, f]) => { const s = document.getElementById(id); const pin = s.classList.contains('sc-act--pinned');
    const y = s.getBoundingClientRect().top + scrollY + f * (pin ? s.offsetHeight - innerHeight : s.offsetHeight * 0.5);
    scrollTo({ top: y, behavior: 'instant' }); }, [id, f]);
  await p.waitForTimeout(450);
}
// ---- desktop
{
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
  await p.goto(URL); await p.waitForTimeout(1500);
  // read the services: open ads + video, linger
  await scrollToAct(p, 'szolgaltatasok', 0.55);
  await p.locator('.svc[data-svc="ads"] button').click(); await p.waitForTimeout(300);
  await p.locator('.svc[data-svc="video"] button').click();
  for (let i = 0; i < 12; i++) { await p.mouse.move(700 + i, 400); await p.waitForTimeout(500); }
  out.svcOpen = await p.locator('.svc.is-open').count();
  out.panelText = (await p.locator('.svc[data-svc="ads"] .panel p').first().innerText()).slice(0, 40);
  await scrollToAct(p, 'eredmenyek', 0.6);
  for (let i = 0; i < 6; i++) { await p.mouse.move(600 + i, 300); await p.waitForTimeout(500); }
  out.dwell = await p.evaluate(() => JSON.parse(sessionStorage.getItem('ss-dwell')));
  // the peak, fully revealed
  await scrollToAct(p, 'erdeklodes', 0.95); await p.waitForTimeout(500);
  out.peakL2 = await p.locator('#pkL2').innerText();
  out.cards = await p.locator('#feed .card .lbl').allInnerTexts();
  out.secs = await p.locator('#feed .card .secs').allInnerTexts();
  out.pressed = await p.locator('#pkChips [aria-pressed="true"]').allInnerTexts();
  await p.screenshot({ path: 'lab/f-peak-d.png' });
  await p.locator('#pkChips [data-t="web"]').click();
  out.pressedAfter = await p.locator('#pkChips [aria-pressed="true"]').allInnerTexts();
  await p.locator('#follow').click(); out.follow = await p.locator('#followNote').innerText();
  await p.locator('#carry').click(); await p.waitForTimeout(900);
  out.formChecked = await p.$$eval('#formChips input:checked', a => a.map(x => x.value));
  out.carryNote = await p.locator('#carryNote').innerText();
  // submit empty, then filled
  await p.locator('#appform button[type=submit]').click();
  out.err = await p.locator('#e-name').innerText();
  await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'teszt@example.com'); await p.fill('#f-brand', 'Teszt Kft');
  await p.selectOption('#f-goal', 'leads');
  let mailto = '';
  p.on('framenavigated', () => {}); 
  await p.evaluate(() => { window.__nav = []; const d = Object.getOwnPropertyDescriptor(Location.prototype, 'href'); });
  await p.locator('#appform button[type=submit]').click().catch(() => {});
  await p.waitForTimeout(600);
  out.sent = (await p.locator('#sent').innerText().catch(() => 'ERR')).slice(0, 120);
  await p.screenshot({ path: 'lab/f-form-d.png' });
  // keyboard: focus a peak chip from below and check it is visible
  await scrollToAct(p, 'rolunk', 0.2);
  await p.focus('#pkChips .chip'); await p.waitForTimeout(400);
  out.focusOpacity = await p.evaluate(() => getComputedStyle(document.getElementById('pkAdjust')).opacity);
  // english
  await p.locator('[data-set-lang="en"]').click(); await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(700);
  out.h1en = await p.locator('#hero-h').innerText();
  out.markEn = await p.locator('#mkOld').innerText() + ' | ' + await p.locator('#mkNew').innerText();
  out.untranslated = await p.evaluate(() => [...document.querySelectorAll('h1,h2,h3,p,a,li,label,legend,option,button,span')].filter(e => e.offsetParent !== null && e.children.length === 0 && /[őűáéíóú]/i.test(e.textContent) && !/Olivér|Péter|Hoofbútor|Rita|kedvel|követ|Fájdalommal|Gyászol|lájk/.test(e.textContent)).map(e => e.textContent.trim().slice(0, 40)).slice(0, 12));
  await p.screenshot({ path: 'lab/f-hero-en.png' });
  out.overflowD = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  out.errsD = errs;
  await ctx.close();
}
// ---- phone
{
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(URL); await p.waitForTimeout(1500);
  out.bands = await p.locator('.band .track').count();
  await scrollToAct(p, 'szolgaltatasok', 0.6);
  await p.locator('.svc[data-svc="social"] button').click();
  for (let i = 0; i < 10; i++) { await p.evaluate(() => scrollBy(0, 1)); await p.waitForTimeout(500); }
  await scrollToAct(p, 'erdeklodes', 0.3); await p.waitForTimeout(1500);
  out.mCards = await p.locator('#feed .card .lbl').allInnerTexts();
  out.mL2 = await p.locator('#pkL2').innerText();
  await p.screenshot({ path: 'lab/f-peak-m.png' });
  out.overflowM = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  out.video = await p.evaluate(() => document.getElementById('herovid').currentSrc.split('/').pop());
  out.errsM = errs;
  await ctx.close();
}
console.log(JSON.stringify(out, null, 1));
await b.close();
