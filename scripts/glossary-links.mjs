#!/usr/bin/env node
// Shows what every glossary link in a module points at, so wrong-sense links are easy to spot.
// It resolves words exactly like the app (glossary-rules.js): own subject (which may shadow core), then core terms, then other subjects'
// multi-word aliases. Lines marked "!" are single words owned by a different module, the usual source of
// wrong-sense links (for example "from" opening a pagination term in an unrelated lesson).
//   node scripts/glossary-links.mjs content/<subject>/<module>          all links, most frequent first
//   node scripts/glossary-links.mjs content/<subject>/<module> --suspect only the "!" lines
import fs from 'node:fs';
import path from 'node:path';
import { glossary as core } from '../glossary-data.js';
import { aliasKey, fallsBack } from '../glossary-rules.js';

const args = process.argv.slice(2);
const dir = path.resolve(args.find((a) => !a.startsWith('--')) ?? '');
const suspectOnly = args.includes('--suspect');
const contentDir = path.resolve('content');
if (!fs.existsSync(path.join(dir, 'module.json'))) {
  console.error('usage: node scripts/glossary-links.mjs content/<subject>/<module> [--suspect]');
  process.exit(1);
}
const subjectOf = (p) => path.relative(contentDir, p).split(path.sep)[0];
const here = { subject: subjectOf(dir), module: path.basename(dir) };

// Load every module glossary in curriculum order, as the build does.
const subjects = fs.readdirSync(contentDir).filter((s) => fs.existsSync(path.join(contentDir, s, 'subject.json')))
  .map((s) => ({ s, order: JSON.parse(fs.readFileSync(path.join(contentDir, s, 'subject.json'))).order ?? 99 }))
  .sort((a, b) => a.order - b.order).map((x) => x.s);
const coreMap = new Map();
for (const e of core) for (const a of [e.term, ...e.aliases]) coreMap.set(aliasKey(a), { id: e.id, owner: 'core', alias: a });
const bySubject = new Map();
const fallback = new Map();
for (const s of subjects)
  for (const m of fs.readdirSync(path.join(contentDir, s)).sort()) {
    const f = path.join(contentDir, s, m, 'glossary.json');
    if (!fs.existsSync(f)) continue;
    let terms = [];
    try { terms = JSON.parse(fs.readFileSync(f, 'utf8')); } catch { continue; }
    const map = bySubject.get(s) ?? bySubject.set(s, new Map()).get(s);
    for (const t of terms) {
      const entry = { ...t, subject: s };
      for (const a of [t.term, ...(t.aliases ?? [])]) {
        const k = aliasKey(a);
        const rec = { id: t.id, owner: `${s}/${m}`, alias: a };
        if (!map.has(k)) map.set(k, rec);
        if (fallsBack(entry, a) && !fallback.has(k)) fallback.set(k, rec);
      }
    }
  }
const maps = [bySubject.get(here.subject), coreMap, fallback].filter(Boolean);
const look = (w) => {
  for (const m of maps) for (const k of ['=' + w, w.toLowerCase()]) if (m.has(k)) return m.get(k);
  return null;
};
const words = [...new Set(maps.flatMap((m) => [...m.values()].map((v) => v.alias.toLowerCase())))].sort((a, b) => b.length - a.length);
const re = new RegExp(`(?<![\\p{L}\\p{N}_])(?:${words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})(?![\\p{L}\\p{N}_])`, 'giu');

let text = '';
for (const f of fs.readdirSync(dir)) {
  const p = path.join(dir, f);
  if (f.endsWith('.md')) text += fs.readFileSync(p, 'utf8').replace(/^---[\s\S]*?---/, '') + '\n';
  else if (f.endsWith('.questions.json'))
    text += JSON.parse(fs.readFileSync(p, 'utf8')).flatMap((q) => [q.prompt, q.workedExample, ...q.options.map((o) => o.explanation)]).join('\n') + '\n';
}
text = text.replace(/```[\s\S]*?```/g, ' ').replace(/\]\([^)]*\)/g, ']');

const counts = new Map();
for (const m of text.matchAll(re)) {
  const e = look(m[0]);
  if (!e) continue;
  const mine = e.owner === `${here.subject}/${here.module}`;
  const suspect = !mine && !/[\s-]/.test(m[0]) && e.owner !== 'core';
  if (suspectOnly && !suspect) continue;
  const key = `${suspect ? '!' : ' '} ${m[0]} → ${e.id} [${mine ? 'this module' : e.owner}]`;
  counts.set(key, (counts.get(key) ?? 0) + 1);
}
for (const [k, n] of [...counts].sort((a, b) => b[1] - a[1])) console.log(`${String(n).padStart(4)} ${k}`);
console.log(`\n${counts.size} distinct link target(s)${suspectOnly ? ' flagged' : ''}. "!" = single word whose definition lives in another module. Most are fine; skim them for a wrong sense (for example "from" opening a pagination term).`);
