---
id: logp-propositional-truth-table-code
title: Checking finite truth tables in code
level: basic
minutes: 3
sourceLesson: logp-propositional
summary: An exhaustive truth table proves an equivalence over its specified Boolean inputs.
---

## Checking equivalence in code

With n variables there are only 2 to the power n rows, so a computer can check any equivalence by brute force.

```python
from itertools import product

def equivalent(f, g, n):
    # Visit every Boolean assignment.
    for v in product([False, True],
                     repeat=n):
        # Unpack inputs; stop at a mismatch.
        if f(*v) != g(*v):
            return False, v
    # All rows matched: no counterexample.
    return True, None

imp = lambda p, q: (not p) or q
contra = lambda p, q: imp(not q, not p)
conv = lambda p, q: imp(q, p)

# Same truth values for all four pairs.
print(equivalent(imp, contra, 2))
# A false premise separates the converse.
print(equivalent(imp, conv, 2))
```

The output is `(True, None)` then `(False, (False, True))`. The second line hands you a counterexample: with p false and q true, p implies q is true but its converse q implies p is false.

How far does brute force go? Count the rows:

Twenty inputs already need about a million rows. Every additional input doubles that work; sixty need over a billion billion rows.

This is often practical for small numbers of Boolean inputs. Exhaustive work at sixty variables is far larger; the actual runtime depends on the cost of evaluating each row. That gap is the subject of the SAT lesson.


## Precedence

By convention, ¬ binds tightest, then ∧, then ∨, then →, then ↔. Implication is usually read right-associatively (grouped from the right):

```formula essential
¬p ∧ q → r   means   ((¬p) ∧ q) → r
p → q → r    means   p → (q → r)
where
p, q, r: propositions, each true or false
¬: NOT: applies only to the thing directly after it
∧: AND: binds more tightly than → (it is grouped first)
→: implies: binds more loosely than ¬ and ∧
In words: NOT is applied first, then AND, then OR, then implication; a chain of implications groups from the right.
```

Python follows the same order for `not`, `and`, `or`. When in doubt, add brackets: other people will read the code too.


## Key takeaways
- An exhaustive truth table proves an equivalence over its specified Boolean inputs.
- Exponential growth makes exhaustive enumeration impractical for many variables; explicit brackets clarify grouping.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Functional completeness — Wikipedia](https://en.wikipedia.org/wiki/Functional_completeness)
