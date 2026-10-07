import { glossary } from './glossary-data.js';
export { glossary };

const esc = (text) => String(text).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const regexEscape = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const byId = new Map();
const aliases = new Map();
for (const entry of glossary) {
  if (!/^[a-z0-9-]+$/.test(entry.id) || byId.has(entry.id) || !entry.term || !entry.definition || !entry.category) throw new Error('Invalid glossary entry: ' + entry.id);
  if (entry.source && !/^https:\/\//.test(entry.source)) throw new Error('Invalid glossary source: ' + entry.id);
  byId.set(entry.id, entry);
  for (const alias of [entry.term, ...entry.aliases]) {
    const key = alias.toLowerCase();
    if (aliases.has(key) && aliases.get(key).entry.id !== entry.id) throw new Error('Ambiguous glossary alias: ' + alias);
    aliases.set(key, { entry, alias, exactCase: /^[A-Z][A-Z0-9/+.-]{1,6}s?$/.test(alias) });
  }
}
const pattern = new RegExp(`(?<![\\p{L}\\p{N}_])(?:${[...aliases.keys()].sort((a,b)=>b.length-a.length).map(regexEscape).join('|')})(?![\\p{L}\\p{N}_])`, 'giu');
export const getTerm = (id) => byId.get(id);
export function exactTerm(text) {
  const match = aliases.get(text.toLowerCase());
  return match && (!match.exactCase || match.alias === text) ? match.entry : null;
}
const termButton = (entry, label) => `<button type="button" class="technical-term" data-term="${entry.id}" aria-haspopup="dialog" aria-expanded="false" aria-controls="term-popover" aria-label="Define ${esc(entry.term)}">${label}</button>`;

// Called only on escaped, known-tag inline HTML from our Markdown renderer.
// Protected tags keep URLs, existing controls and executable examples intact.
export function linkTerms(html, { interactive = true, terms = true } = {}) {
  if (!interactive || !terms) return html;
  let protectedDepth = 0;
  const parts = html.split(/(<[^>]*>)/g);
  return parts.map((part, index) => {
    if (!protectedDepth && part === '<code>' && parts[index+2] === '</code>') {
      const entry = exactTerm(parts[index+1]);
      if (entry) {
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
    return part.replace(pattern, (match) => {
      const entry = exactTerm(match);
      return entry ? termButton(entry, match) : match;
    });
  }).join('');
}
export function searchGlossary(query = '') {
  const words = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return glossary.filter((entry) => words.every((word) => `${entry.term} ${entry.aliases.join(' ')} ${entry.definition} ${entry.category}`.toLowerCase().includes(word)))
    .sort((a,b) => a.term.localeCompare(b.term, 'en', { sensitivity:'base' }));
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
