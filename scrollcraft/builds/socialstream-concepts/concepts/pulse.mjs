// Pulse. Lead reference: Scrolla (a social media agency template). White page, black rounded panels, one hot
// rose. The claim sits in the middle with reel cards floating around it; tag rows and reel rows keep running.
import { C } from '../content.mjs';
import { esc, tx, tw, pair, toSvc, btn, head, scripts, nav, claim, promise, ticks, film, reel, rail, tagItems, count, form, offerCopy, faqList, footer } from '../parts.mjs';

const R = C.reels.firstScreen;
// [class, reel, depth]: how far each card leans toward the cursor; the film's card stays put, its button is on it
const orbit = [
  ['o1', R[0], 0.05], ['o2', null, 0], ['o3', R[3], -0.04], ['o4', R[5], 0.07], ['o5', R[8], -0.05], ['o6', R[10], 0.035],
];

export function page() {
  const s = C.services, r = C.results, w = C.who, st = C.steps, v = C.voices, t = C.team, p = C.problem, cp = C.compare;
  return head({
    title: 'SocialStream Pulse',
    fonts: 'family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Inter:wght@400..700&family=Fraunces:ital,opsz,wght@0,9..144,400;1,9..144,400',
    css: 'pulse.css', theme: '#ffffff',
  }) + nav('p-nav', { ground: 'light', dark: true }) + `
<main>
  <!-- the claim in the middle; reel cards from their own client videos float around it, one of them the brand film -->
  <section class="p-hero" id="top" aria-labelledby="hero-h" data-drift>
    <div class="p-orbit" aria-hidden="true">
      ${orbit.map(([k, id, d]) => id
        ? `<div class="p-o ${k}" data-follow data-k="${d}"><div class="bob">${reel(id, '', false)}</div></div>`
        : `<div class="p-o ${k}"><div class="bob">${film('reel p-film', 'v')}</div></div>`).join('\n      ')}
    </div>
    <div class="wrap p-hero-copy">
      <p class="p-chip" data-r><i aria-hidden="true"></i><span data-en="${esc(C.eyebrow.en)}">${esc(C.eyebrow.hu)}</span></p>
      ${claim('p-claim', 'data-r style="--d:1"')}
      ${promise('p-promise', 'data-r style="--d:2"')}
      <div class="p-cta" data-r style="--d:3">${btn()}${btn(C.ctaResults, 'btn ghost', '#eredmenyek')}</div>
      <div data-r style="--d:3">${ticks('p-ticks')}</div>
    </div>
  </section>

  <!-- two rows of what we do, always running -->
  <div class="p-tags" aria-hidden="true">
    ${rail(tagItems('p-tag'), 'p-rail', 1, 46)}
    ${rail(tagItems('p-tag alt'), 'p-rail', -1, 38)}
  </div>

  <!-- what we do, said once: the sentence lights as it is read, reel cards drift in from the sides -->
  <section class="p-say" aria-label="${esc(C.eyebrow.hu)}" data-drift>
    <div class="p-fly" aria-hidden="true">
      <div class="p-f f1"><div class="bob">${reel(C.reels.all[6])}</div></div>
      <div class="p-f f2"><div class="bob">${reel(C.reels.all[11])}</div></div>
      <div class="p-f f3"><div class="bob">${reel(C.reels.all[14])}</div></div>
      <div class="p-f f4"><div class="bob">${reel(C.reels.all[19])}</div></div>
    </div>
    <div class="wrap">
      <p class="p-statement" data-lit><span data-l="hu">${esc(C.lead1.hu)} A SocialStream egy kézben tartja a kreatívot, a kampányt és a landing oldalt, hogy minden forint a bevételt szolgálja.</span><span data-l="en">${esc(C.lead1.en)} SocialStream keeps the creative, the campaign and the landing page in one pair of hands, so every forint works toward revenue.</span></p>
      <div class="p-facts" data-r>
        <span><b class="num">300M+ Ft</b> <span data-en="budget managed since 2022">kezelt büdzsé 2022 óta</span></span>
        ${tx('span', '', C.final.small)}
      </div>
    </div>
  </section>

  <!-- what goes wrong for a business, each problem with the service that answers it (new, to confirm): the problem
       as a message, the service as the reply; the service's object sits on the card's corner and leans toward the cursor -->
  <section class="p-pains" aria-labelledby="prob-h">
    <div class="wrap">
      <div class="p-head">
        ${tx('p', 'eyebrow', C.pains.eyebrow, 'data-r')}
        ${tw('h2', 'p-h2', { hu: p.h2.hu.join(' '), en: p.h2.en.join(' ') }, 'id="prob-h" data-r')}
        ${tx('p', 'p-body', p.body, 'data-r')}
      </div>
      <ul class="p-pain-grid">
        ${s.items.map((it, i) => `<li class="p-pain" data-r style="--d:${i % 3}">
          <img class="p-pain-ico bob" data-follow data-k="${[0.03, -0.025, 0.04][i % 3]}" style="--dur:${5.2 + i * 0.45}s;--delay:-${i * 0.7}s" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy">
          ${tx('p', 'q', pair(it.pain))}
          ${toSvc(it, 'a')}
        </li>`).join('\n        ')}
      </ul>
      ${tw('p', 'p-turn', p.turn, 'data-r')}
    </div>
  </section>

  <!-- services in a black panel; the objects float, a row of tags runs underneath -->
  <section class="p-panel p-svc" id="szolgaltatasok" aria-labelledby="svc-h" data-dark>
    <div class="wrap">
      <div class="p-head">
        ${tx('p', 'eyebrow', s.eyebrow, 'data-r')}
        ${tw('h2', 'p-h2', s.h2, 'id="svc-h" data-r')}
      </div>
      <div class="p-svc-grid">
        ${s.items.map((it, i) => `<article class="p-svc-card" id="svc-${it.id}" data-r style="--d:${i % 3}">
          <div class="p-ico"><img class="bob" style="--dur:${5.4 + i * 0.5}s;--delay:-${i * 0.9}s" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy"></div>
          ${tx('p', 'k', pair(it.k))}
          ${tx('h3', '', pair(it.t))}
          ${tx('p', 'd', pair(it.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
    ${rail(tagItems('p-tag dark'), 'p-rail in-panel', 1, 34)}
  </section>

  <!-- results: four real numbers that count, then two rows of reel frames that never stop -->
  <section class="p-results" id="eredmenyek" aria-labelledby="res-h">
    <div class="wrap">
      <div class="p-head">
        ${tx('p', 'eyebrow', r.eyebrow, 'data-r')}
        ${tx('h2', 'p-h2', r.h2, 'id="res-h" data-r')}
      </div>
      <div class="p-stats">
        ${r.items.map((it, i) => `<article class="p-stat" data-r style="--d:${i}">
          <img class="p-stat-obj bob" style="--dur:${6 + i * 0.6}s;--delay:-${i * 1.3}s" src="assets/${it.obj}.webp" alt="" width="400" height="400" loading="lazy">
          <p class="n num">${count(it.n, it.unit)}</p>
          ${tx('p', 'who', pair(it.who))}
          ${tx('p', 'd', pair(it.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
    <div class="p-reels">
      <div class="wrap">
        ${tw('h3', 'p-h3 ital', C.reels.h2, 'data-r')}
        ${tx('p', 'p-cap', C.reels.caption, 'data-r')}
      </div>
      ${rail(C.reels.all.slice(0, 11).map(id => reel(id)).join(''), 'p-reel-rail', 1, 42)}
      ${rail(C.reels.all.slice(11).map(id => reel(id)).join(''), 'p-reel-rail', -1, 36)}
    </div>
  </section>

  <!-- elsewhere and with us: the problem's own sentences side by side (new arrangement, to confirm) -->
  <section class="p-problem" aria-labelledby="cmp-h">
    <div class="wrap">
      <div class="p-compare" data-r>
        ${tw('h2', 'ital', cp.h2, 'id="cmp-h"')}
        <div class="p-cmp">
          <div class="p-cmp-else">${tx('p', 'k', cp.elseT)}<ul>${cp.else.map(x => tx('li', '', x)).join('')}</ul></div>
          <div class="p-cmp-us">${tx('p', 'k', cp.usT)}<ul>${cp.us.map(x => tx('li', '', x)).join('')}</ul></div>
        </div>
      </div>
    </div>
  </section>

  <!-- who it is for: four cards, their objects floating -->
  <section class="p-who" id="kiknek" aria-labelledby="who-h">
    <div class="wrap">
      <div class="p-head">
        ${tx('p', 'eyebrow', w.eyebrow, 'data-r')}
        ${tw('h2', 'p-h2', w.h2, 'id="who-h" data-r')}
        ${tx('p', 'p-lead', w.lead, 'data-r')}
      </div>
      <div class="p-who-grid">
        ${w.cards.map((c, i) => `<article class="p-who-card" data-r style="--d:${i}">
          <div class="art"><img class="bob" style="--dur:${6.4 + i * 0.4}s;--delay:-${i * 1.1}s;--amp:-12px" src="assets/${c.img}.webp" alt="" width="640" height="560" loading="lazy"></div>
          <h3 data-en="${esc(c.en[0])}">${esc(c.hu[0])}</h3>
          <p><span data-l="hu">${c.hu[1]}</span><span data-l="en">${c.en[1]}</span></p>
        </article>`).join('\n        ')}
      </div>
      ${tx('p', 'p-notfor', w.notfor, 'data-r')}
    </div>
  </section>

  <!-- how we work: four big numbered cards -->
  <section class="p-steps" id="igy" aria-labelledby="how-h">
    <div class="wrap">
      <div class="p-head row">
        <div>${tx('p', 'eyebrow', st.eyebrow, 'data-r')}${tw('h2', 'p-h2', st.h2, 'id="how-h" data-r')}</div>
        <div data-r>${btn(st.cta)}</div>
      </div>
      <ol class="p-step-grid">
        ${st.items.map((it, i) => `<li class="p-step" data-r style="--d:${i}">
          <span class="p-step-n num" aria-hidden="true">0${i + 1}</span>
          <h3 data-en="${esc(it.en[0])}">${esc(it.hu[0])}</h3>
          <p data-en="${esc(it.en[1])}">${esc(it.hu[1])}</p>
          <div class="chips">${it.chips.map(([hu, en]) => `<span data-en="${esc(en)}">${esc(hu)}</span>`).join('')}</div>
        </li>`).join('\n        ')}
      </ol>
    </div>
  </section>

  <!-- their words: the first one large, then all six on coloured cards -->
  <section class="p-voices" aria-labelledby="vo-h">
    <div class="wrap">
      <div class="p-head">
        ${tx('p', 'eyebrow', v.eyebrow, 'data-r')}
        ${tw('h2', 'p-h2', v.h2, 'id="vo-h" data-r')}
      </div>
      <div class="p-wall">
        ${v.quotes.map((q, i) => `<figure class="p-q q${i % 3}" data-r style="--d:${i % 3}">
          <blockquote data-en="${esc(q.en)}">${esc(q.hu)}</blockquote>
          <figcaption data-en="${esc(q.who[1])}">${esc(q.who[0])}</figcaption>
        </figure>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the team -->
  <section class="p-team" id="csapat" aria-labelledby="tm-h">
    <div class="wrap">
      <div class="p-head">${tx('p', 'eyebrow', t.eyebrow, 'data-r')}${tx('h2', 'p-h2', t.h2, 'id="tm-h" data-r')}</div>
      <div class="p-team-grid">
        ${t.people.map((m, i) => `<article class="p-person" data-r style="--d:${i}">
          <img src="assets/${m.img}.jpg" srcset="assets/${m.img}-400.jpg 400w, assets/${m.img}.jpg 800w" sizes="(max-width: 760px) 90vw, 360px" width="800" height="800" alt="${esc(m.name)}" loading="lazy">
          <div><b>${esc(m.name)}</b>${tx('span', '', pair(m.role))}${tx('p', '', pair(m.p))}</div>
        </article>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the offer in a black panel, the form on white -->
  <section class="p-panel p-offer" id="audit" aria-labelledby="au-h" data-dark>
    <div class="wrap">
      <div class="p-offer-copy">${offerCopy('p-h2')}</div>
      <div class="p-form" data-r style="--d:1">${form()}</div>
    </div>
  </section>

  <!-- questions -->
  <section class="p-faq" id="kerdesek" aria-labelledby="faq-h">
    <div class="wrap">
      <div class="p-head">${tx('p', 'eyebrow', C.faq.eyebrow, 'data-r')}${tx('h2', 'p-h2', C.faq.h2, 'id="faq-h" data-r')}</div>
      ${faqList('faq-list p-faq-list')}
    </div>
  </section>

  <!-- the last call -->
  <section class="p-final" aria-labelledby="fin-h">
    <div class="wrap">
      <div class="p-final-card" data-dark>
        ${tw('h2', 'p-h2 ital', C.final.h2, 'id="fin-h" data-r')}
        <div data-r>${btn()}</div>
        ${tx('p', 'small', C.final.small, 'data-r')}
      </div>
    </div>
  </section>
</main>
` + footer('p-foot', true) + scripts();
}
