#!/usr/bin/env python3
"""Reproduce selected reviewed teaching examples; not a corpus fact certificate."""
from pathlib import Path
import math
import random
import re
import itertools
import json

ROOT = Path(__file__).resolve().parent.parent

def blocks(relative):
    return re.findall(r'```python\n(.*?)```', (ROOT / relative).read_text(), re.S)

# These exact source blocks were manually reviewed before execution. Only
# algorithm definitions are evaluated; this does not execute arbitrary fences.
heap = {}
exec(blocks('content/dsa/05-sorting-searching/sort-heapsort-lower-bound.md')[0], heap)
sparse = {}
s = blocks('content/dsa/10-advanced/adv-sparse-tables.md')
for block in s:
    exec(block, sparse)
rng = random.Random(20261004)
checks = 0
for n in range(65):
    a = [rng.randrange(-10, 11) for _ in range(n)]
    actual = a.copy()
    heap['heapsort'](actual)
    assert actual == sorted(a)
    checks += 1
    if n:
        table = sparse['build'](a)
        for l in range(n):
            for r in range(l, n):
                assert sparse['query'](table, l, r) == min(a[l:r+1])
                checks += 1
root = None
for key in [50, 30, 20, 40, 70]:
    root = sparse['insert'](root, key)
new = sparse['insert'](root, 45)
assert root.left.right.right is None
assert new.left.right.right.key == 45
assert new.right is root.right
Leaf, Concat = sparse['Leaf'], sparse['Concat']
rope = Concat(Concat(Leaf('Hello_'), Leaf('my_')),
              Concat(Leaf('na'), Leaf('me_is_Simon')))
for i, c in enumerate('Hello_my_name_is_Simon'):
    assert sparse['char_at'](rope, i) == c
    checks += 1

# Recompute probability examples and inspect the actual supplied algorithm.
ns = {}
code = blocks('content/theory/06-complexity/cplx-randomised-quantum.md')[0]
exec(code.split('for r in (')[0], ns)
assert math.isclose(ns['majority_error'](3), 7/27)
assert round(ns['majority_error'](101), 8) == 0.00027240
# Exhaust all random vectors for the 2x2 Freivalds worked example.
A, B = [[1,2],[3,4]], [[5,6],[7,8]]
bad = [[19,22],[43,51]]
def mul(m, v): return [sum(a*b for a,b in zip(row,v)) for row in m]
caught = sum(mul(A,mul(B,[a,b])) != mul(bad,[a,b])
             for a in [0,1] for b in [0,1])
assert caught == 2

# Regression counterexample: an additive residual-tree model is not bounded
# by the original training-target range. Two ordinary squared-error stumps,
# learning rate 1, training (0,0)->0, (0,1)->1, (1,0)->1.
x, y = [(0,0),(0,1),(1,0)], [0.,1.,1.]
f = [sum(y)/len(y)] * len(y)
prediction = sum(y)/len(y)
for feature in [0,1]:
    residual = [yi-fi for yi,fi in zip(y,f)]
    leaves = [sum(r for xi,r in zip(x,residual) if xi[feature]==v)
              / sum(xi[feature]==v for xi in x) for v in [0,1]]
    f = [fi + leaves[xi[feature]] for xi,fi in zip(x,f)]
    prediction += leaves[1]
assert math.isclose(prediction, 1.5) and prediction > max(y)
assert (80_000_000_000 - 13_476_831_232) // (524288*4096) == 30
assert sum(2**20 - 2**k + 1 for k in range(21)) == 19_922_966
copies = {}
exec(blocks('content/dsa/03-hashing/hash-resizing.md')[0], copies)
assert copies['total_copies'](1000, lambda c: c*2) == 1023
assert copies['total_copies'](1000, lambda c: c+10) == 49600
for n in range(1, 1001):
    assert copies['total_copies'](n, lambda c: c*2) < 2*n
assert sum((1000+i-1)//i for i in range(1,1001)) == 8053

nfa = {}
exec(blocks('content/theory/04-automata/auto-nfa.md')[0], nfa)
delta = {(0,'a'):{0,1}, (0,'b'):{0}, (1,'b'):{2}}
for n in range(9):
    for letters in itertools.product('ab', repeat=n):
        word = ''.join(letters)
        assert nfa['run_nfa'](delta,0,{2},word) == word.endswith('ab')
assert nfa['close']({(1,''):{2}, (2,''):{3}}, iter([1])) == {1,2,3}
assert len(set(itertools.permutations('BANANA'))) == 60
assert math.comb(9,3) == 84 and math.comb(7,3) == 35
assert 36**6 - 26**6 == 1_867_866_560

quantity = {}
source = next(b for b in blocks('content/software-engineering/01-principles/sep-error-handling.md')
              if 'class Quantity:' in b)
exec(source, quantity)
for value in [1, 42, 99]:
    assert quantity['Quantity'](value).value == value
for value in [True, 1.5, '3', 0, 100]:
    try:
        quantity['Quantity'](value)
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError(f'Quantity accepted invalid value {value!r}')
principles = 'content/software-engineering/01-principles/'
member = {}
exec(next(b for b in blocks(principles + 'sep-clean-code.md')
          if 'class Member:' in b), member)
people = [member['Member']('A', 'B', True, age) for age in [17, 18, 19]]
assert member['adult_member_names'](people) == ['A B']
for bits in itertools.product([False, True], repeat=2):
    calls = []
    env = {'dispatch': lambda order: calls.append(order)}
    from types import SimpleNamespace
    order = SimpleNamespace(paid=bits[0], items=['item'] if bits[1] else [])
    versions = [b for b in blocks(principles + 'sep-clean-code.md') if 'def ship(' in b]
    for source in versions:
        exec(source, env)
        calls.clear()
        env['ship'](order)
        assert bool(calls) == all(bits)
        calls.clear()
        env['ship'](None)
        assert not calls
flatteners = [b for b in blocks(principles + 'sep-dry-kiss-yagni.md') if 'def flatten(' in b]
for source in flatteners:
    env = {}
    exec(source, env)
    assert env['flatten']([1, [2, [], [3]], 4]) == [1, 2, 3, 4]
writing = json.loads((ROOT / principles / 'sep-writing-for-others.questions.json').read_text())
paid_source = re.search(r'```python\n(.*?)```', writing[9]['workedExample'], re.S).group(1)
paid = {}
exec(paid_source, paid)
assert paid['PaidOrder'](1, paid['datetime'](2026, 1, 1)).id == 1
for invalid in [None, '2026-01-01', 42]:
    try:
        paid['PaidOrder'](1, invalid)
    except TypeError:
        pass
    else:
        raise AssertionError('PaidOrder accepted invalid payment time')
normalise = {}
exec(re.search(r'```python\n(.*?)```', writing[11]['prompt'], re.S).group(1), normalise)
scores = [0, 2, 4]
assert normalise['normalise'](scores) is None and scores == [0, .5, 1]
scores = [-2, -1]
normalise['normalise'](scores)
assert max(scores) == 2  # Why the non-negative input contract is necessary.
print(f'PASS: {checks} heap/sparse-table/rope cases; 511 NFA strings; 1,000 resize bounds; counting, domain validation, guard clauses, flattening, persistence, probability, KV sizing and boosted-tree counterexample.')
