# SocialStream concepts: the copy

All the words live in `content.mjs`, Hungarian first and English after. Almost all of it is Daylight's
copy, already agreed. This file lists only what is new in the four concepts and still needs a yes.
There are no new numbers: the only figures on the pages are the real ones.

## NEW, to confirm: a business problem for each service

Each concept has a block before the services that names the problems businesses run into. Every problem
links to the service card that answers it. Each problem is the reverse of that service's own line, or one
of the three questions the old problem section asked. Those three questions are no longer on the pages.

Around the block:

- Eyebrow: Ismerős? / Sound familiar?
- Heading (Daylight's): Posztolsz. Hirdetsz. Mégsem jönnek a vevők? / You post. You advertise. And still no buyers?
- Text (Daylight's): A legtöbb vállalkozás ugyanabba a falba ütközik… / Most businesses hit the same wall…
- Label on each link: Ebben segítünk / How we help
- Closing line, in Pulse, Premiere and Studio (Daylight's): Nem a platformmal van a baj, hanem azzal, hogy *senki nem látja egyben*.

The six problems:

1. **Videó tartalomgyártás / Video production**
   - HU: A videóid mellett mindenki továbbgörget.
   - EN: People scroll straight past your videos.
2. **Social média jelenlét / Social media presence**
   - HU: Posztolsz, amikor jut rá idő, de alig reagál valaki.
   - EN: You post when you find the time, and hardly anyone reacts.
3. **Fizetett hirdetés / Paid advertising**
   - HU: A hirdetés hónapról hónapra drágul, és nem tudod, mit hoz vissza.
   - EN: Ads cost more every month, and you can’t tell what they bring back.
4. **Weboldal és landing / Website and landing pages**
   - HU: Kattintanak, aztán vásárlás nélkül eltűnnek az oldaladról.
   - EN: People click, then leave your site without buying.
5. **Automatizáció és e-mail / Automation and email**
   - HU: Az érdeklődők kihűlnek, mert senki nem keresi őket időben.
   - EN: Leads go cold because nobody gets back to them in time.
6. **Növekedési stratégia / Growth strategy**
   - HU: Nem tudod, melyik videó hozta a vásárlást, és hogy merre tovább.
   - EN: You can’t tell which video brought the sale, or what to do next.

## NEW arrangement, to confirm: elsewhere and with us

The problem's own sentences, set side by side. Pulse has it after the results, Aurora after the services, and
Aurora Mix after the results, as two cards laid over each other.

Heading: Máshol és *nálunk*. / Elsewhere and *with us*.

| Máshol / Elsewhere | A SocialStreamnél / At SocialStream |
|---|---|
| A videót egy ember készíti. / One person makes the video. | Mi gyártjuk a videót. / We make the video. |
| A hirdetést egy másik futtatja. / Another runs the ads. | Mi futtatjuk a hirdetést. / We run the ads. |
| Az oldalt egy harmadik rakta össze. / A third built the website. | Mi építjük az oldalt, ami befejezi, amit a videó elkezdett. / We build the page that finishes what the video started. |
| Senki nem felel azért, hogy legyen vásárlás. / Nobody answers for whether anything sells. | És mi mérjük, mit hozott. / And we measure what it brought in. |

## NEW, to confirm: labels on Aurora Mix only

- On the film's card, as a story's caption: Márkafilm / Brand film
- The two arrows beside the reviews (read out by screen readers, not shown): Előző vélemény / Previous review,
  Következő vélemény / Next review

## NEW, live, for the founder to read: the Spanish pages (2026-11-18)

On "Yes, build Spanish", every page also exists in Spanish under `/es/`. The Spanish is in `site/es-words.mjs`, one
[English, Spanish] pair per text (389 of them), written for Spain: "tú" to the reader, "vosotros" in the questions a
reader asks the team, euros the Spanish way (216K €, 0,29 €, 1.650 €), the same numbers and nothing new. The claim:
"Las ~~redes sociales~~ han muerto. El *interés* ha ocupado su lugar." Words kept as they are: interest media,
landing page(s), leads, copywriting, Reels, Stories, Feed, ROAS, B2B and every name. Hooks are "ganchos", the funnel
"embudo", a partner a "cliente" ("dos nuevos clientes al mes"). The buttons the scripts write are in ss.js, kit.js
and site.js ("Activar sonido" / "Silenciar", "Reproducir" / "Pausa", the form's topics and messages). The film stays
in English on the Spanish pages. Change a line in `site/es-words.mjs` and rebuild.

## NEW, to confirm: the site's pages (2026-11-16)

socialstream.hu grows from one page into 24: the home page and eleven more, each in Hungarian and in English
(`site/pages.mjs` holds every new word; the plan is the Claude Docs doc "SocialStream SEO, AEO and subpage plan").
The new sentences only restate what the site already says: the same six services, the four results, the steps, the
team, the reviews (word for word), "2022 óta", "Tenerife és Budapest", "havonta legfeljebb két új partner". English
pages show the English page's euros (content.mjs), never a new conversion.

Every page has its own title and description, a heading (what the page is, then a line), a two-sentence answer, and
ends with the audit form. Titles and descriptions:

| Page | Title (HU / EN) |
|---|---|
| Home | unchanged: SocialStream · Interest media ügynökség / SocialStream · Interest media agency |
| Szolgáltatások / Services | Szolgáltatások: videó, social media és hirdetés / Services: video, social media and ads |
| Videó / Video | Hirdetési videó és reels készítés / Video production for ads and reels |
| Social | Social media kezelés és tartalomgyártás / Social media management and content |
| Hirdetés / Ads | Facebook, TikTok és Google hirdetéskezelés / Meta, TikTok and Google ads management |
| Weboldal / Web | Landing oldal és weboldal készítés / Landing pages and websites that convert |
| Automatizáció / Automation | E-mail marketing és automatizáció / Email marketing and automation |
| Stratégia / Strategy | Marketing stratégia és funnel audit / Marketing strategy and funnel audit |
| Rólunk / About us | Rólunk: interest media ügynökség 2022 óta / About us: an interest media agency since 2022 |
| Ingyenes audit / Free audit | Ingyenes 30 perces marketing audit / Free 30-minute marketing audit |
| GYIK / FAQ | Gyakori kérdések / Frequently asked questions |
| Kapcsolat / Contact | Kapcsolat / Contact |

Each ends in " · SocialStream". The descriptions are in `site/pages.mjs`.

New on every page:

- Menu (header): Szolgáltatások, Eredmények, Rólunk, Kérdések, Kapcsolat / Services, Results, About us, Questions,
  Contact. On tablets and phones a "Menü" / "Menu" button opens them. The HU / EN switch is a link to the other
  language's page.
- Footer: two columns of links (Szolgáltatások: Minden szolgáltatás and the six; SocialStream: Rólunk, Ingyenes
  audit, Gyakori kérdések, Kapcsolat), and the line "Interest media ügynökség · 2022 óta · Tenerife és Budapest"
  (before: without "2022 óta").
- Breadcrumb (subpages): Főoldal / Szolgáltatások / … (read out as "Morzsamenü" / "Breadcrumb").

New sentences worth a look (all in `site/pages.mjs`):

- The services page: "Hat szolgáltatás, *egy csapattól*." / "Six services, *one team*."
- Each service page's heading line is the service's own line (content.mjs); above it, the search words: "Hirdetési
  videó és reels készítés", "Social media kezelés", "Facebook, TikTok és Google hirdetéskezelés", "Landing oldal és
  weboldal készítés", "E-mail marketing és automatizáció", "Marketing stratégia és funnel audit".
- "Mit kapsz?" / "What you get": a list per service, from the service's own words, the steps' chips and the tags.
- The video page: "Akik csinálják: David (hookok, forgatás, kreatív irány) és Bálint (forgatás, vágás, hang és fotó)."
  and under its reels "Az Up To Youth az alapítónk saját szervezete." / "Up To Youth is our founder's own organisation."
- About us: "Interest media ügynökség, *2022 óta*.", the facts as cards (2022 óta dolgozunk · 300M+ Ft kezelt
  hirdetési büdzsé · 4 ember a csapatban · 2 új partner havonta, legfeljebb), "A nevünk" over the claim and the
  name's line (content.mjs). The first paragraph ends "ma négyen vagyunk, és havonta legfeljebb két új partnert
  vállalunk." / "today there are four of us, and we take on at most two new partners a month."; the places sit under
  the team's heading: "Tenerifén és Budapesten dolgozunk." / "We work from Tenerife and Budapest." (the founder,
  2026-11-16: off the first screen, as on the home page).
- Contact: "Írj nekünk, *válaszolunk*." / "Write to us. *We'll reply.*"
- Questions: the home page's eight (two reworded to stand alone: "Mennyi ideig tart az audit?", "Mi történik, miután
  elküldöm a jelentkezést?", "Mit kapok az audit végén?") and eleven new ones answered from the site's facts (the six
  services, B2B on Facebook, the results, the budget managed, landing page or website, what we automate, what comes
  after the audit, who it is not for, how many new partners, who works on an account, since when). A few of them
  also sit on the service pages.

Case studies (2026-11-16, the founder: "Case studies first"; new copy, waits for the founder's yes). Each says only
what the site already says about its result (content.mjs: results, voices, who) and leaves out what is not there yet:
the period, the budget, what was made and changed.

| Page | Address (HU · EN) | Title (HU / EN) |
|---|---|---|
| Esettanulmányok / Case studies | /esettanulmanyok/ · /en/case-studies/ | Esettanulmányok: valódi ügyfelek, valódi számok / Case studies: real clients, real numbers |
| Ajtó webshop / Door webshop | …/ajto-webshop/ · …/door-webshop/ | Ajtó webshop: 81× ROAS Google Performance Maxszel / Door webshop: 81× ROAS with Google Performance Max |
| Csarnoképítő / Hall builder | …/b2b-csarnokepito/ · …/industrial-hall-builder/ | B2B Facebook-hirdetés: 79M Ft egy hét alatt / B2B Facebook ads: €216K in one week |
| Karóra webshop / Watch webshop | …/karora-webshop/ · …/watch-webshop/ | Karóra webshop: 23× ROAS a karácsonyi szezonban / Watch webshop: 23× ROAS over Christmas |
| Egészségügyi webinár / Healthcare webinar | …/egeszsegugyi-webinar/ · …/healthcare-webinar/ | Webinár-jelentkezők 105 Ft-ért: egészségügyi eset / Webinar registrants at €0.29 each: a healthcare case |

- The hub: "Esettanulmányok: Számok, amiket az ügyfeleinknek hoztunk." (the home page's heading), "Valódi ügyfelek,
  valódi számok: minden esetnél ott a platform, és ahol van, az ügyfél saját szava.", "Válassz egy esetet." / "Pick a
  case.", then the three clients' words from the home page.
- A case: its result as the heading (e.g. "*79M Ft* bevétel egy hét alatt."), a sentence from the site's own words
  (the B2B card, the FAQ's "Ezt egy ajtó webshop Google Performance Max kampányában értük el", the watch webshop's
  and the webinar's quotes retold), the stat card, the client's words where the site has them (none for the door
  webshop: Péter's Hoofbútor quote is not tied to it), "Amivel elértük." / "What it took." (Fizetett hirdetés), and
  "További esetek." / "More cases.".
- Every footer adds "Esettanulmányok" / "Case studies" to the SocialStream column. The header's "Eredmények" still
  goes to the home page's results (the founder's call).
- Drafts, built only with SS_DRAFTS=1 (dist/site-drafts), never uploaded: FlyX Tenerife ("*69K* megtekintés egy
  reelen.", its most-played Facebook reel) and Prof Enzo ("*9,8M+* megtekintés.", every view of the Facebook page
  since it began, with 33K followers), and the social media page's "Ügyfeleink fiókjai, számokban." with both. The
  clients agreed to be named; what SocialStream did for each, and since when, waits for the founder.

Left out until the founder sends them: pricing, the legal notice and privacy policy, a phone number or address,
profile links, proof for automation, the named clients' numbers outside the drafts (Prof Enzo's 9.8M+ views, FlyX's
69K on one reel: the film shows them; the clients agreed, but our part in them is not on the site yet), "Ezt az oldalt is mi
építettük." on the web page (the doc suggests it, the site does not say it), and the doc's title, meta and H1-line
drafts for the home page. Also asked: the home page's reels show Up To Youth's clips without saying it is the
founder's own organisation (the video page says so); the home page stays as it is until the founder decides.
