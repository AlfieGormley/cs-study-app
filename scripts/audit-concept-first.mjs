#!/usr/bin/env node
// Inventory active lessons and verify the provenance of their concept-first editorial review.
// A passing record is evidence of a separate semantic review, not a keyword-based judgement.
// node scripts/audit-concept-first.mjs <report.json> [--require-complete] [--baseline-commit <sha>]
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { lessonHash, checkVerification } from './verification.mjs';
import { formulaFence } from '../formula.js';

export const canonical = (value) => JSON.stringify(value, (_, item) =>
  item && typeof item === 'object' && !Array.isArray(item)
    ? Object.fromEntries(Object.keys(item).sort().map((key) => [key, item[key]])) : item);

export function inspectConceptReview(directory, module, baseline) {
  const verification = JSON.parse(fs.readFileSync(path.join(directory, 'verification.json'), 'utf8'));
  const review = verification.conceptFirstReview;
  const problems = [];
  if (!review) return { reviewed: false, problems: ['No concept-first semantic review.'], lessons: [] };
  const author = review.author?.agent;
  const verifier = review.verifier?.agent;
  if (review.ruleVersion !== 1) problems.push('Unsupported concept-first rule version.');
  if (typeof author !== 'string' || !author || typeof verifier !== 'string' || !verifier || author === verifier || review.verifier?.independent !== true)
    problems.push('Distinct author and independent verifier identities required.');
  if (!Array.isArray(review.verifier?.sources) || !review.verifier.sources.length
    || review.verifier.sources.some((source) => typeof source !== 'string' || !/^https?:\/\//.test(source)))
    problems.push('Fetched primary source URLs required.');
  for (const who of ['author', 'verifier'])
    if (!/^\d{4}-\d{2}-\d{2}$/.test(review[who]?.date ?? '')) problems.push(`${who} review date required.`);
  const baselineQuestions = baseline && new Map(baseline.lessons.flatMap((lesson) => lesson.questions.map((q) => [q.id, q])));
  const baselineOwners = baseline && new Map(baseline.lessons.flatMap((lesson) => lesson.questions.map((q) => [q.id, lesson.id])));
  if (new Set(module.lessons).size !== module.lessons.length) problems.push('Duplicate active lesson id.');
  if (baseline) {
    const originalIds = new Set(baseline.lessons.map((lesson) => lesson.id));
    for (const id of originalIds) if (!module.lessons.includes(id)) problems.push(`Active lesson id lost: ${id}.`);
    for (const id of module.lessons) if (!originalIds.has(id)) problems.push(`Active lesson id added or replaced: ${id}.`);
  }
  const currentIds = new Set();
  const lessons = module.lessons.map((id) => {
    const source = fs.readFileSync(path.join(directory, `${id}.md`), 'utf8');
    const questions = JSON.parse(fs.readFileSync(path.join(directory, `${id}.questions.json`), 'utf8'));
    const rec = review.lessons?.[id];
    const issues = [];
    if (!rec || rec.hash !== lessonHash(directory, id)) issues.push('Missing or stale semantic review hash.');
    if (typeof rec?.rationale !== 'string' || rec.rationale.trim().length < 20) issues.push('Specific editorial rationale required.');
    const changes = rec?.questionsRewritten ?? {};
    const ownIds = new Set(questions.map((q) => q.id));
    for (const [qid, reason] of Object.entries(changes))
      if (!ownIds.has(qid) || typeof reason !== 'string' || reason.trim().length < 10)
        issues.push(`Invalid question revision record: ${qid}.`);
    let changedQuestions = 0;
    for (const q of questions) {
      if (currentIds.has(q.id)) issues.push(`Duplicate question id: ${q.id}.`);
      currentIds.add(q.id);
      if (baselineQuestions) {
        if (!baselineQuestions.has(q.id)) issues.push(`Question id added or replaced: ${q.id}.`);
        else {
          if (baselineOwners.get(q.id) !== id) issues.push(`Question moved from its saved lesson: ${q.id}.`);
          if (canonical(q) !== canonical(baselineQuestions.get(q.id))) {
            changedQuestions++;
            if (!changes[q.id]) issues.push(`Changed question lacks a review reason: ${q.id}.`);
          }
        }
      }
    }
    const fences = [...source.matchAll(/```([^\n]*)\n([\s\S]*?)```/g)]
      .map((match) => formulaFence(match[1])).filter((f) => f.isFormula);
    if (fences.some((f) => !f.essential && !f.reference)) issues.push('Unclassified formula in reviewed lesson.');
    if (fences.some((f) => f.problems.length)) issues.push('Invalid formula marker in reviewed lesson.');
    return { id, reviewed: issues.length === 0, rationale: rec?.rationale ?? '',
      questions: questions.length, changedQuestions, recordedQuestionRevisions: Object.keys(changes).length,
      essentialFormulas: fences.filter((f) => f.essential).length,
      referenceFormulas: fences.filter((f) => f.reference).length,
      questionFormulas: questions.reduce((n, q) => n + (JSON.stringify(q).match(/```formula\b/g) ?? []).length, 0),
      problems: issues };
  });
  for (const id of Object.keys(review.lessons ?? {}))
    if (!module.lessons.includes(id)) problems.push(`Review lists inactive lesson ${id}.`);
  if (baselineQuestions) for (const id of baselineQuestions.keys())
    if (!currentIds.has(id)) problems.push(`Question id lost: ${id}.`);
  problems.push(...checkVerification(directory, module));
  return { reviewed: !problems.length && lessons.every((l) => l.reviewed), problems, lessons };
}

export function auditConceptFirst(root, { baselineCommit } = {}) {
  const modules = [];
  const content = path.join(root, 'content');
  for (const subject of fs.readdirSync(content).sort()) {
    const directory = path.join(content, subject);
    if (!fs.statSync(directory).isDirectory()) continue;
    for (const name of fs.readdirSync(directory).sort()) {
      const modulePath = path.join(directory, name);
      const file = path.join(modulePath, 'module.json');
      if (!fs.existsSync(file)) continue;
      const module = JSON.parse(fs.readFileSync(file, 'utf8'));
      let baseline;
      if (baselineCommit) baseline = JSON.parse(execFileSync('git', ['show', `${baselineCommit}:data/${subject}/${module.id}.json`], { cwd: root, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }));
      const result = inspectConceptReview(modulePath, module, baseline);
      modules.push({ subject, path: path.relative(root, modulePath), id: module.id, title: module.title,
        activeLessons: module.lessons.length, ...result });
    }
  }
  return { ruleVersion: 1, baselineCommit: baselineCommit ?? null,
    note: 'Only active module.json lesson ids are audited. Semantic decisions are supplied by independent reviewers; no keyword match certifies quality.',
    totals: { modules: modules.length, reviewedModules: modules.filter((m) => m.reviewed).length,
      activeLessons: modules.reduce((n, m) => n + m.activeLessons, 0),
      reviewedLessons: modules.reduce((n, m) => n + (m.reviewed ? m.activeLessons : 0), 0) },
    modules };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  const baselineAt = args.indexOf('--baseline-commit');
  const baselineCommit = baselineAt >= 0 ? args[baselineAt + 1] : undefined;
  if (baselineAt >= 0) args.splice(baselineAt, 2);
  const reportFile = args.find((arg) => !arg.startsWith('--'));
  const report = auditConceptFirst(process.cwd(), { baselineCommit });
  if (reportFile) fs.writeFileSync(reportFile, JSON.stringify(report, null, 2) + '\n');
  console.log(`${report.totals.reviewedModules}/${report.totals.modules} modules; ${report.totals.reviewedLessons}/${report.totals.activeLessons} active lessons have current concept-first review records.`);
  if (args.includes('--require-complete') && report.totals.reviewedModules !== report.totals.modules) process.exitCode = 1;
}
