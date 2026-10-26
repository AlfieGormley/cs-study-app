import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { inspectConceptReview } from './audit-concept-first.mjs';
import { lessonHash } from './verification.mjs';

function fixture(run) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'concept-review-'));
  const module = { id: 'demo', lessons: ['active'] };
  const question = { id: 'active-q1', type: 'single', answer: 0, options: [{ text: 'A' }, { text: 'B' }] };
  const baseline = { lessons: [{ id: 'active', questions: [structuredClone(question)] }] };
  const write = (file, value) => fs.writeFileSync(path.join(directory, file), typeof value === 'string' ? value : JSON.stringify(value));
  write('active.md', 'A complete explanation.');
  write('active.questions.json', [question]);
  write('archived.md', '```formula\nx = y\n```');
  const author = { agent: 'author', date: '2026-10-26' };
  const verifier = { agent: 'verifier', date: '2026-10-26', independent: true, sources: ['https://example.test/primary'] };
  const record = { module: module.id, author, verifier,
    summary: { claimsChecked: 1, errorsCorrected: 0, hedgedOrRemoved: 0 },
    corrections: [], gaps: [], lowConfidence: [], lessons: { active: { confidence: 'high' } }, glossary: {},
    conceptFirstReview: { ruleVersion: 1, author, verifier,
      lessons: { active: { rationale: 'The visible explanation teaches the decision without unnecessary arithmetic.', questionsRewritten: {} } } } };
  const save = () => write('verification.json', record);
  const stampFixture = () => {
    record.lessons.active.hash = lessonHash(directory, 'active');
    record.conceptFirstReview.lessons.active.hash = record.lessons.active.hash;
    save();
  };
  stampFixture();
  const inspect = () => inspectConceptReview(directory, module, baseline);
  try { run({ directory, module, baseline, question, record, write, save, stampFixture, inspect }); }
  finally { fs.rmSync(directory, { recursive: true, force: true }); }
}

test('concept review audits active lessons without treating archives as live content', () => fixture(({ inspect }) => {
  const result = inspect();
  assert.equal(result.reviewed, true);
  assert.equal(result.lessons.length, 1);
}));

test('a semantic review requires distinct identities, sources and current hashes', () => {
  for (const mutate of [
    r => { r.conceptFirstReview.verifier = { ...r.verifier, agent: 'author' }; },
    r => { r.conceptFirstReview.verifier = { ...r.verifier, sources: [] }; },
    r => { r.conceptFirstReview.lessons.active.hash = 'old'; },
    r => { delete r.conceptFirstReview; },
  ]) fixture(({ record, save, inspect }) => {
    mutate(record); save(); assert.equal(inspect().reviewed, false);
  });
});

test('changed questions need an explicit independent review reason even with fresh source hashes', () => fixture(({ question, record, write, stampFixture, save, inspect }) => {
  question.answer = 1;
  write('active.questions.json', [question]); stampFixture();
  assert.equal(inspect().reviewed, false);
  assert.match(inspect().lessons[0].problems.join(), /lacks a review reason/);
  record.conceptFirstReview.lessons.active.questionsRewritten[question.id] = 'Rewritten to diagnose the same underlying misconception.';
  save();
  assert.equal(inspect().reviewed, true);
  assert.equal(inspect().lessons[0].changedQuestions, 1);
}));

test('reviewed modules cannot lose, replace or duplicate saved question identities', () => {
  for (const change of [() => [], q => [{ ...q, id: 'replacement' }], q => [q, q]])
    fixture(({ question, write, stampFixture, inspect }) => {
      write('active.questions.json', change(question)); stampFixture();
      assert.equal(inspect().reviewed, false);
    });
});

test('reviewed modules preserve active lesson identities and question ownership', () => {
  fixture(({ baseline, inspect }) => {
    baseline.lessons.push({ id: 'missing', questions: [] });
    assert.equal(inspect().reviewed, false);
    assert.match(inspect().problems.join(), /Active lesson id lost/);
  });
  fixture(({ baseline, inspect }) => {
    baseline.lessons[0].id = 'original';
    assert.equal(inspect().reviewed, false);
    assert.match(inspect().problems.join(), /added or replaced/);
    assert.match(inspect().lessons[0].problems.join(), /moved from its saved lesson/);
  });
  fixture(({ module, inspect }) => {
    module.lessons.push('active');
    assert.equal(inspect().reviewed, false);
    assert.match(inspect().problems.join(), /Duplicate active lesson/);
  });
});

test('reviewed equations need a deliberate essential or reference choice', () => fixture(({ write, stampFixture, inspect }) => {
  const formula = mode => '```formula' + mode + '\nx = 1\nwhere\nx: count\nIn words: There is one item.\n```';
  for (const mode of ['', ' optional', ' reference essential']) {
    write('active.md', formula(mode)); stampFixture();
    assert.equal(inspect().reviewed, false);
  }
  for (const mode of [' essential', ' reference']) {
    write('active.md', formula(mode)); stampFixture();
    assert.equal(inspect().reviewed, true);
  }
}));
