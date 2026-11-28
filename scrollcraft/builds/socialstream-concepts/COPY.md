# SocialStream concepts: the copy

All the words live in `content.mjs`, Hungarian first and English after. Almost all of it is Daylight's
copy, already agreed. This file lists only what is new in the four concepts and still needs a yes.
There are no new numbers: the only figures on the pages are the real ones.

## LIVE since v22: the interest media page and the fields we work in (2026-11-27)

On "Explainer + industry pages" and "all 8 above" (2026-11-26), eight new pages, each in Hungarian, English and
Spanish. Built first as drafts (`SS_DRAFTS=1`), they are live since v22 (.hu) and v2 (.es), 2026-11-27 22:33 UTC, on
the founder's "all of our results". Every sentence restates what the site already says, plus the definition the
founder chose ("Feeds + what we make"); the questions are the FAQ page's own, word for word, and the reviews are the
home page's.

The definition (the explainer's first screen, its first question and its structured data):
"Az interest media olyan marketing, ami azoknak a feedeknek szól, amelyek azt mutatják az embereknek, ami érdekli
őket, nem csak azt, amit a követett fiókok posztolnak: videók, amiket végignéznek, és hirdetések, amik megtérülnek." /
"Interest media is marketing for feeds that show people what interests them, not just what the accounts they follow
post: videos people watch to the end, and ads that pay off."

| Page | Address (HU · EN · ES on socialstream.es) | Title (HU / EN) |
|---|---|---|
| Interest media | /mi-az-interest-media/ · /en/what-is-interest-media/ · /que-es-interest-media/ | Mi az interest media? Meghatározás és példák / What is interest media? Definition and examples |
| Kikkel dolgozunk / Who we work with | /kikkel-dolgozunk/ · /en/who-we-work-with/ · /con-quien-trabajamos/ | Kikkel dolgozunk? Területek, valódi esetekkel / Who we work with: fields, with real cases |
| Webshopok / Webshops | …/webshopok/ · …/webshops/ · …/tiendas-online/ | Webshopok: vásárlások Google és Meta kampányokból / Webshops: sales from Google and Meta campaigns |
| B2B cégek / B2B companies | …/b2b-cegek/ · …/b2b-companies/ · …/empresas-b2b/ | B2B cégek: ajánlatkérések Meta-kampányokból / B2B companies: quote requests from Meta campaigns |
| Webinárok és események / Webinars and events | …/webinarok-es-esemenyek/ · …/webinars-and-events/ · …/webinars-y-eventos/ | Webinárok és események: 105 Ft egy jelentkező / Webinars and events: €0.29 per registrant |
| Helyi szolgáltatók / Local services | …/helyi-szolgaltatok/ · …/local-services/ · …/servicios-locales/ | Helyi szolgáltatók: videó, social és hirdetés / Local services: video, social and ads from one team |
| Egészség és wellness / Health and wellness | …/egeszseg-es-wellness/ · …/health-and-wellness/ · …/salud-y-bienestar/ | Egészség és wellness: videók, oldalak, hirdetések / Health and wellness: videos, pages and ads |
| Turizmus és élmények / Tourism and experiences | …/turizmus-es-elmenyek/ · …/tourism-and-experiences/ · …/turismo-y-experiencias/ | Turizmus és élmények: reelek, foglalási rendszer / Tourism and experiences: reels and a booking system |

Each ends in " · SocialStream"; descriptions, headings and leads are in `site/pages.mjs`, the Spanish (40 new pairs,
not yet read by a native speaker) at the end of `site/es-words.mjs`.

"Kikkel dolgozunk" (who we work with), never "Kiknek dolgozunk" (who we work for): the founder's word, 2026-11-27.
It changed the live who section too (the home and About pages, out with the next upload): the eyebrow "Kikkel
dolgozunk" and the heading "Márkákkal, amelyek már működnek, és most *nőni akarnak*." (were "Kiknek dolgozunk" and
"Márkáknak, …"). The local services lead says "dolgozunk helyi szolgáltatókkal" / "we work with local services" /
"trabajamos con servicios locales" (were "-nak", "for", "para").

The clients the founder named for the pages (2026-11-27), with the results of the founder's case-study PDF
(~/Downloads/Esettanulmányok, vélemények.pdf, 7 pages: three reviews and seven cases with Ads Manager screenshots), as
cards. Since v24 (2026-11-28) the hub and every field page show the cases and the clients as one section, under the
results' eyebrow "Valódi ügyfelek · valódi számok" / "Real clients · real numbers": "Akikkel dolgoztunk." / "Who we
have worked with.", the case cards first, then the clients, each client with its own floating 3D object
(assets/c-*-mix.webp). The founder asked why these were two categories (2026-11-28): until then the field pages had
"Valódi esetek, valódi számok." and, apart, "Ügyfeleink" / "Akikkel még dolgoztunk.". The website service page keeps
"Ügyfeleink" / "Our clients" over "Weboldalak, amiket mi készítettünk." / "Websites we built." Each card:
the figure (or, without one, the name), "name · kind", what we did; the wording is `CLIENTS` in `site/pages.mjs`.
Names as the founder confirmed them; a figure only where the founder or the PDF gives it plainly.

- Webshops: Hoofbútor · Bútor webshop (one word, as in the PDF), 28× ROAS over the years in total, with Péter's review
  beside it (its ad account is named "Medina Shop", never printed); Karaja Makeup Hungary · Kozmetikai webshop, 15× ROAS
  on Google on average (the PDF's "15x ROAS kozmetikai webshopnál", which the founder says is Karaja) and 200+ sales from
  our Facebook ads at about 2500 Ft each (the PDF's ad sets: 1968 and 2680 Ft a purchase); a webshop the founder could
  not name, 9× cheaper per click (€0.18 before, €0.02 ours, €0.03 a landing page view); Realbeauty.hu · Kozmetikai
  webshop, 2×: their best month's revenue doubled in the first month (from July 2023); ZsM Sportruházat · Webshop, 800 Ft
  (€2.19) per smartwatch sale in their first Christmas campaign.
- B2B: Tony Web Studio · Webstúdió, 200+ leads over several months; a luxury real estate company · "Olivér, Meta
  Marketing Pro-ként": +130% leads from not a forint more (the whole account: October 2022, 84 leads from 2 623 941 Ft;
  29 January to 27 February 2023, 193 from 2 622 409 Ft; 31 237 Ft then 13 588 Ft a lead; October's dearest campaign
  181 627 Ft for one lead). It was Big George Properties, advised by the founder as a Meta Marketing Pro, not an agency
  client: unnamed until they agree (the advice to the founder). "A bit more dramatic" was asked for and given with these
  true numbers; "181 627 Ft to 12 028 Ft" is not a headline (the worst campaign set against the best).
- Webinars and events: Karaja Makeup Hungary · Workshopok (several hundred sign-ups from all over the country); Bridle
  Up Hope · Alapítvány (the marketing start in Hungary, no figure); Jézus Krisztus Utolsó Napi Szentjeinek Egyháza ·
  Húsvéti kampány, 30+ countries and languages (Instagram, Facebook, YouTube, a website, social media consulting).
- Local services: Rita’s Beauty Corner · Szépségszalon (website and all marketing, linked to ritasbeautycorner.hu);
  Lunelle Aesthetics · Esztétikai klinika, Budapest (the original website, linked to lunelleclinic.hu); Dorombolda
  Cicahotel · Macskahotel (first ads).
- Website service page: Lunelle Aesthetics and Rita’s Beauty Corner.
- The door webshop is named (live): onlineajtok.hu on its case page (title, crumb, eyebrow, lead, with the PDF's
  "folyamatosan 50-80x" as "50× és 80× közötti megtérülés"), on the result cards and in the running band of numbers.
  The domain no longer answers, so it is not linked. 23× ROAS stays the unnamed watch webshop's.

Waiting for the founder: Tony Web Studio's cost per lead ("2500-3000 forint környékén ... 2024-ben ... igen, 3500"), the
Church's name (the official Hungarian form is on the page; the founder wrote "Az Utolsó Napi Szentek Jézus Krisztus
Egyháza"), Big George Properties' OK to be named, and which old websites to show as demos (with their files). Left out:
the ChatGPT notes' 300% more leads, −50% CPA and 20× average ROAS (no client or dates; some may be Meta work).

What each page shows:

- Interest media: the definition, the claim ("Miért interest media?" / "Why interest media?"), the six problems with
  their services, FlyX Tenerife's 69K and Prof Enzo's 9,8M+ (views on Facebook), the four results, four questions.
- Kikkel dolgozunk / Who we work with: the home page's "who" heading and lead, then under "Területek" / "Fields"
  (since v24; it repeated the page's name before) "Válaszd ki a területed." / "Pick your field." with six cards: the home page's four, plus two new lines: "Videók és oldalak az egészségről:
  Prof Enzo oldala organikusan 9,8M+ megtekintést ért el a Facebookon." / "Videos and pages about health: Prof Enzo's
  page reached 9.8M+ organic views on Facebook." and "Reelek, oldalak, hirdetések és foglalási rendszer egy tenerifei
  élményközpontnak." / "Reels, pages, ads and a booking system for an experience centre on Tenerife."
  Since v23 it also shows all six cases and the twelve clients, each client once (one section since v24, above).
- Each field: three problems (each to its service), "Akikkel dolgoztunk." / "Who we have worked with." (its cases,
  then its clients; "Valódi esetek, valódi számok." until v24), the reviews, a row of clips, "Amivel elérjük." / "What it takes." over the services, three questions.
  Webshops: the door and watch cases, the watch webshop's review. B2B: the hall builder and his review. Webinars and
  events: the healthcare webinar and its review, Up To Youth's clips with their note. Local services: FlyX Tenerife,
  Rita's and János's reviews. Health and wellness: Prof Enzo and the healthcare webinar, three reviews (the webinar's,
  Rita's, János's), Prof Enzo's clips. Tourism: FlyX Tenerife and its clips.
- The footer gains a third group, "Kikkel dolgozunk" / "Who we work with", and "Mi az interest media?" in the
  SocialStream group.
- The menu (since v23): "Kikkel dolgozunk" / "Who we work with" joins it (six links), and its "Eredmények" /
  "Results" goes to the case studies page (it was the home page's #eredmenyek). The home page's service, result and
  field cards link to their pages ("Részletek" / "Details", "Az eset" / "The case"), with "Minden esettanulmány" /
  "All case studies" under the results and "Mind a hat terület és az ügyfeleink" / "All six fields and our clients"
  under the fields.

Still open (the pages went live with these as they are):

- Two pairs overlap: webinars and health both show the healthcare webinar; local services and tourism both lead with
  FlyX Tenerife. Keep both of each pair, or merge one away.
- "Tenerife" is on the first screen of the local services and tourism pages (FlyX Tenerife's name, as on its case
  page), never in a "where we work" sense.
- Rita's and János's reviews sit on both the local services and the health pages.
- The explainer's first question repeats the definition its first screen shows.

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
[English, Spanish] pair per text (389 of them), written for Spain: "tú" to the reader, Canarian "ustedes" (since v17) in the questions a
reader asks the team, euros the Spanish way (216K €, 0,29 €, 1.650 €), the same numbers and nothing new. The claim:
"Las ~~redes sociales~~ han muerto. El *interés* ha ocupado su lugar." Words kept as they are: interest media,
landing page(s), leads, copywriting, Reels, Stories, Feed, ROAS, B2B and every name. Hooks are "ganchos", the funnel
"embudo", a partner a "cliente" ("dos nuevos clientes al mes"). The buttons the scripts write are in ss.js, kit.js
and site.js ("Activar sonido" / "Silenciar", "Reproducir" / "Pausa", the form's topics and messages). Since v18 the
film plays in Spanish on the Spanish pages (its lines below). Change a line in `site/es-words.mjs` and rebuild.

Since 2026-11-26 (the founder: "Spanish site on .es") the Spanish pages live at the root of socialstream.es instead
of under socialstream.hu's `/es/`, with the same words. New with the move, the 404 page of each domain
(`tools/site.mjs`):
- socialstream.es, in Spanish: "Esta página no existe." / "Puede que haya un error en la dirección o que esta página
  ya no exista." / "Volver a la página de inicio", then a Hungarian line ("Ez az oldal nem létezik. Ugrás a magyar
  főoldalra.") and the English one ("This page doesn't exist. Go to the home page.") linking socialstream.hu.
- socialstream.hu keeps its Hungarian page; its Spanish line ("Esta página no existe. Ir a la página de inicio.")
  now links socialstream.es.

## Approved: the brand film in Spanish (2026-11-18)

The founder approved these lines before the first render ("Yes, render them"). They are the Spanish site's own
words for the English cut's lines, so the film and the pages say the same thing; the money is the English cut's
euros written the Spanish way. FlyX's three comments stay in English, as in both cuts. In the film's order (they live
in `video/sizzle/build.py`, `TEXT["es"]`):

- Publicas. / Pagas anuncios. / ¿Y aun así nadie compra?
- Las ~~redes sociales~~ han muerto. / El *interés* ha ocupado su lugar.
- FlyX Tenerife · Centro de experiencias · 69K visualizaciones en un reel · Comentario
- Prof Enzo · Facebook · 9,8M+ visualizaciones · 33K seguidores
- Fragmentos de nuestros vídeos · Rodaje · Edición · Subtítulos · Reels · Podcast y entrevista
- Hacemos el *vídeo*, gestionamos los *anuncios* y medimos lo que *generan*. (chips: 81× · 216K € · 23× · 0,29 €)
- Constructora de naves industriales · B2B · Meta · 216K € · facturación en una semana · Lun Mar Mié Jue Vie Sáb Dom
- Tienda online de puertas · Google Performance Max · 81× ROAS · 1 € → 81 €
- Tienda online de relojes · Navidad · 23× ROAS · más de 21K € de facturación
- Webinar sanitario · ≈5.700 · registros con 1.650 € · 0,29 € por registro
- Desde 2022 · 820K+ € · presupuesto gestionado
- No te fíes de nuestra palabra. *Fíate de la suya.*
- Péter · Hoof Bútor: “Hubo compras desde el día del lanzamiento…” · Cliente constructor de naves · B2B: “…tantas
  solicitudes de presupuesto como antes en medio año.” · Tienda online de relojes: “…la temporada navideña jugó a
  nuestro favor y no en contra.” · Empresa sanitaria: “…el contador se paró en casi 5.700, apenas podíamos creer…” ·
  Rita · Rita’s Beauty Corner: “Los resultados llegaron rápido…” · János · EJ Massage Therapies: “Solo puedo
  recomendarlos.”
- Vídeos que se ven *hasta el final.* / Anuncios que *salen rentables.* / Agencia de interest media

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
  webshop: Péter's Hoof Bútor quote is not tied to it), "Amivel elértük." / "What it took." (Fizetett hirdetés), and
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
