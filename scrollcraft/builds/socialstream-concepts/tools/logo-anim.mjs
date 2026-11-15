// node tools/logo-anim.mjs   (from this build's folder)
// Turns the logo kit's horizontal logo animation (../../brand/socialstream-logo/kit/motion/horizontal/compositions/
// logo.html: the phone arrives, the S swipes up into it, it leans in at 15°, its 15° cut opens, the name streams out
// from behind it, the A's cut opens) into the footer's animated logo for Aurora Mix. Writes logo-anim.mjs, the markup
// that parts.mjs puts in the footer: the composition's two layers (the name under the phone) with every animated
// attribute set to its last value, so the markup alone is the kit's dark master, and the view cropped to the
// lockup. logo-anim.js plays the build in place (without the video's 3x close-up) when the footer comes into view.
import fs from 'node:fs';
const SRC = '../../brand/socialstream-logo/kit/motion/horizontal/compositions/logo.html';
// the kit master's own frame (its 1471 x 256 viewBox, clear space included) in the composition's 1920 x 1080 frame, so
// the footer keeps the size and margins the master image had there. Measured in Chrome at 4x: the finished
// composition draws the lockup over x 384-1536, y 464-616 (60 % of the frame width); the master draws it over
// x 35.75-1435, y 35.75-220.25 of its viewBox; scale 0.8235
const CROP = { x: 354.56, y: 434.56, w: 1211.37, h: 210.82 };
const comp = fs.readFileSync(SRC, 'utf8');
const svgs = comp.match(/<svg[\s\S]*?<\/svg>/g);
if (!svgs || svgs.length !== 2) throw new Error('expected the name layer and the phone layer');
// last values, from the composition's timeline (the "to" side of each tween)
const last = {
  'logo-wipe': { width: '9314.8163' },
  'logo-social': { transform: 'translate(0 0)' },
  'logo-stream': { transform: 'translate(0 0)' },
  'logo-acut-up': { height: '0' },
  'logo-acut-dn': { y: '67.842', height: '0' },
  'logo-cut-up': { height: '0' },
  'logo-cut-dn': { y: '230.5773', height: '0' },
  'logo-hero': { transform: 'translate(128 128) scale(1 1) translate(-128 -128)' },
  'logo-arrive': { transform: 'translate(128 128) scale(1 1) translate(-128 -128)', opacity: '1' },
  'logo-lean': { transform: 'rotate(15 128 128)' },
  'logo-s': { transform: 'translate(0 0)' },
};
let seen = 0;
const finish = svg => svg.replace(/<(\w+)([^>]*?)\sid="(logo-[a-z-]+)"([^>]*?)(\/?)>/g, (m, tag, a, id, b, close) => {
  const set = last[id]; if (!set) return m;
  seen++;
  let attrs = (a + ' id="' + id + '"' + b);
  for (const [k, v] of Object.entries(set)) {
    const re = new RegExp('\\s' + k + '="[^"]*"');
    attrs = re.test(attrs) ? attrs.replace(re, ` ${k}="${v}"`) : attrs + ` ${k}="${v}"`;
  }
  return `<${tag}${attrs}${close}>`;
});
const view = `viewBox="${CROP.x} ${CROP.y} ${CROP.w} ${CROP.h}"`;
const prep = svg => finish(svg).replace('viewBox="0 0 1920 1080"', view).replace(/logo-/g, 'fl-').replace(' aria-hidden="true"', ' aria-hidden="true" focusable="false"');
const [word, phone] = svgs.map(prep);
if (seen !== Object.keys(last).length) throw new Error(`set ${seen} of ${Object.keys(last).length} animated parts: the composition changed`);
const markup = `<span class="giant-anim" data-logo-anim style="aspect-ratio: ${CROP.w} / ${CROP.h}"><span class="fl-word">${word}</span><span class="fl-phone">${phone}</span></span>`;
fs.writeFileSync('logo-anim.mjs', `// written by tools/logo-anim.mjs from the logo kit's horizontal animation; do not edit by hand\nexport const LOGO_ANIM = ${JSON.stringify(markup)};\n`);
console.log(`logo-anim.mjs: ${markup.length} chars, ${seen} animated parts set to their last values, view ${CROP.w} x ${CROP.h}`);
