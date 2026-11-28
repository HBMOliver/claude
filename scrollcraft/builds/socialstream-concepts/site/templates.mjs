// One template per kind of page of socialstream.hu: the home page (Aurora Mix itself), the services page, a service,
// About us, the free audit, the questions, contact. Every page shares the header, the footer and the audit form,
// is in one language (Hungarian at the root, English under /en/), and is laid out in Mix's look (mix.css) with the
// site's own additions (site.css). renderPage(page, 'hu' | 'en') gives the whole document.
//
// Each subpage opens on a panel like the home page's: where it sits (the breadcrumb), what it is (the heading, the
// service's own line), the answer in two sentences, the audit button, and on the right its own picture that floats
// and leans toward the cursor; the aurora moves inside and its light follows the cursor; the real numbers (or the
// service words) run along its foot. Then each kind of page has its own sections, and every page ends on the audit.
import { C } from '../content.mjs';
import { render, esc, t, h, ar, twin, per, asset, tx, tw, pair, btn, head, scripts, nav, footer, rail, tagItems, tickerItems, form, count, figure, ARROW } from '../parts.mjs';
import * as mix from '../concepts/mix.mjs';
import { PAGES, NAV, W, byId, hrefTo, CLIENTS } from './pages.mjs';
import { seo, trail } from './head.mjs';
import { word } from './es.mjs';
import { filmSrc } from './films.mjs';

const SERVICES = PAGES.filter(pg => pg.type === 'service');
const CASES = PAGES.filter(pg => pg.type === 'case');
// the fields we work in (each with its page), and pages that may be drafts: only those built here are linked
const INDUSTRIES = PAGES.filter(pg => pg.type === 'industry');
const built = ids => ids.map(byId).filter(Boolean);
// the site's own script after Mix's: the film with sound, the light round the audit form, the services' beams
const SITE_SCRIPTS = [...mix.PAGE_SCRIPTS, 'site.js'];
const CW = {
  pick: { hu: 'Válassz egy esetet.', en: 'Pick a case.' },
  more: { hu: 'További esetek.', en: 'More cases.' },
  go: { hu: 'Az eset', en: 'The case' },
  used: { hu: 'Amivel elértük.', en: 'What it took.' },
  named: { hu: 'Ügyfeleink fiókjai, számokban.', en: 'Our clients’ accounts, in numbers.' },
  // the explainer and the field pages (live since v22)
  why: { hu: 'Miért interest media?', en: 'Why interest media?' },
  forIt: { hu: 'Amivel elérjük.', en: 'What it takes.' },
  fields: { hu: 'Válaszd ki a területed.', en: 'Pick your field.' },
  // the hub's own eyebrow over its fields (it said the page's name, "Kikkel dolgozunk", again; 2026-11-28)
  fieldsEyebrow: { hu: 'Területek', en: 'Fields' },
  who: { hu: 'Kikkel dolgozunk', en: 'Who we work with' },
  // the website page's own heading over the clients it built sites for (2026-11-27)
  clientsEyebrow: { hu: 'Ügyfeleink', en: 'Our clients' },
  sites: { hu: 'Weboldalak, amiket mi készítettünk.', en: 'Websites we built.' },
  // the home page's ways on (2026-11-27); worked: the one section of cases and clients on the hub and field pages (v24)
  allCases: { hu: 'Minden esettanulmány', en: 'All case studies' },
  allFields: { hu: 'Mind a hat terület és az ügyfeleink', en: 'All six fields and our clients' },
  worked: { hu: 'Akikkel dolgoztunk.', en: 'Who we have worked with.' },
};
// the home page's cards go to their pages: services, cases, fields (the founder, 2026-11-27: they were hard to reach)
const homeLinks = l => ({
  services: { href: it => SERVICES.find(x => x.svc === it.id).path[l], label: W.details },
  results: { card: { href: it => (PAGES.find(x => x.type === 'case' && x.res === it.obj) || byId('cases')).path[l], label: CW.go }, all: { href: byId('cases').path[l], label: CW.allCases } },
  who: { href: c => (INDUSTRIES.find(x => x.art === c.img) || byId('audiences')).path[l], label: W.details, all: { href: byId('audiences').path[l], label: CW.allFields } },
});
// the hub shows every client once (Karaja's workshops stay on the events page), each card going to its field
const HUB_CLIENTS = ['hoof', 'karajaShop', 'traffic', 'realbeauty', 'zsm', 'tony', 'church', 'bgp', 'bridle', 'ritas', 'lunelle', 'dorombolda'];
const plain = s => String(s).replace(/<[^>]+>/g, '');

const siteNav = (pg, l) => ({
  home: byId('home').path[l],
  links: NAV.map(x => ({ href: x.path[l], label: x.nav, current: x.id === pg.id })),
  // the language switch: the same page in each language, a full address where that language has its own domain
  alt: Object.fromEntries(Object.entries(pg.path).map(([x, path]) => [x, hrefTo(path, x, l)])), menu: W.menu,
});
const siteFoot = l => ({
  home: byId('home').path[l], line: W.line,
  groups: [
    { label: W.more, links: [{ href: byId('services').path[l], label: { hu: 'Minden szolgáltatás', en: 'All services' } }, ...SERVICES.map(pg => ({ href: pg.path[l], label: pg.crumb }))] },
    // the fields we work in, once their pages are built (drafts until the founder approves them)
    ...(INDUSTRIES.length ? [{ label: CW.who, links: built(['audiences', ...INDUSTRIES.map(x => x.id)]).map(x => ({ href: x.path[l], label: x.crumb })) }] : []),
    { label: W.pagesGroup, links: built(['interest-media', 'cases', 'about', 'audit', 'faq', 'contact']).map(x => ({ href: x.path[l], label: x.crumb })) },
  ],
});

function shell(pg, l, body, film = false) {
  return head({ title: plain(word(pg.title, l)), desc: word(pg.desc, l), fonts: mix.FONTS, css: ['mix.css', 'site.css'], theme: mix.THEME, seo: seo(pg, l) })
    + nav('mx-nav', { ground: 'dark', film, site: siteNav(pg, l) })
    + `\n<main>\n${body.filter(Boolean).join('\n\n')}\n</main>\n`
    + footer('mx-foot', true, true, siteFoot(l)) + scripts(SITE_SCRIPTS);
}

// ---------- the parts a subpage is made of ----------

// the first screen; art: its picture on the right; band: what runs along its foot ('ticker' or 'tags')
function hero(pg, l, art, { band = 'ticker', cta = true, extra = '' } = {}) {
  const tr = trail(pg);
  return `  <!-- the page's first screen in a panel: the breadcrumb, the heading (what the page is, then its line), the answer,
       the audit button and the page's own picture; the aurora moves inside and its light follows the cursor -->
  <section class="pg-hero" id="top" aria-labelledby="pg-h">
    <div class="mx-panel pg-panel">
      <div class="mx-sky" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><i class="b4"></i><span class="mx-glow" data-follow="in" data-home="0.72,0.42"></span></div>
      <div class="pg-hero-in">
        <div class="pg-copy">
          <nav class="pg-crumbs"${ar(W.crumbs)}><ol>${tr.map((x, i) => i < tr.length - 1 ? `<li><a href="${x.path[l]}">${t(x.crumb)}</a></li>` : `<li aria-current="page">${t(x.crumb)}</li>`).join('')}</ol></nav>
          <h1 class="pg-h1" id="pg-h"><span class="pg-k">${t(pg.h1k)}<span class="sr">:</span></span> <span class="pg-t">${h(pg.h1t)}</span></h1>
          <p class="pg-lead">${h(pg.lead)}</p>${extra}
          ${cta ? `<div class="mx-cta">${btn()}</div>` : ''}
        </div>
        <div class="pg-art">${art}</div>
      </div>
      ${band ? `<div class="mx-band">${band === 'tags' ? rail(tagItems('mx-tk'), 'mx-band-rail', 1, 40) : rail(tickerItems('mx-tk'), 'mx-band-rail', 1, 46)}</div>` : ''}
    </div>
  </section>`;
}
// a picture that floats and leans toward the cursor (k: how far, below zero the other way)
const obj = (f, cls, k, dur, w = 520, hh = 520, eager = true) => `<img class="bob ${cls}" data-follow data-k="${k}" style="--dur:${dur}s;--amp:-16px" src="${asset(f)}" alt="" width="${w}" height="${hh}"${eager ? '' : ' loading="lazy"'}>`;

// a question list; items: [{ q, a, links }]; links: the six services after the answer
function qa(items, l, start = 0) {
  return items.map((it, i) => `  <details><summary><span class="qn">${String(start + i + 1).padStart(2, '0')}</span><span>${t(it.q)}</span><i aria-hidden="true"></i></summary><p>${t(it.a)}</p>${it.links ? `<ul class="pg-qlinks">${SERVICES.map(pg => `<li><a href="${pg.path[l]}">${t(pg.crumb)}</a></li>`).join('')}</ul>` : ''}</details>`).join('\n');
}
const faqBlock = (items, l, { id = 'kerdesek', eyebrow = W.questions, h2 = C.faq.h2 } = {}) => `  <!-- questions about this page's subject -->
  <section class="mx-faq pg-faq" id="${id}" aria-labelledby="${id}-h">
    <div class="wrap">
      <div class="mx-head center">${tx('p', 'mx-eyebrow', eyebrow, 'data-r')}${tx('h2', 'mx-h2', h2, `id="${id}-h" data-r`)}</div>
      <div class="faq-list mx-faq-list" data-r>
${qa(items, l)}
      </div>
    </div>
  </section>`;

// a service page's problem, joined by a line of light to the service's own line
const pain = pg => `  <!-- the business problem this service answers, joined by a running line of light to what we do about it -->
  <section class="pg-pain" aria-labelledby="pain-h">
    <div class="wrap">
      <div class="mx-card pg-pain-card" data-r>
        <div>${tx('p', 'mx-eyebrow', W.pain)}${tx('h2', 'pg-pain-q', pair(pg.s.pain), 'id="pain-h"')}</div>
        <span class="mx-pain-line" aria-hidden="true"></span>
        <div class="pg-pain-a">${tx('p', 'k', C.pains.help)}${tx('p', 'n', pair(pg.s.t))}</div>
      </div>
    </div>
  </section>`;

// what the service includes: the service's own words beside a list
const included = pg => `  <!-- what the service includes -->
  <section class="pg-incl" aria-labelledby="incl-h">
    <div class="wrap pg-split">
      <div class="pg-split-l">
        ${tx('p', 'mx-eyebrow', pair(pg.s.k), 'data-r')}
        ${tx('h2', 'mx-h2', W.included, 'id="incl-h" data-r')}
        ${tx('p', 'mx-sub', pair(pg.s.p), 'data-r')}${pg.who ? `
        ${tx('p', 'pg-who', pg.who, 'data-r')}` : ''}
      </div>
      <ul class="mx-card checks pg-checks" data-r style="--d:1">${pg.included.map(x => tx('li', '', x)).join('')}</ul>
    </div>
  </section>`;

// the results as stat cards (the home page's), each going to its case as on the home page (2026-11-28)
const stats = l => `  <!-- results: the four stat cards, counting up -->
  <section class="mx-res pg-res" id="eredmenyek" aria-labelledby="res-h">
    <div class="wrap">
      <div class="mx-head row">
        <div>${tx('p', 'mx-eyebrow', C.results.eyebrow, 'data-r')}${tx('h2', 'mx-h2', C.results.h2, 'id="res-h" data-r')}</div>
      </div>
      ${mix.statCards(homeLinks(l).results.card)}
    </div>
  </section>`;

// a running row of reels (the home page's, playing while on screen); Up To Youth's are the founder's own organisation
const UTY = ['r-uty', 'r-lv-sunset', 'r-lv-yellow', 'r-lv-hoodie', 'r-lv-cap'];
const ALL_REELS = ['r-watch-1', 'r-enzo-2', 'r-flyx-1', 'r-uty', 'r-miskolc', 'r-andras-1', 'r-lv-yellow', 'r-nike-1', 'r-flyx-2', 'r-lv-sunset', 'r-enzo-1', 'r-soskut', 'r-lv-hoodie', 'r-andras-2', 'r-nike-2', 'r-tr-friends', 'r-lv-cap', 'r-watch-2', 'r-flyx-3'];
const reels = list => { const ids = list === 'all' ? ALL_REELS : list; return `  <!-- clips from our videos, in a row that keeps running -->
  <section class="mx-reels pg-reels" aria-labelledby="reels-h">
    <div class="wrap mx-reels-head">${tw('h2', 'mx-h3', C.reels.h2, 'id="reels-h" data-r')}${tx('p', 'mx-cap', C.reels.caption, 'data-r')}</div>
    ${rail(ids.map(mix.rv).join(''), 'mx-reel-rail', 1, 40)}${ids.some(id => UTY.includes(id)) ? `
    <div class="wrap">${tx('p', 'pg-note', W.uty, 'data-r')}</div>` : ''}
  </section>`; };

// a few clients' words, as cards side by side
const quotes = idx => `  <!-- clients' words about this service -->
  <section class="pg-quotes" aria-labelledby="pq-h">
    <div class="wrap">
      <div class="mx-head">${tx('p', 'mx-eyebrow', C.voices.eyebrow, 'data-r')}${tw('h2', 'mx-h2', C.voices.h2, 'id="pq-h" data-r')}</div>
      <div class="pg-quote-grid n${idx.length}" data-r>
      ${idx.map((n, i) => mix.quote(C.voices.quotes[n], i)).join('\n      ')}
      </div>
    </div>
  </section>`;

// the other five services, as cards that go to their pages
const more = (pg, l) => `  <!-- the other services -->
  <section class="pg-more" aria-labelledby="more-h">
    <div class="wrap">
      <div class="mx-head">${tx('p', 'mx-eyebrow', W.more, 'data-r')}${tw('h2', 'mx-h2', C.services.h2, 'id="more-h" data-r')}</div>
      <ul class="pg-more-grid">
        ${SERVICES.filter(x => x !== pg).map((x, i) => `<li data-r style="--d:${i}"><a class="mx-card pg-more-card" href="${x.path[l]}"><img class="bob" style="--dur:${5.4 + i * 0.5}s;--delay:-${i}s;--amp:-8px" src="${asset(x.s.icon + '-mix.webp')}" alt="" width="520" height="520" loading="lazy"><span class="k">${t(x.crumb)}</span><span class="d">${t(pair(x.s.t))}</span>${ARROW}</a></li>`).join('\n        ')}
      </ul>
    </div>
  </section>`;

// ---------- case studies ----------

// a case's result: the home page's stat (content.mjs, results) or, for a named client's draft, its own figure
const resultOf = pg => pg.res && C.results.items.find(it => it.obj === pg.res);
// one case as the home page's stat card: on its own first screen (hero), or linked to its page
function caseCard(pg, l, { link = false, hero = false, i = 0 } = {}) {
  const it = resultOf(pg), f = pg.fig, tag = link ? 'a' : 'article';
  const img = it ? `<img class="bob" style="--dur:${6.2 + i * 0.5}s;--delay:-${i * 1.2}s;--amp:-10px" src="${asset(it.obj + '-mix.webp')}" alt="" width="400" height="400"${hero ? '' : ' loading="lazy"'}>`
    : f.img ? `<img class="bob pg-case-reel" style="--dur:${6.6 + i * 0.5}s;--delay:-${i * 1.2}s;--amp:-8px" src="${asset(f.img)}" alt="" width="486" height="864"${hero ? '' : ' loading="lazy"'}>` : '';
  // on the first screen the number stands still: kit.js counts up only the cards that are revealed while scrolling
  const num = it ? (hero ? figure : count)(it.n, it.unit, it.en) : `<span>${typeof f.n === 'string' ? esc(f.n) : t(f.n)}</span>`;
  return `<${tag} class="mx-card mx-stat pg-case${hero ? ' bob' : ''}"${link ? ` href="${pg.path[l]}"` : ''}${hero ? ' style="--dur:6.8s;--amp:-8px"' : ` data-r style="--d:${i % 3}"`}>
          ${img}
          <p class="n num">${num}</p>
          ${tx('p', 'who', it ? pair(it.who) : f.who)}
          ${tx('p', 'd', it ? pair(it.p) : f.d)}${link ? `
          <span class="pg-case-go">${t(CW.go)}${ARROW}</span>` : ''}
        </${tag}>`;
}
// the same grid as the clients' (2026-11-28): three to a row, two on a tablet, one on a phone (it squeezed two or three
// cards side by side on a phone before, the objects over the numbers)
const caseGrid = (list, l) => `<div class="mx-stats pg-proof-grid c${colsFor(list.length)}">
        ${list.map((x, i) => caseCard(x, l, { link: true, i })).join('\n        ')}
      </div>`;
// a section of linked case cards under a heading
const caseSec = (list, l, h2, { id, eyebrow = C.results.eyebrow } = {}) => `  <!-- cases as the home page's stat cards, each going to its page -->
  <section class="mx-res pg-res"${id ? ` id="${id}"` : ''} aria-labelledby="${id || 'oc'}-h">
    <div class="wrap">
      <div class="mx-head row"><div>${tx('p', 'mx-eyebrow', eyebrow, 'data-r')}${tx('h2', 'mx-h2', h2, `id="${id || 'oc'}-h" data-r`)}</div></div>
      ${caseGrid(list, l)}
    </div>
  </section>`;
// a client the founder named, as a case's card (one card for both since 2026-11-28): its 3D object, its figure (without
// one, its name), who it is, what we did; the whole card goes to its field page (go) or its own website, if either
const clientCard = (c, i, go = null) => {
  const name = typeof c.name === 'string' ? esc(c.name) : t(c.name), fig = c.n !== undefined;
  const href = go ? go.href : c.url, tag = href ? 'a' : 'article';
  return `<${tag} class="mx-card mx-stat pg-case${fig ? '' : ' pg-noun'}"${href ? ` href="${href}"${go ? '' : ' rel="noopener" target="_blank"'}` : ''} data-r style="--d:${i % 3}">
          <img class="bob" style="--dur:${6.2 + (i % 6) * 0.5}s;--delay:-${(i % 6) * 1.2}s;--amp:-10px" src="${asset(c.obj + '-mix.webp')}" alt="" width="400" height="400" loading="lazy">
          <p class="n${fig ? ' num' : ''}">${fig ? count(c.n, c.unit, c.en) : name}</p>
          <p class="who">${fig ? `${name} · ` : ''}${t(c.kind)}</p>
          ${tx('p', 'd', c.d)}${href ? `
          <span class="pg-case-go">${go ? t(go.label) : esc(new URL(c.url).host)}${ARROW}</span>` : ''}
        </${tag}>`;
};
// columns for a grid of n cards: one, two, or three to a row (site.css centres a last row that is not full)
const colsFor = n => Math.min(n, 3);
// real clients in one section (the founder, 2026-11-28: the cases and "Ügyfeleink" were two categories for one thing):
// the cases first, each going to its page, then the clients the founder named. fields: each client card goes to the
// field page that names it (the hub). The id is the one the hub's clients had (the link sent to the founder).
const proofSec = (cases, ids = [], l, { h2 = CW.worked, eyebrow = C.results.eyebrow, fields = false } = {}) => {
  const n = cases.length + ids.length;
  if (!n) return '';
  const field = id => fields && INDUSTRIES.find(x => (x.clients || []).includes(id));
  return `  <!-- real clients: the cases, each going to its page, and the clients the founder named, as one set of cards -->
  <section class="mx-res pg-res" id="ugyfelek" aria-labelledby="cl-h">
    <div class="wrap">
      <div class="mx-head row"><div>${tx('p', 'mx-eyebrow', eyebrow, 'data-r')}${tx('h2', 'mx-h2', h2, 'id="cl-h" data-r')}</div></div>
      <div class="mx-stats pg-proof-grid c${colsFor(n)}">
        ${[...cases.map((x, i) => caseCard(x, l, { link: true, i })),
          ...ids.map((id, k) => { const f = field(id); return clientCard(CLIENTS[id], cases.length + k, f ? { href: f.path[l], label: f.crumb } : null); })].join('\n        ')}
      </div>
    </div>
  </section>`;
};
// what we do for a named client (the founder's own list), beside its heading, as a service's list is shown
const didSec = pg => pg.did ? `  <!-- what we do for this client -->
  <section class="pg-incl" aria-labelledby="did-h">
    <div class="wrap pg-split">
      <div class="pg-split-l">
        ${tx('p', 'mx-eyebrow', { hu: 'A munka', en: 'The work' }, 'data-r')}
        ${tx('h2', 'mx-h2', { hu: 'Mit csinálunk nekik?', en: 'What we do for them' }, 'id="did-h" data-r')}
      </div>
      <ul class="mx-card checks pg-checks" data-r style="--d:1">${pg.did.map(x => tx('li', '', x)).join('')}</ul>
    </div>
  </section>` : '';
// the services a case took (or a field needs), as the services' cards; fit: all in one row on a wide screen (the fields)
const used = (pg, l, h2 = CW.used, fit = false) => pg.uses ? `  <!-- the services this case took -->
  <section class="pg-more pg-used" aria-labelledby="used-h">
    <div class="wrap">
      <div class="mx-head">${tx('p', 'mx-eyebrow', W.more, 'data-r')}${tx('h2', 'mx-h2', h2, 'id="used-h" data-r')}</div>
      <ul class="pg-more-grid few${fit ? ` fit" style="--n:${pg.uses.length}` : ''}">
        ${pg.uses.map(byId).map((x, i) => `<li data-r style="--d:${i}"><a class="mx-card pg-more-card" href="${x.path[l]}"><img class="bob" style="--dur:${5.4 + i * 0.5}s;--delay:-${i}s;--amp:-8px" src="${asset(x.s.icon + '-mix.webp')}" alt="" width="520" height="520" loading="lazy"><span class="k">${t(x.crumb)}</span><span class="d">${t(pair(x.s.t))}</span>${ARROW}</a></li>`).join('\n        ')}
      </ul>
    </div>
  </section>` : '';

// the name: the claim, as the film says it, and why the name still says social (About us, and the interest media page)
const nameSec = eyebrow => `  <!-- the name: the claim, as the film says it, and why the name still says social -->
  <section class="pg-name" aria-labelledby="name-h">
    <div class="wrap">
      ${tx('p', 'mx-eyebrow', eyebrow, 'data-r')}
      <h2 class="claim pg-claim" id="name-h" data-r>${twin(per(C.claim, a => a.map(x => `<span class="ln">${x}</span>`).join(' ')))}</h2>
      ${tw('p', 'pg-name-p', C.name, 'data-r')}
    </div>
  </section>`;
// the lead's three verbs as three floating objects, joined by lines of light (site.js, after Magic UI's Animated
// Beam): we make the video, we run the ads, we measure what they brought (the services page, the interest media page)
const flowArt = () => `<div class="pg-cluster pg-flow" data-beams>
          <svg class="pg-beams" aria-hidden="true" focusable="false"><defs><linearGradient id="pg-beam-g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7660ff"/><stop offset="1" stop-color="#ff4d6d"/></linearGradient></defs><path class="base" data-from="0" data-to="1" data-bend="0.2"/><path class="run b0" data-from="0" data-to="1" data-bend="0.2" pathLength="100"/><path class="base" data-from="1" data-to="2" data-bend="0.2"/><path class="run b1" data-from="1" data-to="2" data-bend="0.2" pathLength="100"/></svg>
          ${obj('i-video-mix.webp', 'c1', 0.035, 6.2)}${obj('i-ads-mix.webp', 'c2', -0.03, 5.6)}${obj('i-strat-mix.webp', 'c3', 0.05, 7)}
          <span class="pg-flow-l l1">${t({ hu: 'Videó', en: 'Video' })}</span><span class="pg-flow-l l2">${t({ hu: 'Hirdetés', en: 'Ads' })}</span><span class="pg-flow-l l3">${t({ hu: 'Mérés', en: 'Measurement' })}</span>
        </div>`;
// the fields we work in, as cards that go to their pages (the home page's "who it is for", each with its page)
const fieldsSec = l => `  <!-- the fields we work in, each card going to its page -->
  <section class="pg-fields" id="teruletek" aria-labelledby="fields-h">
    <div class="wrap">
      <div class="mx-head center">${tx('p', 'mx-eyebrow', CW.fieldsEyebrow, 'data-r')}${tx('h2', 'mx-h2', CW.fields, 'id="fields-h" data-r')}</div>
      <ul class="pg-fields-grid">
        ${INDUSTRIES.map((x, i) => `<li data-r style="--d:${i % 3}"><a class="mx-card pg-field" href="${x.path[l]}"><img class="bob" style="--dur:${6 + i * 0.5}s;--delay:-${i}s;--amp:-12px" src="${asset(x.art + '-mix.webp')}" alt="" width="640" height="560" loading="lazy"><span class="k">${t(x.crumb)}</span><span class="d">${h(x.card)}</span><span class="pg-case-go">${t(W.details)}${ARROW}</span></a></li>`).join('\n        ')}
      </ul>
      ${tx('p', 'mx-notfor', C.who.notfor, 'data-r')}
    </div>
  </section>`;

// ---------- the templates ----------

const T = {
  home: (pg, l) => head({ title: plain(word(pg.title, l)), desc: word(pg.desc, l), fonts: mix.FONTS, css: ['mix.css', 'site.css'], theme: mix.THEME, seo: seo(pg, l) })
    + nav('mx-nav', { ground: 'dark', film: true, site: siteNav(pg, l) }) + mix.main(homeLinks(l))
    + footer('mx-foot', true, true, siteFoot(l)) + scripts(SITE_SCRIPTS),

  hub: (pg, l) => shell(pg, l, [
    hero(pg, l, flowArt()),
    mix.painsSec(it => SERVICES.find(x => x.svc === it.id).path[l]),
    mix.servicesSec({ href: it => SERVICES.find(x => x.svc === it.id).path[l], label: W.details }),
    mix.compareSec(), mix.stepsSec(), mix.offerSec(),
  ]),

  service: (pg, l) => { const pr = pg.proof || {}; return shell(pg, l, [
    hero(pg, l, `<div class="pg-obj">${obj(pg.s.icon + '-mix.webp', '', 0.035, 6.4)}</div>`, { band: pg.svc === 'ads' || pg.svc === 'strat' ? 'ticker' : 'tags' }),
    pain(pg), included(pg),
    pr.stats ? stats(l) : '', pr.named ? caseSec(pr.named.map(f => byId(f.page)), l, CW.named, { id: 'fiokok' }) : '',
    proofSec([], pg.clients, l, { h2: CW.sites, eyebrow: CW.clientsEyebrow }),
    pr.reels ? reels(pr.reels) : '', pr.quotes ? quotes(pr.quotes) : '', pr.compare ? mix.compareSec() : '',
    mix.stepsSec(), faqBlock(pg.faq, l), more(pg, l), mix.offerSec(),
  ]); },

  cases: (pg, l) => shell(pg, l, [
    hero(pg, l, `<div class="pg-cluster">${obj('o-hall-mix.webp', 'c1', 0.035, 6.2)}${obj('o-door-mix.webp', 'c2', -0.03, 5.6)}${obj('o-webinar-mix.webp', 'c3', 0.05, 7)}</div>`),
    caseSec(CASES, l, CW.pick, { id: 'esetek' }),
    quotes(CASES.filter(x => x.quote != null).map(x => x.quote)),
    mix.stepsSec(), mix.offerSec(),
  ]),

  case: (pg, l) => shell(pg, l, [
    hero(pg, l, `<div class="pg-case-art">${caseCard(pg, l, { hero: true })}</div>`),
    // a short list of reels is repeated so the running row fills the screen
    didSec(pg), pg.quote != null ? quotes([pg.quote]) : '', pg.reels ? reels(Array.from({ length: Math.max(1, Math.ceil(8 / pg.reels.length)) }, () => pg.reels).flat()) : '',
    used(pg, l), caseSec(CASES.filter(x => x !== pg), l, CW.more, { eyebrow: { hu: 'Esettanulmányok', en: 'Case studies' } }), mix.offerSec(),
  ]),

  about: (pg, l) => shell(pg, l, [
    hero(pg, l, `<dl class="pg-facts">${pg.facts.map((f, i) => `<div class="mx-card bob" style="--dur:${6 + i * 0.6}s;--delay:-${i * 1.1}s;--amp:-8px"><dt>${t(f.l)}</dt><dd class="num">${typeof f.n === 'string' ? esc(f.n) : t(f.n)}</dd></div>`).join('')}</dl>`),
    nameSec(pg.name.eyebrow),
    mix.teamSec(pg.teamWhere), mix.stepsSec(), mix.whoSec(), mix.offerSec(),
  ]),

  // what interest media is: the definition on the first screen, the claim, what goes wrong without it and which
  // service answers, then our clients' organic numbers and the results
  explainer: (pg, l) => shell(pg, l, [
    hero(pg, l, flowArt(), { band: 'tags' }),
    nameSec(CW.why),
    mix.painsSec(it => SERVICES.find(x => x.svc === it.id).path[l]),
    // the organic accounts first, then the paid results: one section since 2026-11-28 (it was two, with one eyebrow twice)
    caseSec(built(['case-flyx', 'case-enzo', 'case-door', 'case-hall', 'case-watch', 'case-webinar']), l, C.results.h2, { id: 'eredmenyek' }),
    faqBlock(pg.faq, l), mix.offerSec(),
  ]),

  // the fields we work in, each card going to its page
  audiences: (pg, l) => shell(pg, l, [
    hero(pg, l, `<div class="pg-cluster">${obj('a-shop-mix.webp', 'c1', 0.035, 6.2, 640, 560)}${obj('a-b2b-mix.webp', 'c2', -0.03, 5.6, 640, 560)}${obj('a-events-mix.webp', 'c3', 0.05, 7, 640, 560)}</div>`),
    fieldsSec(l),
    // every case and every client on the hub too (the founder, 2026-11-27: "they are not under the kikkel dolgozunk"),
    // in one section (2026-11-28)
    proofSec(built(PAGES.filter(x => x.type === 'case').map(x => x.id)), HUB_CLIENTS, l, { fields: true }),
    mix.stepsSec(), mix.offerSec(),
  ]),

  // one field: its problems (each to its service), its cases, its clients' words and clips, the services, questions
  industry: (pg, l) => shell(pg, l, [
    hero(pg, l, `<div class="pg-obj">${obj(pg.art + '-mix.webp', '', 0.035, 6.4, 640, 560)}</div>`),
    mix.painsSec(it => SERVICES.find(x => x.svc === it.id).path[l], pg.pains),
    proofSec(built(pg.cases), pg.clients, l),
    pg.quotes ? quotes(pg.quotes) : '',
    // a short list of reels is repeated so the running row fills the screen
    pg.reels ? reels(Array.from({ length: Math.max(1, Math.ceil(8 / pg.reels.length)) }, () => pg.reels).flat()) : '',
    used(pg, l, CW.forIt, true), faqBlock(pg.faq, l), mix.offerSec(),
  ]),

  audit: (pg, l) => { const tr = trail(pg), o = C.offer; return shell(pg, l, [
    `  <!-- the first screen is the offer and the form, in a panel -->
  <section class="pg-hero pg-audit" id="top" aria-labelledby="pg-h">
    <div class="mx-panel pg-panel">
      <div class="mx-sky" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><i class="b4"></i><span class="mx-glow" data-follow="in" data-home="0.3,0.4"></span></div>
      <div class="pg-hero-in">
        <div class="pg-copy">
          <nav class="pg-crumbs"${ar(W.crumbs)}><ol>${tr.map((x, i) => i < tr.length - 1 ? `<li><a href="${x.path[l]}">${t(x.crumb)}</a></li>` : `<li aria-current="page">${t(x.crumb)}</li>`).join('')}</ol></nav>
          <h1 class="pg-h1" id="pg-h"><span class="pg-k">${t(pg.h1k)}<span class="sr">:</span></span> <span class="pg-t">${h(pg.h1t)}</span></h1>
          <p class="pg-lead">${h(pg.lead)}</p>
          <ul class="checks">${o.checks.map(c => tx('li', '', c)).join('')}</ul>
          <dl class="specs">${o.specs.map(([dt, dd]) => `<div><dt>${t(pair(dt))}</dt><dd>${t(pair(dd))}</dd></div>`).join('')}</dl>
          <p class="scarce"><i aria-hidden="true"></i><span>${t(o.scarce)}</span></p>
        </div>
        <div class="mx-form pg-form" id="audit">${form()}</div>
      </div>
      <div class="mx-band">${rail(tickerItems('mx-tk'), 'mx-band-rail', 1, 46)}</div>
    </div>
  </section>`,
    faqBlock(pg.faq, l), stats(l), mix.stepsSec(),
  ]); },

  faq: (pg, l) => { let n = 0; return shell(pg, l, [
    hero(pg, l, `<ul class="pg-index">${pg.groups.map((g, i) => `<li class="bob" style="--dur:${6 + i * 0.5}s;--delay:-${i}s;--amp:-6px"><a class="mx-card" href="#${g.id}"><span class="k">${t(g.h)}</span><span class="d num">${g.items.length}</span></a></li>`).join('')}</ul>`, { band: 'tags' }),
    ...pg.groups.map(g => { const s = n; n += g.items.length; return `  <!-- ${esc(plain(g.h.hu))} -->
  <section class="pg-qgroup" id="${g.id}" aria-labelledby="${g.id}-h">
    <div class="wrap pg-split">
      <div class="pg-split-l">${tx('h2', 'mx-h2', g.h, `id="${g.id}-h" data-r`)}</div>
      <div class="faq-list mx-faq-list" data-r>
${qa(g.items, l, s)}
      </div>
    </div>
  </section>`; }),
    mix.offerSec(),
  ]); },

  contact: (pg, l) => { const c = pg.cards; return shell(pg, l, [
    hero(pg, l, `<div class="pg-contact">
          <div class="mx-card pg-c-mail bob" style="--dur:6.4s;--amp:-8px">${tx('p', 'k', c.mail)}<a class="v" href="mailto:hello@socialstream.hu">hello@socialstream.hu</a><button type="button" class="copy-mini" data-copy="hello@socialstream.hu">${t({ hu: 'Cím másolása', en: 'Copy address' })}</button></div>
          <div class="mx-card pg-c-where bob" style="--dur:7.2s;--delay:-2s;--amp:-8px">${tx('p', 'k', c.where)}${tx('p', 'v', c.places)}</div>
          <a class="mx-card pg-c-audit bob" style="--dur:5.8s;--delay:-1s;--amp:-8px" href="#audit">${tx('span', 'k', c.audit)}<span class="v">${C.ticks.map(x => t(x)).join(' · ')}</span>${ARROW}</a>
        </div>`),
    mix.offerSec(),
  ]); },
};

export function renderPage(pg, l) {
  render({ lang: l, root: '/', word, film: k => filmSrc(l, k) });
  try { return T[pg.type](pg, l); } finally { render({}); }
}
