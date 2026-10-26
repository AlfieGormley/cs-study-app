import test from 'node:test';
import assert from 'node:assert/strict';
import { retireSubjects } from '../subject-retirement.js';

const item = (s, qid) => ({ s, m: 'module', l: 'lesson', qid });
const session = () => ({ id: 'saved', title: 'Mixed quiz', back: '#/practice',
  items: [item('os', 'q1'), item('react', 'q2'), item('theory', 'q3')],
  i: 1, picked: [2], checked: true, results: [{ s: 'os', qid: 'q1', ok: true }, { s: 'react', qid: 'q2', ok: true }],
  currentQuestion: { key: 'react/q2', index: 1, question: { id: 'q2', answer: 2 } } });

test('retirement removes only requested subject progress and is idempotent', () => {
  const state = { last: 'os/module/lesson', days: ['2026-10-26'], fontScale: 1.2 };
  for (const key of ['done', 'answers', 'bookmarks', 'pos', 'lessonMigrations'])
    state[key] = { 'os/old': 42, 'react/kept': 87, 'other/unknown': 99 };
  assert.equal(retireSubjects(state, ['os']), true);
  for (const key of ['done', 'answers', 'bookmarks', 'pos', 'lessonMigrations'])
    assert.deepEqual(state[key], { 'react/kept': 87, 'other/unknown': 99 });
  assert.equal(state.last, null);
  assert.deepEqual(state.days, ['2026-10-26']);
  assert.equal(state.fontScale, 1.2);
  assert.equal(retireSubjects(state, ['os']), false);
});

test('mixed quiz preserves current retained question, selection and result without regrading', () => {
  const state = { session: session() };
  retireSubjects(state, ['os', 'theory']);
  assert.equal(state.session.i, 0);
  assert.deepEqual(state.session.items, [item('react', 'q2')]);
  assert.equal(state.session.currentQuestion.index, 0);
  assert.equal(state.session.currentQuestion.question.answer, 2);
  assert.deepEqual(state.session.picked, [2]);
  assert.equal(state.session.checked, true);
  assert.deepEqual(state.session.results, [{ s: 'react', qid: 'q2', ok: true }]);
  assert.equal(retireSubjects(state, ['os', 'theory']), false);
});

test('removed current question cannot survive through its saved snapshot', () => {
  const ses = session();
  ses.i = 0;
  ses.currentQuestion = { key: 'os/q1', index: 0, question: { id: 'q1' } };
  const state = { session: ses };
  retireSubjects(state, ['os', 'theory']);
  assert.equal(ses.items[ses.i].s, 'react');
  assert.equal(ses.currentQuestion, undefined);
  assert.deepEqual(ses.picked, []);
  assert.equal(ses.checked, false);
  assert.equal(ses.back, '#/practice');
});

test('wholly retired quiz is cleared and unaffected quizzes remain byte-identical', () => {
  const state = { session: session() };
  const before = JSON.stringify(state);
  assert.equal(retireSubjects(state, ['architecture']), false);
  assert.equal(JSON.stringify(state), before);
  retireSubjects(state, ['os', 'react', 'theory']);
  assert.equal(state.session, null);
});
