import test from 'node:test';
import assert from 'node:assert/strict';
import { sessionQuestion, advanceSession } from '../quiz-session.js';

const item = { s: 'example', m: 'module', l: 'lesson', qid: 'q1' };
const original = () => ({ id: 'q1', type: 'single', prompt: 'Original question', options: [{ text: 'Old A' }, { text: 'Old B' }], answer: 1 });
const session = () => ({ i: 0, picked: [], checked: false, results: [] });

test('a paused question keeps its original text, options and answer after an update', () => {
  const s = session(), q = original();
  sessionQuestion(s, item, q, 'Original lesson');
  s.picked = [1];
  q.prompt = 'Updated question'; q.options.reverse(); q.answer = 0;
  const restored = sessionQuestion(JSON.parse(JSON.stringify(s)), item, q, 'Updated lesson');
  assert.deepEqual(restored.question, original());
  assert.equal(restored.lessonTitle, 'Original lesson');
  assert.deepEqual(s.picked, [1]);
});

test('a checked snapshot remains available even if the live question is removed', () => {
  const s = session();
  sessionQuestion(s, item, original(), 'Lesson');
  s.picked = [1]; s.checked = true; s.results.push({ ...item, ok: true });
  const restored = sessionQuestion(s, item, undefined, undefined);
  assert.equal(restored.kind, 'question');
  assert.equal(restored.question.answer, 1);
  assert.deepEqual(s.results, [{ ...item, ok: true }]);
});

test('legacy checked answers retain recorded correctness without regrading new options', () => {
  const s = { ...session(), checked: true, picked: [1], results: [{ ...item, ok: true }] };
  const before = structuredClone(s);
  const restored = sessionQuestion(s, item, { ...original(), answer: 0 }, 'Lesson');
  assert.equal(restored.kind, 'recorded');
  assert.equal(restored.result.ok, true);
  assert.deepEqual(s, before);
});

test('legacy unchecked option numbers are cleared once, without losing earlier results', () => {
  const s = { ...session(), picked: [1], results: [{ ...item, qid: 'earlier', ok: false }] };
  const restored = sessionQuestion(s, item, original(), 'Lesson');
  assert.equal(restored.selectionReset, true);
  assert.deepEqual(s.picked, []);
  s.picked = [0];
  sessionQuestion(s, item, { ...original(), answer: 0 }, 'Lesson');
  assert.deepEqual(s.picked, [0]);
  assert.equal(s.results[0].ok, false);
});

test('advancing drops only the current snapshot and keeps previous results', () => {
  const s = session();
  sessionQuestion(s, item, original(), 'Lesson');
  s.checked = true; s.picked = [1]; s.results = [{ ...item, ok: true }];
  advanceSession(s);
  assert.equal(s.i, 1);
  assert.equal(s.currentQuestion, undefined);
  assert.deepEqual(s.picked, []);
  assert.equal(s.checked, false);
  assert.deepEqual(s.results, [{ ...item, ok: true }]);
});

test('a missing unanswered question does not fabricate a snapshot or result', () => {
  const s = session();
  assert.equal(sessionQuestion(s, item, undefined, undefined).kind, 'missing');
  assert.equal(s.currentQuestion, undefined);
  assert.deepEqual(s.results, []);
});
