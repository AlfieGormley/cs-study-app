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
  const html = render('> [!example]\n> ```flow\n> Source\n> Execute\n> ```\n\n| A | B |\n|---|---|\n| 1 | 2 |', { interactive: false });
  assert.ok(!/<button|<details|tabindex=/.test(html));
  assert.ok(html.includes('<svg'));
  assert.ok(html.includes('<table>'));
});

test('text diagrams with Unicode arrows and ordinary code both stay available', () => {
  assert.ok(render('```diagram\nUncompiled source\n```').includes('Uncompiled source'));
  const html = render('```js\nconst count = 2;\n```');
  assert.ok(html.includes('is-code'));
  assert.ok(html.includes('<code>const count = 2;</code>'));
});
