// Each page's own head lines, after its title and description (parts.mjs head()): the canonical address, the
// language alternates (hu, en, and x-default on the Hungarian page), the share tags and the structured data.
// Structured data only says what the page shows (the doc's AEO point 4): no star ratings, no address, no profile
// links (sameAs) and no credential until the founder sends them.
import { C } from '../content.mjs';
import { esc } from '../parts.mjs';
import { ORIGIN, PAGES, byId, url, W } from './pages.mjs';

const OG = 'assets/og-image.jpg';
// the share image shows the logo and the Hungarian claim, so the English alt says what is on it
const OG_ALT = {
  hu: 'A SocialStream logója és a mondat: A social media meghalt. Az érdeklődés vette át a helyét.',
  en: 'The SocialStream logo and its line in Hungarian: A social media meghalt. (Social media is dead.)',
};
const LOCALE = { hu: 'hu_HU', en: 'en_GB' };
const plain = s => String(s).replace(/<[^>]+>/g, '');
const CLAIM = { hu: plain(C.claim.hu.join(' ')), en: plain(C.claim.en.join(' ')) };
const ORG = ORIGIN + '/#org', SITE = ORIGIN + '/#website';
// the film on the home page (the sizzle, live since 2026-11-16; 59.4 s, tools/hero.sh): what a search engine may show
const FILM = { date: '2026-11-16', duration: 'PT59.4S' };

// the page's breadcrumb, from the home page down to itself
export const trail = pg => { const t = []; for (let x = pg; x; x = x.parent && byId(x.parent)) t.unshift(x); return pg.id === 'home' ? t : [byId('home'), ...t]; };

function graph(pg, l) {
  const u = url(pg, l), home = byId('home');
  const org = { '@type': 'Organization', '@id': ORG, name: 'SocialStream', url: ORIGIN + '/', logo: { '@type': 'ImageObject', url: ORIGIN + '/icon-512.png', width: 512, height: 512 },
    email: 'hello@socialstream.hu', description: home.desc[l], slogan: CLAIM[l], foundingDate: '2022',
    founder: { '@type': 'Person', name: 'Olivér', jobTitle: C.team.people[0].role[l === 'en' ? 1 : 0] } };
  const site = { '@type': 'WebSite', '@id': SITE, url: ORIGIN + '/', name: 'SocialStream', inLanguage: ['hu', 'en'], publisher: { '@id': ORG } };
  // a case stays a WebPage (not an Article) until it has its story and a visible byline
  const type = { about: 'AboutPage', contact: 'ContactPage', faq: 'FAQPage', cases: 'CollectionPage' }[pg.type] || 'WebPage';
  const page = { '@type': type, '@id': u + '#webpage', url: u, name: plain(pg.title[l]), description: pg.desc[l], inLanguage: l, isPartOf: { '@id': SITE }, about: { '@id': ORG } };
  const nodes = [org, site, page];
  if (pg.id !== 'home') {
    page.breadcrumb = { '@id': u + '#breadcrumb' };
    nodes.push({ '@type': 'BreadcrumbList', '@id': u + '#breadcrumb', itemListElement: trail(pg).map((x, i) => ({ '@type': 'ListItem', position: i + 1, name: plain((x.crumb || W.home)[l]), item: url(x, l) })) });
  }
  if (pg.type === 'home') {
    const en = l === 'en' ? '-en' : '';
    page.video = { '@id': u + '#film' };
    nodes.push({ '@type': 'VideoObject', '@id': u + '#film', name: C.film.label[l], description: home.desc[l], inLanguage: l,
      thumbnailUrl: ORIGIN + '/assets/hero-poster.jpg', uploadDate: FILM.date, duration: FILM.duration, contentUrl: `${ORIGIN}/assets/hero-1080${en}.mp4` });
  }
  if (pg.type === 'service') {
    const s = pg.s, i = l === 'en' ? 1 : 0;
    nodes.push({ '@type': 'Service', '@id': u + '#service', name: s.k[i], serviceType: s.k[i], description: `${s.t[i]} ${s.p[i]}`, provider: { '@id': ORG }, url: u });
    page.mainEntity = { '@id': u + '#service' };
  }
  if (pg.type === 'about') {
    // the team as the page shows them: first name, role, and who they work for
    const people = C.team.people.map((m, i) => ({ '@type': 'Person', '@id': `${u}#person-${i + 1}`, name: m.name, jobTitle: m.role[l === 'en' ? 1 : 0], worksFor: { '@id': ORG } }));
    nodes.push(...people);
    org.founder = { '@id': people[0]['@id'] };
    page.mainEntity = { '@id': ORG };
  }
  if (pg.type === 'contact') {
    org.contactPoint = { '@type': 'ContactPoint', email: 'hello@socialstream.hu', contactType: 'customer service' };
  }
  if (pg.type === 'faq') {
    // every question on the page, as it is shown (an answer's links become plain words)
    page.mainEntity = pg.groups.flatMap(g => g.items).map(it => ({ '@type': 'Question', name: it.q[l], acceptedAnswer: { '@type': 'Answer', text: plain(it.a[l]) } }));
  }
  return { '@context': 'https://schema.org', '@graph': nodes };
}

export function seo(pg, l) {
  const u = url(pg, l), other = l === 'hu' ? 'en' : 'hu';
  return [
    `<link rel="canonical" href="${u}">`,
    `<link rel="alternate" hreflang="hu" href="${url(pg, 'hu')}">`,
    `<link rel="alternate" hreflang="en" href="${url(pg, 'en')}">`,
    `<link rel="alternate" hreflang="x-default" href="${url(pg, 'hu')}">`,
    '<meta property="og:type" content="website">',
    '<meta property="og:site_name" content="SocialStream">',
    `<meta property="og:locale" content="${LOCALE[l]}">`,
    `<meta property="og:locale:alternate" content="${LOCALE[other]}">`,
    `<meta property="og:url" content="${u}">`,
    `<meta property="og:title" content="${esc(plain(pg.title[l]))}">`,
    `<meta property="og:description" content="${esc(pg.desc[l])}">`,
    `<meta property="og:image" content="${ORIGIN}/${OG}">`,
    '<meta property="og:image:width" content="1200">',
    '<meta property="og:image:height" content="630">',
    `<meta property="og:image:alt" content="${esc(OG_ALT[l])}">`,
    '<meta name="twitter:card" content="summary_large_image">',
    `<script type="application/ld+json">${JSON.stringify(graph(pg, l)).replace(/</g, '\\u003c')}</script>`,
  ].join('\n');
}
export { PAGES };
