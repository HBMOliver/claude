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
| Aurora Mix | Scrolla's layout in Aurora's look | Night blue. The first screen, the services, Kiknek and the last call sit in inset panels with the aurora moving inside. The film stands beside the claim like a post, and the real numbers run along the panel's foot. The reels close in on the statement, the services are big-object cards over two running tag rows, the stat cards come with a running row of reels, the with-us card lies over the elsewhere card, the steps are big numbered cards, the reviews are a row you scroll, and a giant wordmark sits at the end. A light follows the cursor round the first screen. It opens on the film alone (asked for on 2026-11-12). Scrolling on, on wide screens the film shrinks into its card while the panel and the claim come in; on phones and short screens the panel rises over it. | https://claude.ai/artifact/C52b5BBkmGw83WvDFJyZCF |

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
- `parts.mjs`: shared markup (claim, film, reel, rail, form, questions, footer, `toSvc` link).
- `concepts/<name>.mjs`: each concept's own page.
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

  The brand film opens and closes on the kit's stacked logo since b1ae71e (see `video/README.md`), on every page that plays it.
- **Published links:** they still show the old logo until republished. The host sets its own tab icon, so the
  favicon shows only when the folder is served.

## socialstream.hu (2026-11-12)

Aurora Mix is the page going live on https://socialstream.hu, hosted by Pulse CRM. Pulse serves an uploaded
folder exactly as it is, at the domain root: an agency admin uploads it as a ZIP for the domain under
Settings → Domains, and a new upload replaces the old version in one step. `node tools/site.mjs` writes that
folder to `dist/site/`:

- `index.html`: `mix.html` with the domain's head: the title "SocialStream · Interest media ügynökség", the
  canonical address, share tags with `assets/og-image.jpg` (1200 × 630) and the organisation's details as JSON-LD.
- The page's own files (`base.css`, `mix.css`, `ss.js`, `kit.js`) and only the assets it uses, plus the three cuts
  of the brand film that `kit.js` picks between.
- The logo kit's web icons at the root, where the page's head and the manifest ask for them.
- `404.html` (every link in it starts at the root, so it works at any depth), `robots.txt` and `sitemap.xml`.

It writes real files only (no symlinks), and stops if a file the page names is missing or the folder breaks
Pulse's limits (60 MB, 1,500 files). On 2026-11-12 it was 59 files and 17.6 MB. `tools/og.mjs` renders the share
image from `tools/og.html`: the logo, the claim and three of their reels on the night blue.

To update the live site: change the page, `node build.mjs mix`, `node tools/site.mjs`, run the last three commands
under Run, then zip `dist/site/` and upload it for the domain in Pulse.

Before launch (2026-11-12):

- **Mail: done.** hello@socialstream.hu, which the audit form and the contact link write to, is a free Google
  Workspace alias of Olivér's account. socialstream.hu is a verified secondary domain with MX and SPF records at
  Rackhost. Email signing (DKIM) can only be added 24 to 72 hours after Gmail was switched on.
- **Fonts: open.** The page loads Sora, Inter, Instrument Serif and Fraunces from Google Fonts, which sends each
  visitor's IP address to Google. Serving them from the site is waiting for the user's decision.
- **Film: done.** The title card was re-cut with the new logo (b1ae71e). The opening's shrink now ends at 0.56 of
  the scroll, so the two cuts line up while they crossfade (66918b5).

## Run

```bash
node build.mjs
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root . --port 4560
node lab/check.mjs
node tools/artifact.mjs
BASE=http://localhost:4560/dist/ node lab/check.mjs
node tools/site.mjs
node ../../../.claude/skills/scroll-craft/scripts/serve.mjs --root dist/site --port 4565
BASE=http://localhost:4565/ node lab/check.mjs index
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
