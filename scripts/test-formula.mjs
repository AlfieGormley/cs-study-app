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
test('a quote after a letter is a prime, not a string', () => {
  assert.deepEqual(symbols("Y = A' + B'"), ['Y', "A'", "B'"]);
  assert.deepEqual(symbols("s = 'abc' + t"), ['s', 't']);
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

const formula = (equation, defs, words = 'The quantities are related by this equation.') =>
  `${equation}\nwhere\n${defs}\nIn words: ${words}`;
const equationHtml = (source) => render('```formula\n' + source + '\n```').match(/aria-label="Equation">([\s\S]*?)<\/div><div class="formula-where-label"/)[1];

test('implicit algebra uses defined factors and preserves named quantities', () => {
  const defs = 'f_c: cutoff frequency\nπ: pi\nR: resistance\nC: capacitance';
  assert.deepEqual(checkFormula(formula('f_c = 1 / (2πRC)', defs)), []);
  assert.match(checkFormula(formula('f_c = 1 / (2πRX)', defs)).join(), /undefined symbol/);
  assert.deepEqual(symbols('RC + RTT', new Set(['R', 'C', 'RTT'])), ['R', 'C', 'RTT']);
  assert.deepEqual(symbols('RC', new Set(['R', 'C', 'RC'])), ['RC']);
  assert.match(equationHtml(formula('f_c = 1 / (2πRC)', defs)), /2π<i>R<\/i><i>C<\/i>\)/);
});

test('bracket checking enforces grouping and supports continued equations, intervals and literal strings', () => {
  const defs = 'x: output\na: input\nb: input\nc: input\nf: function\ns: string\ni: start\nj: end';
  for (const eq of ['x = a / (b + c)', 'x = (a + b)^2', 'x = a / (b +\n  c)', 'x = [a, b)', 'x = (a, b]', 'x = f(s[i..j))', 'x = f("(")']) {
    assert.deepEqual(checkFormula(formula(eq, defs)), [], eq);
  }
  for (const eq of ['x = a / (b + c', 'x = (a + b]^2', 'x = a + b)', 'x = a / {b + c)', 'x = f(a, b]']) {
    assert.match(checkFormula(formula(eq, defs)).join(), /bracket/, eq);
  }
});

test('ordinary products become conventional algebra while denominator grouping stays visible', () => {
  const html = equationHtml(formula('f_c = 1 / (2 × π × R × C)', 'f_c: cutoff frequency\nπ: pi\nR: resistance\nC: capacitance'));
  assert.match(html, /1 \/ \(2π<i>R<\/i><i>C<\/i>\)/);
  assert.doesNotMatch(html, /×/);
  assert.match(equationHtml(formula('V = I × R', 'V: voltage\nI: current\nR: resistance')), /<i>I<\/i><i>R<\/i>/);
  assert.match(equationHtml(formula('x = a × (b + c)', 'x: output\na: coefficient\nb: input\nc: input')), /<i>a<\/i>\(<i>b<\/i> \+ <i>c<\/i>\)/);
  assert.match(equationHtml(formula('L = 20 × log_10(x)', 'L: level\nlog_10: base-ten logarithm\nx: ratio')), /20 log<sub>10<\/sub>\(<i>x<\/i>\)/);
});

test('explicit multiplication remains for numbers, names, units, sets, vectors and name collisions', () => {
  for (const [eq, defs] of [
    ['x = 2 × 3', 'x: result'],
    ['x = users × rate', 'x: result\nusers: user count\nrate: per-user rate'],
    ['x = m × s', 'x: result\nm: metres\ns: seconds'],
    ['C = A × B', 'C: Cartesian product\nA: first set\nB: second set'],
    ['c = (a + b) × (a − b)', 'c: cross product\na: first vector\nb: second vector'],
    ['x = R × T × T', 'x: result\nR: coefficient\nT: duration\nRTT: round trip time'],
  ]) assert.match(equationHtml(formula(eq, defs)), /×/, eq);
  assert.match(equationHtml(formula('x = ψ · φ', 'x: inner product\nψ: first quantum state\nφ: second quantum state')), /·/);
});

test('a product after division keeps its operator, including across continuation lines', () => {
  const defs = 'x: output\na: input\nb: input\nc: input\nd: input';
  assert.match(equationHtml(formula('x = a / b × c', defs)), /<i>a<\/i> \/ <i>b<\/i> × <i>c<\/i>/);
  const html = equationHtml(formula('x = a / (b × c\n  × d) × c', defs));
  assert.match(html, /<i>b<\/i><i>c<\/i>/);
  assert.match(html, /\) × <i>c<\/i>/);
});

test('powers retain their whole grouped exponent and do not absorb following arithmetic', () => {
  const defs = 'x: output\na: input\nb: input\nc: input\nn: input\nk_1: exponent';
  assert.match(equationHtml(formula('x = 10^(a / (b × c))', defs)), /10<sup>\(<i>a<\/i> \/ \(<i>b<\/i><i>c<\/i>\)\)<\/sup>/);
  assert.match(equationHtml(formula('x = 2^{n − 1}', defs)), /2<sup><i>n<\/i> − 1<\/sup>/);
  assert.match(equationHtml(formula('x = a^2+b', defs)), /<i>a<\/i><sup>2<\/sup>\+<i>b<\/i>/);
  assert.match(equationHtml(formula('x = 2^{-n+1}', defs)), /2<sup>-<i>n<\/i>\+1<\/sup>/);
  assert.match(equationHtml(formula('x = a^k_1', defs)), /<i>a<\/i><sup><i>k<\/i><sub>1<\/sub><\/sup>/);
  assert.match(equationHtml(formula('x = 2 ^ 3 ^ 2', defs)), /2<sup>3<sup>2<\/sup><\/sup>/);
  assert.match(equationHtml(formula('x = (2 ^ 3) ^ 2', defs)), /\(2<sup>3<\/sup>\)<sup>2<\/sup>/);
  assert.match(equationHtml(formula('x = 2^⌈n / 2⌉', defs)), /2<sup>⌈<i>n<\/i> \/ 2⌉<\/sup>/);
  assert.match(equationHtml(formula('x = |a|^2', defs)), /\|<i>a<\/i>\|<sup>2<\/sup>/);
  assert.match(equationHtml(formula('x = √2^√2', defs)), /\(√2\)<sup>√2<\/sup>/);
});

test('formula text and quoted strings stay escaped when rendering nested scripts', () => {
  const html = equationHtml(formula('x = a^{<img src=x onerror=alert(1)>} + "<script>"', 'x: output\na: input'));
  assert.doesNotMatch(html, /<img|<script>/);
  assert.match(html, /&lt;img/);
  assert.match(html, /&quot;&lt;script&gt;&quot;/);
});
test('glossary terms link once per section', () => {
  const html = render('## A\n\nRedis and Redis.\n\nRedis again.\n\n## B\n\nRedis.');
  assert.equal((html.match(/data-term="redis"/g) || []).length, 2);
});

test('ordered lists resume their numbering after a block', () => {
  assert.match(render('4. four\n5. five'), /<ol start="4">/);
  assert.doesNotMatch(render('1. one\n2. two'), /start=/);
});
