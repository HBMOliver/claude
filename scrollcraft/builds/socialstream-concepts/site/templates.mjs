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
import { render, esc, t, h, ar, twin, asset, tx, tw, pair, btn, head, scripts, nav, footer, rail, tagItems, tickerItems, form, ARROW } from '../parts.mjs';
import * as mix from '../concepts/mix.mjs';
import { PAGES, NAV, W, byId } from './pages.mjs';
import { seo, trail } from './head.mjs';

const SERVICES = PAGES.filter(pg => pg.type === 'service');
const plain = s => String(s).replace(/<[^>]+>/g, '');

const siteNav = (pg, l) => ({
  home: byId('home').path[l],
  links: NAV.map(x => ({ href: x.path[l], label: x.nav, current: x.id === pg.id })),
  alt: pg.path, menu: W.menu,
});
const siteFoot = l => ({
  home: byId('home').path[l], line: W.line,
  groups: [
    { label: W.more, links: [{ href: byId('services').path[l], label: { hu: 'Minden szolgáltatás', en: 'All services' } }, ...SERVICES.map(pg => ({ href: pg.path[l], label: pg.crumb }))] },
    { label: W.pagesGroup, links: ['about', 'audit', 'faq', 'contact'].map(id => ({ href: byId(id).path[l], label: byId(id).crumb })) },
  ],
});

function shell(pg, l, body, film = false) {
  return head({ title: plain(pg.title[l]), desc: pg.desc[l], fonts: mix.FONTS, css: ['mix.css', 'site.css'], theme: mix.THEME, seo: seo(pg, l) })
    + nav('mx-nav', { ground: 'dark', film, site: siteNav(pg, l) })
    + `\n<main>\n${body.filter(Boolean).join('\n\n')}\n</main>\n`
    + footer('mx-foot', true, true, siteFoot(l)) + scripts(mix.PAGE_SCRIPTS);
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

// the results as stat cards (the home page's)
const stats = () => `  <!-- results: the four stat cards, counting up -->
  <section class="mx-res pg-res" id="eredmenyek" aria-labelledby="res-h">
    <div class="wrap">
      <div class="mx-head row">
        <div>${tx('p', 'mx-eyebrow', C.results.eyebrow, 'data-r')}${tx('h2', 'mx-h2', C.results.h2, 'id="res-h" data-r')}</div>
      </div>
      ${mix.statCards()}
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

// ---------- the templates ----------

const T = {
  home: (pg, l) => head({ title: plain(pg.title[l]), desc: pg.desc[l], fonts: mix.FONTS, css: ['mix.css', 'site.css'], theme: mix.THEME, seo: seo(pg, l) })
    + nav('mx-nav', { ground: 'dark', film: true, site: siteNav(pg, l) }) + mix.main()
    + footer('mx-foot', true, true, siteFoot(l)) + scripts(mix.PAGE_SCRIPTS),

  hub: (pg, l) => shell(pg, l, [
    hero(pg, l, `<div class="pg-cluster">${obj('i-video-mix.webp', 'c1', 0.035, 6.2)}${obj('i-ads-mix.webp', 'c2', -0.03, 5.6)}${obj('i-social-mix.webp', 'c3', 0.05, 7)}</div>`),
    mix.painsSec(it => SERVICES.find(x => x.svc === it.id).path[l]),
    mix.servicesSec({ href: it => SERVICES.find(x => x.svc === it.id).path[l], label: W.details }),
    mix.compareSec(), mix.stepsSec(), mix.offerSec(),
  ]),

  service: (pg, l) => { const pr = pg.proof || {}; return shell(pg, l, [
    hero(pg, l, `<div class="pg-obj">${obj(pg.s.icon + '-mix.webp', '', 0.035, 6.4)}</div>`, { band: pg.svc === 'ads' || pg.svc === 'strat' ? 'ticker' : 'tags' }),
    pain(pg), included(pg),
    pr.stats ? stats() : '', pr.reels ? reels(pr.reels) : '', pr.quotes ? quotes(pr.quotes) : '', pr.compare ? mix.compareSec() : '',
    mix.stepsSec(), faqBlock(pg.faq, l), more(pg, l), mix.offerSec(),
  ]); },

  about: (pg, l) => shell(pg, l, [
    hero(pg, l, `<dl class="pg-facts">${pg.facts.map((f, i) => `<div class="mx-card bob" style="--dur:${6 + i * 0.6}s;--delay:-${i * 1.1}s;--amp:-8px"><dt>${t(f.l)}</dt><dd class="num">${typeof f.n === 'string' ? esc(f.n) : t(f.n)}</dd></div>`).join('')}</dl>`),
    `  <!-- the name: the claim, as the film says it, and why the name still says social -->
  <section class="pg-name" aria-labelledby="name-h">
    <div class="wrap">
      ${tx('p', 'mx-eyebrow', pg.name.eyebrow, 'data-r')}
      <h2 class="claim pg-claim" id="name-h" data-r>${twin({ hu: C.claim.hu.map(x => `<span class="ln">${x}</span>`).join(' '), en: C.claim.en.map(x => `<span class="ln">${x}</span>`).join(' ') })}</h2>
      ${tw('p', 'pg-name-p', C.name, 'data-r')}
    </div>
  </section>`,
    mix.teamSec(pg.teamWhere), mix.stepsSec(), mix.whoSec(), mix.offerSec(),
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
    faqBlock(pg.faq, l), stats(), mix.stepsSec(),
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
  render({ lang: l, root: '/' });
  try { return T[pg.type](pg, l); } finally { render({}); }
}
