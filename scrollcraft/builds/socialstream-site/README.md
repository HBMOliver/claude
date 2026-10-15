# SocialStream: full site

Interactive, luxury-positioned site for SocialStream built around the core idea
"Social media is dead. Now it's interest media." Static: `index.html`,
`scrollcraft.css`, `scrollcraft.js`, `assets/`. No build step. HU default, EN via
the switch (remembered, or `?lang=en`).

Sections: layered hero with the live "Social → Interest media" strike; ticker;
I. philosophy and why the name stays ("A stream maradt..."); laws I-II; law III as
the grid-takeover peak; II. feed simulator (sample data, real ranking logic);
III. services as an interactive system ring; IV. results rail with case dialogs;
V. five-question interest test that feeds the audit form; who we work with / who
we don't; VI. founder and team; testimonials; VII. audit application form.

Content sources: client page `socialstream-erdeklodes-kora.html` (copy, numbers,
testimonials, team) and the "HB Marketing weboldal" Drive doc (fit lists). New
copy written for this build: hero line, the stream/name passage, simulator and
test texts, case "what we did" lines (kept to facts in the source).

To check before launch: the form opens the visitor's mail app (mailto) with the
answers filled in; connect it to a real form backend or CRM for production.
Case pages are linked as `case-*.html`, as on the live site. David and Lidi's
photos load from the live site's CDN, with an initial as fallback.
