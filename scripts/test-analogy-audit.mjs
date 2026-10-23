import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { inspectAnalogies, auditAnalogies, analogySummaryCsv } from './audit-analogies.mjs';
import { lessonHash } from './verification.mjs';

const analogy = '> [!analogy] Real-world analogy: a desk\n> A reference is kept close by.\n>\n> **How it maps:** Repeated access can use a nearby copy.\n>\n> **Where it stops:** Copies may need explicit invalidation.';

test('audit distinguishes explicit disclosures, visible review leads and literal code', () => {
  const result = inspectAnalogies('---\nid: sample\n---\n\nThink of a desk.\n\n' + analogy + '\n\n```text\n> [!analogy] Literal example\nThink of a desk.\n```');
  assert.equal(result.blocks.length, 1);
  assert.deepEqual(result.blocks[0].problems, []);
  assert.equal(result.candidates.length, 1);
  assert.equal(result.candidates[0].line, 5);
  assert.equal(inspectAnalogies('> [!analogy]\n> A comparison without mapping or limits.').blocks[0].problems.length, 3);
  assert.ok(inspectAnalogies(analogy + '\n> ```formula\n> x = 1\n> ```').blocks[0].problems.some(p => p.includes('formulas')));
});

test('audit excludes archives, checks question fields, and rejects stale semantic reviews', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'analogy-audit-'));
  try {
    const modulePath = path.join(root, 'content/sample/01-start');
    fs.mkdirSync(modulePath, { recursive: true });
    const json = (file, value) => fs.writeFileSync(file, JSON.stringify(value));
    json(path.join(root, 'content/sample/subject.json'), { id: 'sample', title: 'Sample' });
    json(path.join(modulePath, 'module.json'), { id: 'start', title: 'Start', lessons: ['current'] });
    fs.writeFileSync(path.join(modulePath, 'current.md'), '---\nid: current\ntitle: Current\nlevel: basic\n---\n' + analogy);
    fs.writeFileSync(path.join(modulePath, 'archived.md'), 'Think of a desk.');
    json(path.join(modulePath, 'current.questions.json'), [{ id: 'q1', prompt: analogy, workedExample: analogy, options: [{ text: 'Answer', explanation: 'Explanation' }] }]);
    const hash = lessonHash(modulePath, 'current');
    const verification = { lessons: { current: { hash } }, analogyReview: { ruleVersion: 1, author: { agent: 'author' }, verifier: { agent: 'reviewer', independent: true, sources: ['https://example.com/primary-source'] }, lessons: { current: { decision: 'added', rationale: 'Explains access locality.', hash } } } };
    json(path.join(modulePath, 'verification.json'), verification);
    const report = auditAnalogies(root);
    assert.equal(report.totals.lessons, 1);
    assert.equal(report.totals.independentlyReviewed, 1);
    assert.equal(report.totals.visibleComparisonCandidates, 0);
    assert.equal(report.totals.formatIssues, 1);
    assert.match(analogySummaryCsv(report), /"Sample","Start","1","1","0","0","1","1"/);
    assert.match(report.subjects[0].modules[0].lessons[0].issues[0], /q1: analogy disclosure in prompt/);
    verification.analogyFeedbackReview = verification.analogyReview;
    delete verification.analogyReview;
    json(path.join(modulePath, 'verification.json'), verification);
    assert.equal(auditAnalogies(root).totals.independentlyReviewed, 0);
    assert.equal(auditAnalogies(root).totals.feedbackOnlyReviewed, 1);
    verification.analogyFeedbackReview.questions = { q1: { lesson: 'current', ...verification.analogyFeedbackReview.lessons.current } };
    delete verification.analogyFeedbackReview.lessons;
    json(path.join(modulePath, 'verification.json'), verification);
    assert.equal(auditAnalogies(root).totals.feedbackOnlyReviewed, 1);
    fs.appendFileSync(path.join(modulePath, 'current.md'), '\nChanged.');
    assert.equal(auditAnalogies(root).totals.independentlyReviewed, 0);
    assert.equal(auditAnalogies(root).totals.feedbackOnlyReviewed, 0);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
