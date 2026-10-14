#!/usr/bin/env node
// Checks course migrations against the deployed original index and question index.
// Usage: node scripts/audit-short-lessons.mjs <original-index> <original-questions> [report]
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { migrationProblems } from '../lesson-progress.js';

const original = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const originalQuestions = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const current = JSON.parse(fs.readFileSync('data/index.json', 'utf8'));
const questions = JSON.parse(fs.readFileSync('data/questions.json', 'utf8'));
const rows = [];
for (const subject of original.subjects) for (const previous of subject.modules) {
  const module = current.subjects.find((s) => s.id === subject.id)?.modules.find((m) => m.id === previous.id);
  assert.ok(module, `missing module ${subject.id}/${previous.id}`);
  assert.deepEqual(migrationProblems({ ...module, lessons: module.lessons.map((l) => l.id) }), []);
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
  const expectedQuestions = Object.entries(originalQuestions).filter(([key, value]) => key.startsWith(subject.id + '/') && value[0] === previous.id);
  for (const [key] of expectedQuestions) assert.ok(questions[key] && questions[key][0] === previous.id, `original question ${key} was lost or moved to another module`);
  rows.push({ subject: subject.title, module: module.title, originalLessons: previous.lessons.length, shortLessons: module.lessons.length,
    questions: module.lessons.reduce((n, l) => n + l.questionCount, 0), longestMinutes: Math.max(...module.lessons.map((l) => l.minutes)) });
}
const report = { originalLessons: original.subjects.reduce((n, s) => n + s.modules.reduce((n, m) => n + m.lessons.length, 0), 0),
  shortLessons: rows.reduce((n, r) => n + r.shortLessons, 0), originalQuestions: Object.keys(originalQuestions).length,
  questions: Object.keys(questions).length, modules: rows };
if (process.argv[4]) fs.writeFileSync(process.argv[4], JSON.stringify(report, null, 2) + '\n');
console.log(`${report.originalLessons} originals → ${report.shortLessons} short lessons; all ${report.originalQuestions} original questions retained across ${rows.length} modules.`);
