# Putting the FlyX homepage on GoHighLevel

Use `ghl-embed.html`. It is the full homepage as one paste-in block: fonts, styles, markup and
animation libraries (loaded from public CDNs). The videos already stream from your GoHighLevel
media library. The images load from the GitHub copy of this repo until you swap them (step 5).

## 1. Make a blank page
Sites → Websites (or Funnels) → your FlyX site → edit the home page, or add a new page and
start from blank. Delete the template's header, footer and any default sections. The design
has its own navigation and footer.

## 2. Add one full-width section
Add a **Full Width** section with one row and one column. In each of the three settings panels
set padding and margin to 0, and set the width to full. The embed also includes CSS that removes
GoHighLevel's wrapper padding.

## 3. Paste the code
Drag the **Custom JS/HTML** element (named "Code" in some versions) into the column, open it,
paste the entire contents of `ghl-embed.html`, and save.

## 4. Check it on the preview link, not in the editor
The editor doesn't run the animations. Open **Preview** (or publish to a test path) and scroll
the whole page on desktop and on a phone.
If the page is static or the animations jump, open the site's settings and switch off
**Optimise JavaScript** (and any "lazy load scripts" option), then publish again.

## 5. Move the images into your Media Library (recommended before launch)
Upload the 9 files in `assets/`: hero, volcanic, coast, valleys, terraces, sunset, anaga,
guests (.jpg) and logo (.png). Then, in the pasted code, replace each URL that starts with
`https://cdn.jsdelivr.net/gh/HBMOliver/claude@…/flyx-tenerife/assets/` with that file's
Media Library URL.

## 6. Page settings and publish
Set the page title and meta description under SEO, publish, and check the live domain.

## Things to update in the code
- **Booking button** → currently `https://flyxtenerife.com/the-experience`. Point it at your
  GoHighLevel calendar or booking page if that's where tickets are sold (search for `bookLink`).
- **Footer links** → the Legal and Follow Us links are `#` placeholders.
- **Prices** → `TICKETS` near the top of the script (only the adult "from €23" is confirmed).

## If the scroll effects break inside the builder
Pinned sections need their parent containers to have no `overflow: hidden` or `transform`.
If GoHighLevel's wrappers still interfere after step 2, host `index.html` and `assets/` as a
plain static site, and point the domain there or show it through a full-page iframe.
An iframe keeps the design intact but is weaker for SEO.
