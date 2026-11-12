// Shared pieces of markup. They carry structure and words only; every look lives in the concept's own CSS.
import { C } from './content.mjs';

export const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const attrs = a => (a ? ' ' + a : '');
// plain text in both languages: Hungarian in the element, English in data-en (ss.js swaps it)
export const tx = (tag, cls, p, a = '') => `<${tag}${cls ? ` class="${cls}"` : ''} data-en="${esc(p.en)}"${attrs(a)}>${esc(p.hu)}</${tag}>`;
// text with markup in both languages: twins, one shown at a time
export const tw = (tag, cls, p, a = '') => `<${tag}${cls ? ` class="${cls}"` : ''}${attrs(a)}><span data-l="hu">${p.hu}</span><span data-l="en">${p.en}</span></${tag}>`;
export const pair = ([hu, en]) => ({ hu, en });
export const ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
// from a business problem to the service that answers it (each service card carries id="svc-<id>")
export const toSvc = (it, cls = '') => `<a class="${cls}" href="#svc-${it.id}">${tx('span', 'k', C.pains.help)}${tx('span', 'n', pair(it.k))}${ARROW}</a>`;
export const btn = (p = C.cta, cls = 'btn', href = '#audit') => `<a class="${cls}" href="${href}"><span data-en="${esc(p.en)}">${esc(p.hu)}</span>${ARROW}</a>`;

export function head({ title, fonts, css, theme = '#ffffff', desc }) {
  return `<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc || 'A social media meghalt. Az érdeklődés vette át a helyét. Videó, social és hirdetés egy csapattól.')}">
<meta name="theme-color" content="${theme}">
<!-- the favicon set from the logo kit (kit/web/head-snippet.html); the page keeps its own theme-color above -->
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?${fonts}&display=swap">
<link rel="stylesheet" href="base.css">
<link rel="stylesheet" href="${css}">
</head>
<body>
`;
}
export const scripts = () => `
<script src="ss.js"></script>
<script src="kit.js"></script>
</body>
</html>
`;

// The header logo: files from the logo kit (scrollcraft/brand/socialstream-logo/kit), copied unchanged into assets/.
// The small-cut horizontal lockup from 480 px wide; below that the phone alone, because the kit's floor for the
// lockup is 140 px wide and a phone's bar has less room than that. Light files on light grounds, dark files on dark
// ones, and the corner mark (the kit's mark for video) while the bar lies on the film. They share one cell and
// base.css shows one at a time, from the bar's data-ground and its on-dark and on-film states.
// ground: the page's own ground, 'light' or 'dark'; dark: the dark files too, for a light page with dark parts;
// film: the corner mark too, for a page whose first screen puts the film under the bar
const LG = (f, cls, w, h) => `<img class="lg ${cls}" src="assets/socialstream-${f}.svg" alt="" width="${w}" height="${h}">`;
const LGSET = g => LG(`logo-horizontal-small-${g}`, `lg-full lg-${g}`, 172, 30) + LG(`symbol-${g}`, `lg-mark lg-${g}`, 38, 38);
export function nav(cls = '', { ground = 'light', dark = false, film = false } = {}) {
  const logo = LGSET(ground) + (dark && ground !== 'dark' ? LGSET('dark') : '') + (film ? LG('symbol-corner', 'lg-film', 35, 35) : '');
  return `<header class="nav ${cls}" id="nav" data-ground="${ground}">
  <a class="wm" href="#top" aria-label="SocialStream">${logo}</a>
  <nav class="links" aria-label="Fő menü" data-en-aria="Main menu">
    ${C.nav.map(l => `<a href="${l.href}" data-en="${esc(l.en)}">${esc(l.hu)}</a>`).join('\n    ')}
  </nav>
  <div class="lang" role="group" aria-label="Nyelv / Language"><button type="button" data-set-lang="hu" aria-pressed="true" lang="hu">HU</button><button type="button" data-set-lang="en" aria-pressed="false" lang="en">EN</button></div>
  ${btn(C.navCta, 'btn nav-cta')}
</header>
`;
}

// the claim, one line per sentence; the strike and the italic word come from content.mjs
export const claim = (cls = '', a = '') => `<h1 class="claim ${cls}" id="hero-h"${attrs(a)}><span data-l="hu"><span class="ln">${C.claim.hu[0]}</span> <span class="ln">${C.claim.hu[1]}</span></span><span data-l="en"><span class="ln">${C.claim.en[0]}</span> <span class="ln">${C.claim.en[1]}</span></span></h1>`;
export const claimLine = (i, cls = '') => `<span class="${cls}"><span data-l="hu">${C.claim.hu[i]}</span><span data-l="en">${C.claim.en[i]}</span></span>`;
export const promise = (cls = 'promise', a = '') => `<p class="${cls}"${attrs(a)}><span data-l="hu"><span class="ln">${C.promise.hu[0]}</span> <span class="ln">${C.promise.hu[1]}</span></span><span data-l="en"><span class="ln">${C.promise.en[0]}</span> <span class="ln">${C.promise.en[1]}</span></span></p>`;
export const ticks = (cls = 'ticks') => `<ul class="${cls}">${C.ticks.map(t => tx('li', '', t)).join('')}</ul>`;

// the brand film: cut "v" (vertical), "h" (16:9) or "auto" (vertical on phones); kit.js plays it when seen
export function film(cls = '', cut = 'auto', big = false, extra = '') {
  const poster = cut === 'v' ? `<img src="assets/hero-v-poster.jpg" alt="" width="720" height="1280">`
    : cut === 'h' ? `<img src="assets/hero-poster.jpg" alt="" width="1600" height="900">`
    : `<picture><source media="(max-width: 760px)" srcset="assets/hero-v-poster.jpg"><img src="assets/hero-poster.jpg" alt="" width="1600" height="900"></picture>`;
  return `<div class="film ${cls}" data-film data-cut="${cut}"${big ? ' data-big' : ''}>
  <div class="poster">${poster}</div>
  <video muted loop playsinline preload="none" aria-label="${esc(C.film.label.hu)}" data-en-aria="${esc(C.film.label.en)}"></video>
  <button class="toggle" type="button"></button>${extra}
</div>`;
}

export const reel = (id, cls = '', lazy = true) => `<figure class="reel ${cls}"><img src="assets/${id}.jpg" alt="" width="486" height="864"${lazy ? ' loading="lazy"' : ''} decoding="async"></figure>`;
// a running row: kit.js doubles the track and keeps it moving (faster while the page is scrolled)
export const rail = (inner, cls = '', dir = 1, speed = 40) => `<div class="rail ${cls}" data-rail="${dir}" data-speed="${speed}" aria-hidden="true"><div class="track">${inner}</div></div>`;
export const tagItems = (cls = 'tag') => C.tags.map(([hu, en]) => `<span class="${cls}" data-en="${esc(en)}">${esc(hu)}</span>`).join('');
export const tickerItems = (cls = 'tk') => C.ticker.map(t => `<span class="${cls}" data-en="${esc(t.en)}">${esc(t.hu)}</span>`).join('');

export const count = (n, unit = '') => `<span data-count="${n}">${n}</span>${unit ? `<small>${esc(unit)}</small>` : ''}`;

// the audit form, exactly as on Daylight (same fields, ids and words); kit.js runs it
export function form(cls = 'app') {
  return `<form class="${cls}" id="appform" novalidate>
  <h3 data-en="Apply for the free audit">Jelentkezés az ingyenes auditra</h3>
  <div class="field"><label for="f-name" data-en="Your name">Neved</label><input id="f-name" name="name" autocomplete="name" required><span class="err" id="e-name"></span></div>
  <div class="field"><label for="f-email" data-en="Email">E-mail</label><input id="f-email" name="email" type="email" autocomplete="email" required><span class="err" id="e-email"></span></div>
  <div class="field"><label for="f-brand" data-en="Company or brand">Cég vagy márka</label><input id="f-brand" name="brand" autocomplete="organization" required><span class="err" id="e-brand"></span></div>
  <div class="field"><label for="f-web"><span data-en="Website or Instagram">Weboldal vagy Instagram</span> <span class="opt" data-en="(optional)">(nem kötelező)</span></label><input id="f-web" name="web" autocomplete="url"><span class="err"></span></div>
  <div class="field"><label for="f-budget"><span data-en="Monthly marketing budget">Havi marketing büdzsé</span> <span class="opt" data-en="(optional)">(nem kötelező)</span></label><select id="f-budget" name="budget"><option value="" data-en="Choose a range">Válassz sávot</option><option value="lt300" data-en="Under 300K Ft">300 ezer Ft alatt</option><option value="300-1m" data-en="300K–1M Ft">300 ezer – 1 millió Ft</option><option value="1-3m" data-en="1M–3M Ft">1–3 millió Ft</option><option value="gt3m" data-en="Over 3M Ft">3 millió Ft felett</option></select><span class="err"></span></div>
  <div class="field"><label for="f-goal"><span data-en="Your main goal">Mi a fő célod?</span> <span class="opt" data-en="(optional)">(nem kötelező)</span></label><select id="f-goal" name="goal"><option value="" data-en="Choose a goal">Válassz célt</option><option value="sales" data-en="More sales (e-commerce)">Több eladás (webshop)</option><option value="leads" data-en="More leads and enquiries">Több érdeklődő és ajánlatkérés</option><option value="brand" data-en="Brand and content">Márka és tartalom</option><option value="web" data-en="Website or landing page">Weboldal vagy landing</option></select><span class="err"></span></div>
  <fieldset><legend><span data-en="What can we help with?">Miben segítsünk?</span> <span class="opt" data-en="(optional)">(nem kötelező)</span></legend><div class="pick" id="pick"></div></fieldset>
  <div class="field full"><label for="f-msg"><span data-en="In short: where are you now?">Röviden: hol tartasz most?</span> <span class="opt" data-en="(optional)">(nem kötelező)</span></label><textarea id="f-msg" name="msg" placeholder="Pl. webshopunk van, a Metán hirdetünk, de túl drága egy vásárlás." data-en-ph="E.g. we run a webshop and advertise on Meta, but each sale costs too much."></textarea><span class="err"></span></div>
  <div class="actions">
    <button class="btn" type="submit" aria-describedby="f-hint"><span data-en="Apply by email">Jelentkezem e-mailben</span>${ARROW}</button>
    <p class="hint" id="f-hint" data-en="This opens your mail app with the email filled in. You just press send.">A gomb megnyitja a leveleződ egy kitöltött e-maillel, neked csak el kell küldened.</p>
    <p class="direct"><span data-en="Or write to us:">Vagy írj nekünk:</span> <a href="mailto:hello@socialstream.hu">hello@socialstream.hu</a><button type="button" class="copy-mini" id="copyMail" data-en="Copy address">Cím másolása</button></p>
  </div>
  <div class="sending" id="sending" hidden><i></i><span id="stext"></span></div>
  <div class="sent" id="sent" hidden aria-live="polite"></div>
</form>`;
}
// the offer's own words, to sit beside the form
export function offerCopy(hcls = 'h2') {
  const o = C.offer;
  return `${tx('p', 'eyebrow', o.eyebrow, 'data-r')}
      ${tw('h2', hcls, o.h2, 'id="au-h" data-r')}
      <ul class="checks" data-r>${o.checks.map(c => tx('li', '', c)).join('')}</ul>
      <dl class="specs" data-r>${o.specs.map(([t, d]) => `<div><dt data-en="${esc(t[1])}">${esc(t[0])}</dt><dd data-en="${esc(d[1])}">${esc(d[0])}</dd></div>`).join('')}</dl>
      <p class="scarce" data-r><i aria-hidden="true"></i><span data-en="${esc(o.scarce.en)}">${esc(o.scarce.hu)}</span></p>`;
}
export const faqList = (cls = 'faq-list') => `<div class="${cls}" data-r>
${C.faq.items.map(([q, a], i) => `  <details><summary><span class="qn">${String(i + 1).padStart(2, '0')}</span><span data-en="${esc(q[1])}">${esc(q[0])}</span><i aria-hidden="true"></i></summary><p data-en="${esc(a[1])}">${esc(a[0])}</p></details>`).join('\n')}
</div>`;

export function footer(cls = '', big = false) {
  return `<footer class="foot ${cls}">
  <div class="wrap">
    <a class="wm" href="#top" aria-label="SocialStream">Social<em>Stream</em></a>
    ${tx('span', '', C.footer.line)}
    <span><a href="mailto:hello@socialstream.hu">hello@socialstream.hu</a><button type="button" id="copyMail2" data-en="Copy address">Cím másolása</button></span>
    <span>© 2026 SocialStream</span>
  </div>${big ? `
  <p class="giant" aria-hidden="true">Social<em>Stream</em></p>` : ''}
</footer>`;
}
