"""Build preview.html (labelled concept) and ghl-embed.html (GoHighLevel paste-in) from index.html.
Run from anywhere: python3 flyx-tenerife/tools/build.py"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
s = (root / 'index.html').read_text()

# preview.html: same page, labelled as a concept and hidden from search engines
pv = s.replace('<title>FlyX Tenerife · 5D Flying Cinema</title>', '<title>FlyX Tenerife · Design concept</title>\n<meta name="robots" content="noindex, nofollow">', 1)
pv = pv.replace('</style>', """.concept { position: fixed; left: max(16px, env(safe-area-inset-left, 0px)); bottom: calc(16px + env(safe-area-inset-bottom, 0px)); z-index: 95; font: 500 .66rem/1.3 var(--f-display); letter-spacing: .14em; text-transform: uppercase; color: var(--paper); background: rgba(13,43,49,.86); padding: .55rem .8rem; border-radius: 8px; max-width: calc(100% - 32px); }
@media (max-width: 760px) { .concept { bottom: calc(84px + env(safe-area-inset-bottom, 0px)); } }
</style>""", 1)
pv = pv.replace('<a class="skip" href="#main">Skip to content</a>', '<a class="skip" href="#main">Skip to content</a>\n<div class="concept" role="note">Design concept · not the official FlyX Tenerife website</div>', 1)
(root / 'preview.html').write_text(pv)

# ghl-embed.html: one block for a GoHighLevel Custom JS/HTML element
BASE = 'https://cdn.jsdelivr.net/gh/HBMOliver/claude@ad20ff1b1c9ec9c73b563c68949cca56a7290069/flyx-tenerife/assets/'
head = re.search(r'<head>(.*?)</head>', s, re.S).group(1)
body = re.search(r'<body>(.*?)</body>', s, re.S).group(1)
fonts = re.findall(r'<link rel="(?:preconnect|stylesheet)"[^>]*>', head)
style = re.search(r'<style>.*?</style>', head, re.S).group(0)
cdn = {
    'assets/js/gsap.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js',
    'assets/js/ScrollTrigger.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js',
    'assets/js/lenis.min.js': 'https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js',
}
for k, v in cdn.items():
    body = body.replace(f'src="{k}"', f'src="{v}"')
body = body.replace('src="assets/', f'src="{BASE}')
assert 'assets/' not in body.replace(BASE, ''), 'unrewritten asset path'
ghl_css = """<style>
/* Let the FlyX page run edge to edge inside GoHighLevel's section/row/column wrappers */
html, body { margin: 0 !important; padding: 0 !important; }
.c-section:has(.hero), .c-row:has(.hero), .c-column:has(.hero), .c-custom-code:has(.hero), .inner:has(.hero) { padding: 0 !important; margin: 0 !important; max-width: none !important; width: 100% !important; overflow: visible !important; }
</style>"""
out = ("<!-- FlyX Tenerife homepage: paste this whole file into one GoHighLevel Custom HTML/JS element. -->\n"
       f"<!-- Images load from the GitHub copy. To use your Media Library instead, replace each URL starting with\n     {BASE}\n     with that image's Media Library URL. -->\n"
       "<script>document.documentElement.classList.add('js');</script>\n"
       + "\n".join(fonts) + "\n" + style + "\n" + ghl_css + "\n" + body.strip() + "\n")
(root / 'ghl-embed.html').write_text(out)
print('built preview.html and ghl-embed.html')
