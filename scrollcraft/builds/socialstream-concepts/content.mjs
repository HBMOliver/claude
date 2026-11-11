// Every word the four concepts use, in Hungarian and English, taken from Daylight (COPY.md), the brand film
// and Stream. Nothing here is new except where marked NEW (to be confirmed by the user).
// Text with markup is HTML; plain text is escaped by the parts that print it.

export const C = {
  nav: [
    { href: '#eredmenyek', hu: 'Eredmények', en: 'Results' },
    { href: '#igy', hu: 'Így dolgozunk', en: 'How we work' },
    { href: '#szolgaltatasok', hu: 'Szolgáltatások', en: 'Services' },
    { href: '#csapat', hu: 'Csapat', en: 'Team' },
    { href: '#kerdesek', hu: 'Kérdések', en: 'Questions' },
  ],
  navCta: { hu: 'Ingyenes audit', en: 'Free audit' },

  // the first screen: the brand's claim (the film's own line), the promise, the button
  eyebrow: { hu: 'Interest media ügynökség', en: 'Interest media agency' },
  claim: {
    hu: ['A <span class="strike">social media</span> meghalt.', 'Az <em>érdeklődés</em> vette át a helyét.'],
    en: ['<span class="strike">Social media</span> is dead.', '<em>Interest</em> has taken its place.'],
  },
  promise: { hu: ['Videók, amiket végignéznek.', 'Hirdetések, amik megtérülnek.'], en: ['Videos people watch to the end.', 'Ads that pay off.'] },
  lead: {
    hu: '<strong>Mi gyártjuk a videót, mi futtatjuk a hirdetést, és mi mérjük, mit hozott.</strong> A SocialStream egy kézben tartja a kreatívot, a kampányt és a landing oldalt, hogy minden forint a bevételt szolgálja.',
    en: '<strong>We make the video, we run the ads, and we measure what they bring in.</strong> SocialStream keeps the creative, the campaign and the landing page in one pair of hands, so every forint works toward revenue.',
  },
  lead1: { hu: 'Mi gyártjuk a videót, mi futtatjuk a hirdetést, és mi mérjük, mit hozott.', en: 'We make the video, we run the ads, and we measure what they bring in.' },
  cta: { hu: 'Kérem az ingyenes auditot', en: 'Get my free audit' },
  ctaResults: { hu: 'Megnézem az eredményeket', en: 'See the results' },
  ticks: [{ hu: 'Ingyenes', en: 'Free' }, { hu: '30 perc', en: '30 minutes' }, { hu: 'Kötelezettség nélkül', en: 'No obligation' }],

  // Stream's line about the name
  name: { hu: 'Igen, a nevünkben még ott a social. A <em>stream</em> maradt. Ami benne folyik, az változott.', en: 'Yes, our name still says social. The <em>stream</em> stayed. What flows in it changed.' },

  number: {
    eyebrow: { hu: '2022 óta', en: 'Since 2022' },
    h2: { hu: 'Ennyi hirdetési pénzről döntöttünk eddig.', en: 'This much ad money has passed through our hands.' },
    label: { hu: 'Kezelt büdzsé', en: 'Budget managed' },
    line: { hu: 'Minden forintnál ugyanazt kérdezzük: mit hoz vissza?', en: 'With every forint we ask the same question: what does it bring back?' },
  },

  problem: {
    h2: { hu: ['Posztolsz.', 'Hirdetsz.', 'Mégsem jönnek a vevők?'], en: ['You post.', 'You advertise.', 'And still no buyers?'] },
    body: { hu: 'A legtöbb vállalkozás ugyanabba a falba ütközik. A videót egy ember készíti, a hirdetést egy másik futtatja, az oldalt egy harmadik rakta össze évekkel ezelőtt. Mindenki jól csinálja a saját részét, de senki nem felel azért, hogy a végén legyen vásárlás.', en: 'Most businesses hit the same wall. One person makes the video, another runs the ads, a third built the website years ago. Everyone does their own part well, and nobody answers for whether anything gets sold.' },
    // the three questions are no longer on the pages: they live on in the services' problems (pain) below
    qs: [
      { hu: 'Melyik videó hozta a vásárlást?', en: 'Which video brought the sale?' },
      { hu: 'Miért drágul a hirdetés hónapról hónapra?', en: 'Why do ads cost more every month?' },
      { hu: 'Hová tűnnek az érdeklődők a kattintás után?', en: 'Where do people go after the click?' },
    ],
    drain: { hu: 'Közben a büdzsé elfolyik, és a figyelmet más viszi el.', en: 'Meanwhile the budget drains away, and someone else gets the attention.' },
    turn: { hu: 'Nem a platformmal van a baj, hanem azzal, hogy <em>senki nem látja egyben</em>.', en: 'The platform isn\'t the problem. <em>Nobody sees the whole picture.</em>' },
    whole: { hu: 'Mi egyben látjuk, a videótól a kattintáson át a vásárlásig.', en: 'We see it whole, from the video through the click to the sale.' },
  },

  // NEW, to confirm: each service carries the business problem it answers (services.items[].pain), each one the
  // reverse of that service's own line or one of the questions above; these are the labels around them
  pains: {
    eyebrow: { hu: 'Ismerős?', en: 'Sound familiar?' },
    help: { hu: 'Ebben segítünk', en: 'How we help' },
  },

  // NEW arrangement, to confirm: the problem's own sentences set side by side
  compare: {
    h2: { hu: 'Máshol és <em>nálunk</em>.', en: 'Elsewhere and <em>with us</em>.' },
    elseT: { hu: 'Máshol', en: 'Elsewhere' },
    usT: { hu: 'A SocialStreamnél', en: 'At SocialStream' },
    else: [
      { hu: 'A videót egy ember készíti.', en: 'One person makes the video.' },
      { hu: 'A hirdetést egy másik futtatja.', en: 'Another runs the ads.' },
      { hu: 'Az oldalt egy harmadik rakta össze.', en: 'A third built the website.' },
      { hu: 'Senki nem felel azért, hogy legyen vásárlás.', en: 'Nobody answers for whether anything sells.' },
    ],
    us: [
      { hu: 'Mi gyártjuk a videót.', en: 'We make the video.' },
      { hu: 'Mi futtatjuk a hirdetést.', en: 'We run the ads.' },
      { hu: 'Mi építjük az oldalt, ami befejezi, amit a videó elkezdett.', en: 'We build the page that finishes what the video started.' },
      { hu: 'És mi mérjük, mit hozott.', en: 'And we measure what it brought in.' },
    ],
  },

  who: {
    eyebrow: { hu: 'Kiknek dolgozunk', en: 'Who we work with' },
    h2: { hu: 'Márkáknak, amelyek már működnek, és most <em>nőni akarnak</em>.', en: 'Brands that already work, and now <em>want to grow</em>.' },
    lead: { hu: 'Akkor vagyunk jó választás, ha a vállalkozásod stabil bevételt termel, hosszú távon gondolkodsz, és befektetésnek látod a marketinget.', en: 'We are a good fit if your business has steady revenue, you think long term and you see marketing as an investment.' },
    cards: [
      { img: 'a-shop', hu: ['Webshopok', 'Vásárlások Google és Meta kampányokból. A legjobb e-commerce eredményünk: <b>81× ROAS</b> egy ajtó webshopnál.'], en: ['Webshops', 'Sales from Google and Meta campaigns. Our best e-commerce result: <b>81× ROAS</b> for a door webshop.'] },
      { img: 'a-b2b', hu: ['B2B szolgáltatók', 'Ajánlatkérések ott is, ahol „a Facebook nem működik”. Egy csarnoképítő ügyfélnek <b>79M Ft</b> bevétel egy hét alatt.'], en: ['B2B companies', 'Quote requests even where “Facebook doesn’t work”. <b>79M Ft</b> of revenue in one week for an industrial hall builder.'] },
      { img: 'a-events', hu: ['Webinárok és események', 'Jelentkezők alacsony költséggel: egy egészségügyi webinárnál <b>105 Ft</b> volt egy jelentkező.'], en: ['Webinars and events', 'Sign-ups at a low cost: <b>105 Ft</b> per registrant for a healthcare webinar.'] },
      { img: 'a-local', hu: ['Helyi szolgáltatók és élményprogramok', 'Szépségszalontól a tenerifei élményprogramig: videó, social és hirdetés egy csapattól.'], en: ['Local services and experiences', 'From beauty salons to experiences on Tenerife: video, social and ads from one team.'] },
    ],
    notfor: { hu: 'Nem neked való, ha egy éjszaka alatti sikert vagy olcsó félmegoldást keresel.', en: 'Not for you if you are after overnight success or a cheap half-measure.' },
  },

  steps: {
    eyebrow: { hu: 'Így dolgozunk', en: 'How we work' },
    h2: { hu: 'Négy lépés az első beszélgetéstől a <em>skálázásig</em>.', en: 'Four steps from the first call to <em>scaling</em>.' },
    items: [
      { hu: ['Audit', 'Ingyenes, 30 perces átvilágítás. Megnézzük a kampányaidat, a landing oldaladat és az ajánlatodat, és őszintén megmondjuk, hol folyik el a pénz.'], en: ['Audit', 'A free 30-minute review. We look at your campaigns, your landing page and your offer, and tell you honestly where the money leaks.'], chips: [['Kampányok', 'Campaigns'], ['Landing', 'Landing page'], ['Ajánlat', 'Offer']] },
      { hu: ['Stratégia', 'Kampánystratégia, funnel és pozicionálás: kinek, mit és melyik platformon mutatunk.'], en: ['Strategy', 'Campaign strategy, funnel and positioning: what we show, to whom, and where.'], chips: [['Funnel', 'Funnel'], ['Célzás', 'Targeting'], ['Pozicionálás', 'Positioning']] },
      { hu: ['Gyártás', 'Hookok, kreatív irány, forgatás és vágás. A videót mi készítjük, a koncepciótól a kész anyagig.'], en: ['Production', 'Hooks, creative direction, shooting and editing. We make the video ourselves, from concept to final cut.'], chips: [['Hook', 'Hooks'], ['Forgatás', 'Shooting'], ['Vágás', 'Editing']] },
      { hu: ['Hirdetés és skálázás', 'Meta, TikTok és Google kampányok napi optimalizálással és A/B teszteléssel. Ami működik, azt skálázzuk.'], en: ['Ads and scaling', 'Meta, TikTok and Google campaigns with daily optimisation and A/B testing. What works, we scale.'], chips: [['Meta', 'Meta'], ['TikTok', 'TikTok'], ['Google', 'Google']] },
    ],
    cta: { hu: 'Kezdjük az audittal', en: 'Start with the audit' },
  },

  services: {
    eyebrow: { hu: 'Szolgáltatások', en: 'Services' },
    h2: { hu: 'Minden, ami a növekedéshez kell. <em>Egy csapattól.</em>', en: 'Everything growth needs. <em>From one team.</em>' },
    items: [
      { id: 'video', icon: 'i-video', pain: ['A videóid mellett mindenki továbbgörget.', 'People scroll straight past your videos.'], k: ['Videó tartalomgyártás', 'Video production'], t: ['Videók, amik megállítják a görgetést.', 'Videos that stop the scroll.'], p: ['Hookok, kreatív irány és gyártás: a kampány motorja a kreatív, ezért azt is mi készítjük.', 'Hooks, creative direction and production: creative drives the campaign, so we make that too.'] },
      { id: 'social', icon: 'i-social', pain: ['Posztolsz, amikor jut rá idő, de alig reagál valaki.', 'You post when you find the time, and hardly anyone reacts.'], k: ['Social média jelenlét', 'Social media presence'], t: ['Jelenlét, ami több, mint posztolás.', 'More than posting.'], p: ['Feed, Stories, Reels és TikTok egy stratégiával és egy hanggal: tartalomnaptár, közösségkezelés, szövegírás.', 'Feed, Stories, Reels and TikTok with one strategy and one voice: content calendar, community management, copywriting.'] },
      { id: 'ads', icon: 'i-ads', pain: ['A hirdetés hónapról hónapra drágul, és nem tudod, mit hoz vissza.', 'Ads cost more every month, and you can’t tell what they bring back.'], k: ['Fizetett hirdetés', 'Paid advertising'], t: ['Hirdetés, ami bevételt hoz, nem csak megjelenést.', 'Ads that bring revenue, not just reach.'], p: ['Meta, TikTok és Google kampányok napi optimalizálással, A/B teszteléssel, skálázással.', 'Meta, TikTok and Google campaigns with daily optimisation, A/B testing and scaling.'] },
      { id: 'web', icon: 'i-web', pain: ['Kattintanak, aztán vásárlás nélkül eltűnnek az oldaladról.', 'People click, then leave your site without buying.'], k: ['Weboldal és landing', 'Website and landing pages'], t: ['Oldal, ami befejezi, amit a videó elkezdett.', 'A page that finishes what the video started.'], p: ['Gyors, mobilra tervezett landingek és weboldalak, amik konvertálnak.', 'Fast, mobile-first landing pages and websites that convert.'] },
      { id: 'auto', icon: 'i-auto', pain: ['Az érdeklődők kihűlnek, mert senki nem keresi őket időben.', 'Leads go cold because nobody gets back to them in time.'], k: ['Automatizáció és e-mail', 'Automation and email'], t: ['Követés, ami senkit nem felejt el.', 'Follow-up that forgets no one.'], p: ['Lead-követés, e-mail szekvenciák, automatizált tölcsérek: egyszer beállítjuk, utána dolgozik helyetted.', 'Lead follow-up, email sequences, automated funnels: set up once, then it works for you.'] },
      { id: 'strat', icon: 'i-strat', pain: ['Nem tudod, melyik videó hozta a vásárlást, és hogy merre tovább.', 'You can’t tell which video brought the sale, or what to do next.'], k: ['Növekedési stratégia', 'Growth strategy'], t: ['Stratégia, ami összeköti a többit.', 'The strategy that ties it together.'], p: ['Kampánystratégia, funnel audit és piaci pozicionálás, partnerként.', 'Campaign strategy, funnel audit and market positioning, as a partner.'] },
    ],
  },

  results: {
    eyebrow: { hu: 'Valódi ügyfelek · valódi számok', en: 'Real clients · real numbers' },
    h2: { hu: 'Számok, amiket az ügyfeleinknek hoztunk.', en: 'Numbers we brought our clients.' },
    items: [
      { obj: 'o-door', n: 81, unit: '× ROAS', who: ['Ajtó webshop · Google Performance Max', 'Door webshop · Google Performance Max'], p: ['1 forint hirdetésből 81 forint bevétel.', '81 forints of revenue for every forint of ads.'] },
      { obj: 'o-hall', n: 79, unit: 'M Ft', who: ['Csarnoképítő ügyfél · Meta', 'Industrial hall builder · Meta'], p: ['Bevétel egy hét alatt, egy B2B kampányból.', 'Revenue in one week, from one B2B campaign.'] },
      { obj: 'o-watch', n: 23, unit: '× ROAS', who: ['Karóra webshop · Karácsony', 'Watch webshop · Christmas'], p: ['Ünnepi kampány, több mint 8M Ft bevétellel.', 'A holiday campaign with over 8M Ft in revenue.'] },
      { obj: 'o-webinar', n: 105, unit: 'Ft', who: ['Egészségügyi webinár', 'Healthcare webinar'], p: ['Ennyibe került egy jelentkező: körülbelül 5700 jelentkező 600K Ft-ból.', 'The cost of one registrant: about 5,700 registrants from 600K Ft.'] },
    ],
    cta: { hu: 'Ilyen számokat szeretnék', en: 'I want numbers like these' },
  },
  // a running band of the same real numbers, word for word from the results above
  ticker: [
    { hu: '81× ROAS · Ajtó webshop', en: '81× ROAS · Door webshop' },
    { hu: '79M Ft bevétel egy hét alatt · B2B', en: '79M Ft of revenue in one week · B2B' },
    { hu: '23× ROAS · Karóra webshop, karácsony', en: '23× ROAS · Watch webshop, Christmas' },
    { hu: '105 Ft egy jelentkező · Egészségügyi webinár', en: '105 Ft per registrant · Healthcare webinar' },
    { hu: '300M+ Ft kezelt büdzsé 2022 óta', en: '300M+ Ft budget managed since 2022' },
  ],
  // service and platform words for the running tag bands (all from the services and the steps)
  tags: [
    ['Videó tartalomgyártás', 'Video production'], ['Hook', 'Hooks'], ['Forgatás', 'Shooting'], ['Vágás', 'Editing'],
    ['Social média jelenlét', 'Social media presence'], ['Reels', 'Reels'], ['TikTok', 'TikTok'], ['Fizetett hirdetés', 'Paid advertising'],
    ['Meta', 'Meta'], ['Google', 'Google'], ['A/B tesztelés', 'A/B testing'], ['Weboldal és landing', 'Website and landing pages'],
    ['Automatizáció és e-mail', 'Automation and email'], ['Funnel', 'Funnel'], ['Célzás', 'Targeting'], ['Növekedési stratégia', 'Growth strategy'],
  ],

  reels: {
    h2: { hu: 'Ami <em>megállítja</em> a hüvelykujjat.', en: 'What <em>stops</em> the thumb.' },
    caption: { hu: 'Képkockák az ügyfeleinknek készült videókból.', en: 'Frames from the videos we made for our clients.' },
    // frames from their own client reels; p12 (another creator's name) is out, and the ones with
    // "Tenerife" in the caption never sit on a first screen
    all: ['p02', 'p03', 'p04', 'p05', 'p06', 'p07', 'p08', 'p09', 'p10', 'p11', 'p13', 'p14', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24'],
    firstScreen: ['p02', 'p04', 'p05', 'p14', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p23', 'p24'],
  },

  voices: {
    eyebrow: { hu: 'Ügyfeleink szavaival', en: 'In our clients\' words' },
    h2: { hu: 'Ne nekünk higgy. <em>Nekik.</em>', en: 'Don\'t take our word for it. <em>Take theirs.</em>' },
    pull: { hu: '„Már az induláskor is volt vásárlás – olyan számokat produkált, amit eddig nem is láttunk.”', en: '“There were purchases from launch day, and he produced numbers we had never seen before.”', who: 'Péter · Hoofbútor' },
    quotes: [
      { hu: '„Egyszer már leállítottuk a Facebook hirdetéseinket, mert egyszerűen nem érte meg. Miután megismertük Olivért, adtunk egy újabb esélyt. Már az induláskor is volt vásárlás – olyan számokat produkált, amit eddig nem is láttunk.”', en: '“We had already switched off our Facebook ads once because they simply weren’t worth it. After meeting Olivér we gave it another chance. There were purchases from launch day, and he produced numbers we had never seen before.”', who: ['Péter · Hoofbútor', 'Péter · Hoofbútor'] },
      { hu: '„Azt hittük, a Facebook a fiataloknak és a webshopoknak való – mi csarnokot építünk. Aztán egy hét alatt annyi ajánlatkérésünk lett, mint korábban fél év alatt összesen.”', en: '“We thought Facebook was for young people and webshops; we build industrial halls. Then in one week we got as many quote requests as we used to get in half a year.”', who: ['Csarnoképítő ügyfél · B2B', 'Hall-building client · B2B'], metric: { n: '79M Ft', hu: 'bevétel egy hét alatt', en: 'revenue in one week' } },
      { hu: '„Minden decemberben rettegtünk a hirdetési áraktól. Idén először éreztük úgy, hogy az ünnepi szezon nekünk dolgozik – nem ellenünk.”', en: '“Every December we dreaded ad prices. This year, for the first time, the holiday season felt like it was working for us, not against us.”', who: ['Karóra webshop', 'Watch webshop'], metric: { n: '23× ROAS', hu: 'ünnepi kampány', en: 'holiday campaign' } },
      { hu: '„Pár száz jelentkezőre számítottunk a webinárra. Amikor a számláló majdnem 5700-nál állt meg, alig hittük el, hogy ez ugyanabból a büdzséből jött ki.”', en: '“We expected a few hundred registrants for the webinar. When the counter stopped at almost 5,700, we could hardly believe it came from the same budget.”', who: ['Egészségügyi szolgáltató', 'Healthcare provider'], metric: { n: '105 Ft', hu: 'egy jelentkező', en: 'per registrant' } },
      { hu: '„Profi csapatot szerettem volna az indulás után. Mind Facebook/Instagram, mind weboldal és hirdetés területén profi kampányokat készítenek. Rövid időn belül jöttek az eredmények – nekem semmi dolgom nem volt velük.”', en: '“I wanted a professional team after launch. They build professional campaigns across Facebook/Instagram, the website and ads. Results came quickly, and I had nothing to do.”', who: ['Rita · Rita’s Beauty Corner', 'Rita · Rita’s Beauty Corner'] },
      { hu: '„A Social Stream profi módon készítette el a weboldalam. Mindenkinek tetszett az igényes és könnyen áttekinthető tartalom! Csak ajánlani tudom őket.”', en: '“Social Stream built my website professionally. Everyone loved the polished, easy-to-follow content! I can only recommend them.”', who: ['János · EJ Massage Therapies', 'János · EJ Massage Therapies'] },
    ],
  },

  team: {
    eyebrow: { hu: 'A csapat', en: 'The team' },
    h2: { hu: 'Akik a fiókodon dolgoznak.', en: 'The people working on your account.' },
    people: [
      { img: 'team-oliver', name: 'Olivér', role: ['Alapító, kampánystratéga', 'Founder, campaign strategist'], p: ['Meta Marketing Pro-ként látta, hogyan gondolkodnak a legkomolyabb márkák. 2022-ben alapította a SocialStreamet.', 'As a Meta Marketing Pro he saw how the most serious brands think. He founded SocialStream in 2022.'] },
      { img: 'team-david', name: 'David', role: ['Kreatív és tartalomgyártás', 'Creative and content production'], p: ['Hookok, forgatás, kreatív irány.', 'Hooks, shooting, creative direction.'] },
      { img: 'team-lidi', name: 'Lidi', role: ['Produkció és szerkesztés', 'Production and editing'], p: ['Vágás, ritmus, precizitás, határidőre.', 'Editing, rhythm, precision, on deadline.'] },
    ],
  },

  offer: {
    eyebrow: { hu: 'Az ajánlat', en: 'The offer' },
    h2: { hu: '30 perc, ami megmutatja, <em>hol hagysz pénzt az asztalon</em>.', en: '30 minutes that show <em>where you\'re leaving money on the table</em>.' },
    checks: [
      { hu: 'Átnézzük a hirdetéseidet és a kampányaidat.', en: 'We go through your ads and campaigns.' },
      { hu: 'Megnézzük a landing oldaladat.', en: 'We look at your landing page.' },
      { hu: 'Értékeljük az ajánlatodat.', en: 'We assess your offer.' },
      { hu: 'Őszintén megmondjuk, mit csinálnánk másképp, még mielőtt bármit fizetnél.', en: 'We tell you honestly what we would do differently, before you pay anything.' },
    ],
    specs: [[['Hossz', 'Length'], ['30 perc', '30 minutes']], [['Ár', 'Price'], ['Ingyenes', 'Free']], [['Kötelezettség', 'Obligation'], ['Nincs', 'None']]],
    scarce: { hu: 'Havonta legfeljebb két új partnert vállalunk.', en: 'We take on at most two new partners a month.' },
  },

  faq: {
    eyebrow: { hu: 'Kérdések', en: 'Questions' },
    h2: { hu: 'Amit a legtöbben megkérdeznek.', en: 'What most people ask.' },
    items: [
      [['Mennyibe kerül az audit?', 'What does the audit cost?'], ['Semmibe. Ingyenes, és nem jár kötelezettséggel.', 'Nothing. It\'s free, with no obligation.']],
      [['Mennyi ideig tart?', 'How long does it take?'], ['30 percig.', '30 minutes.']],
      [['Mi történik, miután elküldöm?', 'What happens after I send it?'], ['Válaszolunk az e-mailedre, és egyeztetünk egy időpontot a 30 perces auditra.', 'We reply to your email and set a time for the 30-minute audit.']],
      [['Mit kapok az audit végén?', 'What do I get from it?'], ['Átnézzük a kampányaidat, a landing oldaladat és az ajánlatodat, és őszintén megmondjuk, mit csinálnánk másképp, még mielőtt bármit fizetnél.', 'We go through your campaigns, landing page and offer, and tell you honestly what we would do differently, before you pay anything.']],
      [['Kikkel dolgoztok?', 'Who do you work with?'], ['Stabil bevételű márkákkal, amelyek hosszú távon gondolkodnak, és befektetésnek látják a marketinget. Havonta legfeljebb két új partnert vállalunk.', 'Brands with steady revenue that think long term and see marketing as an investment. We take on at most two new partners a month.']],
      [['A videót is ti készítitek?', 'Do you make the videos too?'], ['Igen. A hookoktól és a kreatív iránytól a forgatáson át a vágásig mi gyártjuk, nem csak hirdetjük.', 'Yes. From hooks and creative direction through shooting to editing, we make them, not just run them.']],
      [['Hol hirdettek?', 'Where do you advertise?'], ['A Meta felületein (Facebook, Instagram), a TikTokon és a Google-ön.', 'On Meta (Facebook, Instagram), TikTok and Google.']],
      [['Hol vagytok?', 'Where are you based?'], ['Tenerifén és Budapesten.', 'Tenerife and Budapest.']],
    ],
  },

  final: {
    h2: { hu: 'A következő vevőd <em>már görget</em>. Te ott vagy?', en: 'Your next customer <em>is already scrolling</em>. Are you there?' },
    small: { hu: 'Havonta legfeljebb két új partner.', en: 'At most two new partners a month.' },
  },
  footer: { line: { hu: 'Interest media ügynökség · Tenerife és Budapest', en: 'Interest media agency · Tenerife and Budapest' } },
  film: { label: { hu: 'A SocialStream márkafilmje', en: 'The SocialStream brand film' } },
};
