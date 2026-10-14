#!/usr/bin/env node
// Checks course migrations against the deployed original index and question index.
// Usage: node scripts/audit-short-lessons.mjs <original-index> <original-questions> [report] [--partial]
// Partial releases still preserve every original question across the whole course.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { migrationProblems, subjectMigrationProblems } from '../lesson-progress.js';

const original = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const originalQuestions = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const current = JSON.parse(fs.readFileSync('data/index.json', 'utf8'));
const questions = JSON.parse(fs.readFileSync('data/questions.json', 'utf8'));
const partial = process.argv.includes('--partial');
const reportFile = process.argv.slice(4).find((arg) => arg !== '--partial');
const rows = [];
let pendingModules = 0;
for (const [key, [module]] of Object.entries(originalQuestions)) {
  assert.equal(questions[key]?.[0], module, `original question ${key} was lost or moved to another module`);
}
for (const subject of current.subjects) assert.deepEqual(subjectMigrationProblems(subject.modules.map((module) => ({ ...module, lessons: module.lessons.map((lesson) => lesson.id) }))), []);
for (const subject of original.subjects) for (const previous of subject.modules) {
  const module = current.subjects.find((s) => s.id === subject.id)?.modules.find((m) => m.id === previous.id);
  assert.ok(module, `missing module ${subject.id}/${previous.id}`);
  assert.deepEqual(migrationProblems({ ...module, lessons: module.lessons.map((l) => l.id) }), []);
  if (partial && !Object.keys(module.migrations ?? {}).length) { pendingModules++; continue; }
  const active = new Set(module.lessons.map((l) => l.id));
  assert.deepEqual([...active].sort(), Object.values(module.migrations ?? {}).flat().sort(), `module ${module.id} has lessons outside its migrations`);
  for (const old of previous.lessons) {
    const children = module.migrations?.[old.id];
    assert.ok(children?.length, `lesson ${subject.id}/${old.id} was not split`);
    assert.equal(active.has(old.id), false, `original ${old.id} is still active`);
    for (const id of children) {
      const lesson = module.lessons.find((l) => l.id === id);
      assert.equal(lesson.sourceLesson, old.id);
      assert.ok(lesson.minutes >= 1 && lesson.minutes <= 5, `${id}: invalid short reading time`);
      assert.ok(lesson.questionCount > 0, `${id}: no focused questions`);
    }
  }
  const subjectDirectory = path.join('content', subject.id);
  const directory = fs.readdirSync(subjectDirectory).map((name) => path.join(subjectDirectory, name)).find((directory) => {
    const file = path.join(directory, 'module.json');
    return fs.existsSync(file) && JSON.parse(fs.readFileSync(file, 'utf8')).id === module.id;
  });
  assert.ok(directory, `missing source directory for ${subject.id}/${module.id}`);
  const compiled = JSON.parse(fs.readFileSync(path.join('data', subject.id, `${module.id}.json`), 'utf8'));
  const movedQuestions = new Map();
  for (const lesson of compiled.lessons) for (const question of lesson.questions) {
    assert.equal(movedQuestions.has(question.id), false, `duplicate question ${question.id}`);
    movedQuestions.set(question.id, question);
  }
  for (const lesson of previous.lessons) {
    const archived = JSON.parse(fs.readFileSync(path.join(directory, `${lesson.id}.questions.json`), 'utf8'));
    for (const question of archived) {
      const moved = movedQuestions.get(question.id);
      assert.ok(moved, `original question ${question.id} is absent from compiled lessons`);
      assert.equal(moved.type, question.type, `original question ${question.id} changed its type`);
      assert.deepEqual(moved.answer, question.answer, `original question ${question.id} changed its answer key`);
      assert.equal(moved.options.length, question.options.length, `original question ${question.id} changed its option count`);
    }
  }
  rows.push({ subject: subject.title, module: module.title, originalLessons: previous.lessons.length, shortLessons: module.lessons.length,
    questions: module.lessons.reduce((n, l) => n + l.questionCount, 0), longestMinutes: Math.max(...module.lessons.map((l) => l.minutes)) });
}
const report = { originalLessons: original.subjects.reduce((n, s) => n + s.modules.reduce((n, m) => n + m.lessons.length, 0), 0),
  shortLessons: rows.reduce((n, r) => n + r.shortLessons, 0), originalQuestions: Object.keys(originalQuestions).length,
  convertedOriginalLessons: rows.reduce((n, r) => n + r.originalLessons, 0),
  questions: Object.keys(questions).length, pendingModules, modules: rows };
if (reportFile) fs.writeFileSync(reportFile, JSON.stringify(report, null, 2) + '\n');
console.log(`${report.convertedOriginalLessons} originals → ${report.shortLessons} short lessons across ${rows.length} modules; all ${report.originalQuestions} original course questions retained. ${pendingModules} modules awaiting conversion.`);
