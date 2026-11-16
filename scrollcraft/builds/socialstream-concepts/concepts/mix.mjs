// Aurora Mix. Aurora's look (night blue, a moving aurora, glass; Sora with Instrument Serif italics) laid out the
// way Scrolla is. It opens on the film alone, which settles into its card as the page scrolls; then the first screen
// in an inset rounded panel with the claim on the left and the film standing on
// the right like a post, the real numbers running along the panel's foot; the statement with their reels closing
// in from the sides; the problems; services as big-object cards in a panel over two running rows of tags; results
// as stat cards with a running row of reel frames; the elsewhere/with-us cards laid over each other; big numbered
// steps; who it is for in a panel; their words in a row the visitor scrolls; the team on photo cards; the offer;
// questions; the last call in a panel and the giant wordmark. With a mouse, the aurora's brightest light follows
// the cursor round the first screen, the reels and the service objects lean toward it, and the buttons are pulled
// toward it.
import { C } from '../content.mjs';
import { esc, t, en, ar, twin, asset, lang, tx, tw, pair, toSvc, btn, head, scripts, nav, claim, promise, film, rail, tagItems, tickerItems, count, form, offerCopy, faqList, footer } from '../parts.mjs';

// labels that only this page has (Hungarian, English); listed in COPY.md as new
const LB = {
  film: { hu: 'Márkafilm', en: 'Brand film' },
  prev: { hu: 'Előző vélemény', en: 'Previous review' },
  next: { hu: 'Következő vélemény', en: 'Next review' },
};
const ARR = dir => `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="${dir < 0 ? 'M14 8H3M7 3.5 2.5 8 7 12.5' : 'M2 8h11M9 3.5 13.5 8 9 12.5'}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
// the reels that close in on the statement: [reel, side (-1 left, 1 right), how far it leans toward the cursor].
// Since 2026-11-15 they and the rail are short silent loops that look like reels (a progress bar, the side icons,
// whose post it is), mixing new faces (Up To Youth, the Latvia challenge, Bálint's Miskolc Plaza reel and Nike spec
// ad, Prof Enzo, Sóskút, the Türkiye film; the founder has their consent), since 2026-11-16 two smartwatch ads the
// founder found and cleared for the site, and a few of the FlyX and András reels.
// Their captions are the clients' own, or words from the source: what is said in the clip, the film's own subtitles,
// the spec ad's end lines laid over its shots, and since 2026-11-16 event titles on Up To Youth's Latvia clips (cut by
// tools/reels.py, see README). f1 and f4 hide on tablets (761-1080 px), so those two are the old ones. The two big ones on
// top are the smartwatch creator's ad and Prof Enzo since 2026-11-16: the founder found the Türkiye close-up and the
// Latvia sunset there not like ads or social content (the sunset went to the rail with an event title).
const FLY = [['r-watch-1', -1, 0.04], ['r-andras-1', -1, -0.03], ['r-uty', -1, 0.06], ['r-enzo-2', 1, -0.04], ['r-flyx-1', 1, 0.05], ['r-miskolc', 1, 0.03]];
const RAIL = ['r-lv-yellow', 'r-nike-1', 'r-flyx-2', 'r-lv-sunset', 'r-enzo-1', 'r-soskut', 'r-lv-hoodie', 'r-andras-2', 'r-nike-2', 'r-tr-friends', 'r-lv-cap', 'r-watch-2', 'r-flyx-3'];
// whose post each reel is: [name, kind] with kind 0 = an account (its initial in a ring), 1 = a place (a pin),
// 2 = no badge (the spec ads, which belong to no client, and the smartwatch ads, whose brand the site does not name:
// whether it is the watch webshop of the results is not confirmed, and that client stays unnamed)
const WATCH_AD = { hu: 'Okosóra hirdetés', en: 'Smartwatch ad' };
const WHO = {
  'r-uty': ['Up to Youth', 0], 'r-miskolc': ['Miskolc Plaza', 0], 'r-soskut': ['Bridle Up Hope', 0],
  'r-enzo-1': ['Prof Enzo', 0], 'r-enzo-2': ['Prof Enzo', 0], 'r-andras-1': ['Gyenis András', 0], 'r-andras-2': ['Gyenis András', 0],
  'r-flyx-1': ['FlyX Tenerife', 0], 'r-flyx-2': ['FlyX Tenerife', 0], 'r-flyx-3': ['FlyX Tenerife', 0],
  // the Latvia clips are Up To Youth's (their event at Bernāti, June 2025), and the Türkiye film (Kemer) is DELSAS's,
  // the Democracy And Law Studies Association (instagram.com/delsas01): the founder, 2026-11-16
  'r-lv-sunset': ['Up to Youth', 0], 'r-lv-yellow': ['Up to Youth', 0], 'r-lv-hoodie': ['Up to Youth', 0], 'r-lv-cap': ['Up to Youth', 0],
  'r-tr-smile': ['DELSAS', 0], 'r-tr-friends': ['DELSAS', 0],
  'r-nike-1': [{ hu: 'Spec hirdetés', en: 'Spec ad' }, 2], 'r-nike-2': [{ hu: 'Spec hirdetés', en: 'Spec ad' }, 2],
  'r-watch-1': [WATCH_AD, 2], 'r-watch-2': [WATCH_AD, 2],
};
const ICO = {
  heart: 'M12 20.3 10.6 19C5.4 14.3 2 11.2 2 7.5 2 4.4 4.4 2 7.5 2c1.7 0 3.4.8 4.5 2.1C13.1 2.8 14.8 2 16.5 2 19.6 2 22 4.4 22 7.5c0 3.7-3.4 6.8-8.6 11.5z',
  chat: 'M21 11.5a8.5 8.5 0 0 1-12.4 7.6L3 21l1.9-5.6A8.5 8.5 0 1 1 21 11.5z',
  send: 'M22 3 9.5 15.5M22 3l-7 19-5.5-6.5L3 10z',
  pin: 'M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12zm0-9.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
};
const ico = d => `<svg viewBox="0 0 24 24"><path d="${d}"/></svg>`;
// a reel: the poster (lazy) under a silent loop that reels.js loads and plays only while it is on screen
export const rv = id => {
  const [name, kind] = WHO[id];
  const badge = kind === 1 ? `<i class="pin">${ico(ICO.pin)}</i>` : kind === 0 ? `<i>${esc(name[0])}</i>` : '';
  const label = typeof name === 'string' ? `<b>${esc(name)}</b>` : tx('b', '', name);
  return `<figure class="reel rv" aria-hidden="true"><img src="${asset(id + '.jpg')}" alt="" width="486" height="864" loading="lazy" decoding="async"><video muted playsinline loop preload="none" data-src="${asset(id + '.mp4')}" width="360" height="640"></video><span class="rv-bar"><i></i></span><span class="rv-side">${ico(ICO.heart)}${ico(ICO.chat)}${ico(ICO.send)}</span><span class="rv-who">${badge}${label}</span></figure>`;
};

// the fonts and the browser bar's colour, shared with the site's pages (site/)
export const FONTS = 'family=Sora:wght@500..800&family=Inter:wght@400..700&family=Instrument+Serif:ital@1&family=Fraunces:ital,opsz,wght@0,9..144,400;1,9..144,400';
export const THEME = '#05070f';
// the two facts beside the statement, and a client's number above their words (the English page's in euros)
const F300 = { hu: '300M+ Ft', en: '€820K+' }, FSINCE = { hu: 'kezelt büdzsé 2022 óta', en: 'budget managed since 2022' };
const metricN = m => lang() ? `<b class="num">${esc(lang() === 'en' && m.n_en ? m.n_en : m.n)}</b>` : `<b class="num"${m.n_en ? ` data-en="${esc(m.n_en)}"` : ''}>${esc(m.n)}</b>`;

// The page's parts, one function each, so the site's other pages (site/templates.mjs) can use them as they are.
// Each returns its section with the comment before it, indented as it sits in <main>.

export const heroSec = () => `  <!-- the opening: the film alone fills the first screen (it carries the claim itself, about eight seconds in). Scrolling
       on, where the screen has room to pin, the film settles into its card beside the claim while the panel, the claim
       and the numbers come in around it; on phones and short screens the panel rises over the film like a sheet.
       kit.js drives it all from one value, --q; without script or with reduced motion the page opens on the panel.
       The panel: the claim on the left, the film standing on the right like a post, the real numbers running along
       its foot; the aurora moves inside, and its brightest light follows the cursor -->
  <section class="mx-hero" id="top" aria-labelledby="hero-h" data-seq="(min-width: 900px) and (min-height: 700px)">
    <div class="mx-open" data-seq-open>
      ${film('mx-openfilm', 'auto', true, `
  <span class="mx-cue" aria-hidden="true"><i></i></span>`)}
    </div>
    <div class="mx-panel mx-hero-panel">
      <div class="mx-sky" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><i class="b4"></i><span class="mx-glow" data-follow="in" data-home="0.3,0.42"></span></div>
      <div class="mx-hero-in">
        <div class="mx-copy">
          <p class="mx-pill"><i aria-hidden="true"></i><span${en(C.eyebrow)}>${t(C.eyebrow)}</span></p>
          ${claim('mx-claim')}
          ${promise('mx-promise')}
          <div class="mx-cta">${btn()}${btn(C.ctaResults, 'btn ghost', '#eredmenyek')}</div>
        </div>
        <div class="mx-post" data-seq-to>
          ${film('mx-film', 'v', false, `
  <div class="progress" aria-hidden="true"></div>
  <p class="mx-acct" aria-hidden="true"><img src="${asset('socialstream-symbol-corner.svg')}" alt="" width="34" height="34">SocialStream</p>
  <p class="mx-fcap" aria-hidden="true"${en(LB.film)}>${t(LB.film)}</p>`)}
        </div>
      </div>
      <div class="mx-band">${rail(tickerItems('mx-tk'), 'mx-band-rail', 1, 46)}</div>
    </div>
  </section>`;

export const saySec = () => `  <!-- what we do, lighting as it is read, while their reels close in from both sides -->
  <section class="mx-say" aria-labelledby="say-h" data-drift>
    <div class="mx-fly" aria-hidden="true">
      ${FLY.map(([id, side, k], i) => `<div class="mx-f f${i}" style="--side:${side}"><div class="mx-f-lean" data-follow data-k="${k}"><div class="bob">${rv(id)}</div></div></div>`).join('\n      ')}
    </div>
    <div class="wrap">
      <h2 class="mx-statement" id="say-h" data-lit>${twin({ hu: esc(C.lead1.hu), en: esc(C.lead1.en) })}</h2>
      <p class="mx-facts" data-r><span><b class="num"${en(F300)}>${t(F300)}</b> <span${en(FSINCE)}>${t(FSINCE)}</span></span>${tx('span', '', C.final.small)}</p>
    </div>
  </section>`;

// href: where each problem's link goes (its card on this page, or on the site its service's own page)
export const painsSec = (href = it => `#svc-${it.id}`) => { const s = C.services, p = C.problem; return `  <!-- what goes wrong for a business, each problem joined by a running line of light to the service that answers
       it (new, to confirm) -->
  <section class="mx-pains" aria-labelledby="prob-h">
    <div class="mx-sky low" aria-hidden="true"><i class="b2"></i></div>
    <div class="wrap">
      <div class="mx-head center">
        ${tx('p', 'mx-eyebrow', C.pains.eyebrow, 'data-r')}
        ${tw('h2', 'mx-h2', { hu: p.h2.hu.join(' '), en: p.h2.en.join(' ') }, 'id="prob-h" data-r')}
        ${tx('p', 'mx-sub', p.body, 'data-r')}
      </div>
      <ul class="mx-pain-list">
        ${s.items.map((it, i) => `<li class="mx-card mx-pain" data-r style="--d:${i % 2};--flow:-${(i * 0.55).toFixed(2)}s">
          ${tx('p', 'q', pair(it.pain))}
          <span class="mx-pain-line" aria-hidden="true"></span>
          <div class="mx-pain-to">
            <img class="bob" style="--dur:${5.2 + i * 0.4}s;--delay:-${i * 0.9}s;--amp:-8px" src="${asset(it.icon + '-mix.webp')}" alt="" width="520" height="520" loading="lazy">
            ${toSvc(it, 'a', href(it))}
          </div>
        </li>`).join('\n        ')}
      </ul>
    </div>
  </section>`; };

// more: on the site, a link from each card to its service's own page ({ href(it), label })
export const servicesSec = (more = null) => { const s = C.services; return `  <!-- services in a panel: each one's object large on its card, two rows of tags running underneath -->
  <section class="mx-svc" id="szolgaltatasok" aria-labelledby="svc-h">
    <div class="mx-panel">
      <div class="mx-sky low" aria-hidden="true"><i class="b1"></i><i class="b4"></i></div>
      <div class="wrap">
        <div class="mx-head center">
          ${tx('p', 'mx-eyebrow', s.eyebrow, 'data-r')}
          ${tw('h2', 'mx-h2', s.h2, 'id="svc-h" data-r')}
        </div>
        <div class="mx-svc-grid">
          ${s.items.map((it, i) => `<article class="mx-card mx-svc-card" id="svc-${it.id}" data-r style="--d:${i % 3};--spin:-${(i * 1.3).toFixed(1)}s">
            <div class="mx-obj"><img class="bob" data-follow data-k="${[0.02, -0.025, 0.03][i % 3]}" style="--dur:${5.6 + i * 0.45}s;--delay:-${i * 0.8}s;--amp:-12px" src="${asset(it.icon + '-mix.webp')}" alt="" width="520" height="520" loading="lazy"></div>
            ${more ? `<h3><a class="pg-card-link" href="${more.href(it)}">${t(pair(it.k))}</a></h3>` : tx('h3', '', pair(it.k))}
            ${tx('p', 'h', pair(it.t))}
            ${tx('p', 'd', pair(it.p))}${more ? `
            <p class="pg-more-l" aria-hidden="true"><span>${t(more.label)}</span>${ARR(1)}</p>` : ''}
          </article>`).join('\n          ')}
        </div>
      </div>
      <div class="mx-tags">
        ${rail(tagItems('mx-tag'), 'mx-tag-rail', 1, 34)}
        ${rail(tagItems('mx-tag alt'), 'mx-tag-rail', -1, 28)}
      </div>
    </div>
  </section>`; };

// the four stat cards alone (the site's paid-advertising page shows them too)
export const statCards = () => `<div class="mx-stats">
        ${C.results.items.map((it, i) => `<article class="mx-card mx-stat" data-r style="--d:${i}">
          <img class="bob" style="--dur:${6.2 + i * 0.5}s;--delay:-${i * 1.2}s;--amp:-10px" src="${asset(it.obj + '-mix.webp')}" alt="" width="400" height="400" loading="lazy">
          <p class="n num">${count(it.n, it.unit, it.en)}</p>
          ${tx('p', 'who', pair(it.who))}
          ${tx('p', 'd', pair(it.p))}
        </article>`).join('\n        ')}
      </div>`;
export const resultsSec = () => { const r = C.results; return `  <!-- results: four stat cards that count up, then a row of reel frames that keeps running -->
  <section class="mx-res" id="eredmenyek" aria-labelledby="res-h">
    <div class="wrap">
      <div class="mx-head row">
        <div>${tx('p', 'mx-eyebrow', r.eyebrow, 'data-r')}${tx('h2', 'mx-h2', r.h2, 'id="res-h" data-r')}</div>
        <div data-r>${btn(r.cta)}</div>
      </div>
      ${statCards()}
    </div>
    <div class="mx-reels">
      <div class="wrap mx-reels-head">${tw('h3', 'mx-h3', C.reels.h2, 'data-r')}${tx('p', 'mx-cap', C.reels.caption, 'data-r')}</div>
      ${rail(RAIL.map(rv).join(''), 'mx-reel-rail', 1, 40)}
    </div>
  </section>`; };

export const compareSec = () => { const cp = C.compare; return `  <!-- elsewhere and with us: two cards, ours laid over theirs (new arrangement, to confirm) -->
  <section class="mx-cmp-sec" aria-labelledby="cmp-h">
    <div class="wrap">
      ${tw('h2', 'mx-h2 center', cp.h2, 'id="cmp-h" data-r')}
      <div class="mx-cmp">
        <div class="mx-card mx-cmp-else" data-r>${tx('p', 'k', cp.elseT)}<ul>${cp.else.map(x => tx('li', '', x)).join('')}</ul></div>
        <div class="mx-card mx-cmp-us" data-r style="--d:1">${tx('p', 'k', cp.usT)}<ul>${cp.us.map(x => tx('li', '', x)).join('')}</ul></div>
      </div>
    </div>
  </section>`; };

export const stepsSec = () => { const st = C.steps; return `  <!-- how we work: four big numbered cards, a light moving slowly through the numbers -->
  <section class="mx-steps" id="igy" aria-labelledby="how-h">
    <div class="wrap">
      <div class="mx-head row">
        <div>${tx('p', 'mx-eyebrow', st.eyebrow, 'data-r')}${tw('h2', 'mx-h2', st.h2, 'id="how-h" data-r')}</div>
        <div data-r>${btn(st.cta)}</div>
      </div>
      <ol class="mx-step-grid">
        ${st.items.map((it, i) => `<li class="mx-card mx-step" data-r style="--d:${i};--sh:-${(i * 1.6).toFixed(1)}s">
          <span class="mx-step-n num" aria-hidden="true">0${i + 1}</span>
          <h3${en({ en: it.en[0] })}>${t({ hu: it.hu[0], en: it.en[0] })}</h3>
          <p${en({ en: it.en[1] })}>${t({ hu: it.hu[1], en: it.en[1] })}</p>
          <ul class="mx-chips">${it.chips.map(c => tx('li', '', pair(c))).join('')}</ul>
        </li>`).join('\n        ')}
      </ol>
    </div>
  </section>`; };

export const whoSec = () => { const w = C.who; return `  <!-- who it is for, in a panel, each card's object floating -->
  <section class="mx-who" id="kiknek" aria-labelledby="who-h">
    <div class="mx-panel">
      <div class="mx-sky low" aria-hidden="true"><i class="b3"></i><i class="b2"></i></div>
      <div class="wrap">
        <div class="mx-head center">
          ${tx('p', 'mx-eyebrow', w.eyebrow, 'data-r')}
          ${tw('h2', 'mx-h2', w.h2, 'id="who-h" data-r')}
          ${tx('p', 'mx-sub', w.lead, 'data-r')}
        </div>
        <div class="mx-who-grid">
          ${w.cards.map((c, i) => `<article class="mx-card" data-r style="--d:${i}">
            <img class="bob" style="--dur:${6 + i * 0.5}s;--delay:-${i}s;--amp:-12px" src="${asset(c.img + '-mix.webp')}" alt="" width="640" height="560" loading="lazy">
            <h3${en({ en: c.en[0] })}>${t({ hu: c.hu[0], en: c.en[0] })}</h3>
            <p>${twin({ hu: c.hu[1], en: c.en[1] })}</p>
          </article>`).join('\n          ')}
        </div>
        ${tx('p', 'mx-notfor', w.notfor, 'data-r')}
      </div>
    </div>
  </section>`; };

// one client's words on a card, their number first where there is one (the site's pages show a few of them too)
export const quote = (q, i) => `<figure class="mx-card mx-q${i === 0 ? ' hot' : ''}">
        ${q.metric ? `<p class="mx-metric">${metricN(q.metric)} <span${en(q.metric)}>${t(q.metric)}</span></p>` : ''}
        <blockquote${en(q)}>${t(q)}</blockquote>
        <figcaption><i aria-hidden="true">${esc(q.who[0].charAt(0))}</i><span${en(pair(q.who))}>${t(pair(q.who))}</span></figcaption>
      </figure>`;
export const voicesSec = () => { const v = C.voices; return `  <!-- their words, in a row the visitor scrolls (or moves with the two arrows); a client's number leads where there is one -->
  <section class="mx-voices" aria-labelledby="vo-h">
    <div class="wrap">
      <div class="mx-head row">
        <div>${tx('p', 'mx-eyebrow', v.eyebrow, 'data-r')}${tw('h2', 'mx-h2', v.h2, 'id="vo-h" data-r')}</div>
        <div class="mx-arrows" data-r>
          <button type="button" data-row-go="-1"${ar(LB.prev)}>${ARR(-1)}</button>
          <button type="button" data-row-go="1"${ar(LB.next)}>${ARR(1)}</button>
        </div>
      </div>
    </div>
    <div class="mx-row" data-row tabindex="0" role="group" aria-labelledby="vo-h">
      ${v.quotes.map(quote).join('\n      ')}
    </div>
  </section>`; };

// the team's cards alone (the site's About us page shows them too)
export const teamCards = () => `<div class="mx-team-grid">
        ${C.team.people.map((m, i) => `<article class="mx-card mx-person" data-r style="--d:${i}">
          <div class="mx-ph"><img class="kb" style="--kb:${17 + i * 3}s;--kbd:-${i * 5}s" src="${asset(m.img + '.jpg')}" srcset="${asset(m.img + '-400.jpg')} 400w, ${asset(m.img + '.jpg')} 800w" sizes="(max-width: 760px) 90vw, 380px" width="800" height="800" alt="${esc(m.name)}" loading="lazy"><p class="mx-name"><b>${esc(m.name)}</b>${tx('span', '', pair(m.role))}</p></div>
          ${tx('p', 'mx-bio', pair(m.p))}
        </article>`).join('\n        ')}
      </div>`;
export const teamSec = () => { const tm = C.team; return `  <!-- the team: each photo moves slowly in its frame, with the name and role on a pill over it -->
  <section class="mx-team" id="csapat" aria-labelledby="tm-h">
    <div class="wrap">
      <div class="mx-head center">${tx('p', 'mx-eyebrow', tm.eyebrow, 'data-r')}${tx('h2', 'mx-h2', tm.h2, 'id="tm-h" data-r')}</div>
      ${teamCards()}
    </div>
  </section>`; };

export const offerSec = () => `  <!-- the offer -->
  <section class="mx-offer" id="audit" aria-labelledby="au-h">
    <div class="mx-sky low" aria-hidden="true"><i class="b1"></i><i class="b3"></i></div>
    <div class="wrap">
      <div class="mx-offer-copy">${offerCopy('mx-h2')}</div>
      <div class="mx-form" data-r style="--d:1">${form()}</div>
    </div>
  </section>`;

export const faqSec = () => `  <!-- questions -->
  <section class="mx-faq" id="kerdesek" aria-labelledby="faq-h">
    <div class="wrap">
      <div class="mx-head center">${tx('p', 'mx-eyebrow', C.faq.eyebrow, 'data-r')}${tx('h2', 'mx-h2', C.faq.h2, 'id="faq-h" data-r')}</div>
      ${faqList('faq-list mx-faq-list')}
    </div>
  </section>`;

export const finalSec = () => `  <!-- the last call in a panel, under the aurora; the giant wordmark follows in the footer -->
  <section class="mx-final" aria-labelledby="fin-h">
    <div class="mx-panel mx-final-panel">
      <div class="mx-sky" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><span class="mx-horizon"></span></div>
      ${tw('h2', 'mx-h2 big', C.final.h2, 'id="fin-h" data-r')}
      <div class="mx-center" data-r>${btn()}</div>
      ${tx('p', 'small', C.final.small, 'data-r')}
    </div>
  </section>`;

// the page's <main>, the same on the concept page and on the site's home
export const main = () => `
<main>
${[heroSec(), saySec(), painsSec(), servicesSec(), resultsSec(), compareSec(), stepsSec(), whoSec(), voicesSec(), teamSec(), offerSec(), faqSec(), finalSec()].join('\n\n')}
</main>
`;
export const PAGE_SCRIPTS = ['logo-anim.js', 'reels.js'];

export function page() {
  return head({ title: 'SocialStream Aurora Mix', fonts: FONTS, css: 'mix.css', theme: THEME })
    + nav('mx-nav', { ground: 'dark', film: true }) + main() + footer('mx-foot', true, true) + scripts(PAGE_SCRIPTS);
}
