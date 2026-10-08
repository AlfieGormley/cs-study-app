// Shared by the app (glossary.js) and the build (scripts/build.mjs).
// Acronyms such as REST or DAC match their exact case only, so "PA" (public address) and "Pa" (pascal) can coexist.
export const isAcronym = (alias) => /^[A-Z][A-Z0-9/+.-]{1,6}s?$/.test(alias);
export const aliasKey = (alias) => (isAcronym(alias) ? '=' + alias : alias.toLowerCase());
// Short aliases mean different things in different subjects (DAC, CV, ISR, dB), so a module term's acronyms,
// aliases of three characters or fewer and aliases containing symbols (I²S, m/s) only link inside its own subject.
// Core terms (glossary-data.js) and longer phrases link everywhere.
export const isScoped = (entry, alias) =>
  !!entry.subject && (isAcronym(alias) || [...alias].length <= 3 || /[^\p{L}\s'’-]/u.test(alias));
