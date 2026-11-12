// Aurora. Lead reference: Conversion (Strivai for the horizon light and the glass). Deep night blue with a
// moving aurora; the claim on the left, real results floating on glass cards on the right; a running band of
// the real numbers; the film in a glass frame whose light follows the cursor; service cards with a light that
// runs round their edge.
import { C } from '../content.mjs';
import { esc, tx, tw, pair, toSvc, btn, head, scripts, nav, claim, promise, ticks, film, rail, tickerItems, count, form, offerCopy, faqList, footer } from '../parts.mjs';

export function page() {
  const s = C.services, r = C.results, w = C.who, st = C.steps, v = C.voices, t = C.team, p = C.problem, cp = C.compare;
  const glass = [0, 1, 3].map(i => r.items[i]);
  return head({
    title: 'SocialStream Aurora',
    fonts: 'family=Sora:wght@500..800&family=Inter:wght@400..700&family=Instrument+Serif:ital@1&family=Fraunces:ital,opsz,wght@0,9..144,400;1,9..144,400',
    css: 'aurora.css', theme: '#060914',
  }) + nav('au-nav', { ground: 'dark' }) + `
<main>
  <!-- the claim on the left; three real results float on glass on the right and lean toward the cursor; the aurora
       moves behind -->
  <section class="au-hero" id="top" aria-labelledby="hero-h">
    <div class="au-sky" aria-hidden="true"><i class="b1" data-follow data-k="-0.05"></i><i class="b2" data-follow data-k="-0.07"></i><i class="b3"></i><i class="b4" data-follow data-k="0.04"></i><span class="au-horizon"></span></div>
    <div class="wrap au-hero-in">
      <div class="au-copy">
        <p class="au-pill" data-r><i aria-hidden="true"></i><span data-en="${esc(C.eyebrow.en)}">${esc(C.eyebrow.hu)}</span></p>
        ${claim('au-claim', 'data-r style="--d:1"')}
        ${promise('au-promise', 'data-r style="--d:2"')}
        <div class="au-cta" data-r style="--d:3">${btn()}${btn(C.ctaResults, 'link', '#eredmenyek')}</div>
        <div data-r style="--d:3">${ticks('au-ticks')}</div>
      </div>
      <div class="au-glass" aria-hidden="true">
        ${glass.map((it, i) => `<div class="au-g g${i}" data-follow data-k="${[0.045, 0.08, 0.03][i]}"><div class="bob">
          <img src="assets/${it.obj}.webp" alt="" width="400" height="400">
          <p class="n num">${it.n}<small>${esc(it.unit)}</small></p>
          <p class="who" data-en="${esc(it.who[1])}">${esc(it.who[0])}</p>
        </div></div>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the real numbers, running -->
  <div class="au-ticker">${rail(tickerItems('au-tk'), 'au-tk-rail', 1, 54)}</div>

  <!-- what we do, lighting as it is read; then the film in a glass frame whose light follows the cursor -->
  <section class="au-say" aria-labelledby="say-h">
    <div class="wrap">
      <h2 class="au-statement" id="say-h" data-lit><span data-l="hu">${esc(C.lead1.hu)}</span><span data-l="en">${esc(C.lead1.en)}</span></h2>
      <div class="au-frame" data-glow data-r>
        <span class="au-frame-light" aria-hidden="true"></span>
        ${film('au-film', 'auto')}
      </div>
    </div>
  </section>

  <!-- what goes wrong for a business, each problem joined by a running line of light to the service that answers
       it (new, to confirm) -->
  <section class="au-pains" aria-labelledby="prob-h">
    <div class="wrap">
      <div class="au-head center">
        ${tx('p', 'au-eyebrow', C.pains.eyebrow, 'data-r')}
        ${tw('h2', 'au-h2', { hu: p.h2.hu.join(' '), en: p.h2.en.join(' ') }, 'id="prob-h" data-r')}
        ${tx('p', 'au-sub', p.body, 'data-r')}
      </div>
      <ul class="au-pain-list">
        ${s.items.map((it, i) => `<li class="au-card au-pain" data-r style="--d:${i % 2};--flow:-${(i * 0.55).toFixed(2)}s">
          ${tx('p', 'q', pair(it.pain))}
          <span class="au-pain-line" aria-hidden="true"></span>
          <div class="au-pain-to">
            <img class="bob" style="--dur:${5.2 + i * 0.4}s;--delay:-${i * 0.9}s;--amp:-8px" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy">
            ${toSvc(it, 'a')}
          </div>
        </li>`).join('\n        ')}
      </ul>
    </div>
  </section>

  <!-- services: glass cards with a light running round the edge -->
  <section class="au-svc" id="szolgaltatasok" aria-labelledby="svc-h">
    <div class="wrap">
      <div class="au-head">
        ${tx('p', 'au-eyebrow', s.eyebrow, 'data-r')}
        ${tw('h2', 'au-h2', s.h2, 'id="svc-h" data-r')}
      </div>
      <div class="au-svc-grid">
        ${s.items.map((it, i) => `<article class="au-card au-svc-card" id="svc-${it.id}" data-r style="--d:${i % 3};--spin:${-i * 1.3}s">
          <img class="bob" style="--dur:${6 + i * 0.4}s;--delay:-${i}s;--amp:-10px" src="assets/${it.icon}.webp" alt="" width="520" height="520" loading="lazy">
          ${tx('p', 'k', pair(it.k))}
          ${tx('h3', '', pair(it.t))}
          ${tx('p', 'd', pair(it.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- elsewhere and with us: the problem's own sentences side by side (new arrangement, to confirm) -->
  <section class="au-cmp-sec" aria-labelledby="cmp-h">
    <div class="wrap">
      ${tw('h2', 'au-cmp-h', cp.h2, 'id="cmp-h" data-r')}
      <div class="au-cmp" data-r>
        <div class="au-card au-cmp-else">${tx('p', 'k', cp.elseT)}<ul>${cp.else.map(x => tx('li', '', x)).join('')}</ul></div>
        <div class="au-card au-cmp-us">${tx('p', 'k', cp.usT)}<ul>${cp.us.map(x => tx('li', '', x)).join('')}</ul></div>
      </div>
    </div>
  </section>

  <!-- results -->
  <section class="au-res" id="eredmenyek" aria-labelledby="res-h">
    <div class="au-sky low" aria-hidden="true"><i class="b2"></i><i class="b4"></i></div>
    <div class="wrap">
      <div class="au-head center">
        ${tx('p', 'au-eyebrow', r.eyebrow, 'data-r')}
        ${tx('h2', 'au-h2', r.h2, 'id="res-h" data-r')}
      </div>
      <div class="au-stats">
        ${r.items.map((it, i) => `<article class="au-card au-stat" data-r style="--d:${i}">
          <img class="bob" style="--dur:${6.4 + i * 0.5}s;--delay:-${i * 1.2}s;--amp:-9px" src="assets/${it.obj}.webp" alt="" width="400" height="400" loading="lazy">
          <p class="n num">${count(it.n, it.unit)}</p>
          ${tx('p', 'who', pair(it.who))}
          ${tx('p', 'd', pair(it.p))}
        </article>`).join('\n        ')}
      </div>
      <div class="au-center" data-r>${btn(r.cta)}</div>
    </div>
  </section>

  <!-- how we work: four steps on a line of light -->
  <section class="au-steps" id="igy" aria-labelledby="how-h">
    <div class="wrap">
      <div class="au-head center">
        ${tx('p', 'au-eyebrow', st.eyebrow, 'data-r')}
        ${tw('h2', 'au-h2', st.h2, 'id="how-h" data-r')}
      </div>
      <ol class="au-step-row">
        ${st.items.map((it, i) => `<li class="au-card" data-r style="--d:${i}">
          <span class="au-step-n num" aria-hidden="true">${i + 1}</span>
          <h3 data-en="${esc(it.en[0])}">${esc(it.hu[0])}</h3>
          <p data-en="${esc(it.en[1])}">${esc(it.hu[1])}</p>
        </li>`).join('\n        ')}
      </ol>
      <div class="au-center" data-r>${btn(st.cta)}</div>
    </div>
  </section>

  <!-- who it is for -->
  <section class="au-who" id="kiknek" aria-labelledby="who-h">
    <div class="wrap">
      <div class="au-head center">
        ${tx('p', 'au-eyebrow', w.eyebrow, 'data-r')}
        ${tw('h2', 'au-h2', w.h2, 'id="who-h" data-r')}
        ${tx('p', 'au-sub', w.lead, 'data-r')}
      </div>
      <div class="au-who-grid">
        ${w.cards.map((c, i) => `<article class="au-card" data-r style="--d:${i}">
          <img class="bob" style="--dur:${6 + i * 0.5}s;--delay:-${i}s;--amp:-10px" src="assets/${c.img}.webp" alt="" width="640" height="560" loading="lazy">
          <h3 data-en="${esc(c.en[0])}">${esc(c.hu[0])}</h3>
          <p><span data-l="hu">${c.hu[1]}</span><span data-l="en">${c.en[1]}</span></p>
        </article>`).join('\n        ')}
      </div>
      ${tx('p', 'au-notfor', w.notfor, 'data-r')}
    </div>
  </section>

  <!-- their words -->
  <section class="au-voices" aria-labelledby="vo-h">
    <div class="wrap">
      <div class="au-head center">
        ${tx('p', 'au-eyebrow', v.eyebrow, 'data-r')}
        ${tw('h2', 'au-h2', v.h2, 'id="vo-h" data-r')}
      </div>
      <div class="au-wall">
        ${v.quotes.map((q, i) => `<figure class="au-card au-q" data-r style="--d:${i % 3}">
          <blockquote data-en="${esc(q.en)}">${esc(q.hu)}</blockquote>
          <figcaption><i aria-hidden="true">${esc(q.who[0].charAt(0))}</i><span data-en="${esc(q.who[1])}">${esc(q.who[0])}</span></figcaption>
        </figure>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the team -->
  <section class="au-team" id="csapat" aria-labelledby="tm-h">
    <div class="wrap">
      <div class="au-head center">${tx('p', 'au-eyebrow', t.eyebrow, 'data-r')}${tx('h2', 'au-h2', t.h2, 'id="tm-h" data-r')}</div>
      <div class="au-team-grid">
        ${t.people.map((m, i) => `<article class="au-card au-person" data-r style="--d:${i}">
          <img src="assets/${m.img}.jpg" srcset="assets/${m.img}-400.jpg 400w, assets/${m.img}.jpg 800w" sizes="(max-width: 760px) 90vw, 360px" width="800" height="800" alt="${esc(m.name)}" loading="lazy">
          <b>${esc(m.name)}</b>${tx('span', '', pair(m.role))}${tx('p', '', pair(m.p))}
        </article>`).join('\n        ')}
      </div>
    </div>
  </section>

  <!-- the offer -->
  <section class="au-offer" id="audit" aria-labelledby="au-h">
    <div class="au-sky low" aria-hidden="true"><i class="b1"></i><i class="b3"></i></div>
    <div class="wrap">
      <div class="au-offer-copy">${offerCopy('au-h2')}</div>
      <div class="au-form" data-r style="--d:1">${form()}</div>
    </div>
  </section>

  <!-- questions -->
  <section class="au-faq" id="kerdesek" aria-labelledby="faq-h">
    <div class="wrap">
      <div class="au-head center">${tx('p', 'au-eyebrow', C.faq.eyebrow, 'data-r')}${tx('h2', 'au-h2', C.faq.h2, 'id="faq-h" data-r')}</div>
      ${faqList('faq-list au-faq-list')}
    </div>
  </section>

  <!-- the last call, under the aurora again -->
  <section class="au-final" aria-labelledby="fin-h">
    <div class="au-sky" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i><span class="au-horizon"></span></div>
    <div class="wrap">
      ${tw('h2', 'au-h2 big', C.final.h2, 'id="fin-h" data-r')}
      <div class="au-center" data-r>${btn()}</div>
      ${tx('p', 'small', C.final.small, 'data-r')}
    </div>
  </section>
</main>
` + footer('au-foot', false) + scripts();
}
