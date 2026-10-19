# FlyX Tenerife homepage: GoHighLevel kit

## What's in the kit
| File | What it's for |
|---|---|
| `1-paste-into-GHL.html` | The whole homepage as one block of code. Paste it into GoHighLevel. |
| `2-image-link-helper.html` | Open in your browser. Paste your Media Library links, and it gives you updated code. |
| `images/` | The 8 images the page uses. |
| `standalone-site/` | The same page as a normal website, in case you ever host it outside GoHighLevel. |

The videos already stream from your GoHighLevel media library, so they need no setup.

## Step 1: Upload the images (5 minutes)
In GoHighLevel open **Media Library**. Upload the 8 files from the `images/` folder:
`coast.jpg`, `hero.jpg`, `inside.jpg`, `lobby.jpg`, `logo.png`, `sunset.jpg`, `valleys.jpg`, `volcanic.jpg`.

## Step 2: Build the code with your image links
1. Open `2-image-link-helper.html` in Chrome, Safari or Edge.
2. In the Media Library, copy each image's link and paste it next to the matching name.
3. Press **Build code**, then **Copy code**.

You can skip steps 1 and 2 for a quick test. `1-paste-into-GHL.html` works as it is, with images loading
from the GitHub copy. Before launch, though, use your Media Library links so the site doesn't depend on GitHub.

## Step 3: Make a blank page
Sites → Websites (or Funnels) → the FlyX site → edit the home page, or add a new page and start
from blank. Delete the template's header, footer and default sections. The design has its own menu
and footer.

## Step 4: Add one full-width section
Add a **Full Width** section with one row and one column. In each of the three, set padding and
margin to 0 and width to full.

## Step 5: Paste the code
Drag a **Custom JS/HTML** element (named "Code" in some versions) into the column. Open it, paste the
code from step 2 (or the contents of `1-paste-into-GHL.html`), and save.

## Step 6: Check on Preview, then publish
The editor doesn't run the animations, so use **Preview**. Scroll the whole page on a phone and on a computer.
- If the page is static, or the animations jump, open the site **Settings** and switch off
  **Optimise JavaScript** (and any "lazy load" option for scripts), then preview again.
- Set the page title and meta description under **SEO**, then **Publish**.

## Before going live, update these in the code
Search the pasted code for these and change them:
- `https://flyxtenerife.com/the-experience`: the **Book** buttons go here. Point them at your
  GoHighLevel booking page or calendar if tickets are sold there.
- `href="#"`: the **Legal** links (Terms, Privacy, Cancellation, Safety) and **Follow Us** links
  (Facebook, Instagram, TikTok) are still placeholders.
- `Read all reviews on Google`: the link opens Google Maps. Swap in your direct Google review link
  if you have it.
- Prices are in `const TICKETS` near the top of the script: Adults 29, Kids 24, Residents 18, Family 100.

## If the scroll effects break inside the builder
The pinned scroll sections need their parent containers to have no `overflow: hidden` or `transform`.
The code already resets GoHighLevel's wrappers, but builder versions differ. If it still misbehaves,
upload `standalone-site/` to any static host (Netlify, Vercel, GitHub Pages) and point your domain
there, or show it inside GoHighLevel with a full-page iframe. An iframe keeps the design intact but is
weaker for SEO.
