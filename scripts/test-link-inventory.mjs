import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { linkFiles } from './link-inventory.mjs';

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'study-link-inventory-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  function write(relative, value) {
    const file = path.join(root, relative);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, typeof value === 'string' ? value : JSON.stringify(value));
    return file;
  }
  return { root, write };
}

test('active link scope follows the manifest and excludes archived and verification files', t => {
  const { root, write } = fixture(t);
  write('subject/01-topic/module.json', { lessons: ['live'] });
  const lesson = write('subject/01-topic/live.md', '[Active link](https://active.test)');
  const questions = write('subject/01-topic/live.questions.json', [{ link: { url: 'https://question.test' } }]);
  write('subject/01-topic/old.md', '[Archived link](https://archive.test)');
  write('subject/01-topic/old.questions.json', []);
  write('subject/01-topic/verification.json', { url: 'https://evidence.test' });
  write('subject/01-topic/glossary.json', [{ source: 'https://dictionary.test' }]);
  assert.deepEqual(linkFiles(root, root, { activeOnly: true }), [lesson, questions]);
  assert.equal(linkFiles(root).length, 7, 'default scope retains the archive inventory');
});

test('link scope respects path boundaries and supports one active file', t => {
  const { root, write } = fixture(t);
  for (const name of ['01-topic', '01-topic-extra']) {
    write(`${name}/module.json`, { lessons: ['live'] });
    write(`${name}/live.md`, 'Lesson');
    write(`${name}/live.questions.json`, []);
  }
  const scope = path.join(root, '01-topic');
  assert.equal(linkFiles(root, scope).length, 3);
  assert.equal(linkFiles(root, scope, { activeOnly: true }).length, 2);
  const lesson = path.join(scope, 'live.md');
  assert.deepEqual(linkFiles(root, lesson, { activeOnly: true }), [lesson]);
});

test('a missing active question file fails rather than silently reducing link coverage', t => {
  const { root, write } = fixture(t);
  write('module/module.json', { lessons: ['live'] });
  write('module/live.md', 'Lesson');
  assert.throws(() => linkFiles(root, root, { activeOnly: true }), /ENOENT/);
});
