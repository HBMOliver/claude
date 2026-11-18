// Shared pieces of markup. They carry structure and words only; every look lives in the concept's own CSS.
//
// Two ways to render (render() sets which, before a page is built):
// - both languages in one page (the concepts, render({})): Hungarian in the element and English in data-en, or both
//   as twin spans (data-l), one shown at a time; ss.js swaps them when the HU / EN buttons are pressed. Files are
//   linked relatively.
// - one language per page (the live site, socialstream.hu, render({ lang: 'hu' | 'en', root: '/' })): only that
//   language's words are in the page, and the HU / EN switch is a link to the other language's page (site/). A twin
//   keeps its data-l wrapper, in the page's own language only, because kit.js and the checks read it. Files are linked
//   from the root, so a page works at any depth (/szolgaltatasok/videogyartas/).
import { C } from './content.mjs';
import { LOGO_ANIM } from './logo-anim.mjs';

// word: how a one-language page finds a pair's word (the site passes site/es.mjs's, which looks up the Spanish by
// the English text); without it, the pair's own
export const LANGS = ['hu', 'en', 'es'];
// film: where a one-language page's film cuts are (the site passes site/films.mjs's, k 'w' wide or 'v' upright);
// without it, kit.js picks them from assets/ by the page's language, as the concepts do
let L = null, ROOT = '', WORD = (p, l) => p[l], FILM = null;
export function render({ lang = null, root = '', word = null, film = null } = {}) { L = LANGS.includes(lang) ? lang : null; ROOT = root; WORD = word || ((p, l) => p[l]); FILM = film; }
export const lang = () => L;
// a pair whose two sides are built from parts (the claim's two lines, a heading's pieces): each side built, and on a
// Spanish page the Spanish built from the English parts, each looked up on its own
export const per = (p, f) => ({ hu: f(p.hu), en: f(p.en), ...(L === 'es' ? { es: f(Array.isArray(p.en) ? p.en.map(x => WORD({ en: x }, L)) : WORD({ en: p.en }, L)) } : {}) });
// a file of the page's own: relative for the concepts, from the root on the site
export const file = f => ROOT + f;
export const asset = f => ROOT + 'assets/' + f;

export const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const attrs = a => (a ? ' ' + a : '');
// the word of the page's language (Hungarian when the page holds both), escaped (t) or as markup (h); en gives the
// data-en attribute that carries the English when the page holds both, and nothing on a one-language page
export const t = p => esc(L ? WORD(p, L) : p.hu);
export const h = p => (L ? WORD(p, L) : p.hu);
export const en = p => (L ? '' : ` data-en="${esc(p.en)}"`);
// an aria-label in both languages (data-en-aria) or the page's one; alt the same way (data-en-alt)
export const ar = p => (L ? ` aria-label="${esc(WORD(p, L))}"` : ` aria-label="${esc(p.hu)}" data-en-aria="${esc(p.en)}"`);
// markup in both languages as twin spans, one shown at a time, or the page's own in its wrapper
export const twin = p => (L ? `<span data-l="${L}">${WORD(p, L)}</span>` : `<span data-l="hu">${p.hu}</span><span data-l="en">${p.en}</span>`);
// plain text in both languages: Hungarian in the element, English in data-en (ss.js swaps it)
export const tx = (tag, cls, p, a = '') => `<${tag}${cls ? ` class="${cls}"` : ''}${en(p)}${attrs(a)}>${t(p)}</${tag}>`;
// text with markup in both languages: twins, one shown at a time
export const tw = (tag, cls, p, a = '') => `<${tag}${cls ? ` class="${cls}"` : ''}${attrs(a)}>${twin(p)}</${tag}>`;
export const pair = ([hu, en]) => ({ hu, en });
export const ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
// from a business problem to the service that answers it (each service card carries id="svc-<id>"; on the site's
// services page the link goes to the service's own page instead)
export const toSvc = (it, cls = '', href = `#svc-${it.id}`) => `<a class="${cls}" href="${href}">${tx('span', 'k', C.pains.help)}${tx('span', 'n', pair(it.k))}${ARROW}</a>`;
export const btn = (p = C.cta, cls = 'btn', href = '#audit') => `<a class="${cls}" href="${href}"><span${en(p)}>${t(p)}</span>${ARROW}</a>`;

// seo: the site's own head lines (title, canonical, alternates, share tags, structured data; site/head.mjs), which
// replace the title here and go right after the description; css: one file or a list
export function head({ title, fonts, css, theme = '#ffffff', desc, seo = '' }) {
  const d = desc || 'A social media meghalt. Az érdeklődés vette át a helyét. Videó, social és hirdetés egy csapattól.';
  return `<!doctype html>
<html lang="${L || 'hu'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(title)}</title>
<meta name="description" content="${esc(d)}">${seo ? '\n' + seo : ''}
<meta name="theme-color" content="${theme}">
<!-- the favicon set from the logo kit (kit/web/head-snippet.html); the page keeps its own theme-color above -->
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?${fonts}&display=swap">
<link rel="stylesheet" href="${file('base.css')}">
${[].concat(css).map(c => `<link rel="stylesheet" href="${file(c)}">`).join('\n')}
</head>
<body>
`;
}
// extra: a page's own scripts after the shared ones (Aurora Mix's footer logo animation)
export const scripts = (extra = []) => `
<script src="${file('ss.js')}"></script>
<script src="${file('kit.js')}"></script>
${extra.map(f => `<script src="${file(f)}"></script>\n`).join('')}</body>
</html>
`;

// The header logo: files from the logo kit (scrollcraft/brand/socialstream-logo/kit), copied unchanged into assets/.
// The small-cut horizontal lockup from 480 px wide; below that the phone alone, because the kit's floor for the
// lockup is 140 px wide and a phone's bar has less room than that. Light files on light grounds, dark files on dark
// ones, and the corner mark (the kit's mark for video) while the bar lies on the film. They share one cell and
// base.css shows one at a time, from the bar's data-ground and its on-dark and on-film states.
// ground: the page's own ground, 'light' or 'dark'; dark: the dark files too, for a light page with dark parts;
// film: the corner mark too, for a page whose first screen puts the film under the bar
// site: on a one-language page, { home, links: [{ href, label: { hu, en } }], alt: { hu, en } (the page's own address
// in each language), menu: { hu, en } }: the logo goes home, the links go to the site's pages, the HU / EN switch is
// a link to the other language's page, and on tablets and phones a menu button opens the links (kit.js)
const LG = (f, cls, w, h) => `<img class="lg ${cls}" src="${asset(`socialstream-${f}.svg`)}" alt="" width="${w}" height="${h}">`;
const LGSET = g => LG(`logo-horizontal-small-${g}`, `lg-full lg-${g}`, 172, 30) + LG(`symbol-${g}`, `lg-mark lg-${g}`, 38, 38);
const MENU = '<svg viewBox="0 0 20 20" aria-hidden="true"><path class="m1" d="M3 7h14"/><path class="m2" d="M3 13h14"/></svg>';
export function nav(cls = '', { ground = 'light', dark = false, film = false, site = null } = {}) {
  const logo = LGSET(ground) + (dark && ground !== 'dark' ? LGSET('dark') : '') + (film ? LG('symbol-corner', 'lg-film', 35, 35) : '');
  if (!site) return `<header class="nav ${cls}" id="nav" data-ground="${ground}">
  <a class="wm" href="#top" aria-label="SocialStream">${logo}</a>
  <nav class="links" aria-label="Fő menü" data-en-aria="Main menu">
    ${C.nav.map(l => `<a href="${l.href}" data-en="${esc(l.en)}">${esc(l.hu)}</a>`).join('\n    ')}
  </nav>
  <div class="lang" role="group" aria-label="Nyelv / Language"><button type="button" data-set-lang="hu" aria-pressed="true" lang="hu">HU</button><button type="button" data-set-lang="en" aria-pressed="false" lang="en">EN</button></div>
  ${btn(C.navCta, 'btn nav-cta')}
</header>
`;
  return `<header class="nav ${cls}" id="nav" data-ground="${ground}">
  <a class="wm" href="${site.home}" aria-label="SocialStream">${logo}</a>
  <nav class="links" id="nav-links"${ar({ hu: 'Fő menü', en: 'Main menu' })}>
    ${site.links.map(l => `<a href="${l.href}"${l.current ? ' aria-current="page"' : ''}>${t(l.label)}</a>`).join('\n    ')}
  </nav>
  <div class="lang" role="group" aria-label="Nyelv / Language / Idioma">${LANGS.filter(l => site.alt[l]).map(l => `<a href="${site.alt[l]}" hreflang="${l}" lang="${l}"${l === L ? ' aria-current="page"' : ''}>${l.toUpperCase()}</a>`).join('')}</div>
  ${btn(C.navCta, 'btn nav-cta')}
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav-links"${ar(site.menu)}>${MENU}</button>
</header>
`;
}

// the claim, one line per sentence; the strike and the italic word come from content.mjs
const lines = p => `<span class="ln">${p[0]}</span> <span class="ln">${p[1]}</span>`;
export const claim = (cls = '', a = '') => `<h1 class="claim ${cls}" id="hero-h"${attrs(a)}>${twin(per(C.claim, lines))}</h1>`;
export const claimLine = (i, cls = '') => `<span class="${cls}">${twin({ hu: C.claim.hu[i], en: C.claim.en[i] })}</span>`;
export const promise = (cls = 'promise', a = '') => `<p class="${cls}"${attrs(a)}>${twin(per(C.promise, lines))}</p>`;
export const ticks = (cls = 'ticks') => `<ul class="${cls}">${C.ticks.map(t => tx('li', '', t)).join('')}</ul>`;

// where the film starts again after its first play: the sizzle (the film since 2026-11-16) opens and ends on the logo,
// so a loop to 0 would show the logo twice within seconds; 3.2 s is the dimmed wall a moment before its first line,
// as dark as the last frame (the video session's sizzle handover). Both frames of a pair share it
const FILM_LOOP = 3.2;

// the brand film: cut "v" (vertical), "h" (16:9) or "auto" (vertical on phones); kit.js plays it when seen
export function film(cls = '', cut = 'auto', big = false, extra = '') {
  const poster = cut === 'v' ? `<img src="${asset('hero-v-poster.jpg')}" alt="" width="720" height="1280">`
    : cut === 'h' ? `<img src="${asset('hero-poster.jpg')}" alt="" width="1600" height="900">`
    : `<picture><source media="(max-width: 760px)" srcset="${asset('hero-v-poster.jpg')}"><img src="${asset('hero-poster.jpg')}" alt="" width="1600" height="900"></picture>`;
  const own = FILM ? ` data-src-w="${esc(FILM('w'))}" data-src-v="${esc(FILM('v'))}"` : '';
  return `<div class="film ${cls}" data-film data-cut="${cut}"${big ? ' data-big' : ''}${own}>
  <div class="poster">${poster}</div>
  <video muted loop playsinline preload="none" data-loop="${FILM_LOOP}"${ar(C.film.label)}></video>
  <button class="toggle" type="button"></button>${extra}
</div>`;
}

export const reel = (id, cls = '', lazy = true) => `<figure class="reel ${cls}"><img src="${asset(id + '.jpg')}" alt="" width="486" height="864"${lazy ? ' loading="lazy"' : ''} decoding="async"></figure>`;
// a running row: kit.js doubles the track and keeps it moving (faster while the page is scrolled)
export const rail = (inner, cls = '', dir = 1, speed = 40) => `<div class="rail ${cls}" data-rail="${dir}" data-speed="${speed}" aria-hidden="true"><div class="track">${inner}</div></div>`;
export const tagItems = (cls = 'tag', tags = C.tags) => tags.map(([hu, en]) => `<span class="${cls}"${en_({ hu, en })}>${t({ hu, en })}</span>`).join('');
const en_ = en;
export const tickerItems = (cls = 'tk') => C.ticker.map(p => `<span class="${cls}"${en(p)}>${t(p)}</span>`).join('');

// a figure with its unit: `count` counts it up the first time it is seen (a figure with decimals stands still), `figure`
// shows it as it is. Where a figure is money, `en` gives the English page its own in euros, the English film's figures
// (content.mjs, results): { pre: '€', n, unit }
const fig = (n, unit, pre, counted) => `${pre ? `<small class="pre">${esc(pre)}</small>` : ''}${counted && Number.isInteger(n) ? `<span data-count="${n}">${n}</span>` : `<span>${n}</span>`}${unit ? `<small>${esc(unit)}</small>` : ''}`;
// a Spanish page shows the English page's euros the Spanish way: the number with a decimal comma, then "K €"
const figEs = (en, counted) => fig(Number.isInteger(en.n) ? en.n : String(en.n).replace('.', ','), (en.unit || '') + (en.pre === '€' ? ' €' : ''), en.pre === '€' ? '' : en.pre, counted);
const both = (n, unit, en, counted) => !L ? (en ? `<span data-l="hu">${fig(n, unit, '', counted)}</span><span data-l="en">${fig(en.n, en.unit, en.pre, counted)}</span>` : fig(n, unit, '', counted))
  : L === 'en' && en ? fig(en.n, en.unit, en.pre, counted) : L === 'es' && en ? figEs(en, counted) : fig(n, unit, '', counted);
export const count = (n, unit = '', en = null) => both(n, unit, en, true);
export const figure = (n, unit = '', en = null) => both(n, unit, en, false);

// the audit form, exactly as on Daylight (same fields, ids and words); kit.js runs it
const F = {
  h: { hu: 'Jelentkezés az ingyenes auditra', en: 'Apply for the free audit' },
  name: { hu: 'Neved', en: 'Your name' }, email: { hu: 'E-mail', en: 'Email' }, brand: { hu: 'Cég vagy márka', en: 'Company or brand' },
  web: { hu: 'Weboldal vagy Instagram', en: 'Website or Instagram' }, opt: { hu: '(nem kötelező)', en: '(optional)' },
  budget: { hu: 'Havi marketing büdzsé', en: 'Monthly marketing budget' },
  budgets: [['', { hu: 'Válassz sávot', en: 'Choose a range' }], ['lt300', { hu: '300 ezer Ft alatt', en: 'Under €800' }], ['300-1m', { hu: '300 ezer – 1 millió Ft', en: '€800–€2,700' }], ['1-3m', { hu: '1–3 millió Ft', en: '€2,700–€8,200' }], ['gt3m', { hu: '3 millió Ft felett', en: 'Over €8,200' }]],
  goal: { hu: 'Mi a fő célod?', en: 'Your main goal' },
  goals: [['', { hu: 'Válassz célt', en: 'Choose a goal' }], ['sales', { hu: 'Több eladás (webshop)', en: 'More sales (e-commerce)' }], ['leads', { hu: 'Több érdeklődő és ajánlatkérés', en: 'More leads and enquiries' }], ['brand', { hu: 'Márka és tartalom', en: 'Brand and content' }], ['web', { hu: 'Weboldal vagy landing', en: 'Website or landing page' }]],
  help: { hu: 'Miben segítsünk?', en: 'What can we help with?' },
  msg: { hu: 'Röviden: hol tartasz most?', en: 'In short: where are you now?' },
  ph: { hu: 'Pl. webshopunk van, a Metán hirdetünk, de túl drága egy vásárlás.', en: 'E.g. we run a webshop and advertise on Meta, but each sale costs too much.' },
  send: { hu: 'Jelentkezem e-mailben', en: 'Apply by email' },
  hint: { hu: 'A gomb megnyitja a leveleződ egy kitöltött e-maillel, neked csak el kell küldened.', en: 'This opens your mail app with the email filled in. You just press send.' },
  or: { hu: 'Vagy írj nekünk:', en: 'Or write to us:' }, copy: { hu: 'Cím másolása', en: 'Copy address' },
};
// a label with "(optional)" after it
const lab = p => `<span${en(p)}>${t(p)}</span> <span class="opt"${en(F.opt)}>${t(F.opt)}</span>`;
const options = list => list.map(([v, p]) => `<option value="${v}"${en(p)}>${t(p)}</option>`).join('');
export function form(cls = 'app') {
  const ph = L ? ` placeholder="${t(F.ph)}"` : ` placeholder="${esc(F.ph.hu)}" data-en-ph="${esc(F.ph.en)}"`;
  return `<form class="${cls}" id="appform" novalidate>
  <h3${en(F.h)}>${t(F.h)}</h3>
  <div class="field"><label for="f-name"${en(F.name)}>${t(F.name)}</label><input id="f-name" name="name" autocomplete="name" required><span class="err" id="e-name"></span></div>
  <div class="field"><label for="f-email"${en(F.email)}>${t(F.email)}</label><input id="f-email" name="email" type="email" autocomplete="email" required><span class="err" id="e-email"></span></div>
  <div class="field"><label for="f-brand"${en(F.brand)}>${t(F.brand)}</label><input id="f-brand" name="brand" autocomplete="organization" required><span class="err" id="e-brand"></span></div>
  <div class="field"><label for="f-web">${lab(F.web)}</label><input id="f-web" name="web" autocomplete="url"><span class="err"></span></div>
  <div class="field"><label for="f-budget">${lab(F.budget)}</label><select id="f-budget" name="budget">${options(F.budgets)}</select><span class="err"></span></div>
  <div class="field"><label for="f-goal">${lab(F.goal)}</label><select id="f-goal" name="goal">${options(F.goals)}</select><span class="err"></span></div>
  <fieldset><legend>${lab(F.help)}</legend><div class="pick" id="pick"></div></fieldset>
  <div class="field full"><label for="f-msg">${lab(F.msg)}</label><textarea id="f-msg" name="msg"${ph}></textarea><span class="err"></span></div>
  <div class="actions">
    <button class="btn" type="submit" aria-describedby="f-hint"><span${en(F.send)}>${t(F.send)}</span>${ARROW}</button>
    <p class="hint" id="f-hint"${en(F.hint)}>${t(F.hint)}</p>
    <p class="direct"><span${en(F.or)}>${t(F.or)}</span> <a href="mailto:hello@socialstream.hu">hello@socialstream.hu</a><button type="button" class="copy-mini" id="copyMail"${en(F.copy)}>${t(F.copy)}</button></p>
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
      <dl class="specs" data-r>${o.specs.map(([dt, dd]) => `<div><dt${en(pair(dt))}>${t(pair(dt))}</dt><dd${en(pair(dd))}>${t(pair(dd))}</dd></div>`).join('')}</dl>
      <p class="scarce" data-r><i aria-hidden="true"></i><span${en(o.scarce)}>${t(o.scarce)}</span></p>`;
}
export const faqList = (cls = 'faq-list') => `<div class="${cls}" data-r>
${C.faq.items.map(([q, a], i) => `  <details><summary><span class="qn">${String(i + 1).padStart(2, '0')}</span><span${en(pair(q))}>${t(pair(q))}</span><i aria-hidden="true"></i></summary><p${en(pair(a))}>${t(pair(a))}</p></details>`).join('\n')}
</div>`;

// kit: the logo kit's files instead of the typed wordmark, for a dark footer (Aurora Mix, the page that goes live):
// the small-cut dark lockup in the line, and the full dark lockup as the giant sign-off. The giant one is the kit's
// logo animation in place (logo-anim.mjs, played by logo-anim.js); its markup alone is the kit's dark master
// site: on a one-language page, { home, line: { hu, en }, groups: [{ label: { hu, en }, links: [{ href, label }] }] }:
// the logo goes home, the line is the site's, and the footer carries a row of links to every page
const COPY_MAIL = { hu: 'Cím másolása', en: 'Copy address' };
export function footer(cls = '', big = false, kit = false, site = null) {
  const wm = kit ? `<img src="${asset('socialstream-logo-horizontal-small-dark.svg')}" alt="" width="172" height="30">` : 'Social<em>Stream</em>';
  const giant = kit ? `<p class="giant giant-kit" aria-hidden="true">${LOGO_ANIM}</p>`
    : '<p class="giant" aria-hidden="true">Social<em>Stream</em></p>';
  const links = site ? `
  <nav class="wrap foot-nav"${ar({ hu: 'Oldalak', en: 'Pages' })}>
    ${site.groups.map(g => `<div>${tx('p', 'foot-k', g.label)}<ul>${g.links.map(l => `<li><a href="${l.href}">${t(l.label)}</a></li>`).join('')}</ul></div>`).join('\n    ')}
  </nav>` : '';
  return `<footer class="foot ${cls}">${links}
  <div class="wrap">
    <a class="wm" href="${site ? site.home : '#top'}" aria-label="SocialStream">${wm}</a>
    ${tx('span', '', site ? site.line : C.footer.line)}
    <span><a href="mailto:hello@socialstream.hu">hello@socialstream.hu</a><button type="button" id="copyMail2"${en(COPY_MAIL)}>${t(COPY_MAIL)}</button></span>
    <span>© 2026 SocialStream</span>
  </div>${big ? `
  ${giant}` : ''}
</footer>`;
}
