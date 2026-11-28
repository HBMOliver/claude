// node ../socialstream-concepts/tools/og.mjs   (run from a folder with playwright-core, e.g. ../socialstream-split)
// Renders tools/og.html, the share image (the logo, the claim and three of their reels on Aurora Mix's night blue), at
// 1200 x 630: assets/og-image.jpg with the claim in Hungarian, and since 2026-11-28 og-image-en.jpg and og-image-es.jpg
// with the claim as the English and Spanish home pages say it (site/head.mjs links each language's own).
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
const { chromium } = createRequire(process.cwd() + '/')('playwright-core');
const here = path.dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
// the claim in three lines, as each home page has it (the struck words and the italic one the same)
// with the eyebrow and the domain line each language's own
const OWN = { en: ['Interest media agency', 'socialstream.hu'], es: ['Agencia de interest media', 'socialstream.es'] };
const CLAIM = {
  hu: null,
  en: '<span class="ln"><span class="strike">Social media</span> is dead.</span><span class="ln"><em>Interest</em> has taken</span><span class="ln">its place.</span>',
  es: '<span class="ln">Las <span class="strike">redes sociales</span></span><span class="ln">han muerto. El <em>interés</em></span><span class="ln">ha ocupado su lugar.</span>',
};
for (const [l, html] of Object.entries(CLAIM)) {
  await p.goto(pathToFileURL(path.join(here, 'og.html')).href, { waitUntil: 'networkidle' });
  if (html) await p.evaluate(([html, l, own]) => { document.documentElement.lang = l; document.querySelector('h1').innerHTML = html; document.querySelector('.eyebrow').textContent = own[0]; document.querySelector('.site').textContent = own[1]; }, [html, l, OWN[l]]);
  await p.evaluate(() => document.fonts.ready);
  const missing = await p.evaluate(() => [...document.images].filter(i => !i.naturalWidth).map(i => i.src));
  if (missing.length) throw new Error('images did not load: ' + missing.join(', '));
  // nothing of the claim may run past the image's right edge
  const over = await p.evaluate(() => [...document.querySelectorAll('h1 .ln')].some(e => e.getBoundingClientRect().right > 1200));
  if (over) throw new Error('the ' + l + ' claim runs past the image');
  const out = path.join(here, '..', 'assets', l === 'hu' ? 'og-image.jpg' : `og-image-${l}.jpg`);
  await p.screenshot({ path: out, type: 'jpeg', quality: 88 });
  console.log('wrote', out);
}
await b.close();
