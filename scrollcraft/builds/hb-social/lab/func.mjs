import { chromium } from 'playwright-core';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
for (const vp of [{width:1440,height:900},{width:390,height:844}]) {
  const p = await b.newPage({ viewport: vp });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('http://localhost:4500/'); await p.waitForTimeout(800);
  const h1hu = await p.locator('h1').innerText();
  await p.click('[data-set-lang="en"]');
  const h1en = await p.locator('h1').innerText();
  const lang = await p.evaluate(()=>document.documentElement.lang+' | '+document.title);
  const mail = await p.getAttribute('.close .ask a','href');
  await p.locator('#atelier summary').first().click();
  const open = await p.locator('#atelier details').first().getAttribute('open');
  const overflow = await p.evaluate(()=>document.documentElement.scrollWidth - innerWidth);
  await p.reload(); await p.waitForTimeout(300);
  const persisted = await p.evaluate(()=>document.documentElement.lang);
  console.log(vp.width, {h1hu, h1en, lang, mail, open, overflow, persisted, errs});
  await p.close();
}
await b.close();
