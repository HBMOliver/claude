import { chromium } from 'playwright-core';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
for (const vp of [{width:1440,height:900},{width:390,height:844}]) {
  const p = await b.newPage({ viewport: vp });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://localhost:4501/'); await p.waitForTimeout(600);
  const hu = await p.locator('h1').innerText();
  await p.click('[data-set-lang="en"]');
  const en = await p.locator('h1').innerText();
  const untranslated = await p.evaluate(()=>[...document.querySelectorAll('h2,h3,p,a,figcaption,blockquote p')].filter(e=>/[őűáéíóú]/i.test(e.textContent) && !/Olivér|Péter|János|Hoofbútor|Rita/.test(e.textContent)).map(e=>e.textContent.trim().slice(0,50)).slice(0,8));
  const mail = await p.getAttribute('.close .btn','href');
  await p.evaluate(()=>document.getElementById('quotes').scrollIntoView({block:'center'}));
  const x0 = await p.evaluate(()=>document.getElementById('quotes').scrollLeft);
  await p.click('[data-q="1"]'); await p.waitForTimeout(700);
  const x1 = await p.evaluate(()=>document.getElementById('quotes').scrollLeft);
  const ov = await p.evaluate(()=>document.documentElement.scrollWidth - innerWidth);
  console.log(vp.width, JSON.stringify({hu, en, mail, rail:[x0,x1], ov, untranslated, errs}));
  await p.close();
}
await b.close();
