/* Shared by the three templates: the content every page carries (services, results, voices,
   people, the audit), written into the page once with its English beside it, and the behaviour
   they have in common (the bar, the film, words that light or rise, numbers that count, shapes
   that move with the cursor, the phone, the form). A page calls TPL.start() last. */
(function () {
  'use strict';
  var SS = window.SS, $ = SS.$, $$ = SS.$$, clamp = SS.clamp, lerp = SS.lerp, reduce = SS.reduce, fine = SS.fine, esc = SS.esc;
  var T = window.TPL = {}, root = document.documentElement, narrow = matchMedia('(max-width: 860px)');
  T.narrow = narrow;
  // a piece of text in both languages: Hungarian shown, English kept beside it for the switch
  function t(tag, hu, en, cls) { return '<' + tag + (cls ? ' class="' + cls + '"' : '') + ' data-en="' + esc(en) + '">' + esc(hu) + '</' + tag + '>'; }
  T.t = t;

  /* ---------------- content ---------------- */
  T.PIC = function (n) { return 'assets/p' + (n < 10 ? '0' : '') + n + '.jpg'; };
  var woke = false, onWake = [];
  // a picture waits for the film before it loads (see wake), then for its own place on the page
  T.pic = function (src, extra) { return '<img ' + (woke ? 'src' : 'data-src') + '="' + src + '" alt="" loading="lazy"' + (extra || '') + '>'; };
  T.onWake = function (f) { if (woke) f(); else onWake.push(f); };
  T.SVC = [
    { d: 'video', hu: 'Videó tartalomgyártás', en: 'Video content production', thu: 'Hookok, kreatív irány, gyártás: a kampány motorja a kreatív. Ezt mi is elkészítjük, a koncepciótól a kész videóig.', ten: 'Hooks, creative direction, production: creative is the engine of the campaign. We make it too, from concept to finished video.' },
    { d: 'social', hu: 'Social média jelenlét', en: 'Social media presence', thu: 'Feed, Stories, Reels, TikTok, egységes stratégiával, egységes hanggal. Content calendar, community management, copywriting.', ten: 'Feed, Stories, Reels, TikTok, with one strategy and one voice. Content calendar, community management, copywriting.' },
    { d: 'ads', hu: 'Fizetett hirdetés', en: 'Paid advertising', thu: 'Meta, TikTok és Google kampányok, amik nem csak elköltik a büdzsét, hanem ROAS-t termelnek. Napi optimalizálás, A/B tesztelés, skálázás.', ten: 'Meta, TikTok and Google campaigns that don’t just spend the budget, they generate ROAS. Daily optimisation, A/B testing, scaling.' },
    { d: 'web', hu: 'Weboldal & landing', en: 'Website & landing pages', thu: 'Gyors, mobilra optimalizált landingek és weboldalak, amik konvertálnak, nem csak jól néznek ki.', ten: 'Fast, mobile-optimised landing pages and websites that convert, not just look good.' },
    { d: 'auto', hu: 'Automatizáció & e-mail', en: 'Automation & email', thu: 'Lead-követés, e-mail szekvenciák, automatizált tölcsérek. Egyszer beállítjuk, utána dolgozik helyetted.', ten: 'Lead follow-up, email sequences, automated funnels. We set it up once, then it works for you.' },
    { d: 'strat', hu: 'Növekedési stratégia', en: 'Growth strategy', thu: 'Stratégiai szintű marketing tanácsadás: kampánystratégia, funnel audit, piaci pozicionálás. Partnerek vagyunk, nem kivitelezők.', ten: 'Strategy-level marketing consulting: campaign strategy, funnel audit, market positioning. We are partners, not contractors.' }
  ];
  T.QS = [
    { hu: '„Egyszer már leállítottuk a Facebook hirdetéseinket, mert egyszerűen nem érte meg. Miután megismertük Olivért, adtunk egy újabb esélyt. Már az induláskor is volt vásárlás – olyan számokat produkált, amit eddig nem is láttunk.”', en: '“We had already switched off our Facebook ads once because they simply weren’t worth it. After meeting Olivér we gave it another chance. There were purchases from launch day, and he produced numbers we had never seen before.”', who: 'Péter · Hoofbútor', whoEn: 'Péter · Hoofbútor' },
    { hu: '„Azt hittük, a Facebook a fiataloknak és a webshopoknak való – mi csarnokot építünk. Aztán egy hét alatt annyi ajánlatkérésünk lett, mint korábban fél év alatt összesen.”', en: '“We thought Facebook was for young people and webshops; we build industrial halls. Then in one week we got as many quote requests as we used to get in half a year.”', who: 'Csarnoképítő ügyfél · B2B', whoEn: 'Hall-building client · B2B' },
    { hu: '„Minden decemberben rettegtünk a hirdetési áraktól. Idén először éreztük úgy, hogy az ünnepi szezon nekünk dolgozik – nem ellenünk.”', en: '“Every December we dreaded ad prices. This year, for the first time, the holiday season felt like it was working for us, not against us.”', who: 'Karóra webshop', whoEn: 'Watch webshop' },
    { hu: '„Pár száz jelentkezőre számítottunk a webinárra. Amikor a számláló majdnem 5700-nál állt meg, alig hittük el, hogy ez ugyanabból a büdzséből jött ki.”', en: '“We expected a few hundred registrants for the webinar. When the counter stopped at almost 5,700, we could hardly believe it came from the same budget.”', who: 'Egészségügyi szolgáltató', whoEn: 'Healthcare provider' },
    { hu: '„Profi csapatot szerettem volna az indulás után. Mind Facebook/Instagram, mind weboldal és hirdetés területén profi kampányokat készítenek. Rövid időn belül jöttek az eredmények – nekem semmi dolgom nem volt velük.”', en: '“I wanted a professional team after launch. They build professional campaigns across Facebook/Instagram, the website and ads. Results came quickly, and I had nothing to do.”', who: 'Rita · Rita’s Beauty Corner', whoEn: 'Rita · Rita’s Beauty Corner' },
    { hu: '„A Social Stream profi módon készítette el a weboldalam. Mindenkinek tetszett az igényes és könnyen áttekinthető tartalom! Csak ajánlani tudom őket.”', en: '“Social Stream built my website professionally. Everyone loved the polished, easy-to-follow content! I can only recommend them.”', who: 'János · EJ Massage Therapies', whoEn: 'János · EJ Massage Therapies' }
  ];
  T.TEAM = [
    { img: 'assets/oliver-sm.jpg', n: 'Olivér', r: ['Alapító & kampánystratéga', 'Founder & campaign strategist'], l: ['Ő olvassa az új kor szabályait: adatból dönti el, mibe fektessük a figyelmet, és miért fogja azt bárki megnézni.', 'He reads the rules of the new age: he decides from data where to invest attention, and why anyone will watch it.'] },
    { img: 'assets/david-sm.jpg', n: 'David', r: ['Kreatív & tartalomgyártás', 'Creative & content production'], l: ['Ami megállítja a hüvelykujjat, az ő keze munkája. Hookok, forgatás, kreatív irány, az új kor nyelvén.', 'Whatever stops the thumb is his handiwork. Hooks, shooting, creative direction, in the language of the new age.'] },
    { img: 'assets/lidi-sm.jpg', n: 'Lidi', r: ['Produkció & szerkesztés', 'Production & editing'], l: ['A gyártás motorja. Nála áll össze nyersanyagból kész tartalom: vágás, ritmus, precizitás, határidőre.', 'The engine of production. Raw footage becomes finished content in her hands: editing, rhythm, precision, on deadline.'] }
  ];
  T.RES = [
    { to: 81, unit: '×', c: ['ROAS, a legjobb eredményünk e-commerce kampányban', 'ROAS, our best result in an e-commerce campaign'], who: ['Ajtó webshop · Google Performance Max', 'Door webshop · Google Performance Max'], obj: 'door' },
    { to: 79, unit: 'M Ft', c: ['bevétel egy hét alatt, B2B Meta kampányból', 'revenue in one week, from a B2B Meta campaign'], who: ['Csarnoképítő ügyfél · Meta', 'Industrial hall builder · Meta'], obj: 'hall' },
    { to: 23, unit: '×', c: ['ROAS ünnepi kampányban, 8M+ Ft bevétel', 'ROAS in a holiday campaign, 8M+ Ft revenue'], who: ['Karóra webshop · Karácsony', 'Watch webshop · Christmas'], obj: 'watch' },
    { to: 105, unit: 'Ft', c: ['jelentkezőnként: ~5700 jelentkező 600K Ft költésből', 'per registrant: ~5,700 registrants from 600K Ft spend'], who: ['Egészségügyi webinár · lead generation', 'Healthcare webinar · lead generation'], obj: 'webinar' }
  ];

  /* ---------------- drawn objects: what each result is about, in the page's own shapes and colours ---------------- */
  // every object carries its own gradients; the ids take a suffix, so an object can appear twice on a page
  function ograd(s) {
    function lg(id, cols, offs, x2, y2) { return '<linearGradient id="' + id + s + '" x1="0" y1="0" x2="' + x2 + '" y2="' + y2 + '">' + cols.map(function (c, i) { return '<stop offset="' + offs[i] + '" style="stop-color:' + c + '"/>'; }).join('') + '</linearGradient>'; }
    return '<defs>' +
      lg('oa', ['color-mix(in srgb, var(--amber) 50%, #fff)', 'var(--amber)', 'var(--rose)'], [0, 0.4, 1], 1, 1) +
      lg('ob', ['var(--rose)', 'color-mix(in srgb, var(--violet) 55%, var(--shade))'], [0, 1], 0.6, 1) +
      lg('oc', ['color-mix(in srgb, var(--violet) 42%, var(--shade))', 'var(--shade)'], [0, 1], 0.4, 1) +
      lg('ol', ['#fff', 'var(--cream)'], [0, 1], 0.5, 1) +
      lg('og', ['color-mix(in srgb, var(--amber) 70%, #fff)', 'var(--amber)', 'var(--rose)'], [0, 0.5, 1], 0, 1) + '</defs>';
  }
  var OBJ = {
    // a door standing open, light behind it
    door: function (s) { return '<ellipse cx="110" cy="187" rx="72" ry="9" fill="rgba(0,0,0,.32)"/><rect x="54" y="14" width="104" height="172" rx="12" fill="url(#oc' + s + ')"/><rect x="63" y="23" width="86" height="163" rx="5" fill="url(#og' + s + ')"/><path d="M118 186h31l26 12H92z" fill="var(--amber)" opacity=".3"/><path d="M63 23l52 13a5 5 0 0 1 4 5v128a5 5 0 0 1-4 5l-52 12z" fill="url(#oa' + s + ')"/><path d="M71 38l38 8v44l-38-2zM71 100l38 1v62l-38 9z" fill="rgba(0,0,0,.13)"/><circle cx="108" cy="106" r="6" fill="url(#ol' + s + ')"/>'; },
    // an industrial hall
    hall: function (s) { return '<ellipse cx="106" cy="172" rx="88" ry="11" fill="rgba(0,0,0,.32)"/><path d="M108 162l70-25V78l-70 24z" fill="url(#ob' + s + ')"/><path d="M34 162V102l37-28 37 28v60z" fill="url(#oa' + s + ')"/><path d="M71 74l70-24 37 28-70 24z" fill="url(#ol' + s + ')"/><path d="M50 162v-42h42v42z" fill="url(#oc' + s + ')"/><path d="M50 131h42M50 142h42M50 153h42" stroke="rgba(255,255,255,.2)" stroke-width="2" fill="none"/><path d="M122 132l44-15v-13l-44 15z" fill="rgba(255,255,255,.34)"/>'; },
    // a wristwatch
    watch: function (s) { return '<rect x="77" y="4" width="46" height="70" rx="15" fill="url(#ob' + s + ')"/><rect x="77" y="126" width="46" height="70" rx="15" fill="url(#ob' + s + ')"/><rect x="146" y="91" width="13" height="18" rx="5" fill="url(#oa' + s + ')"/><circle cx="100" cy="100" r="52" fill="url(#oa' + s + ')"/><path d="M61 76a46 46 0 0 1 31-22" stroke="rgba(255,255,255,.6)" stroke-width="4" stroke-linecap="round" fill="none"/><circle cx="100" cy="100" r="40" fill="url(#ol' + s + ')"/><path d="M100 67v8M100 125v8M67 100h8M125 100h8" stroke="var(--ink2)" stroke-width="4" stroke-linecap="round" fill="none"/><path d="M100 100L85 82M100 100l23-11" stroke="var(--ink2)" stroke-width="5.5" stroke-linecap="round" fill="none"/><circle cx="100" cy="100" r="5" fill="var(--rose)"/>'; },
    // a screen full of people who signed up, with a health cross
    webinar: function (s) {
      var dots = '', i;
      for (i = 0; i < 18; i++) dots += '<circle cx="' + (49 + (i % 6) * 20.4) + '" cy="' + (68 + Math.floor(i / 6) * 25) + '" r="7.5" fill="' + ([1, 4, 6, 9, 11, 14, 16].indexOf(i) > -1 ? 'url(#oa' + s + ')' : 'rgba(255,255,255,.2)') + '"/>';
      return '<ellipse cx="100" cy="187" rx="62" ry="8" fill="rgba(0,0,0,.32)"/><path d="M90 150h20l4 26H86z" fill="url(#oc' + s + ')"/><rect x="64" y="172" width="72" height="11" rx="5.5" fill="url(#ob' + s + ')"/><rect x="20" y="30" width="160" height="124" rx="18" fill="url(#ob' + s + ')"/><rect x="31" y="41" width="138" height="102" rx="10" fill="url(#oc' + s + ')"/>' + dots + '<circle cx="166" cy="40" r="25" fill="url(#oa' + s + ')"/><path d="M166 28v24M154 40h24" stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none"/>';
    }
  };
  T.obj = function (name, s) { s = s || name.charAt(0); return '<svg class="obj o-' + name + '" viewBox="0 0 200 200" aria-hidden="true">' + ograd(s) + OBJ[name](s) + '</svg>'; };

  /* ---------------- one small scene per service ---------------- */
  T.scene = {
    video: function () { return '<div class="mg mg-video"><div class="vb">' + T.pic(T.PIC(1)) + '</div><div class="vf">' + T.pic(T.PIC(2)) + '<i class="vp"></i><span class="vbar"><i></i></span></div></div>'; },
    social: function () { return '<div class="mg mg-social">' + [1, 13, 5, 16, 6, 14, 18, 3, 12].map(function (n, i) { return '<i style="--d:' + i + '">' + T.pic(T.PIC(n)) + '</i>'; }).join('') + '</div>'; },
    ads: function () { return '<svg class="mg draw d-ads" viewBox="0 0 200 150"><path class="ar" d="M22 122 62 104 94 110 132 70 176 36V126H22z"/><line x1="18" y1="126" x2="186" y2="126"/><polyline class="b dash" points="22,122 62,104 94,110 132,70 176,36"/><circle class="end bfill" cx="176" cy="36" r="6"/><g class="pill2"><rect x="92" y="5" width="76" height="24" rx="12"/><text x="130" y="21.5" text-anchor="middle">81× ROAS</text></g></svg>'; },
    web: function () { return '<div class="mg mg-web"><div class="bw"><div class="bb"><i></i><i></i><i></i></div><div class="bg2"><div class="bh">' + T.obj('watch', 'ws') + '</div><div class="bl"><b style="--d:0"></b><b style="--d:1"></b><b style="--d:2"></b><u style="--d:3"></u></div></div></div></div>'; },
    auto: function () { return '<svg class="mg draw d-auto" viewBox="0 0 200 150"><line x1="38" y1="66" x2="162" y2="66"/><circle class="n1" cx="38" cy="66" r="19"/><circle class="n2" cx="100" cy="66" r="19"/><circle class="n3" cx="162" cy="66" r="19"/><circle class="dot" cx="38" cy="66" r="8"/><text x="38" y="114" text-anchor="middle" data-en="Lead">Lead</text><text x="100" y="114" text-anchor="middle" data-en="Email">E-mail</text><text x="162" y="114" text-anchor="middle" data-en="Offer">Ajánlat</text></svg>'; },
    strat: function () { return '<svg class="mg draw d-strat" viewBox="0 0 200 150"><rect class="bar3 q1" style="--d:0" x="16" y="10" width="168" height="27" rx="7"/><rect class="bar3 q2" style="--d:1" x="40" y="45" width="120" height="27" rx="7"/><rect class="bar3 q3" style="--d:2" x="62" y="80" width="76" height="27" rx="7"/><rect class="bar3 q4" style="--d:3" x="82" y="115" width="36" height="27" rx="7"/></svg>'; }
  };

  /* ---------------- blocks: written once, each page lays them out its own way ---------------- */
  // services. 'grid': a card per service with its scene; 'list': a list with one panel (view) beside it; 'acc': rows that open
  T.services = function (el, variant, view) {
    if (variant === 'grid') {
      el.innerHTML = T.SVC.map(function (s) { return '<li class="sv"><div class="scene"><div class="dv">' + T.scene[s.d]() + '</div></div>' + t('h3', s.hu, s.en) + t('p', s.thu, s.ten) + '</li>'; }).join('');
      see($$('.sv', el), function (li, on) { $('.dv', li).classList.toggle('is-on', on); }, 0.35);
    } else if (variant === 'acc') {
      el.innerHTML = T.SVC.map(function (s, i) { return '<li class="ac"><button type="button" aria-expanded="false" aria-controls="ac' + i + '">' + t('h3', s.hu, s.en) + '<i class="plus" aria-hidden="true"></i></button><div class="pan" id="ac' + i + '"><div class="pan-in">' + t('p', s.thu, s.ten) + '<div class="scene"><div class="dv">' + T.scene[s.d]() + '</div></div></div></div></li>'; }).join('');
      var open = function (li) { $$('.ac', el).forEach(function (o) { var on = o === li && !o.classList.contains('is-open'); o.classList.toggle('is-open', on); $('button', o).setAttribute('aria-expanded', String(on)); $('.dv', o).classList.toggle('is-on', on); }); };
      el.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) open(b.parentNode); });
      open($('.ac', el));
    } else {
      var on = -1, hoverAt = 0;
      el.innerHTML = T.SVC.map(function (s, i) { return '<li><button type="button" data-svc="' + i + '">' + t('h3', s.hu, s.en) + t('p', s.thu, s.ten) + '</button></li>'; }).join('');
      view.innerHTML = T.SVC.map(function (s) { return '<div class="dv">' + T.scene[s.d]() + '</div>'; }).join('');
      var set = function (i) { if (i === on) return; on = i; $$('li', el).forEach(function (li, k) { li.classList.toggle('is-on', k === i); }); $$('.dv', view).forEach(function (d, k) { d.classList.toggle('is-on', k === i); }); };
      el.addEventListener('pointerover', function (e) { var b = e.target.closest('[data-svc]'); if (b && fine) { hoverAt = performance.now(); set(+b.dataset.svc); } });
      el.addEventListener('focusin', function (e) { var b = e.target.closest('[data-svc]'); if (b) { hoverAt = performance.now(); set(+b.dataset.svc); } });
      set(0);
      // the row nearest the middle of the screen is the active one, unless the cursor chose
      T.onFrame(function (c) {
        if (c.now - hoverAt < 1600) return; var r = el.getBoundingClientRect(); if (r.bottom < 0 || r.top > c.vh) return;
        var best = 0, bd = 1e9; $$('li', el).forEach(function (li, i) { var b = li.getBoundingClientRect(), d = Math.abs(b.top + b.height / 2 - c.vh * (narrow.matches ? 0.68 : 0.52)); if (d < bd) { bd = d; best = i; } });
        set(best);
      });
    }
  };
  T.results = function (el) {
    el.innerHTML = T.RES.map(function (r) {
      return '<article class="res"><figure class="res-obj">' + T.obj(r.obj) + '</figure><p class="fig num"><span data-count="' + r.to + '">' + r.to + '</span><small>' + r.unit + '</small></p>' + t('p', r.c[0], r.c[1], 'c') + t('p', r.who[0], r.who[1], 'who') + '</article>';
    }).join('');
  };
  T.voices = function (el) {
    el.innerHTML = T.QS.map(function (q) { return '<li><i class="av" aria-hidden="true">' + esc(q.who.charAt(0)) + '</i><div class="qb">' + t('blockquote', q.hu, q.en) + t('cite', q.who, q.whoEn) + '</div></li>'; }).join('');
  };
  T.people = function (el) {
    el.innerHTML = '<div class="founder"><figure data-sc-in><img src="assets/oliver-founder.jpg" alt="Olivér, a SocialStream alapítója" data-en-alt="Olivér, founder of SocialStream" width="1000" height="1250" loading="lazy"></figure><div class="copy">' +
      '<h2 class="h-l" id="tm-h" data-sc-in><span data-l="hu">A korszakváltást <em>belülről</em> láttam.</span><span data-l="en">I saw the shift from the <em>inside</em>.</span></h2>' +
      t('p', 'Dániai tanulmányaim alatt szereztem meg az első ügyfelemet. Aztán Meta Marketing Pro-ként közelről láttam, hogyan gondolkodnak a legkomolyabb márkák, amikor valódi pénz van a kampányban. 2022-ben alapítottam a SocialStreamet; azóta 300M+ Ft büdzsét kezeltünk.', 'I landed my first client while studying in Denmark. Then, as a Meta Marketing Pro, I saw up close how the most serious brands think when there is real money in a campaign. I founded SocialStream in 2022; since then we have managed 300M+ Ft in budget.', 'body') +
      t('p', 'Olivér, alapító és kampánystratéga', 'Olivér, founder and campaign strategist', 'kicker') + '</div></div>' +
      '<ul class="crew" data-sc-in data-sc-stagger="70">' + T.TEAM.map(function (m) { return '<li><img src="' + m.img + '" srcset="' + m.img + ' 400w, ' + m.img.replace('-sm', '') + ' 800w" sizes="(max-width: 860px) 112px, 30vw" alt="' + m.n + '" width="400" height="500" loading="lazy"><b>' + m.n + '</b>' + t('span', m.r[0], m.r[1]) + t('p', m.l[0], m.l[1]) + '</li>'; }).join('') + '</ul>' +
      '<div class="fit">' + t('p', 'Olyan márkákkal dolgozunk, amelyek megbízható, stabil bevétellel rendelkeznek, hosszú távú sikerre törekszenek, és befektetésnek tekintik a marketinget.', 'We work with brands that have reliable, stable revenue, aim for long-term success and see marketing as an investment.', 'body') + t('p', 'Havonta legfeljebb két új partner.', 'At most two new partners a month.', 'big2') + '</div>';
  };
  T.audit = function (el) {
    var opt = function (v, hu, en) { return '<option value="' + v + '"' + (en ? ' data-en="' + esc(en) + '"' : '') + '>' + esc(hu) + '</option>'; };
    var fld = function (id, name, hu, en, more) { return '<div class="field"><label for="' + id + '" data-en="' + esc(en) + '">' + esc(hu) + '</label><input id="' + id + '" name="' + name + '"' + (more || '') + '><span class="err" id="e-' + name + '"></span></div>'; };
    el.innerHTML = '<div class="copy">' +
      '<h2 class="h-l" id="au-h" data-sc-in><span data-l="hu">A piacod már az új korban jár. A marketinged <em>is</em>?</span><span data-l="en">Your market already lives in the new age. Does your <em>marketing</em>?</span></h2>' +
      t('p', '30 perces ingyenes audit: megnézzük a kampányaidat, a landing page-edet és az ajánlatodat, és őszintén megmondjuk, hol játszol még a régi kor szabályaival, még fizetés előtt.', 'A free 30-minute audit: we look at your campaigns, your landing page and your offer, and tell you honestly where you still play by the old rules, before you pay anything.', 'body') +
      '<dl class="specs"><div>' + t('dt', 'Hossz', 'Length') + t('dd', '30 perc', '30 minutes') + '</div><div>' + t('dt', 'Ár', 'Price') + t('dd', 'Ingyenes, kötelezettség nélkül', 'Free, no obligation') + '</div><div>' + t('dt', 'Kapacitás', 'Capacity') + t('dd', 'Havonta legfeljebb két új partner', 'At most two new partners a month') + '</div><div>' + t('dt', 'Nem neked, ha', 'Not for you if') + t('dd', 'egy éjszaka alatti sikert vagy olcsó félmegoldást keresel', 'you want overnight success or cheap half-solutions') + '</div></dl></div>' +
      '<form class="app" id="appform" novalidate data-sc-in>' + fld('f-name', 'name', 'Neved', 'Your name', ' autocomplete="name" required') + fld('f-email', 'email', 'E-mail', 'Email', ' type="email" autocomplete="email" required') + fld('f-brand', 'brand', 'Cég vagy márka', 'Company or brand', ' autocomplete="organization" required') + fld('f-web', 'web', 'Weboldal vagy Instagram', 'Website or Instagram', ' autocomplete="url"') +
      '<div class="field"><label for="f-budget" data-en="Monthly marketing budget">Havi marketing büdzsé</label><select id="f-budget" name="budget">' + opt('', 'Válassz sávot', 'Choose a range') + opt('lt300', '300K Ft alatt', 'Under 300K Ft') + opt('300-1m', '300K–1M Ft') + opt('1-3m', '1M–3M Ft') + opt('gt3m', '3M Ft felett', 'Over 3M Ft') + '</select><span class="err"></span></div>' +
      '<div class="field"><label for="f-goal" data-en="Main goal">Fő cél</label><select id="f-goal" name="goal">' + opt('', 'Válassz célt', 'Choose a goal') + opt('sales', 'Több eladás (webshop)', 'More sales (e-commerce)') + opt('leads', 'Több érdeklődő és ajánlatkérés', 'More leads and enquiries') + opt('brand', 'Márka és tartalom', 'Brand and content') + opt('web', 'Weboldal vagy landing', 'Website or landing page') + '</select><span class="err"></span></div>' +
      '<fieldset><legend data-en="What interests you">Ami érdekel</legend><div class="chips" id="chips"></div></fieldset>' +
      '<div class="field full"><label for="f-msg" data-en="Where are you now?">Hol tartasz most?</label><textarea id="f-msg" name="msg"></textarea><span class="err"></span></div>' +
      '<div class="actions"><button class="btn" type="submit" data-en="Request my free audit">Kérem az ingyenes auditot</button><span class="direct"><span data-en="Or write to us:">Vagy írj nekünk:</span> <a href="mailto:hello@socialstream.hu">hello@socialstream.hu</a><button type="button" class="copy-mini" id="copyMail" data-en="Copy address">Cím másolása</button></span></div>' +
      '<div class="sending" id="sending" hidden><i></i><span id="stext"></span></div><div class="sent" id="sent" hidden aria-live="polite"></div></form>';
    var form = $('#appform'), chips = $('#chips'), sent = $('#sent'), sending = $('#sending'), chosen = [], lastBody = '';
    function renderChips() { chips.innerHTML = SS.TOPICS.map(function (c) { return '<label class="chip"><input type="checkbox" value="' + c.id + '"' + (chosen.indexOf(c.id) > -1 ? ' checked' : '') + '><span>' + esc(SS.T(c)) + '</span></label>'; }).join(''); }
    chips.addEventListener('change', function (e) { var id = e.target.value, k = chosen.indexOf(id); if (e.target.checked && k < 0) chosen.push(id); else if (!e.target.checked && k > -1) chosen.splice(k, 1); });
    function check() {
      var ok = true;
      ['name', 'email', 'brand'].forEach(function (n) {
        var inp = $('#f-' + n), er = $('#e-' + n), v = inp.value.trim(), m = '';
        if (!v) m = SS.T(SS.ERR.req); else if (inp.type === 'email' && !SS.isMail(v)) m = SS.T(SS.ERR.mail);
        er.textContent = m; inp.setAttribute('aria-invalid', String(!!m)); if (m && ok) { inp.focus(); ok = false; }
      });
      return ok;
    }
    function showSent(body) {
      var s = SS.sentText(); sent.hidden = false;
      sent.innerHTML = '<b>' + s.b + '</b><span>' + esc(s.s) + '</span><button type="button" class="btn" id="copyBody">' + s.c + '</button>';
      var cb = $('#copyBody'); cb.addEventListener('click', function () { SS.copy(body, cb, function () { var m = $('#f-msg'); m.value = body; m.focus(); m.select(); }); });
    }
    var sel = function (id) { var s = $('#' + id); return s.value ? s.options[s.selectedIndex].text : ''; };
    form.addEventListener('submit', function (e) {
      e.preventDefault(); if (!check()) return;
      var body = SS.compose({ name: $('#f-name').value.trim(), email: $('#f-email').value.trim(), brand: $('#f-brand').value.trim(), web: $('#f-web').value.trim(), budget: sel('f-budget'), goal: sel('f-goal'), interests: chosen, msg: $('#f-msg').value.trim() });
      lastBody = body; sending.hidden = false; $('#stext').textContent = SS.L === 'en' ? 'Preparing your email…' : 'Készül az e-mailed…';
      var done = function () { $('#stext').textContent = '100%'; showSent(body); SS.send($('#f-brand').value.trim(), body); };
      requestAnimationFrame(function () { sending.style.setProperty('--w', '100%'); });
      if (reduce) done(); else setTimeout(done, 800);
    });
    SS.onLang(function () { renderChips(); if (lastBody) showSent(lastBody); });
  };
  T.footer = function (el) {
    el.innerHTML = '<div class="wrap"><p class="big" aria-hidden="true"><span>Social<em>Stream</em></span></p><span class="sr">SocialStream</span><div class="frow">' + t('span', 'Interest media ügynökség · Tenerife és Budapest', 'Interest media agency · Tenerife and Budapest') +
      '<span><a href="mailto:hello@socialstream.hu">hello@socialstream.hu</a><button type="button" id="copyMail2" data-en="Copy">Másolás</button></span><span>© 2026 SocialStream</span></div></div>';
  };
  T.ticker = function (el) {
    var set = '<div class="tick-set"><span><b>81×</b>' + t('i', 'ROAS, ajtó webshop', 'ROAS, door webshop') + '</span><span><b>79M Ft</b>' + t('i', 'egy hét alatt, B2B', 'in one week, B2B') + '</span><span><b>23×</b>' + t('i', 'ROAS, ünnepi kampány', 'ROAS, holiday campaign') + '</span><span><b>105 Ft</b>' + t('i', 'jelentkezőnként', 'per registrant') + '</span><span><b>300M+ Ft</b>' + t('i', 'kezelve 2022 óta', 'managed since 2022') + '</span></div>';
    el.innerHTML = '<div class="tick-run">' + set + set + '</div>';
  };
  // a reel in a ring that fills as it is watched; the old rules struck out and the new ones in
  T.ring = function (el, n) {
    el.innerHTML = '<svg viewBox="0 0 104 104" aria-hidden="true"><defs><linearGradient id="ringg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" style="stop-color:var(--amber)"/><stop offset="1" style="stop-color:var(--rose)"/></linearGradient></defs><circle class="trk" cx="52" cy="52" r="47"/><circle class="bar2" cx="52" cy="52" r="47" pathLength="100"/></svg><div class="card9">' + T.pic(T.PIC(n || 2)) + '</div><p class="pct"><b class="num">0%</b>' + t('span', 'Végignézve', 'Watched to the end') + '</p>';
    var b = $('.pct b', el), was = '';
    return function (v) { v = clamp(v, 0, 1); var s = v.toFixed(3); if (s === was) return; was = s; el.style.setProperty('--wv', s); b.textContent = Math.round(v * 100) + '%'; };
  };
  T.rules = function (el) {
    el.innerHTML = '<div class="old">' + t('p', 'A régi kor', 'The old age') + '<ul>' + t('li', 'Posztolni', 'Post') + t('li', 'Reménykedni', 'Hope') + '</ul></div><div class="new">' + t('p', 'Az új kor', 'The new age') + '<ul>' + t('li', 'Adatból tudni, mi érdekel', 'Know from data what interests people') + t('li', 'Rendszert építeni', 'Build a system') + t('li', 'Az érdeklődésből bevétel', 'Turn interest into revenue') + '</ul></div>';
    var olds = $$('.old li', el), news = $$('.new li', el);
    return function (o) { olds.forEach(function (li, i) { li.classList.toggle('is-x', o > 0.1 + i * 0.16); }); news.forEach(function (li, i) { li.classList.toggle('is-in', o > 0.42 + i * 0.16); }); };
  };
  // the phone: out of the Following tab, into the For You feed, then post after post, one tag each
  // the feed's two states (who you follow, what interests you) and the tags that stand beside the phone
  T.FEED = '<div class="fw"><div><i></i><b></b><b></b><u></u></div><div><i></i><b></b><b></b><u></u></div><div><i></i><b></b><b></b><u></u></div></div><div class="fy"><div class="feed">' +
    [1, 14, 5, 16, 6].map(function (n, i) { return '<img data-src="' + T.PIC(n) + '" alt="" style="--n:' + i + '">'; }).join('') + '</div><div class="acts"><i class="a-h"></i><i class="a-c"></i><i class="a-s"></i></div><div class="pbar"><i></i></div></div>' +
    '<div class="tabs">' + t('span', 'Követés', 'Following') + t('span', 'Neked', 'For You') + '</div>';
  T.TAGS = '<span class="tag" style="--ty:13%" data-en="#travel">#utazás</span><span class="tag" style="--ty:31%;--tb:var(--rose)" data-en="#comedy">#humor</span><span class="tag" style="--ty:53%;--tb:var(--violet)" data-en="#experience">#élmény</span><span class="tag" style="--ty:67%;--tb:var(--cream)" data-en="#podcast">#podcast</span><span class="tag" style="--ty:30%;--tb:var(--teal)" data-en="#tenerife">#tenerife</span>';
  // wrap already holds a feed (and its tags). The function this returns is told: on (the For You feed is showing) and f (how far through the posts, 0 to 1)
  T.feed = function (wrap) {
    var feed = $('.feed', wrap), heart = $('.a-h', wrap), pbar = $('.pbar', wrap), tags = $$('.tag', wrap), n = feed.children.length, was = {};
    return function (on, f) {
      f = clamp(f, 0, 0.9999) * n; var i = Math.floor(f);
      if (was.on !== on) wrap.classList.toggle('is-fy', on);
      if (was.i !== i || was.on !== on) {
        feed.style.setProperty('--i', i); tags.forEach(function (g, k) { g.classList.toggle('is-on', on && k === i); });
        if (on && !reduce) { heart.classList.remove('pop'); void heart.offsetWidth; heart.classList.add('pop'); }
      }
      was.on = on; was.i = i;
      var pp = (f - i).toFixed(2); if (was.pp !== pp) { was.pp = pp; pbar.style.setProperty('--pp', pp); }
    };
  };
  T.phone = function (wrap) { wrap.innerHTML = '<div class="phone"><div class="scr">' + T.FEED + '</div></div>' + T.TAGS; return T.feed(wrap); };

  /* ---------------- behaviour ---------------- */
  // tell f when an element comes into view and when it leaves
  function see(els, f, th) {
    if (!('IntersectionObserver' in window)) { els.forEach(function (e) { f(e, true); }); return; }
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { f(e.target, e.isIntersecting); }); }, { threshold: th == null ? 0.3 : th });
    els.forEach(function (e) { io.observe(e); });
  }
  T.see = see;
  // how far an element has travelled through the screen: 0 as its top meets the bottom edge, 1 as its bottom leaves the top
  T.through = function (el, vh) { var r = el.getBoundingClientRect(); return clamp((vh - r.top) / (vh + r.height), 0, 1); };
  // a pinned act's own progress, as the scroll engine publishes it
  T.pinP = function (el) { return parseFloat(el.style.getPropertyValue('--sc-p')) || 0; };
  var frames = [];
  T.onFrame = function (f) { frames.push(f); };

  // headlines arrive word by word; punctuation after an accent word stays with it
  function words() {
    $$('.h-l[data-sc-in], .h-xl[data-sc-in], .h-m[data-sc-in]').forEach(function (h) {
      h.classList.add('rise');
      var holders = $$('[data-l]', h); if (!holders.length) holders = [h];
      holders.forEach(function (el) {
        var k = 0, last = null, glue = false;
        function unit(node) { var o = document.createElement('span'), i = document.createElement('span'); o.className = 'wd'; o.style.setProperty('--wi', k++); i.appendChild(node); o.appendChild(i); last = i; return o; }
        Array.prototype.slice.call(el.childNodes).forEach(function (n) {
          if (n.nodeType === 3) {
            var f = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach(function (part) {
              if (!part) return;
              if (/^\s+$/.test(part)) { f.appendChild(document.createTextNode(part)); glue = false; return; }
              if (glue && last) last.appendChild(document.createTextNode(part)); else f.appendChild(unit(document.createTextNode(part)));
              glue = true;
            });
            el.replaceChild(f, n);
          } else if (n.nodeType === 1) {
            if (glue && last) last.appendChild(n); else { var ph = document.createComment(''); el.replaceChild(ph, n); el.replaceChild(unit(n), ph); }
            glue = true;
          }
        });
      });
    });
  }
  // words lit by the scroll
  var lits = [];
  function litSplit() {
    lits = $$('.lit');
    lits.forEach(function (el) {
      (function walk(node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (n) {
          if (n.nodeType === 3) {
            var f = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach(function (part) { if (!part) return; if (/^\s+$/.test(part)) f.appendChild(document.createTextNode(part)); else { var w = document.createElement('span'); w.className = 'w' + (reduce ? ' on' : ''); w.textContent = part; f.appendChild(w); } });
            n.parentNode.replaceChild(f, n);
          } else if (n.nodeType === 1) walk(n);
        });
      })(el);
      el._n = -1;
    });
  }
  function litWords() { lits.forEach(function (el) { el._w = $$('.w', el).filter(function (w) { return w.offsetParent !== null; }); el._n = -1; }); }
  function litTick(vh) {
    if (reduce) return;
    for (var i = 0; i < lits.length; i++) {
      var el = lits[i], r = el.getBoundingClientRect();
      if (r.bottom < -80 || r.top > vh + 80 || !el._w) continue;
      var n = Math.round(clamp((vh * 0.9 - r.top) / (vh * 0.42 + r.height * 0.55), 0, 1) * el._w.length);
      if (n === el._n) continue; el._n = n;
      for (var k = 0; k < el._w.length; k++) el._w[k].classList.toggle('on', k < n);
    }
  }
  // a number counts up the first time it is seen
  function counts() {
    var els = $$('[data-count]');
    function show(el, n) { el.textContent = SS.fmtN(n); }
    see(els, function (el, on) {
      if (!on || el._done) return; el._done = true;
      var to = +el.dataset.count, t0 = performance.now(), dur = 1300;
      if (reduce) { show(el, to); return; }
      (function step(now) { var k = clamp((now - t0) / dur, 0, 1); show(el, Math.round(to * (1 - Math.pow(1 - k, 3)))); if (k < 1) requestAnimationFrame(step); })(t0);
    }, 0.6);
    els.forEach(function (el) { if (!reduce) show(el, 0); });
    SS.onLang(function () { els.forEach(function (el) { if (el._done || reduce) show(el, +el.dataset.count); }); });
  }

  /* ---------------- the bar and the film ---------------- */
  var bar, bands = [], barH = 68, was = {}, vw = 1, vh = 1;
  function rgbOf(c) { var m = /rgba?\(([^)]+)\)/.exec(c); if (!m) return [15, 11, 24]; var v = m[1].split(/[\s,\/]+/).map(Number); return [v[0], v[1], v[2]]; }
  function layout() {
    vw = innerWidth; vh = innerHeight; barH = bar.offsetHeight;
    bands = $$('[data-field]').map(function (el) {
      var r = el.getBoundingClientRect(), cs = getComputedStyle(el), film = el.dataset.field === 'film', bg = rgbOf(cs.backgroundColor);
      return { top: r.top + scrollY, bottom: r.bottom + scrollY, film: film, ink: cs.color, btn: cs.getPropertyValue('--btn').trim(), btnInk: cs.getPropertyValue('--btn-ink').trim(), wm: cs.getPropertyValue('--wm').trim(),
        barBg: 'rgba(' + bg.join(', ') + ', ' + (parseFloat(cs.getPropertyValue('--bar-a')) || 0.8) + ')', theme: film ? '#0b0b0c' : cs.backgroundColor };
    });
    was.band = null; litWords(); fitBig();
    layouts.forEach(function (f) { f(vw, vh); });
  }
  var layouts = [];
  T.onLayout = function (f) { layouts.push(f); };
  function chrome(y) {
    var b = null, at = y + barH / 2, s = bar.style;
    for (var i = 0; i < bands.length; i++) if (at >= bands[i].top && at < bands[i].bottom) b = bands[i];
    if (!b || was.band === b) return; was.band = b;
    bar.setAttribute('data-on', b.film ? 'film' : 'on');
    if (b.film) ['--bar-ink', '--bar-bg', '--wm-em', '--bar-btn', '--bar-btn-ink'].forEach(function (k) { s.removeProperty(k); });
    else { s.setProperty('--bar-ink', b.ink); s.setProperty('--bar-bg', b.barBg); s.setProperty('--wm-em', b.wm || b.ink); s.setProperty('--bar-btn', b.btn); s.setProperty('--bar-btn-ink', b.btnInk); }
    SS.themeColor(b.theme);
  }
  function wake() {
    if (woke) return; woke = true;
    $$('img[data-src]').forEach(function (im) { im.src = im.dataset.src; im.removeAttribute('data-src'); });
    onWake.forEach(function (f) { f(); });
  }
  var big;
  function fitBig() { if (!big) return; big.style.fontSize = '100px'; var w = big.firstElementChild.getBoundingClientRect().width; if (w) big.style.fontSize = (100 * big.clientWidth / w * 0.98).toFixed(2) + 'px'; }

  /* ---------------- start ---------------- */
  T.start = function () {
    bar = $('.bar'); big = $('.foot .big');
    var reelSec = $('#reel'), hero = SS.reel(reelSec, $('#rdisc'));
    T.hero = hero;
    // pictures load once the film is playing, at the first scroll, or after a moment, whichever is first
    hero.video.addEventListener('playing', function () { setTimeout(wake, 300); }, { once: true });
    addEventListener('scroll', wake, { once: true, passive: true });
    if (document.readyState === 'complete') setTimeout(wake, 2600); else addEventListener('load', function () { setTimeout(wake, 2600); }, { once: true });
    ['#copyMail', '#copyMail2'].forEach(function (id) {
      var b = $(id); if (b) b.addEventListener('click', function () { SS.copy(SS.CONTACT, b, function () { var r = document.createRange(), s = getSelection(); r.selectNodeContents(b.previousElementSibling); s.removeAllRanges(); s.addRange(r); }); });
    });
    words(); litSplit(); counts();
    SS.onLang(function () { litWords(); layout(); });
    SS.start();
    if (window.ScrollCraft) ScrollCraft.mount(document.body);
    layout();
    if ('ResizeObserver' in window) new ResizeObserver(layout).observe(document.body); else addEventListener('resize', layout);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);
    // shapes: the cursor moves them a little, by their depth, and so does their own travel through the screen
    var layers = $$('.shapes'), ptr = [0, 0], cur = [0, 0], tPrev = 0, running = true;
    if (fine && !reduce) addEventListener('pointermove', function (e) { if (e.pointerType === 'mouse') { ptr[0] = (e.clientX / vw - 0.5) * 36; ptr[1] = (e.clientY / vh - 0.5) * 36; } }, { passive: true });
    function frame(now) {
      if (!running) return;
      var dt = Math.min(0.05, (now - tPrev) / 1000 || 0.016), y = scrollY, i; tPrev = now;
      hero.tick(); chrome(y); litTick(vh);
      if (!reduce) {
        cur[0] = lerp(cur[0], ptr[0], 0.08); cur[1] = lerp(cur[1], ptr[1], 0.08);
        var mx = cur[0].toFixed(1), my = cur[1].toFixed(1);
        if (was.mx !== mx) { was.mx = mx; root.style.setProperty('--mx', mx); }
        if (was.my !== my) { was.my = my; root.style.setProperty('--my', my); }
        for (i = 0; i < layers.length; i++) {
          var el = layers[i], r = el.getBoundingClientRect(); if (r.bottom < -100 || r.top > vh + 100) continue;
          var sy = (((r.top + r.height / 2) - vh / 2) / vh * -46).toFixed(1); if (el._sy !== sy) { el._sy = sy; el.style.setProperty('--sy', sy); }
        }
      }
      var c = { y: y, vh: vh, vw: vw, now: now, dt: dt };
      for (i = 0; i < frames.length; i++) frames[i](c);
      requestAnimationFrame(frame);
    }
    document.addEventListener('visibilitychange', function () { running = !document.hidden; if (running) { tPrev = performance.now(); requestAnimationFrame(frame); } });
    requestAnimationFrame(frame);
  };
})();
