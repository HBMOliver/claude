// Each page's own head lines, after its title and description (parts.mjs head()): the canonical address, the
// language alternates (hu, en, es where the page has it, and x-default on Hungarian), the share tags and the
// structured data. Every word goes through site/es.mjs's word(), so a Spanish page says it in Spanish.
// Structured data only says what the page shows (the doc's AEO point 4): no star ratings, no address, no profile
// links (sameAs) and no credential until the founder sends them.
import { C } from '../content.mjs';
import { esc, pair, LANGS } from '../parts.mjs';
import { ORIGIN, ORIGINS, PAGES, byId, url, W } from './pages.mjs';
import { word } from './es.mjs';
import { filmUrl } from './films.mjs';

// the share image, each language its own since 2026-11-28 (tools/og.mjs): the logo and the claim as its home page says it
export const OG = { hu: 'assets/og-image.jpg', en: 'assets/og-image-en.jpg', es: 'assets/og-image-es.jpg' };
const OG_ALT = {
  hu: 'A SocialStream logója és a mondat: A social media meghalt. Az érdeklődés vette át a helyét.',
  en: 'The SocialStream logo and its line: Social media is dead. Interest has taken its place.',
  es: 'El logotipo de SocialStream y su frase: Las redes sociales han muerto. El interés ha ocupado su lugar.',
};
const LOCALE = { hu: 'hu_HU', en: 'en_GB', es: 'es_ES' };
const plain = s => String(s).replace(/<[^>]+>/g, '');
// the claim as a sentence in the page's language (the Spanish from its two English lines, each looked up)
const claim = l => plain((l === 'hu' ? C.claim.hu : l === 'en' ? C.claim.en : C.claim.en.map(x => word({ en: x }, l))).join(' '));
// one organisation (its home is socialstream.hu), and one website per domain: socialstream.hu in Hungarian and English,
// socialstream.es in Spanish (since 2026-11-26)
const ORG = ORIGIN + '/#org', SITE = l => ORIGINS[l] + '/#website';
// the film on the home page (the sizzle, 59.4 s, tools/hero.sh): what a search engine may show. Hungarian and English
// live since 2026-11-16; the Spanish cut since v18 (the Spanish page played the English one until then)
const FILM = { date: { hu: '2026-11-16', en: '2026-11-16', es: '2026-11-18' }, duration: 'PT59.4S' };
// the languages a page exists in, in this order
const langs = pg => LANGS.filter(x => pg.path[x]);

// the page's breadcrumb, from the home page down to itself
export const trail = pg => { const t = []; for (let x = pg; x; x = x.parent && byId(x.parent)) t.unshift(x); return pg.id === 'home' ? t : [byId('home'), ...t]; };

function graph(pg, l) {
  const u = url(pg, l), home = byId('home');
  const org = { '@type': 'Organization', '@id': ORG, name: 'SocialStream', url: ORIGIN + '/', logo: { '@type': 'ImageObject', url: ORIGIN + '/icon-512.png', width: 512, height: 512 },
    email: 'hello@socialstream.hu', description: word(home.desc, l), slogan: claim(l), foundingDate: '2022',
    // the founder as the same person the About page names (its #person-1), and what the agency does, its six services
    // as the site names them; the contact point is the address every page shows (2026-11-28, from the SEO/AEO check)
    founder: { '@type': 'Person', '@id': url(byId('about'), l) + '#person-1', name: 'Olivér', jobTitle: word(pair(C.team.people[0].role), l) },
    knowsAbout: PAGES.filter(x => x.type === 'service').map(x => plain(word(x.crumb, l))),
    contactPoint: { '@type': 'ContactPoint', email: 'hello@socialstream.hu', contactType: 'customer service' } };
  const site = { '@type': 'WebSite', '@id': SITE(l), url: ORIGINS[l] + '/', name: 'SocialStream', inLanguage: langs(home).filter(x => ORIGINS[x] === ORIGINS[l]), publisher: { '@id': ORG } };
  // a case stays a WebPage (not an Article) until it has its story and a visible byline
  const type = { about: 'AboutPage', contact: 'ContactPage', faq: 'FAQPage', cases: 'CollectionPage', audiences: 'CollectionPage' }[pg.type] || 'WebPage';
  const page = { '@type': type, '@id': u + '#webpage', url: u, name: plain(word(pg.title, l)), description: word(pg.desc, l), inLanguage: l, isPartOf: { '@id': SITE(l) }, about: { '@id': ORG } };
  const nodes = [org, site, page];
  if (pg.id !== 'home') {
    page.breadcrumb = { '@id': u + '#breadcrumb' };
    nodes.push({ '@type': 'BreadcrumbList', '@id': u + '#breadcrumb', itemListElement: trail(pg).map((x, i) => ({ '@type': 'ListItem', position: i + 1, name: plain(word(x.crumb || W.home, l)), item: url(x, l) })) });
  }
  if (pg.type === 'home') {
    // each language's own cut of the film, the wide one (site/films.mjs: on Pulse's Media Storage)
    page.video = { '@id': u + '#film' };
    nodes.push({ '@type': 'VideoObject', '@id': u + '#film', name: word(C.film.label, l), description: word(home.desc, l), inLanguage: l,
      thumbnailUrl: ORIGINS[l] + '/assets/hero-poster.jpg', uploadDate: FILM.date[l], duration: FILM.duration, contentUrl: filmUrl(l, 'w') });
  }
  if (pg.type === 'service') {
    const s = pg.s, k = word(pair(s.k), l);
    nodes.push({ '@type': 'Service', '@id': u + '#service', name: k, serviceType: k, description: `${word(pair(s.t), l)} ${word(pair(s.p), l)}`, provider: { '@id': ORG }, url: u });
    page.mainEntity = { '@id': u + '#service' };
  }
  if (pg.type === 'about') {
    // the team as the page shows them: first name, role, and who they work for
    const people = C.team.people.map((m, i) => ({ '@type': 'Person', '@id': `${u}#person-${i + 1}`, name: m.name, jobTitle: word(pair(m.role), l), worksFor: { '@id': ORG } }));
    nodes.push(...people);
    org.founder = { '@id': people[0]['@id'] };
    page.mainEntity = { '@id': ORG };
  }
  if (pg.type === 'explainer') {
    // the term and its definition, as the first screen says it (site/pages.mjs DEF, the founder's choice)
    nodes.push({ '@type': 'DefinedTerm', '@id': u + '#term', name: plain(word(pg.h1k, l)), description: plain(word(pg.lead, l)), url: u });
    page.about = page.mainEntity = { '@id': u + '#term' };
  }
  if (pg.type === 'hub' || pg.type === 'cases') {
    // the services, or the case studies, the page lists, each with its page (2026-11-28, as the fields' hub has it)
    page.mainEntity = { '@type': 'ItemList', itemListElement: PAGES.filter(x => x.type === (pg.type === 'hub' ? 'service' : 'case')).map((x, i) => ({ '@type': 'ListItem', position: i + 1, name: plain(word(x.crumb, l)), url: url(x, l) })) };
  }
  if (pg.type === 'audiences') {
    // the fields the page lists, each with its page
    page.mainEntity = { '@type': 'ItemList', itemListElement: PAGES.filter(x => x.type === 'industry').map((x, i) => ({ '@type': 'ListItem', position: i + 1, name: plain(word(x.crumb, l)), url: url(x, l) })) };
  }
  if (pg.type === 'industry') {
    // who the page is for, and the services it shows (each described on its own page)
    page.audience = { '@type': 'BusinessAudience', audienceType: plain(word(pg.crumb, l)) };
    page.mentions = pg.uses.map(id => ({ '@id': url(byId(id), l) + '#service' }));
  }
  if (pg.type === 'faq') {
    // every question on the page, as it is shown (an answer's links become plain words)
    page.mainEntity = pg.groups.flatMap(g => g.items).map(it => ({ '@type': 'Question', name: word(it.q, l), acceptedAnswer: { '@type': 'Answer', text: plain(word(it.a, l)) } }));
  }
  return { '@context': 'https://schema.org', '@graph': nodes };
}

export function seo(pg, l) {
  const u = url(pg, l), ls = langs(pg);
  return [
    `<link rel="canonical" href="${u}">`,
    ...ls.map(x => `<link rel="alternate" hreflang="${x}" href="${url(pg, x)}">`),
    `<link rel="alternate" hreflang="x-default" href="${url(pg, 'hu')}">`,
    '<meta property="og:type" content="website">',
    '<meta property="og:site_name" content="SocialStream">',
    `<meta property="og:locale" content="${LOCALE[l]}">`,
    ...ls.filter(x => x !== l).map(x => `<meta property="og:locale:alternate" content="${LOCALE[x]}">`),
    `<meta property="og:url" content="${u}">`,
    `<meta property="og:title" content="${esc(plain(word(pg.title, l)))}">`,
    `<meta property="og:description" content="${esc(word(pg.desc, l))}">`,
    `<meta property="og:image" content="${ORIGINS[l]}/${OG[l]}">`,
    '<meta property="og:image:width" content="1200">',
    '<meta property="og:image:height" content="630">',
    `<meta property="og:image:alt" content="${esc(OG_ALT[l])}">`,
    '<meta name="twitter:card" content="summary_large_image">',
    `<script type="application/ld+json">${JSON.stringify(graph(pg, l)).replace(/</g, '\\u003c')}</script>`,
  ].join('\n');
}
export { PAGES };
