#!/usr/bin/env node
// Finds equations written outside ```formula blocks, so they can be converted and every symbol explained.
// It is a heuristic finder: each hit must be either converted to a formula block or justified
// (for example a line of real program code). See .claude/skills/writing-formulas/SKILL.md.
//   node scripts/lint-formulas.mjs content/synth/03-electronics   (any path under content/)
//   node scripts/lint-formulas.mjs --summary                        (counts per module)
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const summary = args.includes('--summary');
const target = path.resolve(args.find((a) => !a.startsWith('--')) ?? 'content');

// Program code is code, not maths: these fences are never flagged.
const CODE = /^(python|py|js|javascript|ts|typescript|c|cpp|c\+\+|h|sql|bash|sh|shell|java|go|rust|json|yaml|toml|http|ini|asm|arm|x86|verilog|makefile|cmake|diagram|flow|text-output|console|output)$/;
const ID = String.raw`[A-Za-zͰ-Ͽ][A-Za-z0-9_Ͱ-Ͽ{}′']*(?:\([^)]{0,16}\))?`;
// "x = ...", "f_c ≈ ...", "O(n log n)" style relations with an operator or symbol on the right.
const RELATION = new RegExp(String.raw`(?:^|[\s(\`*])${ID}\s*(?:=|≈|≤|≥|∝|<=|>=)\s*[^=\s>][^\n]*?(?:[\/×*^√·+−-]|\blog|\bsqrt|\bmod\b|[A-Za-zͰ-Ͽ]\s*$)`);
const SYMBOLIC = /[√∑∏∫∝]|\b\w+\^\{?\w|\blog_?\d*\s*\(?\s*[a-zα-ω]\b/;

function lines(text) {
  const out = [];
  let fence = null;
  text.split('\n').forEach((line, i) => {
    const f = line.match(/^\s*```\s*([^\s`]*)/);
    if (f) { fence = fence === null ? f[1].toLowerCase() : null; return; }
    if (fence === 'formula' || (fence !== null && CODE.test(fence))) return;
    // Inline code that is clearly program code (calls, keywords) is skipped; maths in backticks is not.
    const scan = line.replace(/`[^`]*(?:\(\)|\bdef\b|\breturn\b|;|==|\.\w+\()[^`]*`/g, ' ');
    if (RELATION.test(scan) || SYMBOLIC.test(scan)) out.push({ n: i + 1, text: line.trim().slice(0, 140), where: fence === null ? 'prose' : `${fence || 'plain'} fence` });
  });
  return out;
}

const hits = [];
function scanFile(file) {
  const rel = path.relative(process.cwd(), file);
  if (file.endsWith('.md')) for (const h of lines(fs.readFileSync(file, 'utf8'))) hits.push({ file: rel, ...h });
  else if (file.endsWith('.questions.json')) {
    for (const q of JSON.parse(fs.readFileSync(file, 'utf8'))) {
      const fields = { prompt: q.prompt, workedExample: q.workedExample };
      q.options.forEach((o, i) => { fields[`option ${i}`] = o.text; fields[`option ${i} explanation`] = o.explanation; });
      for (const [k, v] of Object.entries(fields))
        for (const h of lines(String(v ?? ''))) hits.push({ file: rel, ...h, n: `${q.id} ${k}` });
    }
  }
}
(function walk(p) {
  if (fs.statSync(p).isDirectory()) fs.readdirSync(p).sort().forEach((f) => walk(path.join(p, f)));
  else if (/\.(md|questions\.json)$/.test(p)) scanFile(p);
})(target);

if (summary) {
  const per = {};
  for (const h of hits) { const m = path.dirname(h.file); per[m] = (per[m] ?? 0) + 1; }
  for (const [m, n] of Object.entries(per).sort((a, b) => b[1] - a[1])) console.log(`${String(n).padStart(5)}  ${m}`);
} else for (const h of hits) console.log(`${h.file}:${h.n} [${h.where}] ${h.text}`);
console.log(`${hits.length} possible formula(s) outside formula blocks`);
