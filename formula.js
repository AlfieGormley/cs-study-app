// Formula blocks: an equation plus a definition of every symbol in it.
// Authoring format (see .claude/skills/writing-formulas/SKILL.md):
//
//   ```formula
//   f = c / (2πa)
//   where
//   f: the frequency where the cone starts to beam, in hertz (Hz)
//   c: the speed of sound in air, about 343 metres per second (m/s)
//   π: pi, the circle constant, about 3.14159
//   a: the radius of the cone, in metres (m)
//   In words: a bigger cone starts beaming at a lower frequency.
//   ```
//
// Every symbol, unit and function name used in the equation lines must be defined after `where`, and an
// "In words:" line must say what the formula means. The build rejects blocks missing either.

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Greek letters are always single symbols, so "2πa" reads as 2, π, a.
// Named Latin runs stay whole ("RTT", "log", "Hz"). Defined single-letter variables
// can also form an implicit product (RC) when the run is not itself a named quantity.
const SUB = String.raw`(?:_(?:\{[^}]*\}|[A-Za-z0-9Ͱ-Ͽ]+))?`;
const TOKEN = new RegExp(String.raw`(?:[Ͱ-Ͽµ]|[A-Za-z][A-Za-z0-9]*)['′]*` + SUB, 'gu');

// Words that join or qualify mathematics ("for all n ≥ 1", "as n → ∞", "n is even") are not symbols and need
// no definition. Any other word in an equation is a variable name and must be defined.
export const CONNECTIVES = new Set(('for all some each every any as so when whenever if iff then else otherwise means gives ' +
  'and or not is are be such that where with to of at in on by until since let per').split(' '));

export function parseFormula(source) {
  const lines = String(source).replace(/\r\n?/g, '\n').split('\n');
  const split = lines.findIndex((l) => /^\s*where:?\s*$/i.test(l));
  const eq = (split < 0 ? lines : lines.slice(0, split)).filter((l) => l.trim());
  const defs = [];
  let words = '';
  for (const raw of split < 0 ? [] : lines.slice(split + 1)) {
    const line = raw.trim();
    if (!line) continue;
    const w = line.match(/^in words:\s*(.+)$/i);
    if (w) { words = w[1]; continue; }
    const i = line.indexOf(': ');
    if (i <= 0) { defs.push({ key: line, text: '', bad: true }); continue; }
    defs.push({ key: line.slice(0, i).trim(), text: line.slice(i + 2).trim() });
  }
  return { eq, defs, words, hasWhere: split >= 0 };
}

// Symbols used in a piece of formula text. Numbers (including 1e-3, 0x1F) and quoted strings are not symbols.
// A quote straight after a letter, digit or bracket is a prime mark (A', f'(x)), not the start of a string.
function productSymbols(token, defined) {
  if (!defined || defined.has(token) || CONNECTIVES.has(token) || !/^[A-Za-z]{2,}$/.test(token)) return [token];
  const factors = [...token];
  return factors.every((factor) => defined.has(factor)) ? factors : [token];
}

export function symbols(text, defined) {
  const stripped = String(text)
    .replace(/"[^"]*"|(?<![\p{L}\p{N}_)\]′'])'[^'\n]*'(?![′'])/gu, ' ')
    .replace(/(?<![\w{])(?:0x[0-9a-f]+|0b[01]+|\d+(?:\.\d+)?(?:e[+-]?\d+)?)/gi, ' ');
  return [...new Set((stripped.match(TOKEN) || []).flatMap((t) => productSymbols(t.replace(/_\{([^}]*)\}$/, '_$1'), defined)))];
}

function bracketProblems(text) {
  const stripped = text.replace(/"[^"]*"|(?<![\p{L}\p{N}_)\]′'])'[^'\n]*'(?![′'])/gu, ' ');
  const pairs = { '(': ')', '[': ']', '{': '}', '⌈': '⌉', '⌊': '⌋' };
  const stack = [];
  for (let i = 0; i < stripped.length; i++) {
    const c = stripped[i];
    if (pairs[c]) stack.push({ c, i });
    else if (Object.values(pairs).includes(c)) {
      const open = stack.pop();
      // Half-open intervals and substring ranges intentionally mix [ and ).
      const interval = open && /,|\.\./.test(stripped.slice(open.i + 1, i))
        && ((open.c === '[' && c === ')') || (open.c === '(' && c === ']'
          && !/[\p{L}\p{N}_]/u.test(stripped[open.i - 1] ?? '')));
      if (!open || (pairs[open.c] !== c && !interval)) return [`unmatched or incorrectly paired bracket "${c}"`];
    }
  }
  return stack.length ? [`unclosed bracket "${stack[stack.length - 1].c}" in equation`] : [];
}

// Problems with a formula block (empty when every symbol is defined).
export function checkFormula(source) {
  const { eq, defs, words, hasWhere } = parseFormula(source);
  const p = [];
  if (!eq.length) p.push('formula block has no equation line');
  p.push(...bracketProblems(eq.join('\n')));
  if (!hasWhere) return [...p, 'formula block needs a "where" line followed by a definition of every symbol'];
  if (!defs.length) p.push('formula block defines no symbols');
  if (!words) p.push(`formula block needs an "In words:" line saying what "${eq[0] ?? ''}" means in plain English`);
  for (const d of defs) if (d.bad || !d.text) p.push(`definition "${d.key}" must be written "symbol: meaning"`);
  const defined = new Set(defs.flatMap((d) => symbols(d.key)));
  const missing = symbols(eq.join('\n'), defined).filter((s) => !defined.has(s) && !CONNECTIVES.has(s));
  const connectiveDefs = defs.filter((d) => CONNECTIVES.has(d.key.trim()));
  if (connectiveDefs.length) p.push(`"${connectiveDefs[0].key}" is a connective word, not a symbol: remove its definition`);
  if (missing.length) p.push(`undefined symbol(s) ${missing.map((s) => `"${s}"`).join(', ')} in "${eq[0]}"`);
  return p;
}

function groupAt(text, start) {
  const open = text[start], close = { '{': '}', '(': ')', '[': ']', '⌈': '⌉', '⌊': '⌋' }[open];
  if (close) {
    let depth = 1, end = start + 1;
    for (; end < text.length; end++) {
      if (text[end] === open) depth++;
      else if (text[end] === close && !--depth) break;
    }
    if (depth) return null;
    return { body: text.slice(start, end + 1), end: end + 1 };
  }
  return null;
}

function rootAt(text, start) {
  if (text[start] !== '√') return null;
  const group = groupAt(text, start + 1);
  const atom = text.slice(start + 1).match(/^(?:\d+(?:\.\d+)?|[A-Za-z][A-Za-z0-9]*|\p{L})/u);
  const end = group?.end ?? (atom ? start + 1 + atom[0].length : 0);
  return end ? { body: text.slice(start, end), end } : null;
}

function scriptAt(text, i) {
  const marker = text[i];
  let start = i + 1;
  while (/\s/.test(text[start] ?? '') && start < text.length) start++;
  const group = groupAt(text, start);
  let value = (text[start] === '{' || marker === '^') ? group : null;
  if (value && text[start] === '{') value = { ...value, body: value.body.slice(1, -1) };
  const pattern = marker === '_'
    ? /^[A-Za-z0-9Ͱ-Ͽµ]+/
    : /^[+−-]?(?:\d+(?:\.\d+)?|[A-Za-z][A-Za-z0-9]*|\p{L})(?:_(?:\{[^}]*\}|[A-Za-z0-9Ͱ-Ͽµ]+))?/u;
  const match = text.slice(start).match(pattern);
  value ??= marker === '^' ? rootAt(text, start) : null;
  value ??= match ? { body: match[0], end: start + match[0].length } : null;
  if (value && marker === '^') {
    let next = value.end;
    while (/\s/.test(text[next] ?? '') && next < text.length) next++;
    // Powers associate to the right: a^b^c is a^(b^c), not (a^b)^c.
    const exponent = text[next] === '^' ? scriptAt(text, next) : null;
    if (exponent) value = { body: value.body + '^{' + exponent.body + '}', end: exponent.end };
  }
  return value;
}

// Format from source tokens rather than modifying generated HTML. Script groups
// stay intact, and simplifying a product never changes the scope of a division.
function mathHtml(text, context, compact = true, scopes = [false]) {
  const { defined, explicit, named, keepProducts } = context;
  const tokens = [];
  for (let i = 0; i < text.length;) {
    const c = text[i];
    if (c === '^' || c === '_') {
      const script = scriptAt(text, i);
      let before = tokens.length - 1;
      while (tokens[before]?.kind === 'space') before--;
      const base = tokens[before];
      if (script && base && ['symbol', 'number', 'close', 'bar', 'root'].includes(base.kind)) {
        const tag = c === '^' ? 'sup' : 'sub';
        if (c === '^' && base.kind === 'root') base.html = `(${base.html})`;
        base.html += `<${tag}>${mathHtml(script.body, context, compact)}</${tag}>`;
        for (let j = before + 1; j < tokens.length; j++) tokens[j].html = '';
        i = script.end;
        continue;
      }
    }
    const tail = text.slice(i);
    const quote = c === '"' ? tail.match(/^"[^"]*"/) : c === "'" ? tail.match(/^'[^'\n]*'/) : null;
    const space = tail.match(/^\s+/);
    const number = tail.match(/^(?:0x[0-9a-f]+|0b[01]+|\d+(?:\.\d+)?(?:e[+-]?\d+)?)/i);
    const word = tail.match(/^(?:[Ͱ-Ͽµ]|[A-Za-z][A-Za-z0-9]*|\p{L})['′]*/u);
    const root = rootAt(text, i);
    if (quote) tokens.push({ kind: 'literal', html: esc(quote[0]) });
    else if (space) tokens.push({ kind: 'space', html: space[0] });
    else if (number) tokens.push({ kind: 'number', base: number[0], html: esc(number[0]), simple: !/[a-z]/i.test(number[0]) });
    else if (root) tokens.push({ kind: 'root', html: '√' + mathHtml(root.body.slice(1), context, compact), simple: true });
    else if (word) {
      const factors = productSymbols(word[0], defined);
      const simple = factors.every((factor) => /^[A-Za-zͰ-Ͽµ]['′]*$/.test(factor) && !explicit.has(factor));
      const html = factors.map((factor) => /^[A-Za-z]['′]*$/.test(factor) ? `<i>${esc(factor)}</i>` : esc(factor)).join('');
      tokens.push({ kind: CONNECTIVES.has(word[0]) ? 'break' : 'symbol', base: word[0], html, simple,
        fn: /^(?:sin|cos|tan|asin|acos|atan|log|ln|exp|max|min|floor|ceil|abs)$/.test(word[0]) });
    } else tokens.push({ kind: '([{⌈⌊'.includes(c) ? 'open' : ')]}⌉⌋'.includes(c) ? 'close' : '×·'.includes(c) ? 'multiply' : c === '/' ? 'divide' : c === '|' ? 'bar' : 'break', html: esc(c), base: c });
    i = root ? root.end : i + ((quote || space || number || word)?.[0].length ?? 1);
  }
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token.kind === 'open') scopes.push(false);
    else if (token.kind === 'close' && scopes.length > 1) scopes.pop();
    else if (token.kind === 'divide') scopes[scopes.length - 1] = true;
    else if (token.kind === 'break') scopes[scopes.length - 1] = false;
    else if (token.kind === 'multiply' && compact && !keepProducts && !scopes[scopes.length - 1]) {
      let left = i - 1, right = i + 1;
      while (tokens[left]?.kind === 'space') left--;
      while (tokens[right]?.kind === 'space') right++;
      const a = tokens[left], b = tokens[right];
      const coefficient = a?.kind === 'number' && a.simple;
      const leftFactor = a?.simple || a?.kind === 'close';
      const rightFactor = b?.simple || b?.fn || b?.kind === 'open';
      const namedCollision = a?.kind === 'symbol' && b?.kind === 'symbol'
        && named.some((name) => name.includes(a.base + b.base));
      if (leftFactor && rightFactor && b?.kind !== 'number' && !namedCollision && (coefficient || a.kind !== 'number')) {
        for (let j = left + 1; j < right; j++) tokens[j].html = '';
        if (b.fn) token.html = ' ';
      }
    }
  }
  return tokens.map((token) => token.html).join('');
}

export function renderFormula(source, inline) {
  const { eq, defs, words } = parseFormula(source);
  const defined = new Set(defs.flatMap((d) => symbols(d.key)));
  // Units, sets, vectors and matrices need their explicit product notation.
  const nonScalar = defs.filter((d) => /\b(?:sets?|vectors?|matri(?:x|ces)|alphabet|ket|bra|quantum state)\b/i.test(d.text));
  const explicit = new Set(defs.filter((d) => nonScalar.includes(d)
    || /^(?:(?:the|a) )?(?:unit\b|metres?\b|meters?\b|seconds?\b|volts?\b|amperes?\b|amps?\b|ohms?\b|farads?\b|watts?\b|joules?\b|hertz\b|bytes?\b|bits?\b|kelvin\b)/i.test(d.text))
    .flatMap((d) => symbols(d.key)));
  const context = { defined, explicit, named: [...defined].filter((s) => /^[A-Za-z]{2,}$/.test(s)),
    keepProducts: !!nonScalar.length || /\b(?:Cartesian|cross|dot|inner|outer|scalar|Kronecker|tensor|Hadamard) product\b/i.test(words + ' ' + defs.map((d) => d.text).join(' ')) };
  const scopes = [false];
  return `<figure class="formula"><figcaption>Formula</figcaption>` +
    `<div class="formula-eq" tabindex="0" role="region" aria-label="Equation">${eq.map((l) => `<div>${mathHtml(l.trim(), context, true, scopes)}</div>`).join('')}</div>` +
    (defs.length ? `<div class="formula-where-label">where</div><dl class="formula-where">${defs.map((d) =>
      `<div><dt>${mathHtml(d.key, context, false)}</dt><dd>${inline(d.text)}</dd></div>`).join('')}</dl>` : '') +
    (words ? `<p class="formula-words"><b>In words</b> ${inline(words)}</p>` : '') +
    `</figure>`;
}
