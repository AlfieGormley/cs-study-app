// Formula blocks: an equation plus a definition of every symbol in it.
// Authoring format (see .claude/skills/writing-formulas/SKILL.md):
//
//   ```formula
//   f = c / (2 × π × a)
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
// Latin runs are one symbol ("RTT", "log", "Hz"); write products explicitly (R × C).
const SUB = String.raw`(?:_(?:\{[^}]*\}|[A-Za-z0-9Ͱ-Ͽ]+))?`;
const TOKEN = new RegExp(String.raw`(?:[Ͱ-Ͽµ]|[A-Za-z][A-Za-z0-9]*)['′]*` + SUB, 'gu');

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
export function symbols(text) {
  const stripped = String(text)
    .replace(/"[^"]*"|'[^']*'(?![′'])/g, ' ')
    .replace(/(?<![\w{])(?:0x[0-9a-f]+|0b[01]+|\d+(?:\.\d+)?(?:e[+-]?\d+)?)/gi, ' ');
  return [...new Set((stripped.match(TOKEN) || []).map((t) => t.replace(/_\{([^}]*)\}$/, '_$1')))];
}

// Problems with a formula block (empty when every symbol is defined).
export function checkFormula(source) {
  const { eq, defs, words, hasWhere } = parseFormula(source);
  const p = [];
  if (!eq.length) p.push('formula block has no equation line');
  if (!hasWhere) return [...p, 'formula block needs a "where" line followed by a definition of every symbol'];
  if (!defs.length) p.push('formula block defines no symbols');
  if (!words) p.push(`formula block needs an "In words:" line saying what "${eq[0] ?? ''}" means in plain English`);
  for (const d of defs) if (d.bad || !d.text) p.push(`definition "${d.key}" must be written "symbol: meaning"`);
  const defined = new Set(defs.flatMap((d) => symbols(d.key)));
  const missing = symbols(eq.join('\n')).filter((s) => !defined.has(s));
  if (missing.length) p.push(`undefined symbol(s) ${missing.map((s) => `"${s}"`).join(', ')} in "${eq[0]}"`);
  return p;
}

// a_b, a_{bc} -> subscript; a^b, a^{bc} -> superscript; single Latin letters in italics.
function mathHtml(text) {
  let s = esc(text);
  s = s.replace(/\^\{([^}]*)\}|\^([A-Za-z0-9Ͱ-Ͽ+−-]+)/g, (_, a, b) => `<sup>${a ?? b}</sup>`);
  s = s.replace(/_\{([^}]*)\}|_([A-Za-z0-9Ͱ-Ͽ]+)/g, (_, a, b) => `<sub>${a ?? b}</sub>`);
  return s.replace(/(^|[^A-Za-z0-9&#;<\/])([A-Za-z])(?![A-Za-z0-9;>])/g, '$1<i>$2</i>');
}

export function renderFormula(source, inline) {
  const { eq, defs, words } = parseFormula(source);
  return `<figure class="formula"><figcaption>Formula</figcaption>` +
    `<div class="formula-eq" tabindex="0" role="region" aria-label="Equation">${eq.map((l) => `<div>${mathHtml(l.trim())}</div>`).join('')}</div>` +
    (defs.length ? `<div class="formula-where-label">where</div><dl class="formula-where">${defs.map((d) =>
      `<div><dt>${mathHtml(d.key)}</dt><dd>${inline(d.text)}</dd></div>`).join('')}</dl>` : '') +
    (words ? `<p class="formula-words"><b>In words</b> ${inline(words)}</p>` : '') +
    `</figure>`;
}
