// Functional pass: versions by hash, EN everywhere, the drag rail, the form and its email, phone.
// node lab/func.mjs   (run from a folder with playwright-core installed)
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const URL = process.env.URL || 'http://localhost:4530/';
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const out = {};
// ---- desktop
{
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write']);
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
  await p.goto(URL + '#dusk', { waitUntil: 'load' }); await p.waitForTimeout(800);
  out.hashVersion = await p.evaluate(() => [document.documentElement.getAttribute('data-v'), document.getElementById('szolgaltatasok').getAttribute('data-tone')]);
  await p.locator('.ver button[data-v="oxblood"]').click();
  out.tonesOxblood = await p.evaluate(() => [...document.querySelectorAll('main > section.sec')].map((s) => s.id + ':' + s.getAttribute('data-tone')).join(' '));
  // the rail drags
  await p.evaluate(() => document.getElementById('velemenyek').scrollIntoView({ block: 'center', behavior: 'instant' })); await p.waitForTimeout(400);
  const rb = await p.locator('#qrail').boundingBox();
  const before = await p.evaluate(() => document.getElementById('qrail').scrollLeft);
  await p.mouse.move(rb.x + rb.width * 0.7, rb.y + rb.height / 2); await p.mouse.down();
  for (let i = 1; i <= 10; i++) { await p.mouse.move(rb.x + rb.width * (0.7 - i * 0.04), rb.y + rb.height / 2); await p.waitForTimeout(20); }
  out.discLabel = await p.locator('#discLabel').innerText();
  await p.mouse.up(); await p.waitForTimeout(700);
  out.railMoved = (await p.evaluate(() => document.getElementById('qrail').scrollLeft)) - before;
  await p.locator('[data-q="1"]').click(); await p.waitForTimeout(700);
  out.railAfterNext = await p.evaluate(() => document.getElementById('qrail').scrollLeft);
  // the form: validation, then a full email
  await p.evaluate(() => document.getElementById('audit').scrollIntoView({ behavior: 'instant' })); await p.waitForTimeout(400);
  out.sentHidden = await p.locator('#sent').isHidden();
  await p.locator('#appform button[type=submit]').click();
  out.err = await p.locator('#e-name').innerText();
  await p.fill('#f-name', 'Teszt Elek'); await p.fill('#f-email', 'nem-email'); await p.fill('#f-brand', 'Teszt Kft');
  await p.locator('#appform button[type=submit]').click();
  out.errMail = await p.locator('#e-email').innerText();
  await p.fill('#f-email', 'teszt@example.com');
  await p.selectOption('#f-budget', '1-3m'); await p.selectOption('#f-goal', 'leads');
  await p.locator('#formChips input[value="video"]').check({ force: true }); await p.locator('#formChips input[value="ads"]').check({ force: true });
  await p.fill('#f-msg', 'Szeretnénk több ajánlatkérést.');
  await p.locator('#appform button[type=submit]').click().catch(() => {});
  await p.waitForTimeout(500);
  out.sent = (await p.locator('#sent').innerText()).slice(0, 70);
  await p.locator('#copyBody').click(); await p.waitForTimeout(300);
  out.body = await p.evaluate(() => navigator.clipboard.readText());
  await p.locator('#copyMail').click(); await p.waitForTimeout(300);
  out.copyMail = [await p.locator('#copyMail').innerText(), await p.evaluate(() => navigator.clipboard.readText())];
  // english, everywhere
  await p.locator('[data-set-lang="en"]').first().click(); await p.waitForTimeout(400);
  out.untranslated = await p.evaluate(() => [...document.querySelectorAll('h1,h2,h3,p,a,li,label,legend,option,button,span,figcaption,b,small')]
    .filter((e) => e.children.length === 0 && /[őűáéíóú]/i.test(e.textContent) && !/Olivér|András|Gyenis|Hoofbútor|Péter|János|hello@|Változat|Teszt|Szeretnénk/.test(e.textContent))
    .map((e) => e.textContent.trim().slice(0, 50)).slice(0, 15));
  out.chipsEn = await p.locator('#formChips .chip span').allInnerTexts();
  out.l1en = await p.evaluate(() => { const s = document.getElementById('torveny'); scrollTo({ top: s.offsetTop + 0.8 * (s.offsetHeight - innerHeight), behavior: 'instant' }); return new Promise((r) => setTimeout(() => r(document.getElementById('l1n').textContent), 700)); });
  out.overflowD = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  out.errsD = errs;
  await ctx.close();
}
// ---- phone
{
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto(URL, { waitUntil: 'load' }); await p.waitForTimeout(2500);
  out.mReel = await p.evaluate(() => document.getElementById('reel').currentSrc.split('/').pop());
  out.mNavHidden = await p.locator('.bar .links').isHidden();
  out.overflowM = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  out.errsM = errs;
  await ctx.close();
}
console.log(JSON.stringify(out, null, 1));
await b.close();
