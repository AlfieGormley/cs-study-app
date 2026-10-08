// Shared by the app (glossary.js) and the build (scripts/build.mjs).
// Acronyms such as REST or DAC match their exact case only, so "PA" (public address) and "Pa" (pascal) can coexist.
export const isAcronym = (alias) => /^[A-Z][A-Z0-9/+.-]{1,6}s?$/.test(alias);
export const aliasKey = (alias) => (isAcronym(alias) ? '=' + alias : alias.toLowerCase());
// Lookup order inside a subject: that subject's module terms, then core terms (glossary-data.js), then other
// subjects' terms as a fallback (earliest module in curriculum order wins). So "jitter" or "patch" can mean one
// thing in System Design and another in Synth Building. Short aliases mean different things in different subjects
// (DAC, CV, ISR, dB), so acronyms, aliases of three characters or fewer and aliases containing symbols (I²S, m/s)
// never act as a fallback outside their own subject.
export const isScoped = (entry, alias) =>
  !!entry.subject && (isAcronym(alias) || [...alias].length <= 3 || /[^\p{L}\s'’-]/u.test(alias));
