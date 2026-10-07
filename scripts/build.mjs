#!/usr/bin/env node
// Validates content/ and compiles it into data/ for the app.
//   node scripts/build.mjs          validate + write data/ and assets.js
//   node scripts/build.mjs --check  validate only
//   node scripts/build.mjs --check content/system-design/03-caching   only report problems under a path
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { plainText } from '../markdown.js';
import { compileCatalogue } from './diagram-compiler.mjs';
import { checkVerification, lessonHash } from './verification.mjs';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const contentDir = path.join(root, 'content');
const dataDir = path.join(root, 'data');
const checkOnly = process.argv.includes('--check');
const onlyPath = process.argv.slice(2).find((a) => !a.startsWith('--'));

const LEVELS = ['basic', 'intermediate', 'advanced'];
const errors = [];
const err = (where, msg) => errors.push(`${path.relative(root, where)}: ${msg}`);

const readJson = (file) => {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    err(file, `invalid JSON (${e.message})`);
    return null;
  }
};

function parseLesson(file) {
  const raw = fs.readFileSync(file, 'utf8');
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) {
    err(file, 'missing frontmatter');
    return null;
  }
  const meta = {};
  for (const line of m[1].split('\n')) {
    const i = line.indexOf(':');
    if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^(["'])(.*)\1$/, '$2');
  }
  meta.minutes = Number(meta.minutes);
  return { meta, body: m[2].trim() };
}

// Lines inside fenced code blocks; diagrams must fit a phone screen.
const codeLines = (text) => [...String(text ?? '').matchAll(/```[^\n]*\n([\s\S]*?)```/g)].flatMap((m) => m[1].split('\n'));
const tooWide = (text, max) => codeLines(text).filter((l) => [...l].length > max);

const isUrl = (u) => typeof u === 'string' && /^https?:\/\/\S+$/.test(u);

function validateQuestion(q, file, ids) {
  const at = `${q?.id ?? '(no id)'}`;
  if (!q || typeof q !== 'object') return err(file, 'question is not an object');
  if (!q.id) err(file, 'question missing id');
  else if (ids.has(q.id)) err(file, `duplicate question id ${q.id}`);
  else ids.add(q.id);
  if (!LEVELS.includes(q.level)) err(file, `${at}: bad level "${q.level}"`);
  if (!['single', 'multi'].includes(q.type)) err(file, `${at}: bad type "${q.type}"`);
  if (!q.prompt) err(file, `${at}: missing prompt`);
  if (!Array.isArray(q.options) || q.options.length < 2 || q.options.length > 6)
    err(file, `${at}: needs 2-6 options`);
  else
    q.options.forEach((o, i) => {
      if (!o?.text) err(file, `${at}: option ${i} missing text`);
      if (!o?.explanation) err(file, `${at}: option ${i} missing explanation`);
    });
  const n = q.options?.length ?? 0;
  const inRange = (a) => Number.isInteger(a) && a >= 0 && a < n;
  if (q.type === 'single' && !inRange(q.answer)) err(file, `${at}: answer must be an index < ${n}`);
  if (q.type === 'multi' && !(Array.isArray(q.answer) && q.answer.length && q.answer.every(inRange)))
    err(file, `${at}: multi answer must be a non-empty array of indices`);
  if (!q.workedExample) err(file, `${at}: missing workedExample`);
  const texts = [q.prompt, q.workedExample, ...(q.options ?? []).flatMap((o) => [o?.text, o?.explanation])];
  const wide = texts.flatMap((t) => tooWide(t, 40));
  if (wide.length) err(file, `${at}: ${wide.length} code line(s) wider than 40 chars, e.g. "${wide[0]}"`);
  if (!q.link?.title || !isUrl(q.link?.url)) err(file, `${at}: link needs title and http(s) url`);
}

const dirs = (p) =>
  fs.existsSync(p)
    ? fs.readdirSync(p, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name).sort()
    : [];

// Modules created before the verification procedure existed. Frozen: never add entries (docs/CONTENT_PROCESS.md).
const legacyFile = path.join(contentDir, 'verification-legacy.json');
const verificationLegacy = fs.existsSync(legacyFile) ? readJson(legacyFile) ?? {} : {};
let legacyCount = 0;

const index = { subjects: [] };
const outputs = {}; // relative path -> object

for (const subjectName of dirs(contentDir)) {
  const subjectPath = path.join(contentDir, subjectName);
  const subject = readJson(path.join(subjectPath, 'subject.json'));
  if (!subject) continue;
  const lessonIds = new Set();
  const questionIds = new Set();
  const subjectEntry = { ...subject, modules: [] };

  for (const moduleName of dirs(subjectPath)) {
    const modulePath = path.join(subjectPath, moduleName);
    const moduleFile = path.join(modulePath, 'module.json');
    if (!fs.existsSync(moduleFile)) {
      err(modulePath, 'missing module.json');
      continue;
    }
    const mod = readJson(moduleFile);
    if (!mod) continue;
    for (const k of ['id', 'title', 'summary']) if (!mod[k]) err(moduleFile, `missing ${k}`);
    if (!Array.isArray(mod.lessons) || !mod.lessons.length) {
      err(moduleFile, 'lessons must be a non-empty array');
      continue;
    }

    const full = { id: mod.id, subject: subject.id, title: mod.title, summary: mod.summary, lessons: [] };
    const entry = { id: mod.id, title: mod.title, summary: mod.summary, order: mod.order, lessons: [] };

    for (const lessonId of mod.lessons) {
      const mdFile = path.join(modulePath, `${lessonId}.md`);
      const qFile = path.join(modulePath, `${lessonId}.questions.json`);
      if (!fs.existsSync(mdFile)) {
        err(moduleFile, `lesson ${lessonId} has no .md file`);
        continue;
      }
      const lesson = parseLesson(mdFile);
      if (!lesson) continue;
      const { meta, body } = lesson;
      if (meta.id !== lessonId) err(mdFile, `frontmatter id "${meta.id}" != "${lessonId}"`);
      if (lessonIds.has(lessonId)) err(mdFile, `duplicate lesson id ${lessonId}`);
      lessonIds.add(lessonId);
      if (!meta.title) err(mdFile, 'missing title');
      if (!LEVELS.includes(meta.level)) err(mdFile, `bad level "${meta.level}"`);
      if (!meta.minutes) err(mdFile, 'missing minutes');
      if (!meta.summary) err(mdFile, 'missing summary');
      const wideL = tooWide(body, 44);
      if (wideL.length) err(mdFile, `${wideL.length} code line(s) wider than 44 chars, e.g. "${wideL[0]}"`);
      if (!/^## Key takeaways/m.test(body)) err(mdFile, 'missing "## Key takeaways"');
      if (!/^## Further reading/m.test(body)) err(mdFile, 'missing "## Further reading"');
      const prose = body.replace(/^\s*```[\s\S]*?^\s*```/gm, '');
      if (/^# /m.test(prose)) err(mdFile, 'uses a top-level "# " heading');

      let questions = [];
      if (!fs.existsSync(qFile)) err(mdFile, 'missing .questions.json');
      else {
        questions = readJson(qFile) ?? [];
        if (!Array.isArray(questions)) {
          err(qFile, 'must be an array');
          questions = [];
        }
        questions.forEach((q) => validateQuestion(q, qFile, questionIds));
      }

      const head = { id: lessonId, title: meta.title, level: meta.level, minutes: meta.minutes, summary: meta.summary };
      full.lessons.push({ ...head, body, questions });
      entry.lessons.push({ ...head, questionCount: questions.length });
    }
    // Mandatory independent verification (docs/CONTENT_PROCESS.md).
    const legacyKey = `${subjectName}/${moduleName}`;
    const legacy = verificationLegacy.modules?.[legacyKey];
    if (legacy && !fs.existsSync(path.join(modulePath, 'verification.json'))) {
      legacyCount++;
      for (const id of mod.lessons)
        if (legacy.lessons?.[id] !== lessonHash(modulePath, id))
          err(path.join(modulePath, `${id}.md`), `legacy lesson ${id} was added or changed without verification: run the full procedure in docs/CONTENT_PROCESS.md and add a verification.json for this module`);
    } else {
      for (const problem of checkVerification(modulePath, mod)) err(modulePath, problem);
    }

    subjectEntry.modules.push(entry);
    outputs[`data/${subject.id}/${mod.id}.json`] = full;
  }
  subjectEntry.modules.sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
  if (subjectEntry.modules.length) index.subjects.push(subjectEntry); // hide subjects with no content yet
}
index.subjects.sort((a, b) => (a.order ?? 0) - (b.order ?? 0));

if (onlyPath) {
  const prefix = path.relative(root, path.resolve(onlyPath));
  const mine = errors.filter((e) => e.startsWith(prefix));
  errors.length = 0;
  errors.push(...mine);
}
if (errors.length) {
  console.error(`✗ ${errors.length} problem(s):\n  ` + errors.join('\n  '));
  process.exit(1);
}

const totals = index.subjects.map((s) => {
  const lessons = s.modules.flatMap((m) => m.lessons);
  return `${s.title}: ${s.modules.length} modules, ${lessons.length} lessons, ${lessons.reduce((n, l) => n + l.questionCount, 0)} questions`;
});
console.log('✓ content valid\n  ' + totals.join('\n  '));
if (legacyCount) console.log(`! ${legacyCount} legacy module(s) predate the verification procedure and have no verification.json; see content/verification-legacy.json`);
const diagramOverrides = readJson(path.join(contentDir, 'diagram-overrides.json'));
if (!diagramOverrides) process.exit(1);
const { catalogue: diagramCatalogue, report: diagramReport } = compileCatalogue(outputs, diagramOverrides);
console.log(`✓ diagrams: ${diagramReport.unique} definitions, ${diagramReport.occurrences} appearances`);
if (checkOnly) process.exit(0);
fs.writeFileSync(path.join(root, 'diagram-catalog.js'), '// Generated by scripts/build.mjs. Do not edit.\nexport default ' + JSON.stringify(diagramCatalogue) + ';\n');
fs.writeFileSync(path.join(root, 'docs/diagram-migration.json'), JSON.stringify(diagramReport, null, 2) + '\n');

fs.rmSync(dataDir, { recursive: true, force: true });
outputs['data/index.json'] = index;

// Small indexes so Search and Review don't need to load every module.
const search = [];
const qindex = {};
for (const [rel, mod] of Object.entries(outputs)) {
  if (!mod.lessons) continue;
  for (const l of mod.lessons) {
    search.push({ s: mod.subject, m: mod.id, l: l.id, t: l.title, sum: l.summary, lv: l.level, mt: mod.title, x: plainText(l.body) });
    for (const q of l.questions)
      qindex[`${mod.subject}/${q.id}`] = [mod.id, l.id, q.level, ((t) => (t.length > 140 ? t.slice(0, 137).replace(/\s+\S*$/, '') + '…' : t))(plainText(q.prompt).trim()), l.title];
  }
}
outputs['data/search.json'] = search;
outputs['data/questions.json'] = qindex;
const hash = crypto.createHash('sha256');
for (const [rel, obj] of Object.entries(outputs)) {
  const file = path.join(root, rel);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const text = JSON.stringify(obj);
  fs.writeFileSync(file, text);
  hash.update(text);
}

// App shell + data files for the service worker to precache.
const shell = ['./', 'index.html', 'styles.css', 'app.js', 'markdown.js', 'examples.js', 'diagrams.js', 'glossary.js', 'glossary-data.js', 'diagram-key.js', 'diagram-catalog.js', 'manifest.webmanifest',
  'icons/icon-180.png', 'icons/icon-192.png', 'icons/icon-512.png'];
for (const f of shell.slice(1)) {
  const p = path.join(root, f);
  if (fs.existsSync(p)) hash.update(fs.readFileSync(p));
}
const assets = [...shell, ...Object.keys(outputs)];
const version = hash.digest('hex').slice(0, 12);
fs.writeFileSync(
  path.join(root, 'assets.js'),
  `// Generated by scripts/build.mjs. Do not edit.\nself.APP_VERSION = '${version}';\nself.APP_ASSETS = ${JSON.stringify(assets, null, 2)};\n`
);
console.log(`✓ wrote ${Object.keys(outputs).length} data files, version ${version}`);
