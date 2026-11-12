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
import { esc, tx, tw, pair, toSvc, btn, head, scripts, nav, claim, promise, film, reel, rail, tagItems, tickerItems, count, form, offerCopy, faqList, footer } from '../parts.mjs';

// labels that only this page has (Hungarian, English); listed in COPY.md as new
const L = {
  film: { hu: 'Márkafilm', en: 'Brand film' },
  prev: { hu: 'Előző vélemény', en: 'Previous review' },
  next: { hu: 'Következő vélemény', en: 'Next review' },
};
const ARR = dir => `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="${dir < 0 ? 'M14 8H3M7 3.5 2.5 8 7 12.5' : 'M2 8h11M9 3.5 13.5 8 9 12.5'}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
// the reels that close in on the statement: [reel, side (-1 left, 1 right), how far it leans toward the cursor]
const FLY = [['p06', -1, 0.04], ['p10', -1, -0.03], ['p13', -1, 0.06], ['p15', 1, -0.04], ['p07', 1, 0.05], ['p22', 1, 0.03]];

export function page() {
  const s = C.services, r = C.results, w = C.who, st = C.steps, v = C.voices, t = C.team, p = C.problem, cp = C.compare;
  return head({
    title: 'SocialStream Aurora Mix',
    fonts: 'family=Sora:wght@500..800&family=Inter:wght@400..700&family=Instrument+Serif:ital@1&family=Fraunces:ital,opsz,wght@0,9..144,400;1,9..144,400',
    css: 'mix.css', theme: '#05070f',
  }) + nav('mx-nav') + `
<main>
  <!-- the opening: the film alone fills the first screen (it carries the claim itself, a few seconds in). Scrolling
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
          <p class="mx-pill"><i aria-hidden="true"></i><span data-en="${esc(C.eyebrow.en)}">${esc(C.eyebrow.hu)}</span></p>
          ${claim('mx-claim')}
          ${promise('mx-promise')}
          <div class="mx-cta">${btn()}${btn(C.ctaResults, 'btn ghost', '#eredmenyek')}</div>
        </div>
        <div class="mx-post" data-seq-to>
          ${film('mx-film', 'v', false, `
  <div class="progress" aria-hidden="true"></div>
  <p class="mx-acct" aria-hidden="true"><i>S</i>SocialStream</p>
  <p class="mx-fcap" aria-hidden="true" data-en="${esc(L.film.en)}">${esc(L.film.hu)}</p>`)}
        </div>
      </div>
      <div class="mx-band">${rail(tickerItems('mx-tk'), 'mx-band-rail', 1, 46)}</div>
    </div>
  </section>

  <!-- what we do, lighting as it is read, while their reels close in from both sides -->
  <section class="mx-say" aria-labelledby="say-h" data-drift>
    <div class="mx-fly" aria-hidden="true">
      ${FLY.map(([id, side, k], i) => `<div class="mx-f f${i}" style="--side:${side}"><div class="mx-f-lean" data-follow data-k="${k}"><div class="bob">${reel(id)}</div></div></div>`).join('\n      ')}
    </div>
    <div class="wrap">
      <h2 class="mx-statement" id="say-h" data-lit><span data-l="hu">${esc(C.lead1.hu)}</span><span data-l="en">${esc(C.lead1.en)}</span></h2>
      <p class="mx-facts" data-r><span><b class="num">300M+ Ft</b> <span data-en="budget managed since 2022">kezelt büdzsé 2022 óta</span></span>${tx('span', '', C.final.small)}</p>
    </div>
  </section>

  <!-- what goes wrong for a business, each problem joined by a running line of light to the service that answers
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
            <img class="bob" style="--dur:${5.2 + i * 0.4}s;--delay:-${i * 0.9}s;--amp:-8px" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy">
            ${toSvc(it, 'a')}
          </div>
        </li>`).join('\n        ')}
      </ul>
    </div>
  </section>

  <!-- services in a panel: each one's object large on its card, two rows of tags running underneath -->
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
            <div class="mx-obj"><img class="bob" data-follow data-k="${[0.02, -0.025, 0.03][i % 3]}" style="--dur:${5.6 + i * 0.45}s;--delay:-${i * 0.8}s;--amp:-12px" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy"></div>
            ${tx('h3', '', pair(it.k))}
            ${tx('p', 'h', pair(it.t))}
            ${tx('p', 'd', pair(it.p))}
          </article>`).join('\n          ')}
        </div>
      </div>
      <div class="mx-tags">
        ${rail(tagItems('mx-tag'), 'mx-tag-rail', 1, 34)}
        ${rail(tagItems('mx-tag alt'), 'mx-tag-rail', -1, 28)}
      </div>
    </div>
  </section>

  <!-- results: four stat cards that count up, then a row of reel frames that keeps running -->
  <section class="mx-res" id="eredmenyek" aria-labelledby="res-h">
    <div class="wrap">
      <div class="mx-head row">
        <div>${tx('p', 'mx-eyebrow', r.eyebrow, 'data-r')}${tx('h2', 'mx-h2', r.h2, 'id="res-h" data-r')}</div>
        <div data-r>${btn(r.cta)}</div>
      </div>
      <div class="mx-stats">
        ${r.items.map((it, i) => `<article class="mx-card mx-stat" data-r style="--d:${i}">
          <img class="bob" style="--dur:${6.2 + i * 0.5}s;--delay:-${i * 1.2}s;--amp:-10px" src="assets/${it.obj}.webp" alt="" width="400" height="400" loading="lazy">
          <p class="n num">${count(it.n, it.unit)}</p>
          ${tx('p', 'who', pair(it.who))}
          ${tx('p', 'd', pair(it.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
    <div class="mx-reels">
      <div class="wrap mx-reels-head">${tw('h3', 'mx-h3', C.reels.h2, 'data-r')}${tx('p', 'mx-cap', C.reels.caption, 'data-r')}</div>
      ${rail(C.reels.all.slice(0, 12).map(id => reel(id)).join(''), 'mx-reel-rail', 1, 40)}
    </div>
  </section>

  <!-- elsewhere and with us: two cards, ours laid over theirs (new arrangement, to confirm) -->
  <section class="mx-cmp-sec" aria-labelledby="cmp-h">
    <div class="wrap">
      ${tw('h2', 'mx-h2 center', cp.h2, 'id="cmp-h" data-r')}
      <div class="mx-cmp">
        <div class="mx-card mx-cmp-else" data-r>${tx('p', 'k', cp.elseT)}<ul>${cp.else.map(x => tx('li', '', x)).join('')}</ul></div>
        <div class="mx-card mx-cmp-us" data-r style="--d:1">${tx('p', 'k', cp.usT)}<ul>${cp.us.map(x => tx('li', '', x)).join('')}</ul></div>
      </div>
    </div>
  </section>

  <!-- how we work: four big numbered cards, a light moving slowly through the numbers -->
  <section class="mx-steps" id="igy" aria-labelledby="how-h">
    <div class="wrap">
      <div class="mx-head row">
        <div>${tx('p', 'mx-eyebrow', st.eyebrow, 'data-r')}${tw('h2', 'mx-h2', st.h2, 'id="how-h" data-r')}</div>
        <div data-r>${btn(st.cta)}</div>
      </div>
      <ol class="mx-step-grid">
        ${st.items.map((it, i) => `<li class="mx-card mx-step" data-r style="--d:${i};--sh:-${(i * 1.6).toFixed(1)}s">
          <span class="mx-step-n num" aria-hidden="true">0${i + 1}</span>
          <h3 data-en="${esc(it.en[0])}">${esc(it.hu[0])}</h3>
          <p data-en="${esc(it.en[1])}">${esc(it.hu[1])}</p>
          <ul class="mx-chips">${it.chips.map(c => tx('li', '', pair(c))).join('')}</ul>
        </li>`).join('\n        ')}
      </ol>
    </div>
  </section>

  <!-- who it is for, in a panel, each card's object floating -->
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
            <img class="bob" style="--dur:${6 + i * 0.5}s;--delay:-${i}s;--amp:-12px" src="assets/${c.img}.webp" alt="" width="640" height="560" loading="lazy">
            <h3 data-en="${esc(c.en[0])}">${esc(c.hu[0])}</h3>
            <p><span data-l="hu">${c.hu[1]}</span><span data-l="en">${c.en[1]}</span></p>
          </article>`).join('\n          ')}
        </div>
        ${tx('p', 'mx-notfor', w.notfor, 'data-r')}
      </div>
    </div>
  </section>

  <!-- their words, in a row the visitor scrolls (or moves with the two arrows); a client's number leads where there is one -->
  <section class="mx-voices" aria-labelledby="vo-h">
    <div class="wrap">
      <div class="mx-head row">
        <div>${tx('p', 'mx-eyebrow', v.eyebrow, 'data-r')}${tw('h2', 'mx-h2', v.h2, 'id="vo-h" data-r')}</div>
        <div class="mx-arrows" data-r>
          <button type="button" data-row-go="-1" aria-label="${esc(L.prev.hu)}" data-en-aria="${esc(L.prev.en)}">${ARR(-1)}</button>
          <button type="button" data-row-go="1" aria-label="${esc(L.next.hu)}" data-en-aria="${esc(L.next.en)}">${ARR(1)}</button>
        </div>
      </div>
    </div>
    <div class="mx-row" data-row tabindex="0" role="group" aria-labelledby="vo-h">
      ${v.quotes.map((q, i) => `<figure class="mx-card mx-q${i === 0 ? ' hot' : ''}">
        ${q.metric ? `<p class="mx-metric"><b class="num">${esc(q.metric.n)}</b> <span data-en="${esc(q.metric.en)}">${esc(q.metric.hu)}</span></p>` : ''}
        <blockquote data-en="${esc(q.en)}">${esc(q.hu)}</blockquote>
        <figcaption><i aria-hidden="true">${esc(q.who[0].charAt(0))}</i><span data-en="${esc(q.who[1])}">${esc(q.who[0])}</span></figcaption>
      </figure>`).join('\n      ')}
    </div>
  </section>

  <!-- the team: each photo moves slowly in its frame, with the name and role on a pill over it -->
  <section class="mx-team" id="csapat" aria-labelledby="tm-h">
    <div class="wrap">
      <div class="mx-head center">${tx('p', 'mx-eyebrow', t.eyebrow, 'data-r')}${tx('h2', 'mx-h2', t.h2, 'id="tm-h" data-r')}</div>
      <div class="mx-team-grid">
        ${t.people.map((m, i) => `<article class="mx-card mx-person" data-r style="--d:${i}">
          <div class="mx-ph"><img class="kb" style="--kb:${17 + i * 3}s;--kbd:-${i * 5}s" src="assets/${m.img}.jpg" srcset="assets/${m.img}-400.jpg 400w, assets/${m.img}.jpg 800w" sizes="(max-width: 760px) 90vw, 380px" width="800" height="800" alt="${esc(m.name)}" loading="lazy"><p class="mx-name"><b>${esc(m.name)}</b>${tx('span', '', pair(m.role))}</p></div>
          ${tx('p', 'mx-bio', pair(m.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the offer -->
  <section class="mx-offer" id="audit" aria-labelledby="au-h">
    <div class="mx-sky low" aria-hidden="true"><i class="b1"></i><i class="b3"></i></div>
    <div class="wrap">
      <div class="mx-offer-copy">${offerCopy('mx-h2')}</div>
      <div class="mx-form" data-r style="--d:1">${form()}</div>
    </div>
  </section>

  <!-- questions -->
  <section class="mx-faq" id="kerdesek" aria-labelledby="faq-h">
    <div class="wrap">
      <div class="mx-head center">${tx('p', 'mx-eyebrow', C.faq.eyebrow, 'data-r')}${tx('h2', 'mx-h2', C.faq.h2, 'id="faq-h" data-r')}</div>
      ${faqList('faq-list mx-faq-list')}
    </div>
  </section>

  <!-- the last call in a panel, under the aurora; the giant wordmark follows in the footer -->
  <section class="mx-final" aria-labelledby="fin-h">
    <div class="mx-panel mx-final-panel">
      <div class="mx-sky" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><span class="mx-horizon"></span></div>
      ${tw('h2', 'mx-h2 big', C.final.h2, 'id="fin-h" data-r')}
      <div class="mx-center" data-r>${btn()}</div>
      ${tx('p', 'small', C.final.small, 'data-r')}
    </div>
  </section>
</main>
` + footer('mx-foot', true) + scripts();
}
