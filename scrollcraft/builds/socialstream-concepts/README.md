# SocialStream: four concepts and a mix

Four whole-page concepts for SocialStream, built from ideas in six Framer sites the client sent
(Talentank, Conversion, Cutflow, Marketia, Strivai, Scrolla). They share the words and the working
parts; each one has its own markup, structure and look. A fifth page, Aurora Mix, puts Aurora's look into
Scrolla's layout. The client asked for it after seeing the four ("aurorat kevernem ezzel", with the Scrolla link);
Aurora itself is unchanged.

| Concept | Lead reference | Look | Published |
|---|---|---|---|
| Pulse | Scrolla | White page, black rounded panels, one hot rose. Reel cards float round the claim. | https://claude.ai/artifact/D7G86aKgXU2nqcDZgQKA8e |
| Premiere | Talentank (Marketia for the giant running words) | Black and cinematic. The claim's two sentences sit above and below a wide film band. | https://claude.ai/artifact/F4yHZA3CbyoiQ7mN5ckVmT |
| Aurora | Conversion (Strivai for the horizon light and the glass) | Night blue with a moving aurora. Real results float on glass cards. | https://claude.ai/artifact/PtcSvRhunabu4nDLBXoL82 |
| Studio | Cutflow | Warm grey with white cards and one coral. The film plays like a story, with reels peeking out behind it. | https://claude.ai/artifact/2GpEg95SqLphnNoG937xu2 |
| Aurora Mix | Scrolla's layout in Aurora's look | Night blue. The first screen, the services, Kiknek and the last call sit in inset panels with the aurora moving inside. The film stands beside the claim like a post, and the real numbers run along the panel's foot. The reels close in on the statement, the services are big-object cards over two running tag rows, the stat cards come with a running row of reels, the with-us card lies over the elsewhere card, the steps are big numbered cards, the reviews are a row you scroll, and a giant wordmark sits at the end. A light follows the cursor round the first screen. It opens on the film alone (asked for on 2026-11-12). Scrolling on, on wide screens the film shrinks into its card while the panel and the claim come in; on phones and short screens the panel rises over it. Since 2026-11-15 blue-purple leads and red-pink is only the accent ("too pink" before): the colours are variables at the top of `mix.css`, and the 3D objects are recoloured copies for Mix only (`assets/*-mix.webp`). The film it plays is the sizzle in `video/sizzle/` (since 2026-11-16; before it, the films in `video/film/`). | https://claude.ai/artifact/C52b5BBkmGw83WvDFJyZCF |

The published pages are private until they are shared from their Share menu.

## What every concept keeps

- **First screen:** the claim is the headline: "A social media meghalt. Az érdeklődés vette át a helyét." Aurora Mix is
  the exception the client asked for: it opens on the film, which says the claim itself, and the headline arrives
  with the scroll.
  - "social media" is struck through the middle.
  - The free-audit button is beside it.
  - Tenerife and Budapest are not on it.
- **Language:** Hungarian first, with an EN switch.
- **Numbers:** only the real ones (see `content.mjs`).
- **Testimonials:** word for word.
- **Contact:** the audit form writes an email to hello@socialstream.hu, the same as in Daylight.
- **Business problems:** one for each service, in their own block before the services. Each one links
  to the service card that answers it (new, see COPY.md).
- **Motion when nobody scrolls:**
  - the brand film
  - running rows
  - floating objects
  - each concept's own loop
- **Cursor:** each concept has something on its first screen that follows the mouse, and its buttons
  pull toward a cursor that comes near.
  - Phones have no cursor, so their pages keep their own motion.
  - With reduced motion, nothing follows and nothing loops.

## Files

- `content.mjs`: every word in both languages. Each service carries its `pain`, the problem it answers.
- `parts.mjs`: shared markup (claim, film, reel, rail, form, questions, footer, `toSvc` link). It renders two ways
  (`render()`): both languages in one page for the concepts (Hungarian in the element, English in `data-en` or a twin
  span, files linked relatively), or one language per page for the live site (`render({ lang, root: '/' })`: only
  that language's words, files linked from the root, the HU / EN / ES switch links to the other languages' pages, a menu
  button on tablets and phones, the footer's links). The concepts' output is byte for byte what it was before.
- `concepts/<name>.mjs`: each concept's own page. `mix.mjs` exports its sections one by one (`heroSec`, `painsSec`,
  `servicesSec`, `statCards`, `stepsSec`, `whoSec`, `quote`, `teamSec`, `offerSec` and the rest) and `main()`, so the
  site's pages are built from the same parts.
- `site/` (since 2026-11-16): the pages of socialstream.hu beyond the home page.
  - `pages.mjs`: one entry per page (its address in both languages, title, description, heading, answer, and the
    words only it has), the menu's links. Every word in it is new (COPY.md) but says only what content.mjs says.
  - `head.mjs`: each page's head lines: canonical, the hu / en / es / x-default alternates, share tags, structured data.
  - `es.mjs` and `es-words.mjs` (since 2026-11-18): the Spanish pages. The site's words stay in Hungarian and English;
    a Spanish page looks each English text up in `es-words.mjs` ([English, Spanish] pairs) through `word()`, and its
    addresses are `es.mjs`'s `SLUGS`. A missing Spanish text stops the build; `SS_ES_TODO=1 node tools/site.mjs`
    writes the missing ones to `dist/es-todo.mjs` instead. Spanish pages show the English page's euros the Spanish
    way (216K €, 0,29 €) and, since v18, play the film's own Spanish cuts (the English ones before).
  - `films.mjs` (since v18): where each language's two cuts of the brand film are. Pulse's Media Storage holds
    them (at `https://socialstream.hu/m/<id>.mp4`, with seeking and a year's cache), so they no longer travel in the
    site's ZIP; each entry keeps the uploaded file's sha256, and a cut not stored yet travels in the ZIP as before.
  - `templates.mjs`: one template per kind of page (home, services, service, about, audit, faq, contact).
- `site.css`: the site's additions to Mix's look (subpages, menu, footer links); only the site's pages load it.
- `base.css`: shared mechanics.
- `<name>.css`: each concept's look.
- `ss.js`: language, form helpers. Copied from Daylight.
- `kit.js`: the behaviour the concepts share:
  - arrivals and counters
  - the film
  - running rows
  - lighting words
  - scroll drift
  - the cursor light
  - `[data-follow]` followers and magnetic buttons
  - the menu
  - the audit form
- `reels.js` (Aurora Mix only, since 2026-11-15): Mix's 19 reels (six around the statement, 13 in the rail) are short silent loops (`assets/r-*.mp4`, 360x640,
  2.1-5.3 s, 3.0 MB together; since 2026-11-16 the two big ones by the statement are the smartwatch ad and Prof Enzo, and the
  Latvia clips are Up To Youth's with event titles, the Türkiye film DELSAS's) over their posters (`assets/r-*.jpg`), with a reel's furniture in markup: a progress
  bar, the side icons, whose post it is. A clip loads and plays only while its card is on screen. With reduced motion
  or a data saver only the posters show.
- `tools/reels.py`: cuts those clips and posters from the founder's footage (paths are local to the founder's Mac).
  Captions are burned in only where the words are real: the clients' own edits (FlyX, András, Prof Enzo, Up To
  Youth, Miskolc Plaza), event titles on Up To Youth's Latvia clips (written for the site since 2026-11-16, when the founder asked for them
  to read as event videos; before that, the words said in them), the Türkiye film's own subtitles
  set for a vertical frame, the Nike spec ad's two end lines laid over its shots, and the two smartwatch ads (added
  2026-11-16): a creator's opening line (transcribed on the Mac, set at the top so the watch stays clear) and the V89
  ad's own caption. Those two are labelled "Okosóra hirdetés" without the brand's name (the V89 caption still names
  the model), and the founder cleared both for the site. For the other new clips the founder has the consent of the
  people shown; the FlyX customers and András's reels come from the clients' own published videos.
- `build.mjs`: writes `pulse.html`, `premiere.html`, `aurora.html`, `studio.html`, `mix.html`. It stops on an em dash
  in visible copy.
- `tools/artifact.mjs`: packages each page for claude.ai.
  - `dist/<name>/index.html` with styles and scripts inlined.
  - `dist/<name>/files.json`, the assets to publish with it.
  - `dist/<name>.html`, a local test wrapper.
- `lab/check.mjs`: checks each page on desktop and phone without looking at it:
  - first screen, strike line, film and its button
  - running rows, counters, the form, English
  - the problems and their links, cursor followers
  - reduced motion, no sideways scroll
  - on the site: `index` is the home page (English by its EN link), `site` every other page from the sitemap (the
    first screen, the cursor followers, the row running at rest, the form in the page's language, the phone menu, no
    sideways scroll at 1440 and 1100 with a mouse at the edges and at 390 and 320, reduced motion), and that a page's
    language comes from the page alone, not from a choice the browser remembers from the one-page site of before.
- `lab/sitecheck.mjs`: the site's folder, served: every file and page answers 200; each page's head (language, one
  h1, a title and description of its own, its canonical address, the alternates both ways, share tags, structured
  data with what its kind of page needs); no words of the other language; every link inside the site goes somewhere
  real; the sitemap, robots.txt, llms.txt and 404 page; and in a browser on every page no failed request, console
  error or other host, nothing left unarrived, no sideways scroll at 390.

## Logo (2026-11-12)

The approved logo (direction G2) comes from the kit in `../../brand/socialstream-logo/kit/`. Its files are
copied unchanged: the header files and the corner mark into `assets/`, and the favicon set from `kit/web/` to
this folder's root, where the head's root paths (`/favicon.ico` and the rest) find it. The page keeps its own
`theme-color` instead of the snippet's.

- **Header:** `nav()` in `parts.mjs` takes `{ ground, dark, film }` and stacks the files in one cell; `base.css`
  shows one at a time.
  - From 480 px wide: the small-cut horizontal lockup, 172 x 30 px.
  - Narrower: the phone alone. The kit's floor for the lockup is 140 px, more than a phone's bar has room for.
  - Light or dark files by the page's ground; Pulse switches to the dark ones over its black panels (`on-dark`).
  - While Mix's opening film lies under the bar, the corner mark (`on-film` in `kit.js`).
- **On the film:** Mix's and Studio's account line uses the corner mark, the kit's mark for video.
- **Mix's footer** (Mix is the page going live on socialstream.hu): `footer(cls, big, kit)` uses the kit's files.
  - The small-cut dark lockup in the line.
  - The full dark lockup as the giant sign-off, as wide as the content column. The typed giant's gradient sheen
    is gone, because the kit allows no effects on the logo.
- **Still typed in Fraunces** on the other four pages:
  - the footer's small wordmark
  - the giant footer wordmark on Pulse and Premiere
  - Premiere's running ghost words

  The brand film opens and closes on the kit's stacked logo since b1ae71e, over the reel wall since ef0dd7e, with a 4.56 s opening since 877347d (see
  `video/README.md`), on every page that plays it.
- **Published links:** they still show the old logo until republished. The host sets its own tab icon, so the
  favicon shows only when the folder is served.

## socialstream.hu (2026-11-12)

Aurora Mix is the page going live on https://socialstream.hu, hosted by Pulse CRM. Pulse serves an uploaded
folder exactly as it is, at the domain root: an agency admin uploads it as a ZIP for the domain under
Settings → Domains, and a new upload replaces the old version in one step. A folder's `index.html` is served at its
address with a trailing slash (`/rolunk/`; `/rolunk` redirects there), and Pulse keeps some first path segments for
itself (`p`, `form`, `book`, `fonts`, `socialstream` and more: `tools/site.mjs` lists them and stops on one).
`node tools/site.mjs` writes that folder to `dist/site/`:

- Since 2026-11-16 the site has 24 pages (phase 2 of the Claude Docs doc "SocialStream SEO, AEO and subpage plan"),
  each in one language: Hungarian at the root, English under `/en/`; since 2026-11-18 also Spanish under `/es/`
  (`/es/servicios/…`, `/es/casos-de-exito/…`, `/es/sobre-nosotros/`, `/es/auditoria-gratuita/`,
  `/es/preguntas-frecuentes/`, `/es/contacto/`), 19 pages in each language. The home page (`/`, `/en/`) is Aurora Mix itself;
  the others are the services page and the six services (`/szolgaltatasok/…`, `/en/services/…`), About us
  (`/rolunk/`), the free audit (`/ingyenes-audit/`), the questions (`/gyik/`, with the FAQPage data) and contact
  (`/kapcsolat/`), each at `<address>/index.html`. Every page has its own title and description, its canonical
  address, the hu / en / x-default alternates, share tags with `assets/og-image.jpg` (1200 × 630) and structured
  data (the organisation and the site; the page with its breadcrumb; the service, the team, the questions, the film as
  the page shows them). The home page keeps its title "SocialStream · Interest media ügynökség" and its description
  until the founder approves the doc's drafts. The case studies (the hub, four anonymous cases, FlyX Tenerife and
  Prof Enzo) are live since v13 and v15; the audience pages, `/en/tenerife/` and the legal pages wait for the
  founder's facts (`site/pages.mjs` lists what is left out).
- `robots.txt` (every crawler allowed, the AI crawlers named), `sitemap.xml` (every page with its alternates) and
  `llms.txt` (the doc's draft with the pages' addresses; Pulse serves the folder's own instead of its generated one).
- The pages' own files (`base.css`, `mix.css`, `site.css`, `ss.js`, `kit.js`, `logo-anim.js`, `reels.js`), linked
  from the root, and only the assets they use. The brand film's cuts that `kit.js` picks between for Mix
  (`hero-1080` for the opening on a wide screen, `hero-v-720` in the card and on phones; Hungarian, English `-en`
  and Spanish `-es`) are not in the package since v18: Pulse's Media Storage holds them, each page names its own
  language's two by their address there (`site/films.mjs`, `data-src-w` and `data-src-v` on the film), and a cut
  not stored yet travels in the package as before. Mix never asks for `hero-540`, so it stays out of the package
  (since 2026-11-16, when the 59 s sizzle became the film).
- The logo kit's web icons at the root, where the page's head and the manifest ask for them.
- `404.html` (every link in it starts at the root, so it works at any depth), `robots.txt` and `sitemap.xml`.

It writes real files only (no symlinks), and stops if a file a page names is missing, a page carries an em dash or
another language's words (or forints on a Spanish page), a top-level name is one of Pulse's own paths, or the
upload breaks Pulse's limits (its `services/page-zip.js`: the ZIP up to 60 MiB, 1,500 entries, 250 MiB unpacked; the
build zips `dist/site` into `dist/site.zip` and measures it). On 2026-11-12 it was 59 files and 18.8 MB; on 2026-11-15, with the new palette and the remade film, 59 files and 19.8 MB (`socialstream-site-v4.zip`); v10 (the sizzle, one page) 87 files and 55.5 MB; on 2026-11-16 with the 24 pages, 112 files and 56.3 MB; on 2026-11-18 with the film's sound and the Spanish
pages, 146 files, 60.4 MB unpacked and a 58.7 MiB ZIP; the films were 55.9 MB of it, and a Spanish pair would not
fit. So since v18 (the Spanish film) all six cuts live in Pulse's Media Storage (the founder's choice, 2026-11-18) and
the package is 142 files, 7.2 MB unpacked and a 5.52 MiB ZIP. `tools/og.mjs` renders the share
image from `tools/og.html`: the logo, the claim and three of their reels on the night blue.

To update the live site: change the page, `node build.mjs mix`, `node tools/site.mjs`, run the last three commands
under Run, then zip `dist/site/` and upload it for the domain in Pulse.

Before launch (2026-11-12):

- **Mail: done.** hello@socialstream.hu, which the audit form and the contact link write to, is a free Google
  Workspace alias of Olivér's account. socialstream.hu is a verified secondary domain with MX and SPF records at
  Rackhost. Email signing (DKIM) is on since 2026-11-15 (TXT google._domainkey).
- **Fonts: open.** The page loads Sora, Inter, Instrument Serif and Fraunces from Google Fonts, which sends each
  visitor's IP address to Google. Serving them from the site is waiting for the user's decision.
- **Film: the sizzle (2026-11-16).** The founder sent Prof Enzo's real views for it (9.8M+) and asked to put it live;
  asked where, they chose to have it replace the film everywhere: the opening, the card and phones, muted. It is
  `video/sizzle/` (59.4 s, 1485 frames, cut to the music; the video session's handover is in the shared notes).
  `sh tools/hero.sh <master-wide> <master-tall> [-en] [poster s]` makes the site's cuts from its four masters (wide
  and upright, Hungarian and English, all on one clock): `hero-1080`, `hero-v-720` and `hero-540` (the other
  concepts' smaller frames), silent, and the posters at 2.6 s, where the logo stands whole on the wall (no words, so
  one pair serves both languages). The upright cut is its own layout, not a crop, so in the card the two dissolve into
  each other. After its first play the film loops from 3.2 s (`data-loop` in `parts.mjs`, `kit.js`): the sizzle opens
  and ends on the logo, and a loop to 0 showed the logo twice within five seconds.
- **Film: v5, "Through the phone" (2026-11-15).** Until 2026-11-16 the site played `video/film/` v5: one moving camera through the
  logo's S, the claim, a stream of their reels and into the phone (35.4 s), in Hungarian and in English; the page's
  language picks the film. Before it, the remake in the site's look (32.12 s, the logo animation first). Before that, the title card was re-cut with the new logo (b1ae71e), then made longer, with the logo on a
  soft night band over the moving reel wall (ef0dd7e), and its opening shortened to 4.56 s (877347d: 774 frames,
  30.96 s, the same timeline in both cuts). The
  opening's shrink now ends at 0.56 of the scroll, so the two cuts line up while they crossfade (66918b5).

## Run

```bash
node build.mjs
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4560
node lab/check.mjs
node tools/artifact.mjs
BASE=http://localhost:4560/dist/ node lab/check.mjs
node tools/site.mjs
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root dist/site --port 4565
BASE=http://localhost:4565/ node lab/check.mjs index,site
node lab/sitecheck.mjs dist/site http://localhost:4565/
```

The checks need `playwright-core` and Google Chrome. The fourth command packages the pages, and the
fifth runs the same checks on the packaged pages. The last four build the socialstream.hu folder, serve it
as a domain root, run the page's checks on it and then `lab/sitecheck.mjs`: every file answers 200, the head,
no failed requests, console errors or other hosts besides Google Fonts, English, and the 404 page.

## Measured (2026-11-11)

**Motion at rest.** Each test stopped once per screen height down the page and took two screenshots
1.2 s apart. A stop counts as moving when at least 1% of the screen changed. Stops past the end of the
page are not counted.

| Concept | Desktop, 1440x900 | Phone, 390x664 |
|---|---|---|
| Pulse | 6 of 15 | 12 of 31 |
| Premiere | 3 of 16 | 7 of 27 |
| Aurora | 3 of 14 | 11 of 29 |
| Studio | 3 of 12 | 7 of 28 |
| Aurora Mix | 10 of 16 | 17 of 28 |

On every page the first two screens keep moving: the film, running rows and floating cards. On Pulse
the services and the results move too, because their rows keep running. Each page's last call moves:
Studio's deck and Aurora's aurora.

Aurora Mix moves at many more stops than Aurora. Since 2026-11-12 it opens on the film itself, and the opening adds stops of its own. Its panels carry the aurora, the reel and tag rows keep running, and the reels close in on the statement. From the reviews down to the questions it is still quiet too.

On the first four pages, from "Kiknek" down to the questions, the sections are mostly still on a computer. In those sections the
floating objects, the problem blocks' own loops and Studio's slow team photos each change less than 1%
of the screen.

**Slow phone.** The test slowed the CPU 4x and used 9 Mbit/s with a 150 ms round trip, from a cold cache.
On every page the claim painted at about 0.7 s and the page loaded in 1.0 to 1.4 s. On Pulse,
Premiere and Studio the film started playing at 1.4 to 1.7 s. Aurora's film sits below its first
screen, so it starts when it is scrolled to.
