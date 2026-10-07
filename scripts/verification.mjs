// Verification records: every module must be independently fact-checked before it ships.
// See docs/CONTENT_PROCESS.md. Each module directory holds a verification.json, and each lesson in it stores
// a hash of the lesson files as they were when verified, so any later edit forces re-verification.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export const CONFIDENCE = ['high', 'medium', 'low'];

export function lessonHash(modulePath, lessonId) {
  const h = crypto.createHash('sha256');
  for (const f of [`${lessonId}.md`, `${lessonId}.questions.json`]) {
    const p = path.join(modulePath, f);
    h.update(f);
    h.update(fs.existsSync(p) ? fs.readFileSync(p) : '');
  }
  return h.digest('hex').slice(0, 16);
}

const isDate = (d) => typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d);
const isCount = (n) => Number.isInteger(n) && n >= 0;

// Returns a list of problems (empty when the record is valid and current).
// With { ignoreHashes: true } it checks structure only (used when stamping).
export function checkVerification(modulePath, mod, { ignoreHashes = false } = {}) {
  const file = path.join(modulePath, 'verification.json');
  if (!fs.existsSync(file)) {
    return ['missing verification.json: the module has not been independently fact-checked (see docs/CONTENT_PROCESS.md)'];
  }
  let v;
  try {
    v = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    return [`verification.json is invalid JSON (${e.message})`];
  }
  const p = [];
  if (v.module !== mod.id) p.push(`verification.json module "${v.module}" != module id "${mod.id}"`);
  if (!isDate(v.author?.date)) p.push('verification.json: author.date (YYYY-MM-DD) required');
  if (!isDate(v.verifier?.date)) p.push('verification.json: verifier.date (YYYY-MM-DD) required');
  if (v.verifier?.independent !== true) p.push('verification.json: verifier.independent must be true (a separate agent, not the author)');
  if (!Array.isArray(v.verifier?.sources) || !v.verifier.sources.length) p.push('verification.json: verifier.sources must list the primary sources checked against');
  const s = v.summary ?? {};
  for (const k of ['claimsChecked', 'errorsCorrected', 'hedgedOrRemoved']) if (!isCount(s[k])) p.push(`verification.json: summary.${k} must be a non-negative integer`);
  if (isCount(s.claimsChecked) && s.claimsChecked === 0) p.push('verification.json: summary.claimsChecked is 0');
  for (const k of ['corrections', 'gaps']) if (!Array.isArray(v[k])) p.push(`verification.json: ${k} must be an array (may be empty)`);
  if (!Array.isArray(v.lowConfidence)) p.push('verification.json: lowConfidence must be an array (may be empty)');
  else
    v.lowConfidence.forEach((c, i) => {
      if (!c?.claim || !c?.lesson || !['medium', 'low'].includes(c?.confidence) || !c?.reason)
        p.push(`verification.json: lowConfidence[${i}] needs lesson, claim, confidence (medium|low) and reason`);
    });

  const lessons = v.lessons ?? {};
  for (const id of mod.lessons) {
    const rec = lessons[id];
    if (!rec) {
      p.push(`lesson ${id} has no verification entry (new or unverified lesson)`);
      continue;
    }
    if (!CONFIDENCE.includes(rec.confidence)) p.push(`lesson ${id}: confidence must be one of ${CONFIDENCE.join('/')}`);
    if (!ignoreHashes && rec.hash !== lessonHash(modulePath, id))
      p.push(`lesson ${id} changed after it was verified: re-verify it, then run node scripts/stamp-verification.mjs ${path.relative(process.cwd(), modulePath)}`);
  }
  for (const id of Object.keys(lessons)) if (!mod.lessons.includes(id)) p.push(`verification.json lists unknown lesson ${id}`);
  return p;
}
