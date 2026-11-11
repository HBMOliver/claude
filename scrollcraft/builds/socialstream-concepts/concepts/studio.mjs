// Studio. Lead reference: Cutflow (a video editing agency template). Warm light grey, white rounded cards,
// one coral. The claim on a white card beside a tall card where the vertical film plays like a story;
// frames from their reels move slowly in their cards; their words carry the number each client got.
import { C } from '../content.mjs';
import { esc, tx, tw, pair, toSvc, btn, head, scripts, nav, claim, promise, ticks, film, reel, count, form, offerCopy, faqList, footer } from '../parts.mjs';

export function page() {
  const s = C.services, r = C.results, w = C.who, st = C.steps, v = C.voices, t = C.team, p = C.problem;
  const work = ['p14', 'p20', 'p05', 'p17', 'p03', 'p23'];
  const deck = ['p16', 'p21', 'p04', 'p19', 'p24'];
  return head({
    title: 'SocialStream Studio',
    fonts: 'family=Manrope:wght@500..800&family=Fraunces:ital,opsz,wght@0,9..144,400;1,9..144,400',
    css: 'studio.css', theme: '#efede9',
  }) + nav('st-nav') + `
<main>
  <!-- the claim on a white card; the vertical film plays beside it like a story, with its own progress line; two
       more of their reels peek out behind it and lean toward the cursor -->
  <section class="st-hero" id="top" aria-labelledby="hero-h">
    <div class="wrap st-hero-in">
      <div class="st-card st-hero-card">
        <p class="st-chip" data-r><i aria-hidden="true"></i><span data-en="${esc(C.eyebrow.en)}">${esc(C.eyebrow.hu)}</span></p>
        ${claim('st-claim', 'data-r style="--d:1"')}
        ${promise('st-promise', 'data-r style="--d:2"')}
        <div class="st-cta" data-r style="--d:3">${btn()}${btn(C.ctaResults, 'link', '#eredmenyek')}</div>
        <figure class="st-mini" data-r style="--d:4">
          <blockquote data-en="${esc(v.pull.en)}">${esc(v.pull.hu)}</blockquote>
          <figcaption><i aria-hidden="true">P</i>${esc(v.pull.who)}</figcaption>
        </figure>
      </div>
      <div class="st-story" data-r style="--d:1">
        <div class="st-peek" aria-hidden="true">
          <div class="st-pk k0" data-follow data-k="0.05"><div class="st-pk-in">${reel('p18', '', false)}</div></div>
          <div class="st-pk k1" data-follow data-k="0.09"><div class="st-pk-in">${reel('p02', '', false)}</div></div>
        </div>
        ${film('st-film', 'v', false, `
  <div class="progress" aria-hidden="true"></div>
  <p class="st-tag" aria-hidden="true"><i>S</i>SocialStream</p>`)}
      </div>
    </div>
    <ul class="wrap st-trust" data-r>
      <li><b class="num">300M+ Ft</b> <span data-en="budget managed since 2022">kezelt büdzsé 2022 óta</span></li>
      ${tx('li', '', C.final.small)}
      <li><span data-en="Meta, TikTok and Google">Meta, TikTok és Google</span></li>
    </ul>
  </section>

  <!-- what stops the thumb: frames from their reels, each moving slowly in its card -->
  <section class="st-work" aria-labelledby="wk-h">
    <div class="wrap">
      <div class="st-head center">
        ${tw('h2', 'st-h2', C.reels.h2, 'id="wk-h" data-r')}
        ${tx('p', 'st-sub', C.reels.caption, 'data-r')}
      </div>
      <div class="st-work-grid" aria-hidden="true">
        ${work.map((id, i) => `<div class="st-work-cell" data-r style="--d:${i % 3}"><div class="kb" style="--kb:${14 + i * 2}s;--kbd:-${i * 3}s">${reel(id)}</div></div>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- what we do, then the four results, each counting up -->
  <section class="st-about" aria-labelledby="ab-h">
    <div class="wrap">
      <div class="st-head center">
        ${tx('p', 'st-eyebrow', C.eyebrow, 'data-r')}
        <h2 class="st-h2" id="ab-h" data-r><span data-l="hu">${esc(C.lead1.hu)}</span><span data-l="en">${esc(C.lead1.en)}</span></h2>
      </div>
      <div class="st-res-grid" id="eredmenyek">
        ${r.items.map((it, i) => `<article class="st-card st-res-card" data-r style="--d:${i}">
          <img class="bob" style="--dur:${6 + i * 0.5}s;--delay:-${i}s;--amp:-10px" src="assets/${it.obj}.webp" alt="" width="400" height="400" loading="lazy">
          <p class="n num">${count(it.n, it.unit)}</p>
          ${tx('p', 'who', pair(it.who))}
          ${tx('p', 'd', pair(it.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- what goes wrong for a business, each problem with the service that answers it (new, to confirm): the problem
       in its own words on the left, the six problems on the right, each one's object floating beside it -->
  <section class="st-prob" aria-labelledby="prob-h">
    <div class="wrap">
      <div class="st-card st-prob-card">
        <div class="st-prob-intro">
          ${tx('p', 'st-eyebrow', C.pains.eyebrow, 'data-r')}
          ${tw('h2', 'st-h2', { hu: p.h2.hu.join(' '), en: p.h2.en.join(' ') }, 'id="prob-h" data-r')}
          ${tx('p', 'st-sub', p.body, 'data-r')}
          ${tw('p', 'st-turn ital', p.turn, 'data-r')}
        </div>
        <ol class="st-pains">
          ${s.items.map((it, i) => `<li class="st-pain" data-r style="--d:${i % 3}">
            <img class="bob" style="--dur:${5.4 + i * 0.4}s;--delay:-${i * 0.8}s;--amp:-7px" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy">
            <div>${tx('p', 'q', pair(it.pain))}${toSvc(it, 'a')}</div>
          </li>`).join('\n          ')}
        </ol>
      </div>
    </div>
  </section>

  <!-- services -->
  <section class="st-svc" id="szolgaltatasok" aria-labelledby="svc-h">
    <div class="wrap">
      <div class="st-head center">${tx('p', 'st-eyebrow', s.eyebrow, 'data-r')}${tw('h2', 'st-h2', s.h2, 'id="svc-h" data-r')}</div>
      <div class="st-svc-grid">
        ${s.items.map((it, i) => `<article class="st-card st-svc-card" id="svc-${it.id}" data-r style="--d:${i % 3}">
          <span class="st-svc-n num" aria-hidden="true">0${i + 1}</span>
          <img class="bob" style="--dur:${5.8 + i * 0.4}s;--delay:-${i * 0.8}s;--amp:-9px" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy">
          ${tx('h3', '', pair(it.k))}
          ${tx('p', 'h', pair(it.t))}
          ${tx('p', 'd', pair(it.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- how we work: a simple list -->
  <section class="st-steps" id="igy" aria-labelledby="how-h">
    <div class="wrap st-steps-in">
      <div class="st-head">${tx('p', 'st-eyebrow', st.eyebrow, 'data-r')}${tw('h2', 'st-h2', st.h2, 'id="how-h" data-r')}<div data-r>${btn(st.cta)}</div></div>
      <ol class="st-step-list">
        ${st.items.map((it, i) => `<li class="st-card" data-r style="--d:${i}">
          <span class="st-step-n num" aria-hidden="true">0${i + 1}</span>
          <div><h3 data-en="${esc(it.en[0])}">${esc(it.hu[0])}</h3><p data-en="${esc(it.en[1])}">${esc(it.hu[1])}</p></div>
        </li>`).join('\n        ')}
      </ol>
    </div>
  </section>

  <!-- their words, with the number each one got where there is one -->
  <section class="st-voices" aria-labelledby="vo-h">
    <div class="wrap">
      <div class="st-head center">${tx('p', 'st-eyebrow', v.eyebrow, 'data-r')}${tw('h2', 'st-h2', v.h2, 'id="vo-h" data-r')}</div>
      <div class="st-wall">
        ${v.quotes.map((q, i) => `<figure class="st-card st-q" data-r style="--d:${i % 3}">
          ${q.metric ? `<p class="st-metric"><b class="num">${esc(q.metric.n)}</b> <span data-en="${esc(q.metric.en)}">${esc(q.metric.hu)}</span></p>` : `<p class="st-quote-mark" aria-hidden="true">„</p>`}
          <blockquote data-en="${esc(q.en)}">${esc(q.hu)}</blockquote>
          <figcaption><i aria-hidden="true">${esc(q.who[0].charAt(0))}</i><span data-en="${esc(q.who[1])}">${esc(q.who[0])}</span></figcaption>
        </figure>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- who it is for -->
  <section class="st-who" id="kiknek" aria-labelledby="who-h">
    <div class="wrap">
      <div class="st-head center">${tx('p', 'st-eyebrow', w.eyebrow, 'data-r')}${tw('h2', 'st-h2', w.h2, 'id="who-h" data-r')}${tx('p', 'st-sub', w.lead, 'data-r')}</div>
      <div class="st-who-grid">
        ${w.cards.map((c, i) => `<article class="st-card" data-r style="--d:${i}">
          <img class="bob" style="--dur:${6.2 + i * 0.4}s;--delay:-${i}s;--amp:-10px" src="assets/${c.img}.webp" alt="" width="640" height="560" loading="lazy">
          <h3 data-en="${esc(c.en[0])}">${esc(c.hu[0])}</h3>
          <p><span data-l="hu">${c.hu[1]}</span><span data-l="en">${c.en[1]}</span></p>
        </article>`).join('\n        ')}
      </div>
      ${tx('p', 'st-notfor', w.notfor, 'data-r')}
    </div>
  </section>

  <!-- the team -->
  <section class="st-team" id="csapat" aria-labelledby="tm-h">
    <div class="wrap">
      <div class="st-head center">${tx('p', 'st-eyebrow', t.eyebrow, 'data-r')}${tx('h2', 'st-h2', t.h2, 'id="tm-h" data-r')}</div>
      <div class="st-team-grid">
        ${t.people.map((m, i) => `<article class="st-card st-person" data-r style="--d:${i}">
          <div class="st-ph"><img class="kb" style="--kb:${17 + i * 3}s;--kbd:-${i * 5}s" src="assets/${m.img}.jpg" srcset="assets/${m.img}-400.jpg 400w, assets/${m.img}.jpg 800w" sizes="(max-width: 760px) 90vw, 360px" width="800" height="800" alt="${esc(m.name)}" loading="lazy"></div>
          <b>${esc(m.name)}</b>${tx('span', '', pair(m.role))}${tx('p', '', pair(m.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the offer -->
  <section class="st-offer" id="audit" aria-labelledby="au-h">
    <div class="wrap">
      <div class="st-card st-offer-copy">${offerCopy('st-h2')}</div>
      <div class="st-form" data-r style="--d:1">${form()}</div>
    </div>
  </section>

  <!-- questions -->
  <section class="st-faq" id="kerdesek" aria-labelledby="faq-h">
    <div class="wrap">
      <div class="st-head center">${tx('p', 'st-eyebrow', C.faq.eyebrow, 'data-r')}${tx('h2', 'st-h2', C.faq.h2, 'id="faq-h" data-r')}</div>
      ${faqList('faq-list st-faq-list')}
    </div>
  </section>

  <!-- the last call, under a fanned deck of their reels -->
  <section class="st-final" aria-labelledby="fin-h">
    <div class="wrap">
      <div class="st-card st-final-card">
        <div class="st-deck" aria-hidden="true">${deck.map((id, i) => `<div class="st-dk d${i}">${reel(id)}</div>`).join('')}</div>
        ${tw('h2', 'st-h2', C.final.h2, 'id="fin-h" data-r')}
        <div data-r>${btn()}</div>
        ${tx('p', 'small', C.final.small, 'data-r')}
      </div>
    </div>
  </section>
</main>
` + footer('st-foot', false) + scripts();
}
