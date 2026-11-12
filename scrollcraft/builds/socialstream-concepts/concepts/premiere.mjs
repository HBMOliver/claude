// Premiere. Lead reference: Talentank (Marketia for the giant running words). Black, cinematic, editorial,
// in the brand film's own colours: warm white type and the dusty blue of "Stream". The claim's two sentences
// stand above and below a wide band where the film plays.
import { C } from '../content.mjs';
import { esc, tx, tw, pair, toSvc, btn, head, scripts, nav, claimLine, promise, ticks, film, rail, count, form, offerCopy, faqList, footer } from '../parts.mjs';

export function page() {
  const s = C.services, r = C.results, w = C.who, st = C.steps, v = C.voices, t = C.team, p = C.problem;
  const giant = s.items.map(it => `<span class="pr-gw" data-en="${esc(it.k[1])}">${esc(it.k[0])}</span><span class="pr-gd" aria-hidden="true">✦</span>`).join('');
  return head({
    title: 'SocialStream Premiere',
    fonts: 'family=Inter+Tight:wght@500..800&family=Inter:wght@400..700&family=Fraunces:ital,opsz,wght@0,9..144,400;1,9..144,300..500',
    css: 'premiere.css', theme: '#070708',
  }) + nav('pr-nav', { ground: 'dark' }) + `
<main>
  <!-- the claim's first sentence, the film in a wide band, the second sentence with the button beside it; a light
       follows the cursor over the black -->
  <section class="pr-hero" id="top" aria-labelledby="hero-h">
    <span class="pr-spot" aria-hidden="true" data-follow="in" data-home="0.74,0.32"></span>
    <h1 class="sr" id="hero-h"><span data-l="hu">${C.claim.hu.join(' ').replace(/<[^>]+>/g, '')}</span><span data-l="en">${C.claim.en.join(' ').replace(/<[^>]+>/g, '')}</span></h1>
    <div class="wrap pr-top" aria-hidden="true">
      <p class="pr-eyebrow"><span data-en="${esc(C.eyebrow.en)}">${esc(C.eyebrow.hu)}</span></p>
      <p class="pr-line pr-l1 claim" data-r>${claimLine(0)}</p>
    </div>
    <div class="pr-band" data-r style="--d:1">${film('pr-film', 'h', true)}</div>
    <div class="wrap pr-bottom">
      <p class="pr-line pr-l2 claim" data-r style="--d:2" aria-hidden="true">${claimLine(1)}</p>
      <div class="pr-act" data-r style="--d:3">
        ${promise('pr-promise')}
        ${btn(C.cta, 'btn')}
      </div>
    </div>
  </section>

  <!-- the six services as giant running words -->
  <div class="pr-giant" aria-hidden="true">${rail(giant, 'pr-giant-rail', 1, 70)}</div>

  <!-- Stream's line about the name, lighting as it is read -->
  <section class="pr-name" aria-label="SocialStream">
    <div class="pr-ghost" aria-hidden="true">${rail('<span class="pr-gh">Social<em>Stream</em></span>'.repeat(3), 'pr-ghost-rail', -1, 26)}</div>
    <div class="wrap">
      <p class="pr-kicker" data-r><span class="num">(01)</span> <span data-en="${esc(C.eyebrow.en)}">${esc(C.eyebrow.hu)}</span></p>
      <p class="pr-say" data-lit><span data-l="hu">Igen, a nevünkben még ott a social. A stream maradt. Ami benne folyik, az változott.</span><span data-l="en">Yes, our name still says social. The stream stayed. What flows in it changed.</span></p>
      ${tw('p', 'pr-lead', C.lead, 'data-r')}
    </div>
  </section>

  <!-- what goes wrong for a business, each problem with the service that answers it (new, to confirm); with a
       mouse, the service's object comes out over the row and follows the cursor along it -->
  <section class="pr-prob" aria-labelledby="prob-h">
    <div class="wrap">
      <p class="pr-kicker" data-r><span class="num">(02)</span> <span data-en="${esc(C.pains.eyebrow.en)}">${esc(C.pains.eyebrow.hu)}</span></p>
      ${tw('h2', 'pr-h2 big', { hu: p.h2.hu.join(' '), en: p.h2.en.join(' ') }, 'id="prob-h" data-r')}
      ${tx('p', 'pr-body', p.body, 'data-r')}
      <ol class="pr-pains">
        ${s.items.map((it, i) => `<li class="pr-pain" data-r>
          <span class="pr-n num" aria-hidden="true">0${i + 1}</span>
          ${tx('p', 'q', pair(it.pain))}
          ${toSvc(it, 'a')}
          <img class="pr-pain-ico" data-follow="in" data-snap data-anchor="-0.12,0.55" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy">
        </li>`).join('\n        ')}
      </ol>
      ${tw('p', 'pr-turn ital', p.turn, 'data-r')}
      ${tx('p', 'pr-body', p.whole, 'data-r')}
    </div>
  </section>

  <!-- services as a numbered list; each row's object floats beside it -->
  <section class="pr-svc" id="szolgaltatasok" aria-labelledby="svc-h">
    <div class="wrap">
      <div class="pr-head">
        <p class="pr-kicker" data-r><span class="num">(03)</span> <span data-en="${esc(s.eyebrow.en)}">${esc(s.eyebrow.hu)}</span></p>
        ${tw('h2', 'pr-h2 ital', s.h2, 'id="svc-h" data-r')}
      </div>
      <ol class="pr-list">
        ${s.items.map((it, i) => `<li class="pr-row" id="svc-${it.id}" data-r>
          <span class="pr-n num">0${i + 1}</span>
          <div class="pr-row-t">${tx('h3', '', pair(it.k))}${tx('p', 'pr-row-h', pair(it.t))}</div>
          ${tx('p', 'pr-row-p', pair(it.p))}
          <img class="pr-row-ico bob" style="--dur:${5.6 + i * 0.5}s;--delay:-${i * 0.8}s" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy">
        </li>`).join('\n        ')}
      </ol>
    </div>
  </section>

  <!-- results as cards that stack over each other as you scroll -->
  <section class="pr-res" id="eredmenyek" aria-labelledby="res-h">
    <div class="wrap">
      <div class="pr-head">
        <p class="pr-kicker" data-r><span class="num">(04)</span> <span data-en="${esc(r.eyebrow.en)}">${esc(r.eyebrow.hu)}</span></p>
        ${tx('h2', 'pr-h2', r.h2, 'id="res-h" data-r')}
      </div>
      <div class="pr-stack">
        ${r.items.map((it, i) => `<article class="pr-case c${i}" style="--i:${i}">
          <div class="pr-case-t">
            ${tx('p', 'who', pair(it.who))}
            <p class="n num" data-r>${count(it.n, it.unit)}</p>
            ${tx('p', 'd', pair(it.p))}
          </div>
          <img class="pr-case-obj bob" style="--dur:${6.5 + i * 0.5}s;--delay:-${i}s" src="assets/${it.obj}.webp" alt="" width="400" height="400" loading="lazy">
        </article>`).join('\n        ')}
      </div>
      <div class="pr-res-cta" data-r>${btn(r.cta)}</div>
    </div>
  </section>

  <!-- who it is for -->
  <section class="pr-who" id="kiknek" aria-labelledby="who-h">
    <div class="wrap">
      <div class="pr-head">
        <p class="pr-kicker" data-r><span class="num">(05)</span> <span data-en="${esc(w.eyebrow.en)}">${esc(w.eyebrow.hu)}</span></p>
        ${tw('h2', 'pr-h2 ital', w.h2, 'id="who-h" data-r')}
        ${tx('p', 'pr-body', w.lead, 'data-r')}
      </div>
      <div class="pr-who-grid">
        ${w.cards.map((c, i) => `<article class="pr-who-card" data-r style="--d:${i}">
          <img class="bob" style="--dur:${6 + i * 0.5}s;--delay:-${i * 1.2}s;--amp:-10px" src="assets/${c.img}.webp" alt="" width="640" height="560" loading="lazy">
          <h3 data-en="${esc(c.en[0])}">${esc(c.hu[0])}</h3>
          <p><span data-l="hu">${c.hu[1]}</span><span data-l="en">${c.en[1]}</span></p>
        </article>`).join('\n        ')}
      </div>
      ${tx('p', 'pr-notfor', w.notfor, 'data-r')}
    </div>
  </section>

  <!-- how we work -->
  <section class="pr-steps" id="igy" aria-labelledby="how-h">
    <div class="wrap">
      <div class="pr-head">
        <p class="pr-kicker" data-r><span class="num">(06)</span> <span data-en="${esc(st.eyebrow.en)}">${esc(st.eyebrow.hu)}</span></p>
        ${tw('h2', 'pr-h2 ital', st.h2, 'id="how-h" data-r')}
      </div>
      <ol class="pr-step-row">
        ${st.items.map((it, i) => `<li data-r style="--d:${i}">
          <span class="pr-step-n num" aria-hidden="true">0${i + 1}</span>
          <h3 data-en="${esc(it.en[0])}">${esc(it.hu[0])}</h3>
          <p data-en="${esc(it.en[1])}">${esc(it.hu[1])}</p>
        </li>`).join('\n        ')}
      </ol>
      <div data-r>${btn(st.cta)}</div>
    </div>
  </section>

  <!-- their words: one large, the rest in a row -->
  <section class="pr-voices" aria-labelledby="vo-h">
    <div class="wrap">
      <p class="pr-kicker" data-r><span class="num">(07)</span> <span data-en="${esc(v.eyebrow.en)}">${esc(v.eyebrow.hu)}</span></p>
      ${tw('h2', 'sr', v.h2, 'id="vo-h"')}
      <figure class="pr-pull" data-r>
        <blockquote data-en="${esc(v.pull.en)}">${esc(v.pull.hu)}</blockquote>
        <figcaption>${esc(v.pull.who)}</figcaption>
      </figure>
      <div class="pr-quotes">
        ${v.quotes.slice(1).map((q, i) => `<figure class="pr-q" data-r style="--d:${i % 3}">
          <blockquote data-en="${esc(q.en)}">${esc(q.hu)}</blockquote>
          <figcaption data-en="${esc(q.who[1])}">${esc(q.who[0])}</figcaption>
        </figure>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the team -->
  <section class="pr-team" id="csapat" aria-labelledby="tm-h">
    <div class="wrap">
      <div class="pr-head">
        <p class="pr-kicker" data-r><span class="num">(08)</span> <span data-en="${esc(t.eyebrow.en)}">${esc(t.eyebrow.hu)}</span></p>
        ${tx('h2', 'pr-h2', t.h2, 'id="tm-h" data-r')}
      </div>
      <div class="pr-team-grid">
        ${t.people.map((m, i) => `<article class="pr-person" data-r style="--d:${i}">
          <img src="assets/${m.img}.jpg" srcset="assets/${m.img}-400.jpg 400w, assets/${m.img}.jpg 800w" sizes="(max-width: 760px) 90vw, 380px" width="800" height="800" alt="${esc(m.name)}" loading="lazy">
          <b>${esc(m.name)}</b>${tx('span', '', pair(m.role))}${tx('p', '', pair(m.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the offer -->
  <section class="pr-offer" id="audit" aria-labelledby="au-h">
    <div class="wrap">
      <div class="pr-offer-copy">${offerCopy('pr-h2 ital')}</div>
      <div class="pr-form" data-r style="--d:1">${form()}</div>
    </div>
  </section>

  <!-- questions -->
  <section class="pr-faq" id="kerdesek" aria-labelledby="faq-h">
    <div class="wrap">
      <div class="pr-head">
        <p class="pr-kicker" data-r><span class="num">(09)</span> <span data-en="${esc(C.faq.eyebrow.en)}">${esc(C.faq.eyebrow.hu)}</span></p>
        ${tx('h2', 'pr-h2', C.faq.h2, 'id="faq-h" data-r')}
      </div>
      ${faqList('faq-list pr-faq-list')}
    </div>
  </section>

  <!-- the last call -->
  <section class="pr-final" aria-labelledby="fin-h">
    <div class="wrap">
      ${tw('h2', 'pr-h2 big ital', C.final.h2, 'id="fin-h" data-r')}
      <div class="pr-final-act" data-r>${btn()}${tx('p', 'small', C.final.small)}</div>
    </div>
  </section>
</main>
` + footer('pr-foot', true) + scripts();
}
