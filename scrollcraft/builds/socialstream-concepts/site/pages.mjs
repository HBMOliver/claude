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
// founder, "i have everyones approval"). FlyX's and Prof Enzo's cases and their numbers on the social media page were
// drafts until v22 (2026-11-27, the founder: "all of our results"). A page with draft: true is built only with
// SS_DRAFTS=1 into dist/site-drafts for review, never into dist/site; none has it now.
// No em dashes anywhere in the copy (tools/site.mjs stops on one).
import { C } from '../content.mjs';
import { ON as ES_ON, SLUGS } from './es.mjs';

const DRAFTS = !!process.env.SS_DRAFTS;
// The site's two domains (2026-11-26, the founder: "Spanish site on .es"): Hungarian and English on socialstream.hu,
// Spanish at the root of socialstream.es. Each domain is its own folder and ZIP (tools/site.mjs); a page's address in
// a language is that language's origin plus its path (url below), and links across domains are full addresses.
export const ORIGIN = 'https://socialstream.hu';
export const ORIGINS = { hu: ORIGIN, en: ORIGIN, es: 'https://socialstream.es' };
export const DOMAINS = [
  { origin: ORIGIN, langs: ['hu', 'en'], out: 'dist/site' },
  { origin: ORIGINS.es, langs: ['es'], out: 'dist/site-es' },
];
// a link from a page in language `from` to a path of language `l`: the path itself on the same domain, else the full address
export const hrefTo = (path, l, from) => (ORIGINS[l] === ORIGINS[from] ? path : ORIGINS[l] + path);
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

// Clients the founder named for the field pages and the website page (2026-11-27): the names as the founder wrote them,
// what we did, and a figure only where the founder gave one plainly; without a figure the name leads the card.
// Euros at the ECB rate of 13 November 2026 (365.6 Ft), costs rounded up: 800 Ft = €2.19, 2500 Ft = €6.84, 26 997 Ft = €73.85,
// 12 028 Ft = €32.90. Later figures from the founder's case-study PDF (Esettanulmányok, vélemények.pdf).
// obj: the card's 3D object (assets/<obj>-mix.webp), one per client, the same wherever the client appears (2026-11-28:
// made in the founder's Figma with GPT Image 2.5 in the 2026-11-11 objects' words, then tools/objects-*.py; no logos).
export const CLIENTS = {
  hoof: { obj: 'c-hoof', n: 28, unit: '× ROAS', name: 'Hoofbútor', kind: p('Bútor webshop', 'Furniture webshop'),
    d: p('1 forint hirdetésből 28 forint bevétel, az évek alatt összesen. Évek óta mi futtatjuk a hirdetéseiket.', '€28 of revenue for every €1 of ads, over the years in total. We have run their ads for years.') },
  zsm: { obj: 'c-zsm', n: 800, unit: 'Ft', en: { pre: '€', n: 2.19, unit: '' }, name: 'ZsM Sportruházat', kind: p('Webshop', 'Webshop'),
    d: p('Ennyibe került egy okosóra-eladás az első karácsonyi kampányukban. Hosszabb ideig dolgoztunk együtt.', 'The cost of one smartwatch sale in their first Christmas campaign. We worked together for a long time.') },
  // 15x: the PDF's "15x ROAS kozmetikai webshopnál" (Google, on average), which the founder says is Karaja; the sales and
  // their cost the founder's own reading of the account (the PDF's Facebook ad sets: 1968 and 2680 Ft a purchase)
  karajaShop: { obj: 'c-karaja', n: 15, unit: '× ROAS', name: 'Karaja Makeup Hungary', kind: p('Kozmetikai webshop', 'Cosmetics webshop'),
    d: p('Átlagos megtérülés a Google-kampányaikban. A Facebook-hirdetéseinkből több mint 200 eladás jött, egyenként nagyjából 2500 Ft-ért.', 'Average return on their Google campaigns. Our Facebook ads brought in over 200 sales, at about €6.84 each.') },
  realbeauty: { obj: 'c-realbeauty', n: 2, unit: '×', name: 'Realbeauty.hu', kind: p('Kozmetikai webshop', 'Cosmetics webshop'),
    d: p('Az első hónapban megdupláztuk az addigi legjobb havi bevételüket. 2023 júliusában kezdtünk.', 'In the first month we doubled their best month’s revenue so far. We started in July 2023.') },
  // a webshop the founder could not name (the PDF's "9x alacsonyabb költség eredményenként"): it stays unnamed
  traffic: { obj: 'c-traffic', n: 9, unit: '×', name: p('Webshop', 'Webshop'), kind: p('Forgalmi kampány', 'Traffic campaign'),
    d: p('Ennyivel olcsóbb lett egy kattintás: a korábbi hirdetéseik 0,18 €-ba kerültek kattintásonként, a mieink 0,02 €-ba, egy érkezésioldal-megtekintés pedig 0,03 €-ba.', 'That much cheaper per click: their earlier ads cost €0.18 a click, ours €0.02, and a landing page view €0.03.') },
  tony: { obj: 'c-tony', n: 200, unit: '+', name: 'Tony Web Studio', kind: p('Webstúdió', 'Web studio'),
    d: p('Lead a hirdetéseinkből, hónapokon át.', 'Leads from our ads, over several months.') },
  // Olivér's own result as a Meta Marketing Pro (October 2022 to February 2023), before the agency: the PDF's "2x lead
  // növekedés" screenshots, counted over the whole account as the founder asked (2026-11-27): October 2022, 84 leads
  // (79 + 3 + 1 + 1) from 2 623 941 Ft in all; 29 January to 27 February 2023, 193 leads (184 + 9) from 2 622 409 Ft:
  // 31 237 Ft then 13 588 Ft a lead (€85.45, €37.17), 2.3x. Big George Properties is not named until they agree to it.
  // the founder asked for it a little more dramatic (2026-11-27): +130% leads (193 against 84), not a forint more spent
  // (2 622 409 Ft against 2 623 941), and October's dearest campaign (181 627 Ft for one website lead, €496.80) as the
  // before; the averages stay in the sentence. Not used: "181 627 Ft to 12 028 Ft" as a headline (worst set against best).
  bgp: { obj: 'c-bgp', n: '+130', unit: '%', en: { pre: '+', n: 130, unit: '%' }, name: p('Luxusingatlan-cég', 'Luxury real estate company'), kind: p('Olivér, Meta Marketing Pro-ként', 'Olivér, as a Meta Marketing Pro'),
    d: p('Egy forinttal sem több pénzből: havi 84 helyett 193 lead. Októberben még volt kampány, ahol egyetlen lead 181 627 Ft-ba került; négy hónappal később egy lead átlagosan 13 588 Ft volt, a korábbi 31 237 Ft helyett. (A fiók összes kampánya, 2022. október – 2023. február.)', 'Not a cent more spent: 193 leads a month instead of 84. In October one campaign was still paying €496.80 for a single lead; four months later a lead cost €37.17 on average, down from €85.45. (Every campaign in the account, October 2022 to February 2023.)') },
  karajaEvents: { obj: 'c-karaja', name: 'Karaja Makeup Hungary', kind: p('Workshopok', 'Workshops'),
    d: p('Évekig mi hirdettük a workshop-bemutatóikat: több száz jelentkező az ország minden pontjáról.', 'For years we ran the ads for their workshop demos: several hundred sign-ups from all over the country.') },
  bridle: { obj: 'c-bridle', name: 'Bridle Up Hope', kind: p('Alapítvány', 'Foundation'),
    d: p('Mi indítottuk el a marketingjüket Magyarországon: fotózás és videó a nyílt napjaikon, közösségi média hirdetések, jelentkezési és adományozási platform, e-mail marketing és CRM.', 'We started their marketing in Hungary: photo and video at their open days, social media ads, sign-up and donation platforms, email marketing and a CRM.') },
  // the Church's official name in each language (the founder wrote "Az Utolsó Napi Szentek Jézus Krisztus Egyháza")
  church: { obj: 'c-church', n: 30, unit: '+', name: p('Jézus Krisztus Utolsó Napi Szentjeinek Egyháza', 'The Church of Jesus Christ of Latter-day Saints'), kind: p('Húsvéti kampány', 'Easter campaign'),
    d: p('Ország és nyelv egy húsvéti kampányban, Európa-szerte: hirdetések az Instagramon, a Facebookon és a YouTube-on, weboldallal. Közösségi média tanácsadást is adtunk nekik.', 'Countries and languages in one Easter campaign across Europe: ads on Instagram, Facebook and YouTube, with a website. We also gave them social media consulting.') },
  ritas: { obj: 'c-ritas', name: 'Rita’s Beauty Corner', kind: p('Szépségszalon', 'Beauty salon'), url: 'https://ritasbeautycorner.hu/',
    d: p('A weboldalukat és a teljes marketingjüket mi csináltuk.', 'We made their website and all of their marketing.') },
  lunelle: { obj: 'c-lunelle', name: 'Lunelle Aesthetics', kind: p('Esztétikai klinika, Budapest', 'Aesthetics clinic, Budapest'), url: 'https://lunelleclinic.hu/',
    d: p('Az eredeti weboldalukat mi készítettük. Azóta ők viszik, alig változtattak rajta.', 'We built their original website. They have run it themselves since, with only small changes.') },
  dorombolda: { obj: 'c-dorombolda', name: 'Dorombolda Cicahotel', kind: p('Macskahotel', 'Cat hotel'),
    d: p('Mi indítottuk az első hirdetéseiket, és ezekből jött össze a kezdőtőke a további fejlődésükhöz.', 'We started their first ads, and those brought in the starting capital for their next steps.') },
};

// The definition of interest media, the founder's choice (2026-11-26, "Feeds + what we make"): the explainer's answer
// and its structured data. The two halves after the colon are the home page's promise, word for word.
const DEF = p('Az interest media olyan marketing, ami azoknak a feedeknek szól, amelyek azt mutatják az embereknek, ami érdekli őket, nem csak azt, amit a követett fiókok posztolnak: videók, amiket végignéznek, és hirdetések, amik megtérülnek.',
  'Interest media is marketing for feeds that show people what interests them, not just what the accounts they follow post: videos people watch to the end, and ads that pay off.');
// a card of the home page's "who it is for" (content.mjs), by its picture: the line under its name
const whoCard = img => { const c = C.who.cards.find(x => x.img === img); return p(c.hu[1], c.en[1]); };

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
    clients: ['lunelle', 'ritas'], proof: { quotes: [5, 4] },
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
    title: p('onlineajtok.hu: 81× ROAS Google Performance Maxszel · SocialStream', 'onlineajtok.hu: 81× ROAS with Google Performance Max · SocialStream'),
    desc: p('Az onlineajtok.hu ajtó webshop Google Performance Max kampányában 1 forint hirdetésből 81 forint bevétel lett. Esettanulmány valódi számokkal.',
      'In the Google Performance Max campaign of onlineajtok.hu, a door webshop, every €1 of ads brought in €81 of revenue. A case study with real numbers.'),
    crumb: p('onlineajtok.hu', 'onlineajtok.hu'),
    h1k: p('onlineajtok.hu · Google Performance Max', 'onlineajtok.hu · Google Performance Max'),
    h1t: p('1 forint hirdetésből <em>81 forint</em> bevétel.', '<em>€81</em> of revenue for every €1 of ads.'),
    lead: p('Ezt az onlineajtok.hu ajtó webshop Google Performance Max kampányában értük el: 1 forint hirdetésből 81 forint bevétel lett, vagyis 81× ROAS. A kampányaik folyamatosan 50× és 80× közötti megtérülést hoztak.',
      'We reached it in the Google Performance Max campaign of onlineajtok.hu, a door webshop: every €1 of ads brought in €81 of revenue, that is 81× ROAS. Their campaigns kept bringing between 50× and 80× ROAS.'),
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
  // The interest media explainer and the fields we work in (the founder, 2026-11-26: "Explainer + industry pages", then
  // "all 8 above": the home page's four groups and two more, health and wellness, tourism and experiences). Drafts
  // first, live since v22 (2026-11-27). Their words say only what the site already says, and the approved
  // definition; their questions are the FAQ page's own (faqFrom: 'group:i' there, or 'page:i' a page's own list).
  {
    id: 'interest-media', type: 'explainer', path: p('/mi-az-interest-media/', '/en/what-is-interest-media/'),
    title: p('Mi az interest media? Meghatározás és példák · SocialStream', 'What is interest media? Definition and examples · SocialStream'),
    desc: p('Az interest media a feedekre épülő marketing: azt mutatják, ami érdekli az embereket. Videók, amiket végignéznek, és hirdetések, amik megtérülnek.',
      'Interest media is marketing for feeds that show people what interests them: videos people watch to the end, and ads that pay off. With real examples.'),
    crumb: p('Mi az interest media?', 'What is interest media?'),
    h1k: p('Interest media', 'Interest media'), h1t: p('Marketing a feedekre, amelyek azt mutatják, <em>ami érdekel</em>.', 'Marketing for feeds that show people <em>what interests them</em>.'),
    lead: DEF,
    faq: [q('Mi az interest media?', 'What is interest media?', DEF.hu, DEF.en)], faqFrom: ['munka:0', 'eredmenyek-kerdesek:0', 'rolunk-kerdesek:0'],
  },
  {
    id: 'audiences', type: 'audiences', path: p('/kikkel-dolgozunk/', '/en/who-we-work-with/'),
    title: p('Kikkel dolgozunk? Területek, valódi esetekkel · SocialStream', 'Who we work with: fields, with real cases · SocialStream'),
    desc: p('Webshopok, B2B cégek, webinárok és események, helyi szolgáltatók, egészség és turizmus: mit hozott a munkánk az egyes területeken, valódi esetekkel.',
      'Webshops, B2B companies, webinars and events, local services, health and tourism: what our work brought in each field, with real cases.'),
    crumb: p('Kikkel dolgozunk', 'Who we work with'),
    h1k: p('Kikkel dolgozunk', 'Who we work with'), h1t: C.who.h2, lead: C.who.lead,
  },
  {
    id: 'ind-shop', type: 'industry', parent: 'audiences', art: 'a-shop', card: whoCard('a-shop'),
    path: p('/kikkel-dolgozunk/webshopok/', '/en/who-we-work-with/webshops/'),
    title: p('Webshopok: vásárlások Google és Meta kampányokból · SocialStream', 'Webshops: sales from Google and Meta campaigns · SocialStream'),
    desc: p('Webshopoknak vásárlásokat hozunk Google és Meta kampányokból: 81× ROAS egy ajtó webshopnál, 23× ROAS egy karóra webshop karácsonyi szezonjában.',
      'We bring webshops sales from Google and Meta campaigns: 81× ROAS for a door webshop, 23× ROAS in a watch webshop’s Christmas season.'),
    crumb: p('Webshopok', 'Webshops'), h1k: p('Webshopok', 'Webshops'),
    h1t: p('Vásárlások <em>Google és Meta</em> kampányokból.', 'Sales from <em>Google and Meta</em> campaigns.'),
    lead: p('A legjobb e-commerce eredményünk 81× ROAS egy ajtó webshopnál. Egy karóra webshopnak a karácsonyi kampány 23× ROAS-t és több mint 8M Ft bevételt hozott.',
      'Our best e-commerce result is 81× ROAS for a door webshop. For a watch webshop, the Christmas campaign brought 23× ROAS and over €21K in revenue.'),
    pains: ['ads', 'web', 'video'], cases: ['case-door', 'case-watch'], clients: ['hoof', 'karajaShop', 'traffic', 'realbeauty', 'zsm'], quotes: [0, 2], uses: ['svc-ads', 'svc-web', 'svc-video'],
    faqFrom: ['svc-ads:3', 'munka:2', 'munka:3'],
  },
  {
    id: 'ind-b2b', type: 'industry', parent: 'audiences', art: 'a-b2b', card: whoCard('a-b2b'),
    path: p('/kikkel-dolgozunk/b2b-cegek/', '/en/who-we-work-with/b2b-companies/'),
    title: p('B2B cégek: ajánlatkérések Meta-kampányokból · SocialStream', 'B2B companies: quote requests from Meta campaigns · SocialStream'),
    desc: p('B2B cégeknek ajánlatkéréseket hozunk hirdetésekből ott is, ahol „a Facebook nem működik”: egy csarnoképítő ügyfelünknél egy hét alatt 79M Ft bevétel lett.',
      'We bring B2B companies quote requests from ads even where “Facebook doesn’t work”: for an industrial hall builder, €216K of revenue in one week.'),
    crumb: p('B2B cégek', 'B2B companies'), h1k: p('B2B cégek', 'B2B companies'),
    h1t: p('Ajánlatkérések ott is, ahol <em>„a Facebook nem működik”</em>.', 'Quote requests even where <em>“Facebook doesn’t work”</em>.'),
    lead: p('Egy csarnoképítő ügyfelünknek egy B2B kampány a Metán egy hét alatt 79M Ft bevételt hozott. Ők is azt hitték, a Facebook a fiataloknak és a webshopoknak való.',
      'For an industrial hall builder, one B2B campaign on Meta brought in €216K of revenue in one week. They too thought Facebook was for young people and webshops.'),
    pains: ['ads', 'auto', 'web'], cases: ['case-hall'], clients: ['tony', 'bgp'], quotes: [1], uses: ['svc-ads', 'svc-auto', 'svc-web'],
    faqFrom: ['eredmenyek-kerdesek:1', 'munka:4', 'munka:2'],
  },
  {
    id: 'ind-events', type: 'industry', parent: 'audiences', art: 'a-events', card: whoCard('a-events'),
    path: p('/kikkel-dolgozunk/webinarok-es-esemenyek/', '/en/who-we-work-with/webinars-and-events/'),
    title: p('Webinárok és események: 105 Ft egy jelentkező · SocialStream', 'Webinars and events: €0.29 per registrant · SocialStream'),
    desc: p('Webinárokra és eseményekre hozunk jelentkezőket alacsony költséggel: egy egészségügyi webinárra 600K Ft-ból körülbelül 5700 jelentkező érkezett.',
      'We bring sign-ups to webinars and events at a low cost: about 5,700 people registered for a healthcare webinar from €1,650.'),
    crumb: p('Webinárok és események', 'Webinars and events'), h1k: p('Webinárok és események', 'Webinars and events'),
    h1t: p('Jelentkezők <em>alacsony költséggel</em>.', 'Sign-ups at a <em>low cost</em>.'),
    lead: p('Egy egészségügyi webinárra körülbelül 5700 jelentkező érkezett 600K Ft-ból, egyenként 105 Ft-ért. A szervező pár száz jelentkezőre számított.',
      'About 5,700 people registered for a healthcare webinar from €1,650, at €0.29 each. The organiser expected a few hundred.'),
    pains: ['ads', 'auto', 'video'], cases: ['case-webinar'], clients: ['karajaEvents', 'bridle', 'church'], quotes: [3], reels: ['r-uty', 'r-lv-sunset', 'r-lv-yellow', 'r-lv-hoodie', 'r-lv-cap'],
    uses: ['svc-ads', 'svc-video', 'svc-auto'], faqFrom: ['munka:4', 'munka:1', 'eredmenyek-kerdesek:0'],
  },
  {
    id: 'ind-local', type: 'industry', parent: 'audiences', art: 'a-local', card: whoCard('a-local'),
    path: p('/kikkel-dolgozunk/helyi-szolgaltatok/', '/en/who-we-work-with/local-services/'),
    title: p('Helyi szolgáltatók: videó, social és hirdetés · SocialStream', 'Local services: video, social and ads from one team · SocialStream'),
    desc: p('Szépségszalontól a tenerifei élményprogramig: helyi szolgáltatóknak egy csapattól készítünk videót, visszük a social médiát és futtatjuk a hirdetéseket.',
      'From beauty salons to experiences on Tenerife: for local services, one team makes the video and runs the social media and the ads.'),
    crumb: p('Helyi szolgáltatók és élményprogramok', 'Local services and experiences'), h1k: p('Helyi szolgáltatók és élményprogramok', 'Local services and experiences'),
    h1t: p('Videó, social és hirdetés <em>egy csapattól</em>.', 'Video, social and ads <em>from one team</em>.'),
    lead: p('Szépségszalontól a tenerifei élményprogramig dolgozunk helyi szolgáltatókkal. A FlyX Tenerife élményközpont egyik reelje organikusan 69K megtekintést ért el.',
      'From beauty salons to experiences on Tenerife, we work with local services. One of the FlyX Tenerife experience centre’s reels reached 69K organic views.'),
    pains: ['social', 'video', 'ads'], cases: ['case-flyx'], clients: ['ritas', 'lunelle', 'dorombolda'], quotes: [4, 5], uses: ['svc-social', 'svc-video', 'svc-ads', 'svc-web'],
    faqFrom: ['svc-social:0', 'munka:3', 'rolunk-kerdesek:3'],
  },
  {
    id: 'ind-health', type: 'industry', parent: 'audiences', art: 'o-webinar',
    card: p('Videók és oldalak az egészségről: Prof Enzo oldala organikusan <b>9,8M+</b> megtekintést ért el a Facebookon.', 'Videos and pages about health: Prof Enzo’s page reached <b>9.8M+</b> organic views on Facebook.'),
    path: p('/kikkel-dolgozunk/egeszseg-es-wellness/', '/en/who-we-work-with/health-and-wellness/'),
    title: p('Egészség és wellness: videók, oldalak, hirdetések · SocialStream', 'Health and wellness: videos, pages and ads · SocialStream'),
    desc: p('Prof Enzo animált MI-orvos oldala organikusan 9,8M+ megtekintést ért el a Facebookon, egy egészségügyi webinárra 105 Ft-ért érkezett egy jelentkező.',
      'Prof Enzo, an animated AI doctor, reached 9.8M+ organic views on Facebook, and a healthcare webinar drew registrants at €0.29 each.'),
    crumb: p('Egészség és wellness', 'Health and wellness'), h1k: p('Egészség és wellness', 'Health and wellness'),
    h1t: p('<em>9,8M+</em> organikus megtekintés a Facebookon, egy MI-orvossal.', '<em>9.8M+</em> organic views on Facebook, with an AI doctor.'),
    lead: p('Prof Enzo animált MI-orvos az egészséges életről beszél; az első posztja óta mi készítjük a videóit és visszük az oldalát. Egy egészségügyi szolgáltató webinárjára 105 Ft-ért érkezett egy jelentkező.',
      'Prof Enzo, an animated AI doctor, talks about healthy living; we have made his videos and run his page since his first post. A healthcare provider’s webinar drew registrants at €0.29 each.'),
    pains: ['video', 'social', 'ads'], cases: ['case-enzo', 'case-webinar'], quotes: [3, 4, 5], reels: ['r-enzo-1', 'r-enzo-2'],
    uses: ['svc-video', 'svc-social', 'svc-ads', 'svc-strat'], faqFrom: ['munka:1', 'svc-social:0', 'eredmenyek-kerdesek:0'],
  },
  {
    id: 'ind-tourism', type: 'industry', parent: 'audiences', art: 'i-video',
    card: p('Reelek, oldalak, hirdetések és foglalási rendszer egy tenerifei élményközpontnak.', 'Reels, pages, ads and a booking system for an experience centre on Tenerife.'),
    path: p('/kikkel-dolgozunk/turizmus-es-elmenyek/', '/en/who-we-work-with/tourism-and-experiences/'),
    title: p('Turizmus és élmények: reelek, foglalási rendszer · SocialStream', 'Tourism and experiences: reels and a booking system · SocialStream'),
    desc: p('Egy tenerifei élményközpontnak az első posztjuk óta mi forgatjuk a reeleket, visszük az oldalakat és a hirdetéseket, és mi programoztuk a foglalási rendszert.',
      'For an experience centre on Tenerife we have shot the reels, run the pages and the ads, and programmed the booking system since their first post.'),
    crumb: p('Turizmus és élmények', 'Tourism and experiences'), h1k: p('Turizmus és élmények', 'Tourism and experiences'),
    h1t: p('Reelek, oldalak és <em>foglalási rendszer</em>.', 'Reels, pages and a <em>booking system</em>.'),
    lead: p('A FlyX Tenerife élményközpontnak az első posztjuk óta mi forgatjuk a reeleket, mi visszük az oldalaikat és a hirdetéseiket, és mi programoztuk a foglalási rendszerüket. Egyik reeljük organikusan 69K megtekintést ért el.',
      'For the FlyX Tenerife experience centre we have shot the reels, run their pages and ads, and programmed their booking system since their first post. One of their reels reached 69K organic views.'),
    pains: ['video', 'ads', 'auto'], cases: ['case-flyx'], reels: ['r-flyx-1', 'r-flyx-2', 'r-flyx-3'],
    uses: ['svc-video', 'svc-social', 'svc-ads', 'svc-web', 'svc-auto'], faqFrom: ['munka:1', 'munka:4', 'munka:2'],
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
// a page's questions taken from the FAQ page ('group:i') or another page's own list ('page:i'), as they stand there
const FAQ_PAGE = ALL.find(x => x.id === 'faq');
for (const pg of ALL) if (pg.faqFrom) pg.faq = [...(pg.faq || []), ...pg.faqFrom.map(ref => {
  const [a, i] = ref.split(':'), g = FAQ_PAGE.groups.find(x => x.id === a), it = g ? g.items[+i] : (ALL.find(x => x.id === a) || {}).faq?.[+i];
  if (!it) throw new Error(`site/pages.mjs: ${pg.id} asks for the question ${ref}, which is not there`);
  return it;
})];
// the Spanish pages (site/es.mjs): every page gets its Spanish address, or the build stops
if (ES_ON) for (const pg of ALL) { if (!SLUGS[pg.id]) throw new Error('site/es.mjs has no Spanish address for ' + pg.id); pg.path.es = SLUGS[pg.id]; }
// the pages that are built: drafts only with SS_DRAFTS=1 (tools/site.mjs then writes dist/site-drafts)
export const PAGES = ALL.filter(pg => DRAFTS || !pg.draft);
export const IS_DRAFTS = DRAFTS;
export const byId = id => PAGES.find(pg => pg.id === id);
export const url = (pg, l) => ORIGINS[l] + pg.path[l];
// the header's links: the services, the results on the home page, About us, the questions, contact
// the founder, 2026-11-27: the case studies and the new pages were hard to reach from the home page, so the header names
// "Kikkel dolgozunk" and its "Eredmények" goes to the case studies page (it was the home page's #eredmenyek)
export const NAV = [byId('services'), { ...byId('audiences'), nav: p('Kikkel dolgozunk', 'Who we work with') }, { ...byId('cases'), nav: p('Eredmények', 'Results') }, byId('about'), byId('faq'), byId('contact')];
