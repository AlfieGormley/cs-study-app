import test from 'node:test';
import assert from 'node:assert/strict';
import { render } from '../markdown.js';

test('examples escape source text and expose a faithful copy source', () => {
  const html = render('```html\n<script>alert("x")</script> & data\n```');
  assert.ok(!html.includes('<script>'));
  assert.ok(html.includes('&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; &amp; data'));
  assert.ok(html.includes('HTML example'));
  assert.ok(html.includes('class="example-source"'));
});

test('compiled diagram retains the original source as a text alternative', () => {
  const html = render('```flow\nSource\nCompile\nExecute\n```');
  assert.ok(html.includes('vector-diagram'));
  assert.ok(html.includes('<path'));
  assert.ok(html.includes('Text version'));
  assert.ok(html.includes('Source\nCompile\nExecute'));
});

test('explicit flow blocks use vector nodes while code stays code', () => {
  const code = render('```python\nx = a -> b\n```');
  assert.ok(!code.includes('<svg'));
  const flow = render('```flow\nSource\nCompile\nExecute\n```');
  assert.ok(flow.includes('data-diagram-type="flow"'));
  assert.ok(flow.includes('<rect'));
});

test('answer choices never contain nested controls, including callouts and tables', () => {
  const html = render('> [!analogy] Real-world analogy\n> Optional comparison.\n\n> [!example]\n> ```flow\n> Source\n> Execute\n> ```\n\n| A | B |\n|---|---|\n| 1 | 2 |', { interactive: false });
  assert.ok(!/<button|<details|tabindex=/.test(html));
  assert.ok(html.includes('<svg'));
  assert.ok(html.includes('<table>'));
});

test('analogy disclosures start closed and keep subsequent technical content visible', () => {
  const html = render('> [!analogy] Real-world analogy: a desk\n> **How it maps:** Redis keeps frequently used values nearby.\n>\n> **Where it stops:** A desk does not expire entries.\n\n## The mechanism\n\nThe technical explanation.');
  assert.match(html, /<details class="callout callout-analogy"><summary>Real-world analogy: a desk<\/summary>/);
  assert.doesNotMatch(html, /<details[^>]*\bopen\b/);
  assert.match(html, /<strong>How it maps:<\/strong>/);
  assert.match(html, /<strong>Where it stops:<\/strong>/);
  assert.match(html, /<\/details><h2>The mechanism<\/h2><p>The technical explanation\.<\/p>/);
});

test('analogy summaries escape markup and contain no nested links or glossary controls', () => {
  const html = render('> [!analogy] [Redis](https://redis.io) <script>alert(1)</script>\n> Redis is still linked in the body.');
  const summary = html.match(/<summary>(.*?)<\/summary>/)[1];
  assert.doesNotMatch(summary, /<a\b|<button\b|<script>/);
  assert.match(summary, /&lt;script&gt;/);
  assert.match(html.split('</summary>')[1], /data-term="redis"/);
});

test('closed analogy terms do not consume glossary links in the visible explanation', () => {
  const html = render('> [!analogy]\n> Redis is like keeping a note nearby.\n\nRedis is the technical example.');
  assert.equal((html.match(/data-term="redis"/g) || []).length, 2);
  assert.match(html, /<summary>Real-world analogy<\/summary>/);
  assert.match(html, /<\/details><p><button[^>]*data-term="redis"/);
  assert.doesNotMatch(render('> [!note] A note\n> Always visible.'), /<details/);
});

test('text diagrams with Unicode arrows and ordinary code both stay available', () => {
  assert.ok(render('```diagram\nUncompiled source\n```').includes('Uncompiled source'));
  const html = render('```js\nconst count = 2;\n```');
  assert.ok(html.includes('is-code'));
  assert.ok(html.includes('<code>const count = 2;</code>'));
});

test('text written on a closing fence line becomes its own paragraph', () => {
  const html = render('```python\nx = 1\n``` Then this shows.\n\nNext.');
  assert.ok(html.includes('<p>Then this shows.</p>'));
  assert.ok(html.includes('<p>Next.</p>'));
});
