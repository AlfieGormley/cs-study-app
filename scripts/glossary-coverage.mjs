#!/usr/bin/env node
// Lists likely technical terms in lessons and questions that have no glossary entry, so they can be added.
// Candidates: **bold** phrases (lessons bold a term where they introduce it), acronyms and unit symbols.
// Use it as a floor, not a ceiling: also read the lessons for jargon this misses. See
// .claude/skills/glossary-terms/SKILL.md.
//   node scripts/glossary-coverage.mjs content/synth/03-electronics
//   node scripts/glossary-coverage.mjs --summary
import fs from 'node:fs';
import path from 'node:path';
import { glossary as core } from '../glossary-data.js';

const args = process.argv.slice(2);
const summary = args.includes('--summary');
const target = path.resolve(args.find((a) => !a.startsWith('--')) ?? 'content');
const contentDir = path.resolve('content');

// Every term and alias known anywhere: core plus all module glossary.json files.
const known = new Set(core.flatMap((e) => [e.term, ...e.aliases].map((a) => a.toLowerCase())));
(function walk(p) {
  for (const f of fs.readdirSync(p, { withFileTypes: true })) {
    const fp = path.join(p, f.name);
    if (f.isDirectory()) walk(fp);
    else if (f.name === 'glossary.json') {
      let terms = [];
      try { terms = JSON.parse(fs.readFileSync(fp, 'utf8')); } catch { console.error(`(skipping unreadable ${path.relative(process.cwd(), fp)})`); }
      for (const e of terms) for (const a of [e?.term, ...(e?.aliases ?? [])]) if (a) known.add(String(a).toLowerCase());
    }
  }
})(contentDir);

const stripCode = (t) => t.replace(/```[\s\S]*?```/g, ' ').replace(/`[^`]*`/g, ' ');
const singular = (s) => s.replace(/(?<=[a-z]{3})(ies)$/, 'y').replace(/(?<=[a-z]{3})(es|s)$/, '');
const covered = (term) => {
  const t = term.toLowerCase();
  return known.has(t) || known.has(singular(t)) || [...known].some((k) => k.length > 3 && (t === k + 's' || t.includes(k) && t.split(/\s+/).length <= k.split(/\s+/).length + 1 && k.split(/\s+/).length > 1));
};

function candidates(text) {
  const out = [];
  const prose = stripCode(text);
  for (const m of prose.matchAll(/\*\*([^*]{2,48})\*\*/g)) {
    const t = m[1].replace(/[.:,;]$/, '').trim();
    if (/^(note|tip|warning|example|why|correct|wrong|yes|no|rule|step \d+)\b/i.test(t) || /\d{3,}/.test(t) || t.split(/\s+/).length > 5) continue;
    out.push(t);
  }
  for (const m of prose.matchAll(/(?<![\w-])([A-Z][A-Z0-9]{1,7}s?)(?![\w-])/g)) if (!/^(I|A|OK|TODO)$/.test(m[1])) out.push(m[1].replace(/s$/, ''));
  return out;
}

const per = new Map(); // module dir -> Map(term -> count)
(function walk(p) {
  if (fs.statSync(p).isDirectory()) return fs.readdirSync(p).sort().forEach((f) => walk(path.join(p, f)));
  let text = '';
  if (p.endsWith('.md')) text = fs.readFileSync(p, 'utf8').replace(/^---[\s\S]*?---/, '').replace(/^## Further reading[\s\S]*$/m, '');
  else if (p.endsWith('.questions.json'))
    text = JSON.parse(fs.readFileSync(p, 'utf8')).flatMap((q) => [q.prompt, q.workedExample, ...q.options.flatMap((o) => [o.text, o.explanation])]).join('\n');
  else return;
  const mod = path.relative(process.cwd(), path.dirname(p));
  if (!per.has(mod)) per.set(mod, new Map());
  for (const c of candidates(text)) if (!covered(c)) per.get(mod).set(c, (per.get(mod).get(c) ?? 0) + 1);
})(target);

let total = 0;
for (const [mod, terms] of per) {
  total += terms.size;
  if (summary) { if (terms.size) console.log(`${String(terms.size).padStart(5)}  ${mod}`); continue; }
  if (!terms.size) continue;
  console.log(`\n${mod} (${terms.size})`);
  for (const [t, n] of [...terms].sort((a, b) => b[1] - a[1])) console.log(`  ${t}${n > 1 ? `  ×${n}` : ''}`);
}
console.log(`\n${total} candidate term(s) with no glossary entry`);
