import { chromium } from 'playwright-core';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
for (const [w,h,n] of [[1440,900,'d'],[390,844,'m']]) {
  const p = await b.newPage({ viewport: { width: w, height: h } });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://localhost:4503/'); await p.waitForTimeout(2600);
  const board = await p.evaluate(()=>[...document.querySelectorAll('#board .cell span')].map(s=>s.textContent).join(''));
  await p.screenshot({ path: `lab/x-hero-${n}.png` });
  const go = async (id) => { await p.evaluate(i=>document.getElementById(i).scrollIntoView({block:'start',behavior:'instant'}), id); await p.waitForTimeout(500); };
  await go('probald');
  await p.click('[data-mode="social"]'); await p.waitForTimeout(600);
  const soc = await p.locator('#posts .post:not(.is-hidden)').count();
  await p.click('[data-mode="interest"]'); await p.waitForTimeout(600);
  const top = await p.locator('#posts .post:not(.is-hidden) .nm').first().innerText();
  await p.screenshot({ path: `lab/x-sim-${n}.png` });
  await go('rendszer'); await p.locator('#svclist button').nth(2).click(); await p.waitForTimeout(400);
  const rel = await p.locator('#svclist button.rel').count(); const svc = await p.locator('#svcpanel h3').innerText();
  await p.screenshot({ path: `lab/x-sys-${n}.png` });
  await go('eredmenyek'); await p.waitForTimeout(1500);
  const nums = await p.evaluate(()=>[...document.querySelectorAll('.wall [data-sc-count]')].map(e=>e.textContent).join(','));
  await p.locator('[data-case="2"]').click(); await p.waitForTimeout(400);
  const dlg = await p.evaluate(()=>document.getElementById('casedlg').open);
  await p.screenshot({ path: `lab/x-case-${n}.png` }); await p.keyboard.press('Escape');
  await go('teszt'); for (const k of [2,2,1,2,2]) { await p.locator('.opt').nth(k).click(); await p.waitForTimeout(100); }
  const score = await p.locator('.qres .score').innerText();
  await p.screenshot({ path: `lab/x-quiz-${n}.png` });
  await p.click('[data-carry]'); await p.waitForTimeout(900);
  const msg = await p.inputValue('#f-msg');
  await p.click('#appform button[type=submit]'); const err = await p.locator('#e-name').innerText();
  await p.evaluate(()=>document.querySelector('.voices').scrollIntoView()); await p.click('#vnext'); const vc = await p.locator('#vcount').innerText();
  let menu = 'n/a';
  if (n==='m') { await p.click('#menubtn'); menu = await p.evaluate(()=>!document.getElementById('sheet').hidden); await p.screenshot({ path: `lab/x-menu-m.png` }); await p.click('#sheet a[href="#teszt"]'); }
  await p.click('[data-set-lang="en"]'); await p.waitForTimeout(300);
  const untranslated = await p.evaluate(()=>[...document.querySelectorAll('h1,h2,h3,p,a,li,label,option,button,figcaption,span.desc,span.meta')].filter(e=>e.offsetParent!==null && /[őűéáíóú]/i.test(e.textContent) && !/Olivér|Péter|János|Hoofbútor|Tenerife|kati|szomsz|sarok|regi|kilincs|csarnok\.|ora\.|utazo/.test(e.textContent)).map(e=>e.textContent.trim().slice(0,40)).slice(0,10));
  const ov = await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  console.log(n, JSON.stringify({board, soc, top, rel, svc, nums, dlg, score, msg:msg.slice(0,40), err, vc, menu, untranslated, ov, errs}));
  await p.close();
}
await b.close();
