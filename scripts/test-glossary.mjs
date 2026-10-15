import test from 'node:test';
import assert from 'node:assert/strict';
import { inline, render } from '../markdown.js';
import { glossary, exactTerm, searchGlossary } from '../glossary.js';

test('dictionary entries resolve and searches include aliases', () => {
  assert.ok(glossary.length >= 150);
  for (const entry of glossary) assert.equal(exactTerm(entry.term, entry.subject)?.id, entry.id);
  assert.ok(searchGlossary('Postgres').some(e => e.term === 'PostgreSQL'));
  assert.equal(searchGlossary('nonexistentxyz').length, 0);
});
test('matching respects case, boundaries and longest phrases', () => {
  assert.equal(exactTerm('rest'), null);
  assert.ok(exactTerm('REST'));
  assert.equal((inline('Redis Redisish αRedis Redis_thing').match(/data-term=/g)||[]).length, 1);
  assert.equal((inline('binary search tree').match(/data-term=/g)||[]).length, 1);
});
test('code and existing links stay safe and unnested', () => {
  assert.match(inline('`Redis`'), /<button[^>]+><code>Redis<\/code><\/button>/);
  assert.doesNotMatch(inline('`redis.get(key)`'), /<button/);
  assert.doesNotMatch(inline('[`Redis`](https://redis.io) [Redis](https://redis.io)'), /<button/);
  assert.doesNotMatch(render('```js\nRedis.get(key)\n```'), /data-term/);
  assert.doesNotMatch(inline('<img src=x onerror=alert(1)> Redis'), /<img/);
});
test('escaped generic code terms link without unescaping displayed markup', () => {
  const options = { subject: 'languages' };
  const entry = exactTerm('Box<T>', options.subject);
  assert.ok(entry);
  const linked = inline('`Box<T>`', options);
  assert.ok(linked.includes(`data-term="${entry.id}"`));
  assert.match(linked, /<code>Box&lt;T&gt;<\/code>/);
  assert.equal((inline('`Box<T>` and `Box<Expr>`', { ...options, seen: new Set() }).match(/data-term=/g) || []).length, 1);
  assert.doesNotMatch(inline('`Box&lt;T&gt;`', options), /data-term=/);
  assert.doesNotMatch(inline('[`Box<T>`](https://doc.rust-lang.org/)', options), /data-term=/);
  const unsafe = inline('`Box<T><img src=x onerror=alert(1)>`', options);
  assert.doesNotMatch(unsafe, /<img|data-term=/);
  assert.match(unsafe, /&lt;img/);
});
test('noninteractive content never gains dictionary buttons', () => {
  const source = '# Redis\n\nRedis and `Redis`\n\n- Redis\n\n| Redis | SQL |\n|---|---|\n| Redis | SQL |\n\n> [!note] Redis\n> Redis';
  assert.doesNotMatch(render(source, {interactive:false}), /<button/);
  assert.doesNotMatch(render(source, {terms:false}), /data-term/);
  assert.match(render(source), /data-term="redis"/);
});

test('subject terms win inside their subject; short aliases never leak to other subjects', async () => {
  const { exactTerm: find } = await import('../glossary.js');
  for (const e of glossary.filter((x) => x.subject)) assert.equal(find(e.term, e.subject)?.id, e.id);
});
test('short aliases are scoped to their subject; acronyms match exact case', async () => {
  const { isScoped, aliasKey } = await import('../glossary-rules.js');
  const t = { subject: 'synth' };
  assert.ok(isScoped(t, 'DAC') && isScoped(t, 'dB') && isScoped(t, 'I²S') && isScoped(t, 'm/s'));
  assert.ok(!isScoped(t, 'sample rate') && !isScoped(t, 'op-amp') && !isScoped({}, 'DAC'));
  assert.notEqual(aliasKey('PA'), aliasKey('Pa'));
  const { fallsBack } = await import('../glossary-rules.js');
  assert.ok(fallsBack(t, 'tree depth') && fallsBack(t, 'low-pass') && !fallsBack(t, 'depth') && !fallsBack({}, 'tree depth'));
  assert.equal(aliasKey('Sample Rate'), aliasKey('sample rate'));
});

test('word buckets preserve literal punctuation, longest phrases and Unicode boundaries', () => {
  for (const [subject, label] of [
    ['system-design', 'binary search tree'],
    ['system-design', 'HTTP/2'],
    ['system-design', 'cache-aside'],
    ['synth', 'm/s'],
    ['synth', 'I²S'],
    ['synth', 'dB'],
  ]) {
    const entry = exactTerm(label, subject);
    assert.ok(entry, label + ' must exist in the dictionary');
    assert.match(inline(`(${label}), ${label}.`, { subject }), new RegExp(`data-term="${entry.id}"`));
  }
  assert.doesNotMatch(inline('1-Redis αRedis Redis_thing Redisish'), /data-term=/);
  assert.doesNotMatch(inline('rest and http/2', { subject: 'system-design' }), /data-term=/);
});

test('dictionary searches retain alphabetical order without exposing their cached order', () => {
  const entries = searchGlossary();
  const firstId = entries[0].id;
  entries.reverse();
  assert.equal(searchGlossary()[0].id, firstId);
  const compare = new Intl.Collator('en', { sensitivity: 'base' }).compare;
  const results = searchGlossary('cache');
  assert.ok(results.length > 1);
  assert.ok(results.every((entry, i) => !i || compare(results[i - 1].term, entry.term) <= 0));
});
