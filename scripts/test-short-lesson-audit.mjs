import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { lessonHash } from './verification.mjs';

const script = fileURLToPath(new URL('./audit-short-lessons.mjs', import.meta.url));

function fixture(run) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'short-lesson-audit-'));
  const write = (file, value) => {
    const target = path.join(root, file);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, JSON.stringify(value));
  };
  const q1 = { id: 'q1', type: 'single', answer: 0, options: [{}, {}] };
  const q2 = { id: 'q2', type: 'multi', answer: [0, 1], options: [{}, {}, {}] };
  const short = (id, sourceLesson) => ({ id, sourceLesson, minutes: 3, questionCount: 1 });
  const original = { subjects: [{ id: 'study', title: 'Study', modules: [
    { id: 'converted', title: 'Converted', lessons: [{ id: 'old-one' }, { id: 'old-two' }] },
    { id: 'untouched', title: 'Untouched', lessons: [{ id: 'old-three' }] }
  ] }] };
  const current = structuredClone(original);
  Object.assign(current.subjects[0].modules[0], {
    migrations: { 'old-one': ['new-one'], 'old-two': ['new-two'] },
    lessons: [short('new-one', 'old-one'), short('new-two', 'old-two')]
  });
  const compiled = { lessons: [{ id: 'new-one', questions: [q1] }, { id: 'new-two', questions: [q2] }] };
  const questionIndex = { 'study/q1': ['converted', 'new-one'], 'study/q2': ['converted', 'new-two'], 'study/q3': ['untouched', 'old-three'] };
  write('original-index.json', original);
  write('original-questions.json', { 'study/q1': ['converted', 'old-one'], 'study/q2': ['converted', 'old-two'], 'study/q3': ['untouched', 'old-three'] });
  write('data/index.json', current);
  write('data/questions.json', questionIndex);
  write('data/study/converted.json', compiled);
  write('content/study/01-converted/module.json', { id: 'converted' });
  write('content/study/01-converted/old-one.questions.json', [q1]);
  write('content/study/01-converted/old-two.questions.json', [q2]);
  const audit = (partial = true) => spawnSync(process.execPath,
    [script, 'original-index.json', 'original-questions.json', 'report.json', ...(partial ? ['--partial'] : [])],
    { cwd: root, encoding: 'utf8' });
  try { run({ root, write, compiled, questionIndex, audit }); }
  finally { fs.rmSync(root, { recursive: true, force: true }); }
}

test('partial release audits converted answers and preserves all course question IDs', () => fixture(({ root, audit }) => {
  const result = audit();
  assert.equal(result.status, 0, result.stderr);
  const report = JSON.parse(fs.readFileSync(path.join(root, 'report.json'), 'utf8'));
  assert.equal(report.convertedOriginalLessons, 2);
  assert.equal(report.shortLessons, 2);
  assert.equal(report.originalQuestions, 3);
  assert.equal(report.pendingModules, 1);
}));

test('full audit rejects an unfinished course', () => fixture(({ audit }) => {
  const result = audit(false);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /lessons outside its migrations/);
}));

test('explicit retirement excludes a subject but an unlisted missing subject still fails', () => fixture(({ write, audit }) => {
  write('data/index.json', { subjects: [], retiredSubjects: ['study'] });
  write('data/questions.json', {});
  assert.equal(audit().status, 0);
  write('data/index.json', { subjects: [], retiredSubjects: [] });
  assert.notEqual(audit().status, 0);
}));

test('partial release rejects a lost question in an untouched module', () => fixture(({ write, questionIndex, audit }) => {
  delete questionIndex['study/q3'];
  write('data/questions.json', questionIndex);
  const result = audit();
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /original question study\/q3 was lost/);
}));

test('audit rejects changed single and multiple answer keys', () => {
  for (const [i, answer] of [[0, 1], [1, [0, 2]]]) fixture(({ write, compiled, audit }) => {
    compiled.lessons[i].questions[0].answer = answer;
    write('data/study/converted.json', compiled);
    const result = audit();
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /changed its answer key/);
  });
});

test('audit rejects duplicate questions and absent compiled questions', () => {
  for (const duplicate of [true, false]) fixture(({ write, compiled, audit }) => {
    if (duplicate) compiled.lessons[1].questions.push(compiled.lessons[0].questions[0]);
    else compiled.lessons[0].questions = [];
    write('data/study/converted.json', compiled);
    const result = audit();
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, duplicate ? /duplicate question q1/ : /q1 is absent from compiled lessons/);
  });
});

test('intentional question revisions require current independent review and matching compiled content', () => {
  for (const staleCompiled of [false, true]) fixture(({ root, write, compiled, audit }) => {
    compiled.lessons[0].questions[0].answer = 1;
    const directory = 'content/study/01-converted';
    const lessons = {};
    const editorial = {};
    for (const lesson of compiled.lessons) {
      const markdown = path.join(root, directory, `${lesson.id}.md`);
      fs.writeFileSync(markdown, 'The main concept and reasoning stay visible.');
      write(`${directory}/${lesson.id}.questions.json`, lesson.questions);
      const hash = lessonHash(path.join(root, directory), lesson.id);
      lessons[lesson.id] = { confidence: 'high', hash };
      editorial[lesson.id] = { hash, rationale: 'Reviewed the scenario, its conceptual objective and every answer option.',
        questionsRewritten: lesson.id === 'new-one' ? { q1: 'Replaced routine arithmetic with diagnosis of the same underlying concept.' } : {} };
    }
    const author = { agent: 'editor', date: '2026-10-26' };
    const verifier = { agent: 'reviewer', date: '2026-10-26', independent: true, sources: ['https://example.test/primary'] };
    write(`${directory}/verification.json`, { module: 'converted', author, verifier,
      summary: { claimsChecked: 2, errorsCorrected: 0, hedgedOrRemoved: 0 }, corrections: [], gaps: [], lowConfidence: [],
      lessons, glossary: {}, conceptFirstReview: { ruleVersion: 1, author, verifier, lessons: editorial } });
    if (staleCompiled) compiled.lessons[0].questions[0].options.push({ text: 'Unreviewed choice' });
    write('data/study/converted.json', compiled);
    const result = audit();
    if (staleCompiled) {
      assert.notEqual(result.status, 0);
      assert.match(result.stderr, /changed its answer key/);
    } else {
      assert.equal(result.status, 0, result.stderr);
      const report = JSON.parse(fs.readFileSync(path.join(root, 'report.json'), 'utf8'));
      assert.equal(report.reviewedQuestionRevisions.length, 1);
      assert.equal(report.reviewedQuestionRevisions[0].question, 'q1');
    }
  });
});
