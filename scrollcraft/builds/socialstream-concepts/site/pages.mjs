// The pages of socialstream.hu: one entry per page, each with its address in both languages, its title and
// description, and the words only that page has. The plan is the Claude Docs doc "SocialStream SEO, AEO and subpage
// plan" (2026-11-16); this is its phase 2, the core pages. Hungarian sits at the root, English under /en/.
//
// The words: everything here is NEW and waits for the founder's yes (COPY.md lists it), but it says nothing that is
// not already on the site (content.mjs): the same services, numbers, steps, team and reviews, in new sentences.
// Left out until the founder sends them (the doc's "Needed from you"): pricing, the legal notice and privacy policy,
// a phone number or address, profile links, proof for automation, the audience pages and /en/tenerife/.
// Case studies (2026-11-16, the founder: "Case studies first"): the hub and the four anonymous cases, from the
// site's own results and their clients' words only. The named clients agreed to be named with numbers (the
// founder, "i have everyones approval"), but what SocialStream did for FlyX and Prof Enzo, and since when, is not
// on the site yet: their cases and their numbers on the social media page are drafts (draft: true), built only with
// SS_DRAFTS=1 into dist/site-drafts for review, never into dist/site.
// No em dashes anywhere in the copy (tools/site.mjs stops on one).
import { C } from '../content.mjs';

const DRAFTS = !!process.env.SS_DRAFTS;
export const ORIGIN = 'https://socialstream.hu';
const p = (hu, en) => ({ hu, en });
const svc = id => C.services.items.find(s => s.id === id);
// a question from the home page's eight (content.mjs, faq), as it stands there
const homeQ = i => ({ q: p(...C.faq.items[i][0]), a: p(...C.faq.items[i][1]) });
const q = (qhu, qen, ahu, aen) => ({ q: p(qhu, qen), a: p(ahu, aen) });

// The named clients' own numbers, worded as the film words them (video/sizzle/SPEC.md, Honesty). 69K is one of FlyX
// Tenerife's reels on Facebook, organic (the founder: some of their videos have far more). 9,8M+ is every view of Prof
// Enzo's Facebook page since it began (Meta's "All views", 9,828,876, rounded down), all organic: we have run the page
// since its first post, and its ads bring in leads, not views (the founder, 2026-11-18). So "views on Facebook",
// never "reel views".
const NAMED = [
  // img: one of their own reels (already on the site) on the number's card
  { n: '69K', who: p('FlyX Tenerife · Élményközpont', 'FlyX Tenerife · Experience centre'), d: p('organikus megtekintés egy reelen', 'organic views on one reel'), page: 'case-flyx', img: 'r-flyx-1.jpg' },
  { n: p('9,8M+', '9.8M+'), who: p('Prof Enzo · Facebook', 'Prof Enzo · Facebook'), d: p('organikus megtekintés · 33K követő', 'organic views · 33K followers'), page: 'case-enzo', img: 'r-enzo-1.jpg' },
];

// shared words of the site's pages
export const W = {
  home: p('Főoldal', 'Home'),
  menu: p('Menü', 'Menu'),
  crumbs: p('Morzsamenü', 'Breadcrumb'),
  details: p('Részletek', 'Details'),
  included: p('Mit kapsz?', 'What you get'),
  questions: p('Kérdések', 'Questions'),
  pain: p('Ismerős?', 'Sound familiar?'),
  more: p('Szolgáltatások', 'Services'),
  line: p('Interest media ügynökség · 2022 óta · Tenerife és Budapest', 'Interest media agency · Since 2022 · Tenerife and Budapest'),
  pagesGroup: p('SocialStream', 'SocialStream'),
  // Up To Youth is the founder's own organisation: wherever its videos are shown as our work, the page says so
  uty: p('Az Up To Youth az alapítónk saját szervezete.', 'Up To Youth is our founder’s own organisation.'),
};

// The pages. nav: the header's links, in this order; parent: the page above it in the breadcrumb.
const ALL = [
  {
    id: 'home', type: 'home', path: p('/', '/en/'),
    // the live title and description stay until the founder approves the doc's drafts (its "Five fixes first", 2):
    // Title (HU) "SocialStream | Videós social media és hirdetési ügynökség", Meta (HU) "Videót gyártunk, Meta, TikTok és
    // Google hirdetést futtatunk, és mérjük, mit hozott. 81× ROAS, 79M Ft egy hét alatt. Ingyenes 30 perces audit."
    title: p('SocialStream · Interest media ügynökség', 'SocialStream · Interest media agency'),
    desc: p('A social media meghalt. Az érdeklődés vette át a helyét. Videó, social és hirdetés egy csapattól.', 'Social media is dead. Interest has taken its place. Video, social and ads from one team.'),
    crumb: p('Főoldal', 'Home'),
  },
  {
    id: 'services', type: 'hub', path: p('/szolgaltatasok/', '/en/services/'),
    title: p('Szolgáltatások: videó, social media és hirdetés · SocialStream', 'Services: video, social media and ads · SocialStream'),
    desc: p('Videógyártás, social media kezelés, Meta, TikTok és Google hirdetések, weboldal és landing oldal, automatizáció és növekedési stratégia, egy csapattól.',
      'Video production, social media management, Meta, TikTok and Google ads, websites and landing pages, automation and growth strategy, from one team.'),
    crumb: p('Szolgáltatások', 'Services'), nav: p('Szolgáltatások', 'Services'),
    // its own line, because the services' heading (content.mjs) stands over the cards further down the page
    h1k: C.services.eyebrow, h1t: p('Hat szolgáltatás, <em>egy csapattól</em>.', 'Six services, <em>one team</em>.'), lead: C.lead,
  },
  {
    id: 'svc-video', type: 'service', svc: 'video', parent: 'services', path: p('/szolgaltatasok/videogyartas/', '/en/services/video-production/'),
    title: p('Hirdetési videó és reels készítés · SocialStream', 'Video production for ads and reels · SocialStream'),
    desc: p('Hirdetési videókat és reelseket gyártunk a hooktól a vágásig, a koncepciótól a kész anyagig. Utána mi futtatjuk a hirdetést, és mi mérjük, mit hozott.',
      'We make ad videos and reels, from the hook to the final cut. Then we run the ads ourselves and measure what they bring in.'),
    h1k: p('Hirdetési videó és reels készítés', 'Video production for ads and reels'),
    lead: p('Hookot írunk, kreatív irányt adunk, forgatunk és vágunk: a videót a koncepciótól a kész anyagig mi készítjük. A kampány motorja a kreatív, ezért ugyanaz a csapat futtatja a hirdetést, és méri, mit hozott.',
      'We write the hooks, set the creative direction, shoot and edit: we make the video from concept to final cut. Creative drives the campaign, so the same team runs the ads and measures what they bring in.'),
    included: [p('Hookok és kreatív irány', 'Hooks and creative direction'), p('Forgatás', 'Shooting'), p('Vágás, hang és fotó', 'Editing, sound and photography'), p('Reels, TikTok és hirdetési videók', 'Reels, TikTok and ad videos'), p('A hirdetés és a mérés ugyanattól a csapattól', 'The ads and the measurement from the same team')],
    // who does it, from the team's own lines (content.mjs, team)
    who: p('Akik csinálják: David (hookok, forgatás, kreatív irány) és Bálint (forgatás, vágás, hang és fotó).', 'Who makes it: David (hooks, shooting, creative direction) and Bálint (shooting, editing, sound and photography).'),
    proof: { reels: 'all' },
    faq: [homeQ(5), homeQ(6)],
  },
  {
    id: 'svc-social', type: 'service', svc: 'social', parent: 'services', path: p('/szolgaltatasok/social-media-kezeles/', '/en/services/social-media-management/'),
    title: p('Social media kezelés és tartalomgyártás · SocialStream', 'Social media management and content · SocialStream'),
    desc: p('Feed, Stories, Reels és TikTok egy stratégiával és egy hanggal: tartalomnaptár, közösségkezelés és szövegírás. A videókat is mi gyártjuk.',
      'Feed, Stories, Reels and TikTok with one strategy and one voice: content calendar, community management and copywriting. We make the videos too.'),
    h1k: p('Social media kezelés', 'Social media management'),
    lead: p('Feed, Stories, Reels és TikTok egy stratégiával és egy hanggal. Mi készítjük a tartalomnaptárt, mi kezeljük a közösséget, mi írjuk a szövegeket, és a videókat is mi gyártjuk.',
      'Feed, Stories, Reels and TikTok with one strategy and one voice. We plan the content calendar, manage the community, write the copy and make the videos ourselves.'),
    included: [p('Tartalomnaptár', 'Content calendar'), p('Közösségkezelés', 'Community management'), p('Szövegírás', 'Copywriting'), p('Feed, Stories és Reels', 'Feed, Stories and Reels'), p('TikTok', 'TikTok'), p('A videók is tőlünk', 'The videos from us too')],
    // Rita's words name Facebook/Instagram; FlyX's and Prof Enzo's numbers (NAMED), both organic, since the founder
    // said what we do for them (2026-11-18)
    proof: { reels: ['r-flyx-1', 'r-enzo-2', 'r-flyx-2', 'r-enzo-1', 'r-flyx-3', 'r-andras-1', 'r-andras-2'], quotes: [4], named: NAMED },
    faq: [q('Melyik felületekkel foglalkoztok?', 'Which platforms do you cover?', 'Feed, Stories, Reels és TikTok, egy stratégiával és egy hanggal.', 'Feed, Stories, Reels and TikTok, with one strategy and one voice.'), homeQ(5), homeQ(4)],
  },
  {
    id: 'svc-ads', type: 'service', svc: 'ads', parent: 'services', path: p('/szolgaltatasok/hirdeteskezeles/', '/en/services/paid-ads/'),
    title: p('Facebook, TikTok és Google hirdetéskezelés · SocialStream', 'Meta, TikTok and Google ads management · SocialStream'),
    desc: p('Meta, TikTok és Google kampányok napi optimalizálással és A/B teszteléssel. 81× ROAS egy ajtó webshopnál, 79M Ft bevétel egy hét alatt egy B2B kampányból.',
      'Meta, TikTok and Google campaigns with daily optimisation and A/B testing. 81× ROAS for a door webshop, €216K of revenue in one week from one B2B campaign.'),
    h1k: p('Facebook, TikTok és Google hirdetéskezelés', 'Meta, TikTok and Google ads management'),
    lead: p('Meta (Facebook, Instagram), TikTok és Google kampányokat futtatunk napi optimalizálással és A/B teszteléssel, és amelyik működik, azt skálázzuk. 2022 óta több mint 300M Ft hirdetési pénzről döntöttünk, és minden forintnál ugyanazt kérdezzük: mit hoz vissza?',
      'We run Meta (Facebook, Instagram), TikTok and Google campaigns with daily optimisation and A/B testing, and we scale what works. Since 2022, more than €820K of ad money has passed through our hands, and with every euro we ask the same question: what does it bring back?'),
    included: [p('Meta: Facebook és Instagram', 'Meta: Facebook and Instagram'), p('TikTok', 'TikTok'), p('Google, Performance Max is', 'Google, Performance Max too'), p('Napi optimalizálás', 'Daily optimisation'), p('A/B tesztelés', 'A/B testing'), p('Célzás és skálázás', 'Targeting and scaling')],
    proof: { stats: true, quotes: [0, 1, 2] },
    faq: [homeQ(6),
      q('Működik a Facebook-hirdetés B2B cégeknek?', 'Do Facebook ads work for B2B companies?', 'Egy csarnoképítő ügyfelünknél egy B2B kampány egy hét alatt 79M Ft bevételt hozott. Ők is azt hitték, hogy a Facebook a fiataloknak és a webshopoknak való.', 'For an industrial hall builder, one B2B campaign brought in €216K of revenue in one week. They, too, thought Facebook was for young people and webshops.'),
      q('Mennyi hirdetési pénzt kezeltetek eddig?', 'How much ad budget have you managed?', '2022 óta több mint 300M Ft-ot. Minden forintnál ugyanazt kérdezzük: mit hoz vissza?', 'More than €820K since 2022. With every euro we ask the same question: what does it bring back?'),
      q('Mit jelent a 81× ROAS?', 'What does 81× ROAS mean?', 'Azt, hogy 1 forint hirdetésből 81 forint bevétel lett. Ezt egy ajtó webshop Google Performance Max kampányában értük el.', 'That every €1 of ads brought in €81 of revenue, in a door webshop’s Google Performance Max campaign.')],
  },
  {
    id: 'svc-web', type: 'service', svc: 'web', parent: 'services', path: p('/szolgaltatasok/weboldal-es-landing-oldal/', '/en/services/websites-and-landing-pages/'),
    title: p('Landing oldal és weboldal készítés · SocialStream', 'Landing pages and websites that convert · SocialStream'),
    desc: p('Gyors, mobilra tervezett landing oldalak és weboldalak, amik konvertálnak. A videót és a hirdetést is mi készítjük, így az oldal befejezi, amit a videó elkezdett.',
      'Fast, mobile-first landing pages and websites that convert. We make the video and run the ads too, so the page finishes what the video started.'),
    h1k: p('Landing oldal és weboldal készítés', 'Landing pages and websites'),
    lead: p('Gyors, mobilra tervezett landing oldalakat és weboldalakat építünk, amik konvertálnak. A videót és a hirdetést is mi készítjük, így az oldal azt fejezi be, amit a videó elkezdett.',
      'We build fast, mobile-first landing pages and websites that convert. We make the video and run the ads too, so the page finishes what the video started.'),
    included: [p('Landing oldalak', 'Landing pages'), p('Weboldalak', 'Websites'), p('Mobilra tervezve', 'Designed for phones first'), p('Gyors betöltés', 'Fast to load'), p('Konverzióra építve', 'Built to convert')],
    // "we built this site too" is left out until the founder says so (the doc suggests it; the site does not say it)
    proof: { quotes: [5, 4] },
    faq: [q('Landing oldalt vagy teljes weboldalt készítetek?', 'Do you build landing pages or whole websites?', 'Mindkettőt: gyors, mobilra tervezett landing oldalakat és weboldalakat, amik konvertálnak.', 'Both: fast, mobile-first landing pages and websites that convert.'),
      q('Ki építi az oldalt?', 'Who builds the site?', 'David, a fejlesztőnk: weboldalak, landing oldalak, automatizálás.', 'David, our developer: websites, landing pages, automation.'),
      q('A hirdetést is ti futtatjátok hozzá?', 'Do you run the ads for it too?', 'Igen. Mi gyártjuk a videót, mi futtatjuk a hirdetést, és mi építjük az oldalt, ami befejezi, amit a videó elkezdett.', 'Yes. We make the video, we run the ads, and we build the page that finishes what the video started.')],
  },
  {
    id: 'svc-auto', type: 'service', svc: 'auto', parent: 'services', path: p('/szolgaltatasok/automatizacio-es-email/', '/en/services/automation-and-email/'),
    title: p('E-mail marketing és automatizáció · SocialStream', 'Email marketing and automation · SocialStream'),
    desc: p('Lead-követés, e-mail szekvenciák és automatizált tölcsérek: egyszer beállítjuk, utána dolgozik helyetted, és nem hűlnek ki az érdeklődők.',
      'Lead follow-up, email sequences and automated funnels: set up once, then it works for you, and leads don’t go cold.'),
    h1k: p('E-mail marketing és automatizáció', 'Email marketing and automation'),
    lead: p('Lead-követést, e-mail szekvenciákat és automatizált tölcséreket építünk. Egyszer beállítjuk, utána dolgozik helyetted, így az érdeklődő akkor kap választ, amikor még érdekli.',
      'We build lead follow-up, email sequences and automated funnels. Set up once, it works for you, so a lead hears back while they are still interested.'),
    included: [p('Lead-követés', 'Lead follow-up'), p('E-mail szekvenciák', 'Email sequences'), p('Automatizált tölcsérek', 'Automated funnels'), p('Egyszer beállítjuk, utána dolgozik', 'Set up once, then it works')],
    // no proof yet: the doc asks the founder for examples
    proof: {},
    faq: [q('Mit automatizáltok?', 'What do you automate?', 'A lead-követést, az e-mail szekvenciákat és a tölcséreket: egyszer beállítjuk, utána dolgozik helyetted.', 'Lead follow-up, email sequences and funnels: set up once, then it works for you.'),
      q('Ki építi meg?', 'Who builds it?', 'David, a fejlesztőnk: weboldalak, landing oldalak, automatizálás.', 'David, our developer: websites, landing pages, automation.'), homeQ(4)],
  },
  {
    id: 'svc-strat', type: 'service', svc: 'strat', parent: 'services', path: p('/szolgaltatasok/novekedesi-strategia/', '/en/services/growth-strategy/'),
    title: p('Marketing stratégia és funnel audit · SocialStream', 'Marketing strategy and funnel audit · SocialStream'),
    desc: p('Kampánystratégia, funnel audit és piaci pozicionálás, partnerként: egyben látjuk a videót, a kattintást és a vásárlást. Kezdd az ingyenes 30 perces audittal.',
      'Campaign strategy, funnel audit and market positioning, as a partner: we see the video, the click and the sale as one. Start with the free 30-minute audit.'),
    h1k: p('Marketing stratégia és funnel audit', 'Marketing strategy and funnel audit'),
    lead: p('Kampánystratégiát, funnel auditot és piaci pozicionálást adunk, partnerként. Nem a platformmal van a baj, hanem azzal, hogy senki nem látja egyben. Mi egyben látjuk, a videótól a kattintáson át a vásárlásig.',
      'We bring campaign strategy, a funnel audit and market positioning, as a partner. The platform isn’t the problem. Nobody sees the whole picture. We see it whole, from the video through the click to the sale.'),
    included: [p('Kampánystratégia', 'Campaign strategy'), p('Funnel audit', 'Funnel audit'), p('Piaci pozicionálás', 'Market positioning'), p('Célzás: kinek, mit és melyik platformon mutatunk', 'Targeting: what we show, to whom, and where')],
    proof: { compare: true },
    faq: [homeQ(3), homeQ(0),
      q('Mi jön az audit után?', 'What comes after the audit?', 'A stratégia: kampánystratégia, funnel és pozicionálás, vagyis kinek, mit és melyik platformon mutatunk. Utána jön a gyártás, végül a hirdetés és a skálázás.', 'The strategy: campaign strategy, funnel and positioning, that is, what we show, to whom, and where. Then production, and finally the ads and scaling.')],
  },
  // ---- case studies: the hub, then one page per case. res: the result on the home page (content.mjs, results) the
  // case is built on; quote: its client's words there (voices); uses: the service pages it took. A case says only
  // what the site already says about it: no period, budget or method until the founder sends them.
  {
    id: 'cases', type: 'cases', path: p('/esettanulmanyok/', '/en/case-studies/'),
    title: p('Esettanulmányok: valódi ügyfelek, valódi számok · SocialStream', 'Case studies: real clients, real numbers · SocialStream'),
    desc: p('81× ROAS egy ajtó webshopnál, 79M Ft bevétel egy hét alatt egy B2B kampányból, 23× ROAS karácsonykor, 105 Ft egy webinár-jelentkező. Ügyfeleink számai, platformmal.',
      '81× ROAS for a door webshop, €216K in a week from one B2B campaign, 23× ROAS at Christmas, €0.29 per webinar registrant. Real clients, real numbers.'),
    crumb: p('Esettanulmányok', 'Case studies'),
    h1k: p('Esettanulmányok', 'Case studies'), h1t: C.results.h2,
    lead: p('Valódi ügyfelek, valódi számok: minden esetnél ott a platform, és ahol van, az ügyfél saját szava.', 'Real clients, real numbers: each case with its platform and, where there is one, the client’s own words.'),
  },
  {
    id: 'case-door', type: 'case', parent: 'cases', res: 'o-door', uses: ['svc-ads'], path: p('/esettanulmanyok/ajto-webshop/', '/en/case-studies/door-webshop/'),
    title: p('Ajtó webshop: 81× ROAS Google Performance Maxszel · SocialStream', 'Door webshop: 81× ROAS with Google Performance Max · SocialStream'),
    desc: p('Egy ajtó webshop Google Performance Max kampányában 1 forint hirdetésből 81 forint bevétel lett. Esettanulmány valódi számokkal.',
      'In a door webshop’s Google Performance Max campaign, every €1 of ads brought in €81 of revenue. A case study with real numbers.'),
    crumb: p('Ajtó webshop', 'Door webshop'),
    h1k: p('Ajtó webshop · Google Performance Max', 'Door webshop · Google Performance Max'),
    h1t: p('1 forint hirdetésből <em>81 forint</em> bevétel.', '<em>€81</em> of revenue for every €1 of ads.'),
    lead: p('Ezt egy ajtó webshop Google Performance Max kampányában értük el: 1 forint hirdetésből 81 forint bevétel lett, vagyis 81× ROAS.',
      'We reached it in a door webshop’s Google Performance Max campaign: every €1 of ads brought in €81 of revenue, that is 81× ROAS.'),
  },
  {
    id: 'case-hall', type: 'case', parent: 'cases', res: 'o-hall', quote: 1, uses: ['svc-ads'], path: p('/esettanulmanyok/b2b-csarnokepito/', '/en/case-studies/industrial-hall-builder/'),
    title: p('B2B Facebook-hirdetés: 79M Ft egy hét alatt · SocialStream', 'B2B Facebook ads: €216K in one week · SocialStream'),
    desc: p('Egy csarnoképítő ügyfelünk azt hitte, a Facebook a fiataloknak és a webshopoknak való. Egy B2B kampány a Metán egy hét alatt 79M Ft bevételt hozott.',
      'An industrial hall builder thought Facebook was for young people and webshops. One B2B campaign on Meta brought in €216K of revenue in one week.'),
    crumb: p('Csarnoképítő ügyfél', 'Industrial hall builder'),
    h1k: p('Csarnoképítő ügyfél · B2B · Meta', 'Industrial hall builder · B2B · Meta'),
    h1t: p('<em>79M Ft</em> bevétel egy hét alatt.', '<em>€216K</em> of revenue in one week.'),
    lead: p('Ajánlatkérések ott is, ahol „a Facebook nem működik”: egy csarnoképítő ügyfélnek egy B2B kampány a Metán egy hét alatt 79M Ft bevételt hozott.',
      'Quote requests even where “Facebook doesn’t work”: for an industrial hall builder, one B2B campaign on Meta brought in €216K of revenue in one week.'),
  },
  {
    id: 'case-watch', type: 'case', parent: 'cases', res: 'o-watch', quote: 2, uses: ['svc-ads'], path: p('/esettanulmanyok/karora-webshop/', '/en/case-studies/watch-webshop/'),
    title: p('Karóra webshop: 23× ROAS a karácsonyi szezonban · SocialStream', 'Watch webshop: 23× ROAS over Christmas · SocialStream'),
    desc: p('Ünnepi kampány egy karóra webshopnak: 23× ROAS és több mint 8M Ft bevétel. Esettanulmány valódi számokkal.',
      'A holiday campaign for a watch webshop: 23× ROAS and over €21K in revenue. A case study with real numbers.'),
    crumb: p('Karóra webshop', 'Watch webshop'),
    h1k: p('Karóra webshop · Karácsony', 'Watch webshop · Christmas'),
    h1t: p('<em>23×</em> ROAS az ünnepi szezonban.', '<em>23×</em> ROAS in the holiday season.'),
    lead: p('Ünnepi kampány egy karóra webshopnak: 23× ROAS és több mint 8M Ft bevétel, egy ügyfélnél, aki korábban minden decemberben a hirdetési áraktól tartott.',
      'A holiday campaign for a watch webshop: 23× ROAS and over €21K in revenue, for a client who used to dread ad prices every December.'),
  },
  {
    id: 'case-webinar', type: 'case', parent: 'cases', res: 'o-webinar', quote: 3, uses: ['svc-ads'], path: p('/esettanulmanyok/egeszsegugyi-webinar/', '/en/case-studies/healthcare-webinar/'),
    title: p('Webinár-jelentkezők 105 Ft-ért: egészségügyi eset · SocialStream', 'Webinar registrants at €0.29 each: a healthcare case · SocialStream'),
    desc: p('Egy egészségügyi szolgáltató webinárjára körülbelül 5700 jelentkező érkezett 600K Ft-ból: 105 Ft egy jelentkező. Pár százra számítottak.',
      'About 5,700 people registered for a healthcare provider’s webinar from €1,650: €0.29 per registrant. They expected a few hundred.'),
    crumb: p('Egészségügyi webinár', 'Healthcare webinar'),
    h1k: p('Egészségügyi webinár', 'Healthcare webinar'),
    h1t: p('<em>105 Ft</em> egy jelentkező.', '<em>€0.29</em> per registrant.'),
    lead: p('Egy egészségügyi szolgáltató webinárjára körülbelül 5700 jelentkező érkezett 600K Ft-ból. Ők pár száz jelentkezőre számítottak.',
      'About 5,700 people registered for a healthcare provider’s webinar from €1,650. They had expected a few hundred.'),
  },
  // the named clients, from the founder's answers (2026-11-18): what we do for them, since their first post; their
  // numbers are organic. did: the work, as a list on the page
  {
    id: 'case-flyx', type: 'case', parent: 'cases', fig: NAMED[0], reels: ['r-flyx-1', 'r-flyx-2', 'r-flyx-3'], uses: ['svc-video', 'svc-social', 'svc-ads', 'svc-web', 'svc-auto'], path: p('/esettanulmanyok/flyx-tenerife/', '/en/case-studies/flyx-tenerife/'),
    title: p('FlyX Tenerife: reelek, oldalak, foglalási rendszer · SocialStream', 'FlyX Tenerife: reels, pages and a booking system · SocialStream'),
    desc: p('Az első posztjuk óta mi visszük a FlyX Tenerife online jelenlétét: reelek, promófilm, oldalak, hirdetések, foglalási rendszer és automatizáció.',
      'Since their first post we have run FlyX Tenerife’s whole online presence: reels, promo film, pages, ads, their booking system and automation.'),
    crumb: p('FlyX Tenerife', 'FlyX Tenerife'),
    h1k: NAMED[0].who, h1t: p('<em>69K</em> organikus megtekintés egy reelen.', '<em>69K</em> organic views on one reel.'),
    lead: p('A FlyX Tenerife élményközpontnak az első posztjuk óta mi forgatjuk a reeleket és mi készítettük a promófilmet, és mi visszük az oldalaikat és a hirdetéseiket. A reeljeik organikusan nőnek: ez az egy 69K megtekintést ért el, több videójuk ennél jóval többet.',
      'For the FlyX Tenerife experience centre we have shot the reels and made the promo film since their first post, and we run their pages and ads. Their reels grow organically: this one reached 69K views, and several of their videos reached far more.'),
    did: [p('Reelek: forgatás és vágás', 'Reels: shooting and editing'), p('A promófilmjük', 'Their promo film'), p('Az oldalaik vezetése', 'Running their pages'), p('Hirdetések', 'Ads'), p('A foglalási rendszerük, mi programoztuk', 'Their booking system, programmed by us'), p('Véleménykezelés', 'Reputation management'), p('Pénzügyi és adminisztratív automatizáció', 'Finance and admin automation'), p('Influenszer-együttműködések', 'Influencer work')],
  },
  {
    id: 'case-enzo', type: 'case', parent: 'cases', fig: NAMED[1], reels: ['r-enzo-1', 'r-enzo-2'], uses: ['svc-video', 'svc-social', 'svc-strat', 'svc-ads'], path: p('/esettanulmanyok/prof-enzo/', '/en/case-studies/prof-enzo/'),
    title: p('Prof Enzo: 9,8M+ organikus megtekintés a Facebookon · SocialStream', 'Prof Enzo: 9.8M+ organic views on Facebook · SocialStream'),
    desc: p('Prof Enzo animált MI-orvos, aki az egészséges életről beszél. Az első posztja óta mi készítjük a videóit és visszük az oldalát: 9,8M+ organikus megtekintés.',
      'Prof Enzo, an animated AI doctor, talks about healthy living. Since his first post we have made his videos and run his page: 9.8M+ organic views.'),
    crumb: p('Prof Enzo', 'Prof Enzo'),
    h1k: NAMED[1].who, h1t: p('<em>9,8M+</em> organikus megtekintés.', '<em>9.8M+</em> organic views.'),
    lead: p('Prof Enzo animált MI-orvos karakter: az egészséges életmódról, étkezésről, szokásokról és a jóllétről beszél, és doTERRA-termékeket ajánl. Az első posztja óta mi készítjük a videóit, mi visszük a Facebook-oldalát és mi tervezzük a stratégiáját; az oldal organikusan nőtt 9,8M+ megtekintésre és 33K követőre.',
      'Prof Enzo is an animated AI doctor character who talks about healthy living, healthy eating, good habits and well-being, and recommends doTERRA products. Since his first post we have made his videos, run his Facebook page and planned its strategy; the page grew organically to 9.8M+ views and 33K followers.'),
    did: [p('A videók, az ötlettől a vágásig', 'The videos, from idea to edit'), p('A Facebook-oldal vezetése', 'Running the Facebook page'), p('Stratégia: mit posztol az oldal és miért', 'Strategy: what the page posts and why'), p('Hirdetések, amik érdeklődőket hoznak, nem megtekintést', 'Ads that bring in leads, not views')],
  },
  {
    id: 'about', type: 'about', path: p('/rolunk/', '/en/about/'),
    title: p('Rólunk: interest media ügynökség 2022 óta · SocialStream', 'About us: an interest media agency since 2022 · SocialStream'),
    desc: p('2022 óta gyártjuk a videót, futtatjuk a hirdetést és mérjük, mit hozott. Négyen dolgozunk Tenerifén és Budapesten, havonta legfeljebb két új partnerrel.',
      'Since 2022 we have made the video, run the ads and measured what they bring in. A team of four in Tenerife and Budapest, with at most two new partners a month.'),
    crumb: p('Rólunk', 'About us'), nav: p('Rólunk', 'About us'),
    h1k: p('Rólunk', 'About us'), h1t: p('Interest media ügynökség, <em>2022 óta</em>.', 'An interest media agency <em>since 2022</em>.'),
    // Tenerife and Budapest stay off the first screen, as on the home page (the founder, 2026-11-16): they sit under the
    // team's heading lower down (teamWhere)
    lead: p('Mi gyártjuk a videót, mi futtatjuk a hirdetést, és mi mérjük, mit hozott. Olivér 2022-ben alapította a SocialStreamet; ma négyen vagyunk, és havonta legfeljebb két új partnert vállalunk.',
      'We make the video, we run the ads, and we measure what they bring in. Olivér founded SocialStream in 2022; today there are four of us, and we take on at most two new partners a month.'),
    teamWhere: p('Tenerifén és Budapesten dolgozunk.', 'We work from Tenerife and Budapest.'),
    // the one set of facts (the doc's AEO point 3), as figures; 300M+ Ft is €820K+ on the English page (content.mjs)
    facts: [
      { n: '2022', l: p('óta dolgozunk', 'the year we started') },
      { n: p('300M+ Ft', '€820K+'), l: p('kezelt hirdetési büdzsé', 'ad budget managed') },
      { n: '4', l: p('ember a csapatban', 'people on the team') },
      { n: '2', l: p('új partner havonta, legfeljebb', 'new partners a month, at most') },
    ],
    name: { eyebrow: p('A nevünk', 'Our name') },
  },
  {
    id: 'audit', type: 'audit', path: p('/ingyenes-audit/', '/en/free-audit/'),
    title: p('Ingyenes 30 perces marketing audit · SocialStream', 'Free 30-minute marketing audit · SocialStream'),
    desc: p('Ingyenes, 30 perces átvilágítás: átnézzük a hirdetéseidet és a kampányaidat, a landing oldaladat és az ajánlatodat, és őszintén megmondjuk, hol folyik el a pénz.',
      'A free 30-minute review: we go through your ads and campaigns, your landing page and your offer, and tell you honestly where the money leaks.'),
    crumb: p('Ingyenes audit', 'Free audit'),
    h1k: p('Ingyenes audit', 'Free audit'), h1t: C.offer.h2,
    lead: p(C.steps.items[0].hu[1], C.steps.items[0].en[1]),
    faq: [homeQ(0), homeQ(1), homeQ(2), homeQ(3), homeQ(4)],
  },
  {
    id: 'faq', type: 'faq', path: p('/gyik/', '/en/faq/'),
    title: p('Gyakori kérdések · SocialStream', 'Frequently asked questions · SocialStream'),
    desc: p('Mennyibe kerül az audit, mit kapsz a végén, kikkel dolgozunk, hol hirdetünk és hol vagyunk: válaszok a leggyakoribb kérdésekre.',
      'What the audit costs, what you get from it, who we work with, where we advertise and where we are: answers to the questions people ask most.'),
    crumb: p('Gyakori kérdések', 'FAQ'), nav: p('Kérdések', 'Questions'),
    h1k: p('Gyakori kérdések', 'Frequently asked questions'), h1t: C.faq.h2,
    lead: p('Ha nem találod itt a válaszod, írj nekünk: <a href="mailto:hello@socialstream.hu">hello@socialstream.hu</a>.', 'If your question isn’t here, write to us: <a href="mailto:hello@socialstream.hu">hello@socialstream.hu</a>.'),
    // the groups; a question from the home page keeps its words, except where it needs its subject to stand alone here
    groups: [
      { id: 'audit-kerdesek', h: p('Az ingyenes audit', 'The free audit'), items: [homeQ(0),
        { q: p('Mennyi ideig tart az audit?', 'How long does the audit take?'), a: homeQ(1).a },
        { q: p('Mi történik, miután elküldöm a jelentkezést?', 'What happens after I send my application?'), a: homeQ(2).a },
        { q: p('Mit kapok az audit végén?', 'What do I get from the audit?'), a: homeQ(3).a }] },
      { id: 'munka', h: p('A munka', 'The work'), items: [
        { q: p('Milyen szolgáltatásaitok vannak?', 'What services do you offer?'), a: p('Hat: videó tartalomgyártás, social média jelenlét, fizetett hirdetés, weboldal és landing, automatizáció és e-mail, növekedési stratégia. Mindet egy csapattól.', 'Six: video production, social media presence, paid advertising, websites and landing pages, automation and email, and growth strategy. All from one team.'), links: true },
        homeQ(5), homeQ(6),
        q('Landing oldalt vagy teljes weboldalt készítetek?', 'Do you build landing pages or whole websites?', 'Mindkettőt: gyors, mobilra tervezett landing oldalakat és weboldalakat, amik konvertálnak.', 'Both: fast, mobile-first landing pages and websites that convert.'),
        q('Mit automatizáltok?', 'What do you automate?', 'A lead-követést, az e-mail szekvenciákat és a tölcséreket: egyszer beállítjuk, utána dolgozik helyetted.', 'Lead follow-up, email sequences and funnels: set up once, then it works for you.'),
        q('Mi jön az audit után?', 'What comes after the audit?', 'A stratégia: kampánystratégia, funnel és pozicionálás, vagyis kinek, mit és melyik platformon mutatunk. Utána jön a gyártás, végül a hirdetés és a skálázás.', 'The strategy: campaign strategy, funnel and positioning, that is, what we show, to whom, and where. Then production, and finally the ads and scaling.')] },
      { id: 'eredmenyek-kerdesek', h: p('Eredmények', 'Results'), items: [
        q('Milyen eredményeket hoztatok?', 'What results have you brought?', 'Néhány valódi szám: 81× ROAS egy ajtó webshopnál (Google Performance Max), 79M Ft bevétel egy hét alatt egy csarnoképítő ügyfél B2B kampányából (Meta), 23× ROAS és több mint 8M Ft bevétel egy karóra webshop karácsonyi kampányában, és 105 Ft egy jelentkező egy egészségügyi webinárnál, körülbelül 5700 jelentkezővel.',
          'A few real numbers: 81× ROAS for a door webshop (Google Performance Max), €216K of revenue in one week from an industrial hall builder’s B2B campaign (Meta), 23× ROAS and over €21K of revenue in a watch webshop’s Christmas campaign, and €0.29 per registrant for a healthcare webinar, with about 5,700 registrants.'),
        q('Működik a Facebook-hirdetés B2B cégeknek?', 'Do Facebook ads work for B2B companies?', 'Egy csarnoképítő ügyfelünknél egy B2B kampány egy hét alatt 79M Ft bevételt hozott. Ők is azt hitték, hogy a Facebook a fiataloknak és a webshopoknak való.', 'For an industrial hall builder, one B2B campaign brought in €216K of revenue in one week. They, too, thought Facebook was for young people and webshops.'),
        q('Mennyi hirdetési pénzt kezeltetek eddig?', 'How much ad budget have you managed?', '2022 óta több mint 300M Ft-ot. Minden forintnál ugyanazt kérdezzük: mit hoz vissza?', 'More than €820K since 2022. With every euro we ask the same question: what does it bring back?')] },
      { id: 'rolunk-kerdesek', h: p('Rólunk', 'About us'), items: [homeQ(4),
        q('Kinek nem való a SocialStream?', 'Who is SocialStream not for?', 'Annak, aki egy éjszaka alatti sikert vagy olcsó félmegoldást keres.', 'Anyone after overnight success or a cheap half-measure.'),
        q('Hány új partnert vállaltok?', 'How many new partners do you take on?', C.offer.scarce.hu, C.offer.scarce.en),
        q('Kik dolgoznak a fiókomon?', 'Who works on my account?', 'Négyen: Olivér (alapító, kampánystratéga), David (kreatív és tartalomgyártás), Bálint (produkció és vágás) és David (fejlesztő).', 'Four of us: Olivér (founder, campaign strategist), David (creative and content production), Bálint (production and editing) and David (developer).'),
        homeQ(7),
        q('Mióta működtök?', 'How long have you been around?', '2022 óta: Olivér ekkor alapította a SocialStreamet.', 'Since 2022, when Olivér founded SocialStream.')] },
    ],
  },
  {
    id: 'contact', type: 'contact', path: p('/kapcsolat/', '/en/contact/'),
    title: p('Kapcsolat · SocialStream', 'Contact · SocialStream'),
    desc: p('Írj nekünk a hello@socialstream.hu címre, vagy jelentkezz az ingyenes 30 perces auditra. Tenerifén és Budapesten dolgozunk.',
      'Write to hello@socialstream.hu or apply for the free 30-minute audit. We work from Tenerife and Budapest.'),
    crumb: p('Kapcsolat', 'Contact'), nav: p('Kapcsolat', 'Contact'),
    h1k: p('Kapcsolat', 'Contact'), h1t: p('Írj nekünk, <em>válaszolunk</em>.', 'Write to us. <em>We’ll reply.</em>'),
    lead: p('A legegyszerűbb, ha jelentkezel az ingyenes 30 perces auditra: válaszolunk az e-mailedre, és egyeztetünk egy időpontot. Ha csak kérdeznél, írj a hello@socialstream.hu címre.',
      'The simplest way is to apply for the free 30-minute audit: we’ll reply to your email and set a time. If you only have a question, write to hello@socialstream.hu.'),
    cards: {
      mail: p('E-mail', 'Email'),
      where: p('Hol dolgozunk', 'Where we work'), places: p('Tenerife és Budapest', 'Tenerife and Budapest'),
      audit: p('Ingyenes audit', 'Free audit'),
    },
  },
];

// a service page's service (content.mjs) and its page
for (const pg of ALL) if (pg.svc) { pg.s = svc(pg.svc); pg.crumb = p(...pg.s.k); pg.h1t = p(...pg.s.t); }
// the pages that are built: drafts only with SS_DRAFTS=1 (tools/site.mjs then writes dist/site-drafts)
export const PAGES = ALL.filter(pg => DRAFTS || !pg.draft);
export const IS_DRAFTS = DRAFTS;
export const byId = id => PAGES.find(pg => pg.id === id);
export const url = (pg, l) => ORIGIN + pg.path[l];
// the header's links: the services, the results on the home page, About us, the questions, contact
export const NAV = [byId('services'), { id: 'results', path: p('/#eredmenyek', '/en/#eredmenyek'), nav: p('Eredmények', 'Results') }, byId('about'), byId('faq'), byId('contact')];
