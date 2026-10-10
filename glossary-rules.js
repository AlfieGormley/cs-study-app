// Shared by the app (glossary.js) and the build (scripts/build.mjs).
// Acronyms and all-caps names (REST, DAC, SETTINGS, PRIORITY) match their exact case only, so "PA" (public address) and "Pa" (pascal) can coexist.
// So do single capital letters in any script (Δ, Σ, Θ, C), so "Δ" (maximum degree) never captures "δ" (a transition function).
// All-caps phrases (NOT IN, MUST NOT, GROUP BY) match exact case too, so they never capture everyday "not in" or "must not".
const isCapsWord = (alias) => /^(?:\p{Lu}|\p{Lu}[\p{Lu}\p{N}/+._-]{1,15}s?)$/u.test(alias);
const isCapsPhrase = (alias) => /^\p{Lu}[\p{Lu}\p{N}/+._-]*(?: [\p{Lu}\p{N}][\p{Lu}\p{N}/+._-]*)+$/u.test(alias);
// Short mixed-case names (reST, eTLD, iOS) match exact case too, so "reST" never captures "rest".
const isShortMixedCase = (alias) => /^\S{2,5}$/u.test(alias) && /\p{Ll}\p{Lu}/u.test(alias);
export const isAcronym = (alias) => isCapsWord(alias) || isCapsPhrase(alias) || isShortMixedCase(alias);
export const aliasKey = (alias) => (isAcronym(alias) ? '=' + alias : alias.toLowerCase());
// Lookup order inside a subject: that subject's module terms (which may shadow a core term), then core terms
// (glossary-data.js), then other
// subjects' terms as a fallback (earliest module in curriculum order wins). So "jitter" or "patch" can mean one
// thing in System Design and another in Synth Building. Short aliases mean different things in different subjects
// (DAC, CV, ISR, dB), so acronyms, aliases of three characters or fewer and aliases containing symbols (I²S, m/s)
// never act as a fallback outside their own subject, and neither do single words (see fallsBack).
// A single word ("depth", "leaf", "patch") means different things in different subjects, so only multi-word or
// hyphenated aliases ("tree depth", "low-pass filter") act as a fallback in other subjects.
export const fallsBack = (entry, alias) => !!entry.subject && !isScoped(entry, alias) && /[\s-]/.test(alias.trim());
export const isScoped = (entry, alias) =>
  !!entry.subject && (isCapsWord(alias) || [...alias].length <= 3 || /[^\p{L}\s'’-]/u.test(alias));
