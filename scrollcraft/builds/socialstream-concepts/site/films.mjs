// Where the live site's brand film comes from. Since v18 (2026-11-18) the site cuts of the sizzle (59.4 s, wide and
// upright, in Hungarian, English and Spanish) live in Pulse's Media Storage, the SocialStream sub-account's, and not in
// the site's ZIP: with a Spanish pair the six cuts outgrew Pulse's 60 MiB ZIP (v16 was 58.7 MiB with four). Pulse
// serves a stored file on the site's own domain at /m/<id>.mp4, with Range requests (so the film seeks) and a year's
// cache (Pulse CRM, server/services/media.js, sendMedia). The ZIP keeps the two posters.
//
// Each cut: the file in this folder that was uploaded (tools/hero.sh made it from the film's masters), its sha256, and
// the address Media Storage gave it. A cut with no address yet travels in the ZIP as before, at /assets/<file>.
// tools/site.mjs stops if a stored cut's file is no longer the one uploaded (it was encoded again: upload the new
// file, then change its sha256 and address here); lab/sitecheck.mjs fetches every address and compares the bytes.
//   w: the wide cut (hero-1080, 1920 x 1080), where Mix's opening fills a wide screen
//   v: the upright cut (hero-v-720, 720 x 1280), in Mix's card and on phones
import { ORIGINS } from './pages.mjs';

// a cut: its file here, that file's sha256, and its id in Media Storage (all six are in the folder "socialstream.hu
// website films" of the SocialStream sub-account, uploaded 2026-11-18 as socialstream-film-<lang>-<wide|upright>.mp4;
// no id: not stored, it travels in the ZIP). Deleting one there stops that film on the site.
// Pulse serves a stored file at /m/<id>.mp4 on every domain of the sub-account, so each cut is named on the domain of
// its language: the Spanish ones on socialstream.es since 2026-11-26 (checked there: a Range request answers 206).
const cut = (file, sha256 = null, id = null, host = ORIGINS.hu) => ({ file, sha256, url: id && `${host}/m/${id}.mp4` });
export const FILMS = {
  hu: {
    w: cut('assets/hero-1080.mp4', '436cfd6d20ca013f53476d20c6f49e86bc6c52ec1824838c651f662239ae4984', 'med_lf1pIO1lKXtKqA'),
    v: cut('assets/hero-v-720.mp4', 'c06393b3f846987387fc48f1234a7d067ba3a265f82d99e7cbd0383107c2b0ca', 'med_tCK7z1RisxoNiw'),
  },
  en: {
    w: cut('assets/hero-1080-en.mp4', '613fa968918a01778a25545d35375179f0812db6a5b0527fc1447fc7b2efa723', 'med_x63hmF_65H7XDA'),
    v: cut('assets/hero-v-720-en.mp4', '0dd0635b1cfcce8802b7a315b3b68237f21edbf9ff0f3730f870a9d6963ee4f0', 'med_2AUSm2GZuMdxpw'),
  },
  es: {
    w: cut('assets/hero-1080-es.mp4', '5a5c84fde8b2b920cf9d09c8c77b37176280181d468f9fd578dcc56e0cabd293', 'med_fSLq-WYiV4u8vQ', ORIGINS.es),
    v: cut('assets/hero-v-720-es.mp4', 'e507ffedf70388c40c0c2f217bd962790b2a3d0a495dd52317dcfdc96a48fa12', 'med_BwnDucjcd5Jgvw', ORIGINS.es),
  },
};
export const CUTS = ['w', 'v'];
// a stored cut's address, as Pulse makes it (newId('med') and FILE_RE in media.js)
export const STORED = /^https:\/\/socialstream\.(hu|es)\/m\/med_[\w-]{1,40}\.mp4$/;

// the address a page names for a cut: Media Storage's, or its own file in the ZIP
export const filmSrc = (l, k) => FILMS[l][k].url || '/' + FILMS[l][k].file;
// the same as a full address (the structured data's contentUrl)
export const filmUrl = (l, k) => FILMS[l][k].url || ORIGINS[l] + '/' + FILMS[l][k].file;
// the cuts of these languages that still travel in the ZIP
export const filmFiles = langs => langs.flatMap(l => CUTS.filter(k => !FILMS[l][k].url).map(k => FILMS[l][k].file));
