import test from 'node:test';
import assert from 'node:assert/strict';
import { inline, render } from '../markdown.js';
import { glossary, exactTerm, searchGlossary } from '../glossary.js';

test('dictionary entries resolve and searches include aliases', () => {
  assert.ok(glossary.length >= 150);
  for (const entry of glossary) assert.equal(exactTerm(entry.term)?.id, entry.id);
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
test('noninteractive content never gains dictionary buttons', () => {
  const source = '# Redis\n\nRedis and `Redis`\n\n- Redis\n\n| Redis | SQL |\n|---|---|\n| Redis | SQL |\n\n> [!note] Redis\n> Redis';
  assert.doesNotMatch(render(source, {interactive:false}), /<button/);
  assert.doesNotMatch(render(source, {terms:false}), /data-term/);
  assert.match(render(source), /data-term="redis"/);
});
