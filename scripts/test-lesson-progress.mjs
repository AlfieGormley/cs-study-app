import test from 'node:test';
import assert from 'node:assert/strict';
import { migrateLessonProgress, migratedLessonId, updateOriginalCompletion, migrationProblems, subjectMigrationProblems } from '../lesson-progress.js';

const module = { id: 'module', migrations: { long: ['short-a', 'short-b'] }, lessons: ['short-a', 'short-b'] };
const index = { subjects: [{ id: 's', modules: [module] }, { id: 'other', modules: [{ id: 'module', lessons: ['long'] }] }] };
const state = () => ({ done: { 's/long': 1234, 'other/long': 5678 }, answers: { 's/old-q1': { last: true } }, bookmarks: { 's/old-q1': 2468 }, pos: { 's/long': 100 }, last: 's/module/long', session: { items: [{ s: 's', m: 'module', l: 'long', qid: 'old-q1' }], i: 0 } });

test('existing completed lessons expand with the exact original completion date and retain all other progress', () => {
  const before = state(), after = structuredClone(before);
  assert.equal(migrateLessonProgress(after, index), true);
  assert.equal(after.done['s/short-a'], 1234);
  assert.equal(after.done['s/short-b'], 1234);
  assert.equal(after.done['s/long'], 1234);
  assert.equal(after.done['other/long'], 5678);
  for (const field of ['answers', 'bookmarks', 'pos', 'session']) assert.deepEqual(after[field], before[field]);
  assert.equal(after.last, 's/module/short-a');
});

test('an uncompleted original remains uncompleted and resumes at the first unfinished short lesson', () => {
  const progress = { done: { 's/short-a': 1111 }, last: 's/module/long' };
  migrateLessonProgress(progress, index);
  assert.equal(progress.done['s/short-b'], undefined);
  assert.equal(progress.last, 's/module/short-b');
  assert.equal(migratedLessonId('s', module, 'long', progress.done), 'short-b');
});

test('migration runs once and does not restore a short lesson the user unmarked', () => {
  const progress = state();
  migrateLessonProgress(progress, index);
  delete progress.done['s/short-b'];
  assert.equal(migrateLessonProgress(progress, index), false);
  assert.equal(progress.done['s/short-b'], undefined);
  assert.equal(migratedLessonId('s', module, 'long', progress.done), 'short-b');
  assert.equal(migratedLessonId('s', module, 'unrelated', progress.done), 'unrelated');
});

test('existing dates on individual short lessons are not overwritten during migration', () => {
  const progress = state();
  progress.done['s/short-a'] = 9999;
  migrateLessonProgress(progress, index);
  assert.equal(progress.done['s/short-a'], 9999);
  assert.equal(progress.done['s/short-b'], 1234);
});

test('a later release migrates newly split modules without restoring unmarked parts from an earlier release', () => {
  const progress = state();
  progress.done['s/later-long'] = 4321;
  migrateLessonProgress(progress, index);
  delete progress.done['s/short-b'];
  updateOriginalCompletion('s', module, { sourceLesson: 'long' }, progress.done);
  const updated = structuredClone(index);
  updated.subjects[0].modules.push({ id: 'later', lessons: ['later-a', 'later-b'], migrations: { 'later-long': ['later-a', 'later-b'] } });
  assert.equal(migrateLessonProgress(progress, updated), true);
  assert.equal(progress.done['s/later-a'], 4321);
  assert.equal(progress.done['s/later-b'], 4321);
  assert.equal(progress.done['s/short-a'], 1234);
  assert.equal(progress.done['s/short-b'], undefined);
  assert.equal(migrateLessonProgress(progress, updated), false);
});

test('original completion mirrors all short lessons, without changing individual dates', () => {
  const done = { 's/short-a': 1000, 's/short-b': 2000 };
  updateOriginalCompletion('s', module, { id: 'short-b', sourceLesson: 'long' }, done);
  assert.equal(done['s/long'], 2000);
  assert.equal(done['s/short-a'], 1000);
  delete done['s/short-b'];
  updateOriginalCompletion('s', module, { id: 'short-b', sourceLesson: 'long' }, done);
  assert.equal(done['s/long'], undefined);
  assert.equal(done['s/short-a'], 1000);
});

test('invalid or overlapping migrations are rejected before reaching devices', () => {
  assert.deepEqual(migrationProblems(module), []);
  assert.deepEqual(migrationProblems({ lessons: ['legacy'] }), []);
  for (const bad of [null, true, [], 'text']) if (bad !== null) assert.ok(migrationProblems({ lessons: [], migrations: bad }).length);
  assert.ok(migrationProblems({ lessons: ['long'], migrations: { long: ['long'] } }).length);
  assert.ok(migrationProblems({ lessons: ['a'], migrations: { x: ['a'], y: ['a'] } }).length);
  assert.ok(migrationProblems({ lessons: ['a'], migrations: { x: ['missing'] } }).length);
  assert.ok(migrationProblems({ lessons: ['a'], migrations: { x: 'a' } }).length);
  assert.ok(migrationProblems({ lessons: ['a', 'b'], migrations: { x: ['b', 'a'] } }).length);
});

test('a retired completion key cannot be reused or claimed by another module', () => {
  assert.deepEqual(subjectMigrationProblems([module, { lessons: ['unrelated'] }]), []);
  assert.ok(subjectMigrationProblems([module, { lessons: ['long'] }]).length);
  assert.ok(subjectMigrationProblems([module, { lessons: ['other'], migrations: { long: ['other'] } }]).length);
});
