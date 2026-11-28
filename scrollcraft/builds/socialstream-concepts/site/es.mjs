// The Spanish pages (the founder, 2026-11-18: "build Spanish", for Tenerife): under socialstream.hu/es/ until v20, at
// the root of their own domain, socialstream.es, since 2026-11-26 (site/pages.mjs ORIGINS, DOMAINS). The site's words
// stay { hu, en } pairs in content.mjs and site/pages.mjs; the Spanish is looked up here by the English text, so a
// change to an English sentence shows up as a missing Spanish one and stops the build (tools/site.mjs), never as a
// page that silently falls back to Hungarian or English. The words live in es-words.mjs.
// Spanish pages show the English page's figures in euros (written the Spanish way, "216K €", "0,29 €") and play the
// film's Spanish cut (since v18, site/films.mjs).
import { WORDS } from './es-words.mjs';

// LIVE: the Spanish pages are part of the site; SS_ES=1 builds them anyway, SS_ES_TODO=1 lists what is missing
export const LIVE = true;
export const ON = LIVE || !!process.env.SS_ES || !!process.env.SS_ES_TODO;
export const TODO = !!process.env.SS_ES_TODO;

export const ES = new Map();
for (const [en, es] of WORDS) {
  if (ES.has(en)) throw new Error('es-words.mjs: the English "' + en.slice(0, 60) + '" is there twice');
  ES.set(en, es);
}

// every page's Spanish address, by its id (site/pages.mjs); the results link of the menu goes to the home page's part
export const SLUGS = {
  home: '/',
  services: '/servicios/',
  'svc-video': '/servicios/produccion-de-video/',
  'svc-social': '/servicios/gestion-de-redes-sociales/',
  'svc-ads': '/servicios/publicidad-de-pago/',
  'svc-web': '/servicios/paginas-web-y-landing-pages/',
  'svc-auto': '/servicios/automatizacion-y-email/',
  'svc-strat': '/servicios/estrategia-de-crecimiento/',
  cases: '/casos-de-exito/',
  'case-door': '/casos-de-exito/tienda-online-de-puertas/',
  'case-hall': '/casos-de-exito/constructora-de-naves-industriales/',
  'case-watch': '/casos-de-exito/tienda-online-de-relojes/',
  'case-webinar': '/casos-de-exito/webinar-sanitario/',
  'case-flyx': '/casos-de-exito/flyx-tenerife/',
  'case-enzo': '/casos-de-exito/prof-enzo/',
  'interest-media': '/que-es-interest-media/',
  audiences: '/con-quien-trabajamos/',
  'ind-shop': '/con-quien-trabajamos/tiendas-online/',
  'ind-b2b': '/con-quien-trabajamos/empresas-b2b/',
  'ind-events': '/con-quien-trabajamos/webinars-y-eventos/',
  'ind-local': '/con-quien-trabajamos/servicios-locales/',
  'ind-health': '/con-quien-trabajamos/salud-y-bienestar/',
  'ind-tourism': '/con-quien-trabajamos/turismo-y-experiencias/',
  about: '/sobre-nosotros/',
  audit: '/auditoria-gratuita/',
  faq: '/preguntas-frecuentes/',
  contact: '/contacto/',
};

// what a Spanish page could not find, with the page it was on (tools/site.mjs names the page before rendering it)
export const MISSES = new Map();
let PAGE = '';
export const onPage = name => { PAGE = name; };
const miss = en => { const at = MISSES.get(en) || new Set(); at.add(PAGE); MISSES.set(en, at); return en; };

// the word of a { hu, en } pair (or one with its own es) in a page's language
export const word = (p, l) => {
  if (l !== 'es') return p[l];
  if (p.es != null) return p.es;
  const en = p.en;
  if (en == null) return miss(String(p.hu));
  const es = ES.get(en);
  return es ? es : miss(en);
};
