import { glossary as core } from './glossary-data.js';
import moduleTerms from './glossary-terms.js';
import { aliasKey, fallsBack } from './glossary-rules.js';
// Core terms plus the verified per-module terms the build collects from content/**/glossary.json.
export const glossary = [...core, ...moduleTerms];

const esc = (text) => String(text).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const escapedCharacters = { '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'" };
// Decode once for lookup only; keep the displayed HTML escaped.
const unescapeText = (text) => text.replace(/&(?:amp|lt|gt|quot|#39);/g, (entity) => escapedCharacters[entity]);
const byId = new Map();
const coreMap = new Map();         // alias key -> { entry, alias }: core terms, every subject
const bySubject = new Map();       // subject id -> Map(alias key -> { entry, alias })
const fallback = new Map();        // longer module aliases, first in curriculum order, for other subjects
for (const entry of glossary) {
  if (!/^[a-z0-9-]+$/.test(entry.id) || byId.has(entry.id) || !entry.term || !entry.definition || !entry.category) throw new Error('Invalid glossary entry: ' + entry.id);
  if (entry.source && !/^https:\/\//.test(entry.source)) throw new Error('Invalid glossary source: ' + entry.id);
  byId.set(entry.id, entry);
  for (const alias of [entry.term, ...entry.aliases]) {
    const key = aliasKey(alias);
    const map = entry.subject ? (bySubject.get(entry.subject) ?? bySubject.set(entry.subject, new Map()).get(entry.subject)) : coreMap;
    if (map.has(key) && map.get(key).entry.id !== entry.id) throw new Error('Ambiguous glossary alias: ' + alias);
    map.set(key, { entry, alias });
    if (fallsBack(entry, alias) && !fallback.has(key)) fallback.set(key, { entry, alias });
  }
}
const lookups = (subject) => [bySubject.get(subject), coreMap, fallback].filter(Boolean);
// Match only aliases sharing the next word. A single giant expression containing
// every glossary phrase takes seconds to compile on a phone's first lesson.
const firstToken = /^[\p{L}\p{N}_]+|[^\p{L}\p{N}_]/u;
const candidateStarts = /(?<![\p{L}\p{N}_])(?<!\p{N}-)(?:[\p{L}\p{N}_]+|[^\p{L}\p{N}_])/gu;
const wordCharacter = /[\p{L}\p{N}_]/u;
const matchers = new Map();
const matcherFor = (subject) => {
  if (!matchers.has(subject)) {
    const buckets = new Map();
    const words = new Set();
    for (const map of lookups(subject)) {
      for (const { alias } of map.values()) {
        const word = alias.toLowerCase();
        if (words.has(word)) continue;
        words.add(word);
        const key = word.match(firstToken)?.[0];
        if (!key) continue;
        if (!buckets.has(key)) buckets.set(key, []);
        buckets.get(key).push(word);
      }
    }
    for (const bucket of buckets.values()) bucket.sort((a, b) => b.length - a.length);
    matchers.set(subject, buckets);
  }
  return matchers.get(subject);
};
export const getTerm = (id) => byId.get(id);
export function exactTerm(text, subject = '') {
  for (const map of lookups(subject))
    for (const key of ['=' + text, text.toLowerCase()]) {
      const match = map.get(key);
      if (match) return match.entry;
    }
  return null;
}
const termButton = (entry, label) => `<button type="button" class="technical-term" data-term="${entry.id}" aria-haspopup="dialog" aria-expanded="false" aria-controls="term-popover" aria-label="Define ${esc(entry.term)}">${label}</button>`;

// Called only on escaped, known-tag inline HTML from our Markdown renderer.
// Protected tags keep URLs, existing controls and executable examples intact.
// With a `seen` set, each term is linked only the first time it appears.
export function linkTerms(html, { interactive = true, terms = true, seen = null, subject = '' } = {}) {
  if (!interactive || !terms) return html;
  const first = (entry) => !seen || (!seen.has(entry.id) && seen.add(entry.id));
  let protectedDepth = 0;
  const parts = html.split(/(<[^>]*>)/g);
  return parts.map((part, index) => {
    if (!protectedDepth && part === '<code>' && parts[index+2] === '</code>') {
      const entry = exactTerm(unescapeText(parts[index+1]), subject);
      if (entry && first(entry)) {
        const label = `<code>${parts[index+1]}</code>`;
        parts[index+1] = ''; parts[index+2] = '';
        return termButton(entry, label);
      }
    }
    if (part.startsWith('<')) {
      const tag = part.match(/^<(\/)?(a|code|button|svg|pre)\b/i);
      if (tag) protectedDepth += tag[1] ? -1 : 1;
      return part;
    }
    if (protectedDepth) return part;
    const buckets = matcherFor(subject);
    let out = '', end = 0;
    for (const candidate of part.matchAll(candidateStarts)) {
      const start = candidate.index;
      if (start < end) continue;
      const aliases = buckets.get(candidate[0].toLowerCase());
      if (!aliases) continue;
      const alias = aliases.find((word) =>
        part.slice(start, start + word.length).toLowerCase() === word &&
        !wordCharacter.test(String.fromCodePoint(part.codePointAt(start + word.length) ?? 0)));
      if (!alias) continue;
      const label = part.slice(start, start + alias.length);
      const entry = exactTerm(label, subject);
      out += part.slice(end, start) + (entry && first(entry) ? termButton(entry, label) : label);
      end = start + label.length;
    }
    return out + part.slice(end);
  }).join('');
}
const termOrder = new Intl.Collator('en', { sensitivity: 'base' });
let dictionaryOrder;
const searchText = new WeakMap();
export function searchGlossary(query = '') {
  const words = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  dictionaryOrder ??= [...glossary].sort((a, b) => termOrder.compare(a.term, b.term));
  if (!words.length) return [...dictionaryOrder];
  return dictionaryOrder.filter((entry) => {
    if (!searchText.has(entry)) searchText.set(entry, `${entry.term} ${entry.aliases.join(' ')} ${entry.definition} ${entry.category}`.toLowerCase());
    const text = searchText.get(entry);
    return words.every((word) => text.includes(word));
  });
}

export function installGlossary() {
  const panel = document.createElement('section');
  panel.id = 'term-popover'; panel.className = 'term-popover'; panel.hidden = true;
  panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Technical term definition');
  panel.setAttribute('aria-labelledby', 'term-popover-title');
  panel.setAttribute('aria-describedby', 'term-popover-definition');
  document.body.append(panel);
  let anchor = null, frame;
  const close = (restore = false) => {
    if (!anchor) return;
    const previous = anchor;
    previous.setAttribute('aria-expanded','false');
    panel.hidden = true; anchor = null; cancelAnimationFrame(frame);
    if (restore && previous.isConnected) previous.focus({preventScroll:true});
  };
  const position = () => {
    if (!anchor) return;
    if (!anchor.isConnected) { close(); return; }
    const viewport = window.visualViewport;
    const left = viewport?.offsetLeft || 0, top = viewport?.offsetTop || 0;
    const width = viewport?.width || innerWidth, height = viewport?.height || innerHeight;
    const rect = anchor.getBoundingClientRect();
    if (rect.bottom < top || rect.top > top+height) { close(panel.contains(document.activeElement)); return; }
    panel.style.width = `${Math.min(350,width-24)}px`;
    panel.style.maxHeight = `${Math.max(80,height-24)}px`;
    const bounds = panel.getBoundingClientRect();
    const x = Math.max(left+12,Math.min(rect.left,left+width-bounds.width-12));
    const below = rect.bottom+10;
    const y = below+bounds.height <= top+height-12 ? below : Math.max(top+12,rect.top-bounds.height-10);
    panel.style.left = `${x}px`; panel.style.top = `${y}px`;
  };
  const schedulePosition = () => { if (anchor) { cancelAnimationFrame(frame); frame = requestAnimationFrame(position); } };
  const open = (button) => {
    const entry = getTerm(button.dataset.term);
    if (!entry) return;
    if (anchor === button) { close(true); return; }
    close(); anchor = button;
    panel.innerHTML = `<header><div><span class="term-category">${esc(entry.category)}</span><h2 id="term-popover-title">${esc(entry.term)}</h2></div><button type="button" class="term-close" aria-label="Close definition">✕</button></header><p id="term-popover-definition">${esc(entry.definition)}</p>${entry.example ? `<p class="term-example"><b>Example</b> ${esc(entry.example)}</p>` : ''}<footer><a href="#/dictionary?q=${encodeURIComponent(entry.term)}">Open dictionary ↗</a>${entry.source ? `<a href="${esc(entry.source)}" target="_blank" rel="noopener">Source ↗</a>` : ''}</footer>`;
    button.setAttribute('aria-expanded','true'); panel.hidden = false; position();
    panel.querySelector('.term-close').onclick = () => close(true);
    panel.querySelector('.term-close').focus({preventScroll:true});
  };
  document.addEventListener('click', (event) => {
    const button = event.target.closest('[data-term]');
    if (button) open(button);
    else if (!panel.contains(event.target)) close();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && anchor) { event.preventDefault(); event.stopPropagation(); close(true); }
  });
  document.addEventListener('focusin', (event) => { if (anchor && event.target !== anchor && !panel.contains(event.target)) close(); });
  addEventListener('hashchange', () => close());
  addEventListener('resize', schedulePosition);
  document.addEventListener('scroll', schedulePosition, true);
  window.visualViewport?.addEventListener('resize', schedulePosition);
  window.visualViewport?.addEventListener('scroll', schedulePosition);
  new MutationObserver(() => { if (anchor && !anchor.isConnected) close(); }).observe(document.querySelector('#view'), {childList:true,subtree:true});
  return close;
}
