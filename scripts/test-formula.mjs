import test from 'node:test';
import assert from 'node:assert/strict';
import { checkFormula, symbols, parseFormula } from '../formula.js';
import { render } from '../markdown.js';

const good = 'f = c / (2 × π × a)\nwhere\nf: beaming frequency, in hertz\nc: speed of sound, metres per second\nπ: pi, about 3.14159\na: cone radius, in metres\nIn words: bigger cones beam lower.';

test('symbols: Greek splits, Latin runs stay whole, numbers are not symbols', () => {
  assert.deepEqual(symbols('2πa'), ['π', 'a']);
  assert.deepEqual(symbols('RTT = 2 × d_{prop}'), ['RTT', 'd_prop']);
  assert.deepEqual(symbols('x = 1.5e3 + 0x1F'), ['x']);
  assert.deepEqual(symbols('V_out = V_in × R_2'), ['V_out', 'V_in', 'R_2']);
});
test('every symbol must be defined', () => {
  assert.deepEqual(checkFormula(good), []);
  assert.match(checkFormula('f = c / λ').join(), /where/);
  assert.match(checkFormula('f = c / λ\nwhere\nf: frequency\nc: speed').join(), /"λ"/);
  assert.match(checkFormula('y = x\nwhere\ny = output').join(), /symbol: meaning/);
  assert.deepEqual(checkFormula('v = 3 m/s\nwhere\nv: speed\nm/s: metres per second\nIn words: it moves 3 metres each second.'), []);
  assert.match(checkFormula('v = 3\nwhere\nv: speed').join(), /In words/);
  assert.equal(parseFormula(good).words, 'bigger cones beam lower.');
});
test('connective words need no definition and must not be defined', () => {
  assert.deepEqual(checkFormula('n^2 ≤ c × n   for all n ≥ n_0\nwhere\nn: input size\nc: a constant\nn_0: threshold\nIn words: eventually below.'), []);
  assert.match(checkFormula('a = b for x\nwhere\na: x\nb: y\nx: z\nfor: for\nIn words: w').join(), /connective/);
});
test('formula blocks render equation, definitions and plain reading', () => {
  const html = render('```formula\n' + good + '\n```');
  assert.match(html, /class="formula"/);
  assert.match(html, /<dt><i>f<\/i><\/dt>/);
  assert.match(html, /In words/);
  assert.match(render('```formula\nV_{out} = x^2\nwhere\nV_{out}: out\nx: in\n```'), /<i>V<\/i><sub>out<\/sub> = <i>x<\/i><sup>2<\/sup>/);
});
test('glossary terms link once per section', () => {
  const html = render('## A\n\nRedis and Redis.\n\nRedis again.\n\n## B\n\nRedis.');
  assert.equal((html.match(/data-term="redis"/g) || []).length, 2);
});

test('ordered lists resume their numbering after a block', () => {
  assert.match(render('4. four\n5. five'), /<ol start="4">/);
  assert.doesNotMatch(render('1. one\n2. two'), /start=/);
});
